"""
Chat API Router
Endpoints for AI assistant chat conversations.
"""

from fastapi import APIRouter, HTTPException, Path as PathParam
from typing import Dict, List, Optional
import logging
from datetime import datetime
import os
import uuid

from app.database import get_supabase, Tables
from app.models import ChatRequest, ChatResponse, ChatMessage
from app.services.chat_assistant import ChatAssistant


def validate_uuid(uuid_string: str, field_name: str = "ID") -> None:
    """Validate UUID format and raise 404 if invalid"""
    try:
        uuid.UUID(uuid_string)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=404,
            detail=f"Invalid {field_name} format"
        )


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])

# In-memory storage for active chat sessions (in production, use Redis)
active_chats: Dict[str, ChatAssistant] = {}


@router.post("/start/{analysis_id}", response_model=Dict)
async def start_chat(
    analysis_id: str = PathParam(..., description="ID of the analysis to discuss")
):
    """
    Start a new chat conversation about an analysis.
    
    Initializes the AI assistant with the analysis context.
    
    - **analysis_id**: ID of the completed analysis
    
    Returns:
    - **session_id**: Unique session ID for this conversation
    - **message**: Confirmation message
    - **mode**: AI mode (gemini-ai or rule-based)
    """
    # Validate UUID format first
    validate_uuid(analysis_id, "Analysis ID")
    
    try:
        # Get analysis results from database
        supabase = get_supabase()
        response = supabase.table(Tables.ANALYSIS_RESULTS).select("*").eq("id", analysis_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Analysis not found: {analysis_id}")
        
        analysis_data = response.data[0]
        
        # Get full analysis results (assuming stored as JSON)
        analysis_results = analysis_data.get("results", {})
        
        if not analysis_results:
            raise HTTPException(
                status_code=400,
                detail="Analysis results not available. Complete analysis first."
            )
        
        # Create chat assistant
        api_key = os.getenv("GEMINI_API_KEY")
        assistant = ChatAssistant(api_key=api_key)
        
        # Start conversation with analysis context
        welcome_message = assistant.start_conversation(analysis_results)
        
        # Store active chat session
        session_id = f"chat_{analysis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        active_chats[session_id] = assistant
        
        # Get assistant info
        info = assistant.get_assistant_info()
        
        logger.info(f"Chat started: {session_id} for analysis {analysis_id}")
        
        return {
            "session_id": session_id,
            "analysis_id": analysis_id,
            "message": welcome_message,
            "mode": info["mode"],
            "instructions": (
                "You can now ask questions about your analysis. Examples:\n"
                "- Why do you recommend X nurses?\n"
                "- What if we only have Y staff available?\n"
                "- How can we reduce bottlenecks?\n"
                "- When are the peak congestion times?\n"
                "- Where should we position staff?"
            )
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting chat: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start chat: {str(e)}")


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message in an ongoing conversation.
    
    The AI assistant will respond based on:
    - Analysis context
    - Conversation history
    - Your specific question
    
    - **analysis_id**: ID of the analysis being discussed
    - **message**: Your question or message
    - **conversation_history**: Previous messages (optional)
    
    Returns:
    - **response**: AI assistant's answer
    - **timestamp**: Response timestamp
    """
    # Validate UUID format first
    validate_uuid(request.analysis_id, "Analysis ID")
    
    try:
        # Get analysis results
        supabase = get_supabase()
        response = supabase.table(Tables.ANALYSIS_RESULTS).select("*").eq("id", request.analysis_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Analysis not found: {request.analysis_id}")
        
        analysis_data = response.data[0]
        analysis_results = analysis_data.get("results", {})
        
        # Check for existing chat session
        session_key = None
        for key in active_chats.keys():
            if request.analysis_id in key:
                session_key = key
                break
        
        if session_key and session_key in active_chats:
            # Use existing session
            assistant = active_chats[session_key]
            logger.info(f"Using existing chat session: {session_key}")
        else:
            # Create new session
            api_key = os.getenv("GEMINI_API_KEY")
            assistant = ChatAssistant(api_key=api_key)
            assistant.start_conversation(analysis_results)
            
            session_key = f"chat_{request.analysis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            active_chats[session_key] = assistant
            logger.info(f"Created new chat session: {session_key}")
        
        # Send message and get response
        response_data = assistant.send_message(
            message=request.message,
            conversation_history=request.conversation_history
        )
        
        # Store message in conversation history (optional - implement persistence later)
        # For now, client maintains history
        
        return ChatResponse(
            response=response_data["response"],
            timestamp=datetime.fromisoformat(response_data["timestamp"])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.get("/history/{analysis_id}", response_model=Dict)
async def get_conversation_summary(
    analysis_id: str = PathParam(..., description="ID of the analysis")
):
    """
    Get summary of conversation for an analysis.
    
    Shows:
    - Number of messages
    - Topics discussed
    - Conversation status
    
    - **analysis_id**: ID of the analysis
    
    Returns conversation summary.
    """
    try:
        # Find active chat session
        session_key = None
        for key in active_chats.keys():
            if analysis_id in key:
                session_key = key
                break
        
        if not session_key:
            return {
                "analysis_id": analysis_id,
                "status": "no_conversation",
                "message": "No active conversation found for this analysis."
            }
        
        assistant = active_chats[session_key]
        
        # Get conversation info
        # Note: In full implementation, retrieve from database
        info = assistant.get_assistant_info()
        
        return {
            "analysis_id": analysis_id,
            "session_id": session_key,
            "status": "active" if info["chat_active"] else "inactive",
            "mode": info["mode"],
            "message": "Conversation is active. Continue asking questions!"
        }
    
    except Exception as e:
        logger.error(f"Error getting conversation summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


@router.delete("/clear/{analysis_id}")
async def clear_conversation(
    analysis_id: str = PathParam(..., description="ID of the analysis")
):
    """
    Clear conversation history for an analysis.
    
    Removes the active chat session. A new conversation can be started.
    
    - **analysis_id**: ID of the analysis
    
    Returns confirmation.
    """
    try:
        # Find and remove chat session
        session_key = None
        for key in active_chats.keys():
            if analysis_id in key:
                session_key = key
                break
        
        if session_key:
            assistant = active_chats[session_key]
            assistant.clear_conversation()
            del active_chats[session_key]
            logger.info(f"Cleared chat session: {session_key}")
            
            return {
                "analysis_id": analysis_id,
                "status": "cleared",
                "message": "Conversation cleared successfully."
            }
        else:
            return {
                "analysis_id": analysis_id,
                "status": "no_conversation",
                "message": "No active conversation to clear."
            }
    
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear conversation: {str(e)}")


@router.get("/sessions", response_model=Dict)
async def list_active_sessions():
    """
    List all active chat sessions.
    
    For debugging and monitoring.
    
    Returns list of active session IDs.
    """
    try:
        sessions = []
        for session_id, assistant in active_chats.items():
            info = assistant.get_assistant_info()
            sessions.append({
                "session_id": session_id,
                "mode": info["mode"],
                "active": info["chat_active"]
            })
        
        return {
            "total_sessions": len(sessions),
            "sessions": sessions
        }
    
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")
