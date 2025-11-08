"""
Chat Assistant Service
Interactive AI assistant for discussing video analysis results.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logging.warning("google-generativeai not installed. Chat will be limited.")

logger = logging.getLogger(__name__)


class ChatAssistant:
    """
    Interactive AI assistant for discussing analysis results.
    
    Features:
    - Answer questions about analysis
    - Explain recommendations
    - Discuss what-if scenarios
    - Provide actionable advice
    - Maintain conversation context
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.8,
        max_output_tokens: int = 1024
    ):
        """
        Initialize the ChatAssistant.
        
        Args:
            api_key: Google Gemini API key
            model_name: Gemini model to use
            temperature: Response creativity (0.0-1.0, higher = more creative)
            max_output_tokens: Maximum response length
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.chat_session = None
        self.model = None
        
        # Initialize Gemini if available
        if GENAI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_output_tokens,
                    }
                )
                logger.info(f"Chat Assistant initialized with model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                logger.warning("Chat will use rule-based responses")
        else:
            if not GENAI_AVAILABLE:
                logger.warning("google-generativeai package not available")
            if not api_key:
                logger.warning("No API key provided for Gemini")
            logger.info("Using rule-based chat responses")
    
    def start_conversation(
        self,
        analysis_results: Dict,
        system_context: Optional[str] = None
    ) -> str:
        """
        Start a new conversation with analysis context.
        
        Args:
            analysis_results: Complete video analysis results
            system_context: Optional additional context
            
        Returns:
            Conversation ID or confirmation message
        """
        # Build comprehensive context from analysis results
        context = self._build_analysis_context(analysis_results)
        
        if system_context:
            context = f"{system_context}\n\n{context}"
        
        # Initialize chat session with context
        if self.model:
            try:
                # Start chat with initial context message
                self.chat_session = self.model.start_chat(history=[])
                
                # Send context as first message (won't be shown to user)
                system_prompt = f"""You are an expert healthcare operations assistant helping hospital administrators understand and act on video analysis results from their emergency room waiting area.

ANALYSIS CONTEXT:
{context}

Your role:
- Answer questions about the analysis clearly and concisely
- Explain recommendations and their reasoning
- Discuss "what-if" scenarios and alternatives
- Provide actionable, practical advice
- Reference specific data points from the analysis
- Be professional but conversational
- Admit if you don't have enough information

Remember: You're helping busy healthcare professionals make data-driven decisions to improve patient flow and safety."""
                
                # Initialize with system context
                response = self.chat_session.send_message(system_prompt)
                
                logger.info("Chat conversation started with analysis context")
                return "Conversation started. Ask me anything about your video analysis!"
            
            except Exception as e:
                logger.error(f"Error starting chat: {e}")
                return "Chat assistant ready (rule-based mode). Ask your questions!"
        else:
            logger.info("Chat ready in rule-based mode")
            return "Chat assistant ready. Ask me about your analysis!"
    
    def send_message(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Send a message and get AI response.
        
        Args:
            message: User's question or message
            conversation_history: Previous messages for context
            
        Returns:
            Response dictionary with answer and metadata
        """
        try:
            # Use Gemini chat if available
            if self.model and self.chat_session:
                return self._generate_ai_response(message, conversation_history)
            else:
                # Fallback to rule-based responses
                return self._generate_rule_based_response(message, conversation_history)
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I'm having trouble processing that question. Could you rephrase it?",
                "error": str(e),
                "generated_by": "error-fallback",
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_ai_response(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Generate response using Gemini AI."""
        try:
            # Send message to ongoing chat
            response = self.chat_session.send_message(message)
            ai_response = response.text
            
            return {
                "response": ai_response,
                "generated_by": "gemini-ai",
                "model": self.model_name,
                "timestamp": datetime.now().isoformat(),
                "message_count": len(conversation_history) + 1 if conversation_history else 1
            }
        
        except Exception as e:
            logger.error(f"Error with AI response: {e}")
            # Fallback to rule-based
            return self._generate_rule_based_response(message, conversation_history)
    
    def _generate_rule_based_response(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Generate response using rule-based logic."""
        
        message_lower = message.lower()
        response = ""
        
        # Pattern matching for common questions
        if any(word in message_lower for word in ["why", "reason", "explain"]):
            if "nurse" in message_lower or "staff" in message_lower:
                response = ("Staff recommendations are based on standard healthcare ratios "
                          "(1 nurse per 8-10 people in waiting areas) combined with your "
                          "crowd density analysis. Higher density and bottleneck periods "
                          "require more staff to maintain safety and service quality.")
            elif "bottleneck" in message_lower:
                response = ("Bottlenecks are identified when crowd levels exceed threshold "
                          "for sustained periods. They indicate times when patient flow "
                          "is restricted, potentially leading to longer wait times and "
                          "safety concerns. Focus staffing during these peak periods.")
            else:
                response = ("The recommendations are based on comprehensive crowd analytics "
                          "including density, spatial distribution, and flow patterns. "
                          "Each suggestion aims to improve patient safety and flow efficiency.")
        
        elif "what if" in message_lower or "scenario" in message_lower:
            if "less" in message_lower or "fewer" in message_lower:
                response = ("With reduced staffing, you may experience: longer wait times, "
                          "reduced patient monitoring, potential safety issues during peak "
                          "congestion. Consider flexible scheduling or on-call staff for "
                          "bottleneck periods.")
            elif "more" in message_lower or "additional" in message_lower:
                response = ("Additional staff would help: reduce wait times, improve patient "
                          "monitoring, handle peak periods more effectively, and provide "
                          "better service quality. Focus extra resources on identified "
                          "bottleneck times and high-density zones.")
            else:
                response = ("I can help explore different scenarios. Could you be more specific "
                          "about what changes you're considering? (e.g., staff levels, "
                          "operating hours, patient flow changes)")
        
        elif "how" in message_lower:
            if "reduce" in message_lower and "bottleneck" in message_lower:
                response = ("To reduce bottlenecks: 1) Increase staff during peak times, "
                          "2) Position staff in high-density zones, 3) Improve triage process, "
                          "4) Consider express lanes for simple cases, 5) Adjust scheduling "
                          "based on predictable patterns.")
            elif "improve" in message_lower:
                response = ("Key improvement strategies: 1) Data-driven staffing based on "
                          "historical patterns, 2) Strategic staff positioning in hotspot "
                          "zones, 3) Clear signage and patient flow guidance, 4) Regular "
                          "monitoring and adjustment, 5) Staff training on crowd management.")
            else:
                response = ("I can provide specific guidance on implementing recommendations. "
                          "What aspect would you like to know more about?")
        
        elif "when" in message_lower:
            if "peak" in message_lower or "busy" in message_lower:
                response = ("Check the 'peak_congestion_time' in your analysis results for "
                          "exact peak periods. Bottleneck analysis shows specific time ranges "
                          "with severity levels. Focus resources during these critical windows.")
            else:
                response = ("Timing information is available in the bottleneck analysis section, "
                          "showing when crowd levels exceed thresholds and for how long.")
        
        elif any(word in message_lower for word in ["where", "area", "zone", "location"]):
            response = ("Spatial distribution analysis identifies hotspot zones where crowds "
                      "concentrate. Check the 'spatial_distribution' section for specific "
                      "zones. Position staff and resources in these high-activity areas.")
        
        elif "thank" in message_lower or "thanks" in message_lower:
            response = ("You're welcome! I'm here to help you make the most of your analysis "
                      "data. Feel free to ask more questions about staffing, bottlenecks, "
                      "or operational improvements.")
        
        elif any(word in message_lower for word in ["hello", "hi", "hey"]):
            response = ("Hello! I'm here to help you understand your crowd analysis results "
                      "and make data-driven decisions. What would you like to know?")
        
        elif "help" in message_lower:
            response = ("I can help with:\n"
                      "- Explaining staff recommendations\n"
                      "- Understanding bottleneck causes and solutions\n"
                      "- Discussing what-if scenarios\n"
                      "- Identifying peak times and hotspot zones\n"
                      "- Suggesting operational improvements\n\n"
                      "Just ask me a question about your analysis!")
        
        else:
            # Generic response
            response = ("I understand you're asking about the analysis. I can explain "
                      "recommendations, discuss staffing scenarios, or help interpret "
                      "the data. Could you be more specific about what you'd like to know?")
        
        return {
            "response": response,
            "generated_by": "rule-based",
            "timestamp": datetime.now().isoformat(),
            "message_count": len(conversation_history) + 1 if conversation_history else 1
        }
    
    def _build_analysis_context(self, analysis_results: Dict) -> str:
        """Build comprehensive context from analysis results."""
        
        # Extract key sections
        video_meta = analysis_results.get("video_metadata", {})
        stats = analysis_results.get("statistics", {})
        insights = analysis_results.get("insights", {})
        enhanced = analysis_results.get("enhanced_analytics", {})
        ai_insights = analysis_results.get("ai_insights", {})
        
        # Build context string
        context = f"""VIDEO ANALYSIS SUMMARY:
Duration: {video_meta.get('duration_formatted', 'N/A')}
Frames Analyzed: {stats.get('frames_analyzed', 0)}

CROWD STATISTICS:
- Average People: {stats.get('average_person_count', 0):.1f}
- Peak Count: {stats.get('max_person_count', 0)}
- Crowd Level: {insights.get('crowd_level', 'Unknown')}
- Suggested Staff: {insights.get('suggested_nurses', 0)} nurse(s)

ENHANCED ANALYTICS:"""
        
        # Add density info
        density = enhanced.get("crowd_density", {})
        if density:
            context += f"""
- Density Level: {density.get('density_level', 'N/A')}
- Density per sqm: {density.get('density_per_sqm', 0):.3f}
- Severity Score: {density.get('severity_score', 0)}/5"""
        
        # Add bottleneck info
        bottlenecks = enhanced.get("bottleneck_analysis", {})
        if bottlenecks:
            context += f"""
- Bottlenecks Detected: {bottlenecks.get('bottlenecks_detected', 0)}
- Peak Congestion: {insights.get('peak_congestion_time', 'N/A')}"""
        
        # Add spatial info
        spatial = enhanced.get("spatial_distribution", {})
        if spatial:
            hotspots = spatial.get("hotspots", [])
            if hotspots:
                hotspot_names = [h.get('zone', 'Unknown') if isinstance(h, dict) else str(h) for h in hotspots[:3]]
                context += f"""
- Distribution Pattern: {spatial.get('distribution_pattern', 'N/A')}
- Hotspot Zones: {', '.join(hotspot_names) if hotspot_names else 'None'}"""
        
        # Add flow info
        flow = enhanced.get("flow_metrics", {})
        if flow:
            context += f"""
- Flow Trend: {flow.get('trend', 'N/A')}
- Flow Rate: {flow.get('flow_rate', 0):.2f} people/sec"""
        
        # Add AI insights summary if available
        if ai_insights and not ai_insights.get("error"):
            context += f"""

AI INSIGHTS:
{ai_insights.get('ai_summary', 'N/A')[:300]}

KEY RECOMMENDATIONS:"""
            for i, rec in enumerate(ai_insights.get('priority_actions', [])[:3], 1):
                context += f"""
{i}. {rec}"""
        
        return context
    
    def get_conversation_summary(
        self,
        conversation_history: List[Dict]
    ) -> Dict[str, Any]:
        """
        Generate summary of conversation.
        
        Args:
            conversation_history: List of messages
            
        Returns:
            Summary with key topics and insights
        """
        if not conversation_history:
            return {
                "message_count": 0,
                "topics": [],
                "summary": "No conversation yet."
            }
        
        # Analyze conversation topics
        topics = set()
        user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
        
        for msg in user_messages:
            content = msg.get("content", "").lower()
            if "staff" in content or "nurse" in content:
                topics.add("Staffing")
            if "bottleneck" in content:
                topics.add("Bottlenecks")
            if "what if" in content or "scenario" in content:
                topics.add("Scenarios")
            if "peak" in content or "busy" in content:
                topics.add("Peak Times")
            if "zone" in content or "area" in content:
                topics.add("Spatial Distribution")
            if "reduce" in content or "improve" in content:
                topics.add("Improvements")
        
        return {
            "message_count": len(conversation_history),
            "user_messages": len(user_messages),
            "topics_discussed": list(topics),
            "last_message_time": conversation_history[-1].get("timestamp") if conversation_history else None,
            "conversation_active": True
        }
    
    def clear_conversation(self):
        """Clear current conversation context."""
        self.chat_session = None
        logger.info("Conversation cleared")
    
    def get_assistant_info(self) -> Dict:
        """Get information about the assistant configuration."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "gemini_available": GENAI_AVAILABLE,
            "model_initialized": self.model is not None,
            "mode": "gemini-ai" if self.model else "rule-based",
            "chat_active": self.chat_session is not None
        }


# Convenience function for quick chat responses
def quick_chat(
    message: str,
    analysis_results: Dict,
    conversation_history: Optional[List[Dict]] = None,
    api_key: Optional[str] = None
) -> str:
    """
    Quick function to get chat response.
    
    Args:
        message: User's question
        analysis_results: Analysis results for context
        conversation_history: Previous messages
        api_key: Optional Gemini API key
        
    Returns:
        Assistant's response text
    """
    assistant = ChatAssistant(api_key=api_key)
    assistant.start_conversation(analysis_results)
    response = assistant.send_message(message, conversation_history)
    return response.get("response", "Sorry, I couldn't generate a response.")
