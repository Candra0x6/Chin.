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
        self.analysis_results = {}  # Store analysis context for dynamic responses
        
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
            logger.info("Using dynamic rule-based chat responses")
    
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
        # Store analysis results for dynamic response generation
        self.analysis_results = analysis_results
        
        # Extract key data for dynamic responses
        self._extract_analysis_data()
        
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
            logger.info("Chat ready in dynamic rule-based mode")
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
        """Generate response using rule-based logic with dynamic data extraction."""
        
        message_lower = message.lower()
        response = ""
        
        # Log the user question
        logger.info(f"[CHAT] User question: {message}")
        
        # Extract keywords to understand intent
        keywords = {
            'time': ['when', 'time', 'hour', 'period', 'peak'],
            'crowd': ['people', 'crowd', 'pople', 'person', 'crowded', 'busy', 'density'],
            'staff': ['nurse', 'staff', 'doctor', 'personnel', 'worker', 'employee'],
            'bottleneck': ['bottleneck', 'congestion', 'stuck', 'blocked', 'flow'],
            'scenario': ['what if', 'if', 'scenario', 'suppose', 'imagine', 'reduce', 'increase', 'less', 'more'],
            'help': ['help', 'how', 'why', 'explain', 'tell', 'what', 'problem', 'issue']
        }
        
        # Find matching keyword categories
        matched_keywords = set()
        for category, words in keywords.items():
            if any(word in message_lower for word in words):
                matched_keywords.add(category)
        
        logger.info(f"[CHAT] Matched keyword categories: {matched_keywords}")
        
        # ========== CROWD-RELATED QUESTIONS ==========
        if 'crowd' in matched_keywords:
            if 'time' in matched_keywords or any(w in message_lower for w in ['when', 'highest', 'peak', 'maximum']):
                # User asking: "When was the crowd highest?"
                response = self._generate_crowd_timing_response()
            
            elif 'staff' in matched_keywords:
                # User asking: "The people it too much how" or similar
                response = self._generate_crowd_staff_response()
            
            elif 'help' in matched_keywords or 'scenario' in matched_keywords:
                # User asking: "People too much how" or "How much crowd"
                response = self._generate_crowd_staff_response()  # Same as crowd_staff
            
            else:
                response = self._generate_crowd_summary_response()
        
        # ========== STAFF-RELATED QUESTIONS ==========
        elif 'staff' in matched_keywords:
            if 'recommended' in message_lower or 'suggest' in message_lower or 'should' in message_lower:
                # User asking: "How much recommended nurses"
                response = self._generate_staff_recommendation_response()
            
            elif 'scenario' in matched_keywords:
                if 'nothing' in message_lower or 'no' in message_lower or 'less' in message_lower:
                    # User asking: "How if nurses nothing left"
                    response = self._generate_staff_shortage_scenario()
                else:
                    response = self._generate_staff_scenario_response()
            
            else:
                response = self._generate_staff_summary_response()
        
        # ========== BOTTLENECK QUESTIONS ==========
        elif 'bottleneck' in matched_keywords:
            response = self._generate_bottleneck_response()
        
        # ========== HOW/WHY EXPLANATION QUESTIONS ==========
        elif 'help' in matched_keywords:
            if 'why' in message_lower:
                response = self._generate_explanation_response(message)
            elif 'how' in message_lower:
                response = self._generate_how_response(message)
            else:
                response = self._generate_general_guidance()
        
        # ========== FALLBACK: Provide context-aware generic response ==========
        else:
            response = self._generate_contextual_fallback(message)
        
        # Ensure we have a response
        if not response:
            response = self._generate_contextual_fallback(message)
        
        result = {
            "response": response,
            "generated_by": "dynamic-rule-based",
            "timestamp": datetime.now().isoformat(),
            "message_count": len(conversation_history) + 1 if conversation_history else 1,
            "matched_keywords": list(matched_keywords)
        }
        
        logger.info(f"[CHAT] Response: {response[:100]}...")
        return result
    
    def _extract_analysis_data(self) -> None:
        """Extract and cache key data points from analysis results for quick access."""
        try:
            stats = self.analysis_results.get("statistics", {})
            insights = self.analysis_results.get("insights", {})
            enhanced = self.analysis_results.get("enhanced_analytics", {})
            
            # Cache frequently used data
            self.avg_people = stats.get('average_person_count', 0)
            self.max_people = stats.get('max_person_count', 0)
            self.suggested_nurses = insights.get('suggested_nurses', 0)
            self.peak_time = insights.get('peak_congestion_time', 'N/A')
            
            # Bottleneck data
            bottlenecks = enhanced.get("bottleneck_analysis", {})
            self.bottleneck_count = bottlenecks.get('bottlenecks_detected', 0)
            self.bottleneck_severity = bottlenecks.get('severity_level', 'Unknown')
            self.bottleneck_duration = bottlenecks.get('total_duration_seconds', 0)
            
            # Density data
            density = enhanced.get("crowd_density", {})
            self.density_level = density.get('density_level', 'Unknown')
            self.density_per_sqm = density.get('density_per_sqm', 0)
            
            # Spatial data
            spatial = enhanced.get("spatial_distribution", {})
            self.hotspots = spatial.get('hotspots', [])
            
            logger.info(f"[CHAT] Extracted data: avg={self.avg_people}, max={self.max_people}, nurses={self.suggested_nurses}")
        except Exception as e:
            logger.error(f"[CHAT] Error extracting analysis data: {e}")
    
    def _generate_crowd_timing_response(self) -> str:
        """Generate response for: 'When was the crowd highest?'"""
        if self.peak_time and self.peak_time != 'N/A':
            return (f"The crowd was highest at **{self.peak_time}**, when we detected "
                   f"**{self.max_people} people** in the area (average was {self.avg_people:.0f}). "
                   f"This is when you should have maximum staff deployed.")
        return (f"Based on the analysis, peak crowd occurred when {self.max_people} people "
               f"were present (average: {self.avg_people:.0f}). Check the bottleneck analysis "
               f"section for specific timing details.")
    
    def _generate_crowd_staff_response(self) -> str:
        """Generate response for: 'The people it too much how' or vague crowd questions"""
        return (f"Yes, with **{self.max_people} people** at peak (average: {self.avg_people:.0f}), "
               f"the area becomes overcrowded. I recommend **{self.suggested_nurses} nurses** to maintain "
               f"safe supervision and manage flow. The density level is **{self.density_level}** "
               f"({self.density_per_sqm:.2f} people/sqm). Strategic staff positioning in hotspot "
               f"zones can significantly improve crowd management.")
    
    def _generate_crowd_summary_response(self) -> str:
        """Generate response for general crowd questions"""
        return (f"The crowd analysis shows:\n"
               f"- **Average**: {self.avg_people:.0f} people\n"
               f"- **Peak**: {self.max_people} people at {self.peak_time}\n"
               f"- **Density Level**: {self.density_level} ({self.density_per_sqm:.2f} per sqm)\n"
               f"- **Recommended Staff**: {self.suggested_nurses} nurses\n\n"
               f"The peak periods require careful attention and additional staffing.")
    
    def _generate_staff_recommendation_response(self) -> str:
        """Generate response for: 'How much recommended nurses'"""
        return (f"Based on the analysis, I recommend **{self.suggested_nurses} nurses** for proper "
               f"crowd management. This recommendation is based on:\n"
               f"- Peak crowd of **{self.max_people} people**\n"
               f"- Average crowd of **{self.avg_people:.0f} people**\n"
               f"- Crowd density of **{self.density_level}** ({self.density_per_sqm:.2f}/sqm)\n\n"
               f"Focus extra staff during **{self.peak_time}** when congestion is highest.")
    
    def _generate_staff_shortage_scenario(self) -> str:
        """Generate response for: 'How if nurses nothing left'"""
        return (f"⚠️ **With NO additional nurses**, the situation becomes critical:\n"
               f"- **{self.max_people} people** at peak with only baseline staff creates safety risks\n"
               f"- No buffer for emergencies or special situations\n"
               f"- Patient wait times will increase significantly\n"
               f"- Risk of missed patient issues due to overwhelmed staff\n\n"
               f"**Recommendation**: Prioritize hiring {self.suggested_nurses} nurses, or at minimum:\n"
               f"1. Deploy on-call staff during peak periods\n"
               f"2. Stagger break times to maintain minimum coverage\n"
               f"3. Implement patient flow optimization to reduce effective demand")
    
    def _generate_staff_scenario_response(self) -> str:
        """Generate response for staff what-if scenarios"""
        return (f"Current staffing is recommended at **{self.suggested_nurses} nurses**. "
               f"Different scenarios:\n\n"
               f"**More staff (+2 nurses)**: Better response times, reduced stress, ability to "
               f"handle surges.\n\n"
               f"**Current ({self.suggested_nurses} nurses)**: Adequate for average load of "
               f"{self.avg_people:.0f} people.\n\n"
               f"**Less staff (-1 nurse)**: Risk during peak periods of {self.max_people} people. "
               f"What specific scenario interests you?")
    
    def _generate_staff_summary_response(self) -> str:
        """Generate response for general staff questions"""
        return (f"Staff analysis summary:\n"
               f"- **Recommended nurses**: {self.suggested_nurses}\n"
               f"- **Peak load**: {self.max_people} people\n"
               f"- **Average load**: {self.avg_people:.0f} people\n\n"
               f"This maintains a 1 nurse per {self.max_people/max(self.suggested_nurses, 1):.1f} "
               f"people ratio at peak. Would you like to discuss staffing scenarios?")
    
    def _generate_bottleneck_response(self) -> str:
        """Generate response for bottleneck questions"""
        duration_mins = self.bottleneck_duration / 60 if self.bottleneck_duration else 0
        return (f"**Bottleneck Analysis**:\n"
               f"- **Instances detected**: {self.bottleneck_count}\n"
               f"- **Severity**: {self.bottleneck_severity}\n"
               f"- **Total duration**: {duration_mins:.1f} minutes\n"
               f"- **Peak congestion time**: {self.peak_time}\n\n"
               f"These bottlenecks occur when crowd flow is restricted. Solutions:\n"
               f"1. Increase staff during peak times\n"
               f"2. Improve signage and patient routing\n"
               f"3. Position staff in hotspot zones to direct flow")
    
    def _generate_explanation_response(self, message: str) -> str:
        """Generate response for 'why' questions"""
        if 'recommend' in message.lower():
            return (f"The {self.suggested_nurses} nurse recommendation is based on healthcare "
                   f"safety standards (typically 1 nurse per 8-10 people) applied to your peak "
                   f"load of {self.max_people} people. This ensures adequate monitoring and "
                   f"care even during surge periods.")
        return (f"Recommendations are based on real data: {self.max_people} peak people, "
               f"{self.avg_people:.0f} average, {self.density_level} density level. Each metric "
               f"contributes to safe and efficient operations.")
    
    def _generate_how_response(self, message: str) -> str:
        """Generate response for 'how' questions"""
        if 'improve' in message.lower() or 'reduce' in message.lower():
            return (f"To improve operations with {self.max_people} peak people:\n"
                   f"1. **Deploy {self.suggested_nurses} nurses** (currently recommended)\n"
                   f"2. **Position staff in hotspot zones** during peak time\n"
                   f"3. **Monitor during {self.peak_time}** - the critical period\n"
                   f"4. **Use data-driven scheduling** - plan extra help when needed\n"
                   f"5. **Implement flow optimization** - better signage and routing")
        return (f"Start by implementing the recommended {self.suggested_nurses} nurses. "
               f"Monitor the peak time of {self.peak_time}. Track metrics and adjust based on results.")
    
    def _generate_general_guidance(self) -> str:
        """Generate general helpful guidance"""
        return (f"I can help you optimize operations! Key insights from your data:\n"
               f"- **{self.max_people} peak visitors** need **{self.suggested_nurses} nurses**\n"
               f"- **Busiest period**: {self.peak_time}\n"
               f"- **Density level**: {self.density_level}\n\n"
               f"Ask me about: staffing needs, peak times, bottleneck solutions, or scenarios!")
    
    def _generate_contextual_fallback(self, message: str) -> str:
        """Generate intelligent fallback using context data"""
        # If message contains generic terms, provide smart suggestions
        if len(message) < 10:  # Very short message
            return (f"To help you better, tell me what you'd like to know!\n\n"
                   f"I can explain:\n"
                   f"- **Staffing**: Why {self.suggested_nurses} nurses are recommended\n"
                   f"- **Timing**: When peak crowd occurs ({self.peak_time})\n"
                   f"- **Scenarios**: What if staffing changes\n"
                   f"- **Improvements**: How to optimize operations")
        
        # Generic but data-aware response
        return (f"Your analysis shows {self.max_people} peak people with {self.density_level} density. "
               f"I recommend {self.suggested_nurses} nurses, especially during {self.peak_time}. "
               f"What would you like to explore further?")
    
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
