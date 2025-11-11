"""
Hospital Analytics Service
Advanced algorithms for staffing recommendations and resource optimization
using hospital context (staff, beds, current occupancy).

Popular Algorithms Used:
1. Erlang C Formula - for waiting time prediction
2. Queueing Theory (M/M/c) - for server (staff) dimensioning
3. Bed Occupancy Forecasting
4. Lee-Longton Algorithm - for workload estimation
"""

import logging
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class HospitalAnalytics:
    """
    Advanced analytics for hospital operations using crowd detection data
    combined with staffing and resource information.
    """
    
    def __init__(self):
        """Initialize hospital analytics service."""
        logger.info("HospitalAnalytics initialized")
    
    @staticmethod
    def erlang_c_formula(
        arrival_rate: float,
        service_rate: float,
        num_agents: int
    ) -> float:
        """
        Calculate Erlang C - probability of waiting in queue.
        Used in healthcare for predicting wait times.
        
        Args:
            arrival_rate: λ - arrivals per hour
            service_rate: μ - services per hour per agent
            num_agents: c - number of agents (nurses/doctors)
            
        Returns:
            Probability of waiting (0-1)
        """
        if num_agents <= 0 or service_rate <= 0:
            return 1.0
        
        intensity = arrival_rate / service_rate  # Traffic intensity
        
        if intensity >= num_agents:
            # System is overloaded
            return 1.0
        
        # Erlang C formula
        erlang_b_numerator = (intensity ** num_agents) / np.math.factorial(num_agents)
        erlang_b_sum = sum(
            (intensity ** n) / np.math.factorial(n)
            for n in range(num_agents + 1)
        )
        
        erlang_c = erlang_b_numerator / (erlang_b_sum + erlang_b_numerator * (num_agents - intensity))
        
        return min(max(erlang_c, 0.0), 1.0)
    
    @staticmethod
    def calculate_average_wait_time(
        arrival_rate: float,
        service_rate: float,
        num_agents: int
    ) -> float:
        """
        Calculate average wait time in queue using Erlang C.
        
        Args:
            arrival_rate: λ - arrivals per hour
            service_rate: μ - services per hour per agent
            num_agents: c - number of agents
            
        Returns:
            Average wait time in minutes
        """
        if num_agents <= 0 or service_rate <= 0 or arrival_rate >= num_agents * service_rate:
            return float('inf')
        
        erlang_c = HospitalAnalytics.erlang_c_formula(arrival_rate, service_rate, num_agents)
        intensity = arrival_rate / service_rate
        
        wait_time_hours = (erlang_c / (num_agents * service_rate - arrival_rate))
        wait_time_minutes = wait_time_hours * 60
        
        return max(0, wait_time_minutes)
    
    @staticmethod
    def estimate_arrival_rate_from_crowd(
        average_person_count: float,
        peak_person_count: int,
        video_duration_minutes: float
    ) -> float:
        """
        Estimate arrival rate (λ) from crowd detection data.
        Assumes steady-state with some arrivals and departures.
        
        Args:
            average_person_count: Average detected people
            peak_person_count: Maximum detected people
            video_duration_minutes: Video duration in minutes
            
        Returns:
            Estimated arrival rate (people per hour)
        """
        # Use peak as indicator of maximum system capacity
        # Estimate arrivals as rate needed to maintain average level
        if video_duration_minutes <= 0:
            return 0.0
        
        # Assume system is near equilibrium
        # Arrivals ≈ Departures at steady state
        # Use average as proxy for equilibrium level
        arrival_rate = (average_person_count * 2) * (60 / video_duration_minutes)
        
        return max(0, arrival_rate)
    
    @staticmethod
    def estimate_service_rate_from_context(
        available_staff: int,
        area_sqm: float
    ) -> float:
        """
        Estimate service rate (μ) based on staff and area.
        Rule: 1 nurse can serve ~5-8 patients/hour depending on complexity.
        
        Args:
            available_staff: Number of available nurses/doctors
            area_sqm: Area being served in square meters
            
        Returns:
            Service rate (people per hour per agent)
        """
        # Base service rate: 1 nurse serves 6 people/hour on average
        base_service_rate_per_agent = 6.0
        
        # Adjust for area - larger areas may have slightly lower efficiency
        area_factor = 1.0 if area_sqm < 200 else (200 / area_sqm)
        
        # Adjusted service rate
        service_rate = base_service_rate_per_agent * area_factor
        
        return max(1.0, service_rate)
    
    def calculate_optimal_staffing(
        self,
        average_person_count: float,
        peak_person_count: int,
        current_nurses: int,
        available_nurses: int,
        video_duration_minutes: float,
        target_wait_time_minutes: float = 10.0,
        area_sqm: float = 100.0
    ) -> Dict:
        """
        Calculate optimal staffing using Erlang C and queueing theory.
        
        Args:
            average_person_count: Average detected people
            peak_person_count: Peak detected people
            current_nurses: Total nurses on duty
            available_nurses: Currently available nurses
            video_duration_minutes: Video duration in minutes
            target_wait_time_minutes: Target acceptable wait time
            area_sqm: Area being monitored
            
        Returns:
            Staffing recommendation with detailed analysis
        """
        # Estimate arrival and service rates
        arrival_rate = self.estimate_arrival_rate_from_crowd(
            average_person_count,
            peak_person_count,
            video_duration_minutes
        )
        
        service_rate = self.estimate_service_rate_from_context(
            available_nurses,
            area_sqm
        )
        
        # Find optimal number of agents
        intensity = arrival_rate / service_rate if service_rate > 0 else 0
        min_agents = int(np.ceil(intensity)) + 1  # Minimum to keep system stable
        
        # Test different staffing levels
        staffing_analysis = {}
        optimal_staffing = available_nurses
        best_wait_time = float('inf')
        
        for num_agents in range(max(1, min_agents - 1), min_agents + 5):
            wait_time = self.calculate_average_wait_time(
                arrival_rate, service_rate, num_agents
            )
            erlang_c = self.erlang_c_formula(arrival_rate, service_rate, num_agents)
            
            staffing_analysis[num_agents] = {
                "wait_time_minutes": round(wait_time, 1) if wait_time != float('inf') else "Unstable",
                "probability_waiting": round(erlang_c, 3),
                "system_utilization": round(intensity / num_agents, 3) if num_agents > 0 else 0
            }
            
            # Track optimal (closest to target without exceeding)
            if wait_time <= target_wait_time_minutes and wait_time < best_wait_time:
                optimal_staffing = num_agents
                best_wait_time = wait_time
        
        # Additional staff needed
        current_available = available_nurses
        additional_staff = max(0, optimal_staffing - current_available)
        
        # Confidence score (0-1)
        confidence = min(
            1.0,
            (optimal_staffing / max(current_available, 1)) * 0.8 + 0.2
        )
        
        return {
            "recommended_nurses": optimal_staffing,
            "additional_nurses_needed": additional_staff,
            "current_available": current_available,
            "arrival_rate_per_hour": round(arrival_rate, 1),
            "service_rate_per_agent": round(service_rate, 1),
            "system_intensity": round(intensity, 2),
            "predicted_wait_time_minutes": round(best_wait_time, 1) if best_wait_time != float('inf') else "High",
            "probability_waiting": round(self.erlang_c_formula(arrival_rate, service_rate, optimal_staffing), 3),
            "system_utilization": round(intensity / optimal_staffing, 3) if optimal_staffing > 0 else 0,
            "staffing_analysis": {str(k): v for k, v in staffing_analysis.items()},
            "confidence": round(confidence, 2),
            "algorithm": "Erlang C + Queueing Theory (M/M/c)"
        }
    
    def calculate_bed_demand_forecasting(
        self,
        average_person_count: float,
        peak_person_count: int,
        total_beds: int,
        occupied_beds: int,
        available_beds: int,
        critical_care_ratio: float = 0.2
    ) -> Dict:
        """
        Forecast bed demand using Lee-Longton Algorithm and occupancy patterns.
        Assumes: people detected ≈ waiting patients needing beds.
        
        Args:
            average_person_count: Average detected people (waiting patients)
            peak_person_count: Peak detected people
            total_beds: Total hospital beds
            occupied_beds: Currently occupied beds
            available_beds: Currently available beds
            critical_care_ratio: Ratio of critical care beds (0-1)
            
        Returns:
            Bed demand forecast with recommendations
        """
        # Estimate patients needing beds from crowd detection
        estimated_waiting_patients = average_person_count
        estimated_peak_patients = peak_person_count
        
        # Apply typical ER triage split: ~20% need critical care, ~80% general
        estimated_critical_need = estimated_waiting_patients * critical_care_ratio
        estimated_general_need = estimated_waiting_patients * (1 - critical_care_ratio)
        
        # Current occupancy rate
        current_occupancy_rate = (occupied_beds / total_beds) if total_beds > 0 else 0
        
        # Projected occupancy with detected patients
        projected_additional_occupancy = estimated_waiting_patients
        projected_occupancy_rate = (occupied_beds + projected_additional_occupancy) / total_beds if total_beds > 0 else 1
        
        # Lee-Longton adjustment for variance
        variance_factor = 1.15  # 15% buffer for uncertainty
        adjusted_projected_occupancy = projected_occupancy_rate * variance_factor
        
        # Bed shortage calculation
        beds_at_capacity = total_beds * 0.95  # 95% is practical max
        estimated_additional_capacity_needed = max(
            0,
            estimated_waiting_patients - available_beds
        )
        
        urgency_level = self._classify_urgency(
            adjusted_projected_occupancy,
            estimated_additional_capacity_needed,
            total_beds
        )
        
        return {
            "estimated_waiting_patients": round(estimated_waiting_patients, 1),
            "estimated_peak_patients": peak_person_count,
            "current_occupancy_rate": round(current_occupancy_rate, 3),
            "projected_occupancy_rate": round(adjusted_projected_occupancy, 3),
            "current_available_beds": available_beds,
            "estimated_beds_needed": round(estimated_waiting_patients, 0),
            "additional_capacity_needed": max(0, round(estimated_additional_capacity_needed, 0)),
            "critical_care_beds_needed": round(estimated_critical_need, 1),
            "general_beds_needed": round(estimated_general_need, 1),
            "urgency_level": urgency_level,
            "recommendation": self._generate_bed_recommendation(
                urgency_level,
                estimated_additional_capacity_needed,
                available_beds
            ),
            "algorithm": "Lee-Longton Algorithm + Occupancy Forecasting"
        }
    
    @staticmethod
    def _classify_urgency(
        occupancy_rate: float,
        shortage: float,
        total_beds: int
    ) -> str:
        """Classify urgency level based on occupancy and shortage."""
        if occupancy_rate >= 1.0 or shortage > 10:
            return "Critical - Immediate action required"
        elif occupancy_rate >= 0.9 or shortage > 5:
            return "High - Plan additional capacity"
        elif occupancy_rate >= 0.75 or shortage > 2:
            return "Moderate - Monitor closely"
        elif occupancy_rate >= 0.6:
            return "Low - Normal operations"
        else:
            return "Very Low - Adequate capacity"
    
    @staticmethod
    def _generate_bed_recommendation(
        urgency: str,
        shortage: float,
        available_beds: int
    ) -> str:
        """Generate bed-related recommendation."""
        if "Critical" in urgency:
            return f"URGENT: Implement surge capacity protocols. Missing ~{int(shortage)} beds. Divert non-critical admissions."
        elif "High" in urgency:
            return f"Prepare surge beds and notify administration. Potential shortage of ~{int(shortage)} beds."
        elif "Moderate" in urgency:
            return f"Monitor bed status closely. May need ~{int(shortage)} additional beds soon."
        else:
            return f"Normal operations. Adequate bed capacity available ({available_beds} beds free)."
    
    def calculate_comprehensive_hospital_metrics(
        self,
        average_person_count: float,
        peak_person_count: int,
        video_duration_minutes: float,
        hospital_context: Dict
    ) -> Dict:
        """
        Calculate comprehensive metrics combining crowd and hospital context.
        
        Args:
            average_person_count: Average detected people
            peak_person_count: Peak detected people
            video_duration_minutes: Video duration in minutes
            hospital_context: Hospital staffing and resource data
            
        Returns:
            Comprehensive analysis combining all factors
        """
        staffing = hospital_context.get("staffing", {})
        resources = hospital_context.get("resources", {})
        area_sqm = hospital_context.get("area_sqm", 100.0)
        location = hospital_context.get("location_name", "Hospital Area")
        
        # Extract values with defaults
        current_nurses = staffing.get("total_nurses", 0)
        available_nurses = staffing.get("available_nurses", 0)
        total_beds = resources.get("total_beds", 0)
        occupied_beds = resources.get("occupied_beds", 0)
        available_beds = resources.get("available_beds", 0)
        
        # Calculate staffing recommendations
        staffing_rec = self.calculate_optimal_staffing(
            average_person_count,
            peak_person_count,
            current_nurses,
            available_nurses,
            video_duration_minutes,
            area_sqm=area_sqm
        )
        
        # Calculate bed demand
        bed_rec = self.calculate_bed_demand_forecasting(
            average_person_count,
            peak_person_count,
            total_beds,
            occupied_beds,
            available_beds
        )
        
        # Overall capacity score (0-100)
        capacity_score = self._calculate_capacity_score(
            staffing_rec,
            bed_rec,
            available_nurses,
            available_beds
        )
        
        return {
            "location": location,
            "analysis_timestamp": datetime.now().isoformat(),
            "staffing_analysis": staffing_rec,
            "bed_analysis": bed_rec,
            "capacity_score": round(capacity_score, 1),
            "overall_status": self._classify_status(capacity_score),
            "critical_alerts": self._generate_alerts(staffing_rec, bed_rec),
            "summary": self._generate_comprehensive_summary(
                average_person_count,
                staffing_rec,
                bed_rec,
                location
            )
        }
    
    @staticmethod
    def _calculate_capacity_score(
        staffing_rec: Dict,
        bed_rec: Dict,
        available_nurses: int,
        available_beds: int
    ) -> float:
        """Calculate overall capacity score (0-100)."""
        # Staffing component (0-50)
        staffing_component = min(50, (available_nurses / max(1, staffing_rec["recommended_nurses"])) * 50)
        
        # Bed component (0-50)
        bed_component = min(50, (available_beds / max(1, bed_rec["estimated_beds_needed"])) * 50) if bed_rec["estimated_beds_needed"] > 0 else 50
        
        total_score = staffing_component + bed_component
        
        return max(0, min(100, total_score))
    
    @staticmethod
    def _classify_status(capacity_score: float) -> str:
        """Classify overall status based on capacity score."""
        if capacity_score >= 80:
            return "Optimal - All resources adequate"
        elif capacity_score >= 60:
            return "Good - Minor constraints"
        elif capacity_score >= 40:
            return "Fair - Notable constraints"
        elif capacity_score >= 20:
            return "Poor - Significant strain"
        else:
            return "Critical - Severe strain"
    
    @staticmethod
    def _generate_alerts(staffing_rec: Dict, bed_rec: Dict) -> List[str]:
        """Generate critical alerts based on analysis."""
        alerts = []
        
        # Staffing alerts
        additional_staff = staffing_rec.get("additional_nurses_needed", 0)
        if additional_staff >= 3:
            alerts.append(f"CRITICAL: Need {additional_staff} additional nurses to meet optimal staffing")
        elif additional_staff >= 1:
            alerts.append(f"WARNING: Need {additional_staff} additional nurse(s)")
        
        # Bed alerts
        additional_beds = bed_rec.get("additional_capacity_needed", 0)
        if "Critical" in bed_rec.get("urgency_level", ""):
            alerts.append(f"CRITICAL: Bed shortage of {int(additional_beds)} beds")
        elif "High" in bed_rec.get("urgency_level", ""):
            alerts.append(f"WARNING: May need {int(additional_beds)} additional beds")
        
        # Wait time alerts
        wait_time = staffing_rec.get("predicted_wait_time_minutes", 0)
        if isinstance(wait_time, (int, float)) and wait_time > 30:
            alerts.append(f"Alert: Predicted wait time {wait_time:.0f} minutes (target: 10 min)")
        
        return alerts
    
    @staticmethod
    def _generate_comprehensive_summary(
        average_person_count: float,
        staffing_rec: Dict,
        bed_rec: Dict,
        location: str
    ) -> str:
        """Generate comprehensive summary of analysis."""
        summary = f"Analysis for {location}: "
        summary += f"Detected average of {average_person_count:.1f} waiting patients. "
        
        additional_nurses = staffing_rec.get("additional_nurses_needed", 0)
        if additional_nurses > 0:
            summary += f"Recommend {staffing_rec['recommended_nurses']} nurses (add {int(additional_nurses)}). "
        else:
            summary += f"Current staffing ({staffing_rec['current_available']} nurses) appears adequate. "
        
        additional_beds = bed_rec.get("additional_capacity_needed", 0)
        if additional_beds > 0:
            summary += f"May need {int(additional_beds)} additional beds. "
        else:
            summary += f"Bed capacity appears adequate. "
        
        wait_time = staffing_rec.get("predicted_wait_time_minutes", 0)
        if isinstance(wait_time, (int, float)):
            summary += f"Expected wait time: {wait_time:.0f} minutes."
        
        return summary
