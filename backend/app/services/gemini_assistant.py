"""
Gemini AI Assistant Service
Integrates Google Gemini API for generating insights and recommendations.
"""

import logging
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logging.warning("google-generativeai not installed. AI insights will be limited.")

logger = logging.getLogger(__name__)


class GeminiAssistant:
    """
    Google Gemini AI Assistant for generating insights and recommendations.
    
    Features:
    - Natural language insights from analytics data
    - Context-aware staff recommendations
    - Bottleneck area identification
    - Actionable improvement suggestions
    - Fallback to rule-based recommendations when API unavailable
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
        hospital_context: Optional[Dict] = None
    ):
        """
        Initialize the GeminiAssistant.
        
        Args:
            api_key: Google Gemini API key
            model_name: Gemini model to use (gemini-1.5-flash, gemini-1.5-pro)
            temperature: Response creativity (0.0-1.0)
            max_output_tokens: Maximum response length
            hospital_context: Hospital staffing and resource data
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.hospital_context = hospital_context or {}
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
                logger.info(f"Gemini AI Assistant initialized with model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                logger.warning("Falling back to rule-based recommendations")
        else:
            if not GENAI_AVAILABLE:
                logger.warning("google-generativeai package not available")
            if not api_key:
                logger.warning("No API key provided for Gemini")
            logger.info("Using rule-based recommendations only")
    
    def generate_insights(
        self,
        analysis_results: Dict,
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """
        Generate AI-powered insights from analysis results.
        
        Args:
            analysis_results: Complete video analysis results
            include_recommendations: Include staff recommendations
            
        Returns:
            Dictionary with AI insights, summary, and recommendations
        """
        try:
            # Extract key metrics
            stats = analysis_results.get("statistics", {})
            insights = analysis_results.get("insights", {})
            enhanced = analysis_results.get("enhanced_analytics", {})
            video_meta = analysis_results.get("video_metadata", {})
            
            # If Gemini is available, use it
            if self.model:
                return self._generate_ai_insights(
                    stats, insights, enhanced, video_meta, include_recommendations
                )
            else:
                # Fallback to rule-based insights
                return self._generate_rule_based_insights(
                    stats, insights, enhanced, video_meta, include_recommendations
                )
        
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            # Always have a fallback
            return self._generate_basic_insights(analysis_results)
    
    def _generate_ai_insights(
        self,
        stats: Dict,
        insights: Dict,
        enhanced: Dict,
        video_meta: Dict,
        include_recommendations: bool
    ) -> Dict[str, Any]:
        """Generate insights using Gemini AI."""
        try:
            # Build comprehensive prompt
            prompt = self._build_insights_prompt(
                stats, insights, enhanced, video_meta, include_recommendations
            )
            
            # Generate response
            response = self.model.generate_content(prompt)
            ai_text = response.text
            
            # Parse AI response into structured format
            parsed = self._parse_ai_response(ai_text, stats, insights, enhanced)
            
            return {
                "ai_summary": parsed.get("summary", ai_text[:500]),
                "key_findings": parsed.get("key_findings", []),
                "recommendations": parsed.get("recommendations", []),
                "staff_suggestions": parsed.get("staff_suggestions", {}),
                "bottleneck_areas": parsed.get("bottleneck_areas", []),
                "priority_actions": parsed.get("priority_actions", []),
                "raw_ai_response": ai_text,
                "generated_by": "gemini-ai",
                "generated_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error with AI generation: {e}")
            # Fallback to rule-based
            return self._generate_rule_based_insights(
                stats, insights, enhanced, video_meta, include_recommendations
            )
    
    def _build_insights_prompt(
        self,
        stats: Dict,
        insights: Dict,
        enhanced: Dict,
        video_meta: Dict,
        include_recommendations: bool
    ) -> str:
        """Build comprehensive prompt for Gemini with hospital context."""
        
        # Extract enhanced analytics data
        density = enhanced.get("crowd_density", {})
        bottlenecks = enhanced.get("bottleneck_analysis", {})
        spatial = enhanced.get("spatial_distribution", {})
        flow = enhanced.get("flow_metrics", {})
        
        # Extract hospital context
        staffing = self.hospital_context.get("staffing", {})
        resources = self.hospital_context.get("resources", {})
        location = self.hospital_context.get("location_name", "Hospital Area")
        area_sqm = self.hospital_context.get("area_sqm", 100)
        
        prompt = f"""You are an expert healthcare operations analyst specializing in emergency room and hospital waiting area flow optimization. 
Analyze the following video analysis results combined with real-time hospital resource data and provide actionable insights.

HOSPITAL LOCATION & CONTEXT:
- Location: {location}
- Area being monitored: {area_sqm} square meters
- Analysis Date: {video_meta.get('created_at', 'N/A')}

VIDEO INFORMATION:
- Duration: {video_meta.get('duration_formatted', 'N/A')}
- Resolution: {video_meta.get('width', 0)}x{video_meta.get('height', 0)}
- Total frames analyzed: {stats.get('frames_analyzed', 0)}

HOSPITAL STAFFING STATUS (Real-time):
- Total Nurses on Duty: {staffing.get('total_nurses', 'N/A')}
- Currently Available Nurses: {staffing.get('available_nurses', 'N/A')}
- Total Doctors on Duty: {staffing.get('total_doctors', 'N/A')}
- Currently Available Doctors: {staffing.get('available_doctors', 'N/A')}
- Shift Type: {staffing.get('shift_type', 'N/A')}

HOSPITAL RESOURCES STATUS (Real-time):
- Total Beds: {resources.get('total_beds', 'N/A')}
- Occupied Beds: {resources.get('occupied_beds', 'N/A')}
- Available Beds: {resources.get('available_beds', 'N/A')}
- Critical Care Beds: {resources.get('critical_care_beds', 'N/A')}
- General Beds: {resources.get('general_beds', 'N/A')}

CROWD DETECTION STATISTICS:
- Average people count: {stats.get('average_person_count', 0):.1f}
- Peak people count: {stats.get('max_person_count', 0)}
- Minimum people count: {stats.get('min_person_count', 0)}
- Total detections: {stats.get('total_detections', 0)}

CROWD DENSITY ANALYSIS:
- Density level: {density.get('density_level', 'N/A')}
- Density per sqm: {density.get('density_per_sqm', 0):.3f}
- Severity score: {density.get('severity_score', 0)}/5

BOTTLENECK ANALYSIS:
- Bottlenecks detected: {bottlenecks.get('bottlenecks_detected', 0)}
- Threshold used: {bottlenecks.get('threshold_used', 0):.1f} people
- Total bottleneck duration: {bottlenecks.get('total_bottleneck_duration_seconds', 0):.1f} seconds
"""

        # Add bottleneck periods if available
        if bottlenecks.get("bottleneck_periods"):
            prompt += "\n- Critical periods:\n"
            for i, period in enumerate(bottlenecks["bottleneck_periods"][:3], 1):
                prompt += f"  {i}. {period.get('start_time', '')} to {period.get('end_time', '')}: "
                prompt += f"{period.get('severity', '')} (score: {period.get('severity_score', 0):.1f})\n"
                prompt += f"     Peak: {period.get('peak_count', 0)} people, Duration: {period.get('duration_seconds', 0):.1f}s\n"
        
        # Add spatial distribution
        prompt += f"""
SPATIAL DISTRIBUTION:
- Pattern: {spatial.get('distribution_pattern', 'N/A')}
- Hotspot zones: {', '.join([h.get('zone', 'Unknown') if isinstance(h, dict) else str(h) for h in spatial.get('hotspots', [])]) or 'None'}
"""
        
        # Add flow metrics
        prompt += f"""
CROWD FLOW METRICS:
- Trend: {flow.get('trend', 'N/A')} (flow rate: {flow.get('flow_rate', 0):.2f} people/sec)
- Variability: {flow.get('variability', 'N/A')}
- Coefficient of variation: {flow.get('coefficient_of_variation', 0):.2f}

CURRENT ASSESSMENT:
- Crowd level: {insights.get('crowd_level', 'N/A')}
- Peak congestion time: {insights.get('peak_congestion_time', 'N/A')}
- Bottleneck detected: {'Yes' if insights.get('bottleneck_detected', False) else 'No'}
"""

        if include_recommendations:
            prompt += f"""
RESOURCE CONSTRAINTS & CONSIDERATIONS:
- Current available nurses: {staffing.get('available_nurses', 'N/A')} out of {staffing.get('total_nurses', 'N/A')}
- Current available beds: {resources.get('available_beds', 'N/A')} out of {resources.get('total_beds', 'N/A')}
- Estimated waiting patients: {stats.get('average_person_count', 0):.1f}

Please provide recommendations CONSIDERING CURRENT HOSPITAL CAPACITY:
1. **Executive Summary** (2-3 sentences): Overall assessment of the situation RELATIVE TO current staffing and bed availability
2. **Key Findings** (3-5 bullet points): Most important observations
3. **Bottleneck Areas**: Specific locations or times requiring attention
4. **Staff Recommendations**: 
   - IMPORTANT: Consider current staff availability: {staffing.get('available_nurses', 'N/A')} nurses currently available
   - Provide specific recommendations based on detected crowd vs available staff
   - Include realistic assessments given hospital constraints
5. **Bed Capacity Assessment**:
   - Current situation: {resources.get('available_beds', 'N/A')} beds available for {stats.get('average_person_count', 0):.1f} waiting patients
   - Provide capacity recommendations
6. **Priority Actions** (numbered list): Immediate steps to improve flow WITH CURRENT RESOURCES
7. **Resource Requests** (if needed): What additional staff or beds would optimize operations

Format your response clearly with these sections. Be specific, actionable, and data-driven.
Focus on practical recommendations that hospital administrators can implement immediately.
Consider the reality of current staffing and bed availability - don't recommend unrealistic resource levels.
"""
        else:
            prompt += """
Please provide:
1. **Executive Summary**: Overall assessment
2. **Key Findings**: Most important observations
3. **Insights**: What the data reveals about crowd patterns

Be concise, specific, and data-driven.
"""
        
        return prompt
    
    def _parse_ai_response(
        self,
        ai_text: str,
        stats: Dict,
        insights: Dict,
        enhanced: Dict
    ) -> Dict:
        """Parse AI response into structured format."""
        
        # Simple parsing - extract sections
        sections = {
            "summary": "",
            "key_findings": [],
            "recommendations": [],
            "staff_suggestions": {},
            "bottleneck_areas": [],
            "priority_actions": []
        }
        
        try:
            lines = ai_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect sections
                lower_line = line.lower()
                if "executive summary" in lower_line or "summary" in lower_line[:20]:
                    current_section = "summary"
                    continue
                elif "key finding" in lower_line:
                    current_section = "key_findings"
                    continue
                elif "staff recommendation" in lower_line or "staffing" in lower_line:
                    current_section = "staff_suggestions"
                    continue
                elif "bottleneck area" in lower_line:
                    current_section = "bottleneck_areas"
                    continue
                elif "priority action" in lower_line or "immediate step" in lower_line:
                    current_section = "priority_actions"
                    continue
                elif "recommendation" in lower_line or "long-term" in lower_line:
                    current_section = "recommendations"
                    continue
                
                # Add content to current section
                if current_section == "summary" and len(sections["summary"]) < 500:
                    sections["summary"] += line + " "
                elif current_section == "key_findings" and line.startswith(('-', '•', '*', '1', '2', '3', '4', '5')):
                    sections["key_findings"].append(line.lstrip('-•*0123456789. '))
                elif current_section == "recommendations" and line.startswith(('-', '•', '*', '1', '2', '3', '4', '5')):
                    sections["recommendations"].append(line.lstrip('-•*0123456789. '))
                elif current_section == "bottleneck_areas":
                    sections["bottleneck_areas"].append(line.lstrip('-•*0123456789. '))
                elif current_section == "priority_actions" and line.startswith(('1', '2', '3', '4', '5', '-', '•')):
                    sections["priority_actions"].append(line.lstrip('-•*0123456789. '))
            
            # Extract staff suggestions
            sections["staff_suggestions"] = {
                "suggested_nurses": insights.get("suggested_nurses", 0),
                "reasoning": ai_text if "nurse" in ai_text.lower() or "staff" in ai_text.lower() else "Based on crowd density analysis"
            }
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
        
        # Clean up summary
        sections["summary"] = sections["summary"].strip() or ai_text[:500]
        
        return sections
    
    def _generate_rule_based_insights(
        self,
        stats: Dict,
        insights: Dict,
        enhanced: Dict,
        video_meta: Dict,
        include_recommendations: bool
    ) -> Dict[str, Any]:
        """Generate insights using rule-based logic (fallback)."""
        
        avg_count = stats.get("average_person_count", 0)
        max_count = stats.get("max_person_count", 0)
        crowd_level = insights.get("crowd_level", "Unknown")
        bottleneck = insights.get("bottleneck_detected", False)
        
        # Extract enhanced analytics
        density = enhanced.get("crowd_density", {})
        bottlenecks = enhanced.get("bottleneck_analysis", {})
        spatial = enhanced.get("spatial_distribution", {})
        flow = enhanced.get("flow_metrics", {})
        
        # Build summary
        summary = f"Analysis of {video_meta.get('duration_formatted', 'N/A')} video reveals {crowd_level.lower()} crowd levels "
        summary += f"with an average of {avg_count:.1f} people. "
        
        if bottleneck:
            summary += f"Critical bottleneck detected with peak congestion of {max_count} people. "
        
        if spatial.get("hotspots"):
            hotspot_names = [h.get('zone', 'Unknown') if isinstance(h, dict) else str(h) for h in spatial['hotspots']]
            summary += f"High-density areas identified in {', '.join(hotspot_names)} zones. "
        
        if flow.get("trend") == "Increasing":
            summary += "Crowd levels are trending upward, indicating growing demand. "
        
        # Key findings
        key_findings = []
        key_findings.append(f"Average occupancy: {avg_count:.1f} people ({density.get('density_level', 'N/A')} density)")
        key_findings.append(f"Peak congestion: {max_count} people at {insights.get('peak_congestion_time', 'N/A')}")
        
        if bottlenecks.get("bottlenecks_detected", 0) > 0:
            key_findings.append(f"Detected {bottlenecks['bottlenecks_detected']} bottleneck period(s) requiring attention")
        
        if spatial.get("hotspots"):
            hotspot_names = [h.get('zone', 'Unknown') if isinstance(h, dict) else str(h) for h in spatial['hotspots']]
            key_findings.append(f"Crowd concentration in: {', '.join(hotspot_names)}")
        
        key_findings.append(f"Crowd flow trend: {flow.get('trend', 'Stable')} with {flow.get('variability', 'moderate')} variability")
        
        # Recommendations
        recommendations = []
        priority_actions = []
        
        if include_recommendations:
            suggested_nurses = insights.get("suggested_nurses", 1)
            
            if crowd_level in ["High", "Very High"]:
                recommendations.append("Increase staffing immediately to handle high crowd density")
                priority_actions.append(f"Deploy {suggested_nurses} nurse(s) to waiting area")
                recommendations.append("Monitor crowd levels closely for safety compliance")
            
            if bottleneck:
                recommendations.append("Address bottleneck periods with additional staff during peak times")
                priority_actions.append(f"Focus resources during peak time: {insights.get('peak_congestion_time', 'N/A')}")
            
            if spatial.get("hotspots"):
                hotspot_names = [h.get('zone', 'Unknown') if isinstance(h, dict) else str(h) for h in spatial['hotspots']]
                hotspots_str = ', '.join(hotspot_names)
                recommendations.append(f"Position staff strategically in high-density {hotspots_str} zones")
                priority_actions.append(f"Station personnel in {hotspots_str} areas")
            
            if flow.get("trend") == "Increasing":
                recommendations.append("Prepare for continued growth - consider long-term capacity planning")
                priority_actions.append("Review scheduling to accommodate increasing demand")
            
            if flow.get("variability") == "High":
                recommendations.append("High variability detected - implement flexible staffing model")
        
        # Bottleneck areas
        bottleneck_areas = []
        if spatial.get("hotspots"):
            bottleneck_areas = [h.get('zone', 'Unknown') if isinstance(h, dict) else str(h) for h in spatial["hotspots"]]
        if bottlenecks.get("bottleneck_periods"):
            for period in bottlenecks["bottleneck_periods"][:2]:
                bottleneck_areas.append(f"Time {period.get('start_time', '')} - {period.get('end_time', '')} ({period.get('severity', '')})")
        
        return {
            "ai_summary": summary.strip(),
            "key_findings": key_findings,
            "recommendations": recommendations if include_recommendations else [],
            "staff_suggestions": {
                "suggested_nurses": insights.get("suggested_nurses", 1),
                "reasoning": f"Based on average crowd of {avg_count:.1f} people and {crowd_level.lower()} density level. "
                            f"Standard ratio: 1 nurse per 8-10 people in waiting area."
            } if include_recommendations else {},
            "bottleneck_areas": bottleneck_areas,
            "priority_actions": priority_actions if include_recommendations else [],
            "generated_by": "rule-based",
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_basic_insights(self, analysis_results: Dict) -> Dict[str, Any]:
        """Generate minimal insights when everything else fails."""
        stats = analysis_results.get("statistics", {})
        insights = analysis_results.get("insights", {})
        
        return {
            "ai_summary": insights.get("summary", "Analysis completed. Review detailed statistics for insights."),
            "key_findings": [
                f"Average count: {stats.get('average_person_count', 0):.1f}",
                f"Peak count: {stats.get('max_person_count', 0)}",
                f"Crowd level: {insights.get('crowd_level', 'Unknown')}"
            ],
            "recommendations": [],
            "staff_suggestions": {
                "suggested_nurses": insights.get("suggested_nurses", 1),
                "reasoning": "Based on standard staffing ratios"
            },
            "bottleneck_areas": [],
            "priority_actions": [],
            "generated_by": "basic-fallback",
            "generated_at": datetime.now().isoformat()
        }
    
    def get_model_info(self) -> Dict:
        """Get information about the AI assistant configuration."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "gemini_available": GENAI_AVAILABLE,
            "model_initialized": self.model is not None,
            "mode": "gemini-ai" if self.model else "rule-based"
        }


# Convenience function for quick insights generation
def generate_quick_insights(analysis_results: Dict, api_key: Optional[str] = None) -> Dict:
    """
    Quick function to generate insights from analysis results.
    
    Args:
        analysis_results: Complete video analysis results
        api_key: Optional Gemini API key
        
    Returns:
        AI insights and recommendations
    """
    assistant = GeminiAssistant(api_key=api_key)
    return assistant.generate_insights(analysis_results, include_recommendations=True)
