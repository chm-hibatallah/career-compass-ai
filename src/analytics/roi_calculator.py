"""
ROI Calculator for skill investments
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ROICalculator:
    """Calculate ROI for learning different skills"""
    
    def __init__(self, market_data: pd.DataFrame, salary_data: pd.DataFrame = None):
        self.market_data = market_data
        self.salary_data = salary_data or self._load_default_salary_data()
        
        # Learning time estimates (hours)
        self.learning_time_estimates = {
            'beginner': {
                'python': 40,
                'sql': 30,
                'excel': 20,
                'tableau': 25,
                'powerbi': 30
            },
            'intermediate': {
                'machine learning': 60,
                'aws': 50,
                'docker': 25,
                'spark': 40,
                'airflow': 35
            },
            'advanced': {
                'deep learning': 80,
                'kubernetes': 40,
                'mlops': 60,
                'distributed systems': 70,
                'llm': 50
            }
        }
        
        # Course costs (approximate)
        self.course_costs = {
            'free': 0,
            'udemy': 15,
            'coursera': 50,
            'pluralsight': 30,
            'bootcamp': 10000,
            'university': 50000
        }
    
    def _load_default_salary_data(self) -> pd.DataFrame:
        """Load default salary data"""
        # In production, use real salary data from Glassdoor, Levels.fyi, etc.
        salary_data = {
            'role': ['Data Analyst', 'Data Scientist', 'ML Engineer', 'Data Engineer', 
                    'MLOps Engineer', 'AI Researcher'],
            'entry_level': [65000, 85000, 95000, 90000, 100000, 120000],
            'mid_level': [85000, 120000, 140000, 130000, 150000, 180000],
            'senior_level': [110000, 160000, 190000, 170000, 200000, 250000],
            'skill_premium': {
                'python': 15000,
                'machine learning': 25000,
                'aws': 20000,
                'docker': 15000,
                'kubernetes': 20000,
                'spark': 18000,
                'tensorflow': 20000,
                'pytorch': 22000
            }
        }
        return pd.DataFrame(salary_data)
    
    def calculate_skill_roi(self, skill: str, current_role: str = None, 
                          target_role: str = None, hours_per_week: int = 10) -> Dict:
        """Calculate ROI for learning a specific skill"""
        
        # Get skill demand from market data
        skill_demand = self._calculate_skill_demand(skill)
        
        # Estimate learning time
        learning_time = self._estimate_learning_time(skill)
        
        # Calculate time to learn
        weeks_to_learn = learning_time / hours_per_week
        
        # Estimate salary impact
        salary_impact = self._estimate_salary_impact(skill, current_role, target_role)
        
        # Calculate costs
        learning_cost = self._estimate_learning_cost(skill)
        
        # Calculate ROI metrics
        if salary_impact['annual_increase'] > 0 and learning_time > 0:
            # Simple ROI calculation
            roi_ratio = (salary_impact['annual_increase'] * 3) / (learning_cost + (weeks_to_learn * 100))
            
            # Time to break even
            months_to_break_even = (learning_cost / (salary_impact['monthly_increase'])) if salary_impact['monthly_increase'] > 0 else 999
            
            roi_score = min(100, roi_ratio * 10)
        else:
            roi_ratio = 0
            months_to_break_even = 999
            roi_score = 0
        
        return {
            'skill': skill,
            'demand_analysis': skill_demand,
            'learning_estimates': {
                'total_hours': learning_time,
                'weeks_at_10hrs_week': weeks_to_learn,
                'months_at_10hrs_week': weeks_to_learn / 4.33,
                'difficulty_level': self._get_difficulty_level(skill)
            },
            'financial_impact': salary_impact,
            'cost_analysis': {
                'learning_cost': learning_cost,
                'opportunity_cost': weeks_to_learn * 100,  # Approx $100/week opportunity cost
                'total_investment': learning_cost + (weeks_to_learn * 100)
            },
            'roi_metrics': {
                'roi_ratio': round(roi_ratio, 2),
                'roi_score': round(roi_score, 2),
                'months_to_break_even': round(months_to_break_even, 1),
                'payback_period': 'Good' if months_to_break_even < 12 else 'Moderate' if months_to_break_even < 24 else 'Long'
            },
            'recommendation': self._generate_recommendation(roi_score, skill_demand['percentage'])
        }
    
    def _calculate_skill_demand(self, skill: str) -> Dict:
        """Calculate current demand for skill"""
        skill_lower = skill.lower()
        
        # Count occurrences in job descriptions
        if 'description' in self.market_data.columns:
            descriptions = self.market_data['description'].astype(str).str.lower()
            skill_count = descriptions.str.contains(r'\b' + re.escape(skill_lower) + r'\b').sum()
        else:
            skill_count = 0
        
        # Count in skills lists
        if 'skills' in self.market_data.columns:
            skills_count = 0
            for skills_list in self.market_data['skills'].dropna():
                if isinstance(skills_list, list):
                    if any(skill_lower in str(s).lower() for s in skills_list):
                        skills_count += 1
        else:
            skills_count = 0
        
        total_jobs = len(self.market_data)
        total_count = skill_count + skills_count
        
        percentage = (total_count / total_jobs) * 100 if total_jobs > 0 else 0
        
        return {
            'job_count': total_count,
            'percentage': round(percentage, 2),
            'demand_level': self._categorize_demand(percentage)
        }
    
    def _estimate_learning_time(self, skill: str) -> int:
        """Estimate learning time in hours"""
        skill_lower = skill.lower()
        
        # Check each difficulty level
        for level, skills in self.learning_time_estimates.items():
            for skill_name, hours in skills.items():
                if skill_lower in skill_name.lower() or skill_name.lower() in skill_lower:
                    return hours
        
        # Default estimates based on skill type
        if any(tech in skill_lower for tech in ['python', 'sql', 'javascript']):
            return 40
        elif any(tech in skill_lower for tech in ['aws', 'docker', 'spark']):
            return 50
        elif any(tech in skill_lower for tech in ['machine learning', 'deep learning', 'mlops']):
            return 60
        elif any(tech in skill_lower for tech in ['kubernetes', 'terraform', 'airflow']):
            return 35
        else:
            return 30  # Default
    
    def _estimate_salary_impact(self, skill: str, current_role: str = None, 
                              target_role: str = None) -> Dict:
        """Estimate salary impact of learning skill"""
        
        # Get base salary premium for skill
        skill_lower = skill.lower()
        base_premium = 0
        
        for skill_name, premium in self.salary_data.get('skill_premium', {}).items():
            if skill_lower in skill_name.lower() or skill_name.lower() in skill_lower:
                base_premium = premium
                break
        
        # If skill not found, estimate based on type
        if base_premium == 0:
            if any(tech in skill_lower for tech in ['machine learning', 'deep learning', 'ai']):
                base_premium = 25000
            elif any(tech in skill_lower for tech in ['aws', 'azure', 'gcp']):
                base_premium = 20000
            elif any(tech in skill_lower for tech in ['docker', 'kubernetes']):
                base_premium = 15000
            elif any(tech in skill_lower for tech in ['python', 'sql']):
                base_premium = 10000
            else:
                base_premium = 5000
        
        # Calculate role transition impact if provided
        role_transition_impact = 0
        if current_role and target_role:
            current_salary = self._get_role_salary(current_role, 'mid_level')
            target_salary = self._get_role_salary(target_role, 'mid_level')
            role_transition_impact = max(0, target_salary - current_salary)
        
        # Total impact is sum of skill premium and role transition
        total_annual_increase = base_premium + (role_transition_impact * 0.3)  # Assuming skill enables 30% of transition
        
        return {
            'skill_premium': base_premium,
            'role_transition_impact': role_transition_impact,
            'annual_increase': total_annual_increase,
            'monthly_increase': total_annual_increase / 12,
            'hourly_rate_increase': total_annual_increase / 2080  # Assuming 2080 work hours/year
        }
    
    def _get_role_salary(self, role: str, level: str = 'mid_level') -> int:
        """Get salary for a specific role and level"""
        role_data = self.salary_data[self.salary_data['role'].str.contains(role, case=False, na=False)]
        
        if not role_data.empty:
            return int(role_data.iloc[0][level])
        
        # Default salaries if role not found
        default_salaries = {
            'data analyst': 85000,
            'data scientist': 120000,
            'machine learning engineer': 140000,
            'data engineer': 130000,
            'mlops engineer': 150000,
            'software engineer': 110000
        }
        
        for role_name, salary in default_salaries.items():
            if role_name in role.lower():
                return salary
        
        return 80000  # Default
    
    def _estimate_learning_cost(self, skill: str) -> float:
        """Estimate learning cost"""
        # Simple cost estimation
        if any(tech in skill.lower() for tech in ['machine learning', 'deep learning', 'ai']):
            return self.course_costs['coursera']  # $50
        elif any(tech in skill.lower() for tech in ['aws', 'azure', 'gcp']):
            return self.course_costs['udemy']  # $15
        elif any(tech in skill.lower() for tech in ['docker', 'kubernetes']):
            return self.course_costs['free']  # $0 (good free resources)
        else:
            return self.course_costs['udemy']  # $15 default
    
    def _get_difficulty_level(self, skill: str) -> str:
        """Determine difficulty level"""
        skill_lower = skill.lower()
        
        if any(tech in skill_lower for tech in ['python', 'sql', 'excel', 'tableau']):
            return 'Beginner'
        elif any(tech in skill_lower for tech in ['aws', 'docker', 'spark', 'airflow']):
            return 'Intermediate'
        elif any(tech in skill_lower for tech in ['kubernetes', 'mlops', 'distributed', 'llm']):
            return 'Advanced'
        else:
            return 'Intermediate'
    
    def _categorize_demand(self, percentage: float) -> str:
        """Categorize demand level"""
        if percentage > 25:
            return 'Very High'
        elif percentage > 15:
            return 'High'
        elif percentage > 8:
            return 'Medium'
        elif percentage > 3:
            return 'Low'
        else:
            return 'Niche'
    
    def _generate_recommendation(self, roi_score: float, demand_percentage: float) -> str:
        """Generate recommendation based on ROI and demand"""
        if roi_score > 70 and demand_percentage > 15:
            return 'STRONGLY RECOMMENDED - High ROI and strong market demand'
        elif roi_score > 50 and demand_percentage > 10:
            return 'RECOMMENDED - Good ROI and solid market demand'
        elif roi_score > 30 or demand_percentage > 15:
            return 'CONSIDER - Either good ROI or high demand'
        else:
            return 'LOW PRIORITY - Lower ROI and demand'
    
    def compare_multiple_skills(self, skills: List[str], hours_per_week: int = 10) -> pd.DataFrame:
        """Compare ROI for multiple skills"""
        results = []
        
        for skill in skills:
            roi_data = self.calculate_skill_roi(skill, hours_per_week=hours_per_week)
            
            results.append({
                'skill': skill,
                'demand_percentage': roi_data['demand_analysis']['percentage'],
                'demand_level': roi_data['demand_analysis']['demand_level'],
                'learning_hours': roi_data['learning_estimates']['total_hours'],
                'salary_increase': roi_data['financial_impact']['annual_increase'],
                'learning_cost': roi_data['cost_analysis']['learning_cost'],
                'roi_score': roi_data['roi_metrics']['roi_score'],
                'months_to_break_even': roi_data['roi_metrics']['months_to_break_even'],
                'recommendation': roi_data['recommendation']
            })
        
        df = pd.DataFrame(results)
        
        # Sort by ROI score
        df = df.sort_values('roi_score', ascending=False)
        
        # Add rank
        df['rank'] = range(1, len(df) + 1)
        
        return df
    
    def generate_learning_plan(self, current_skills: List[str], target_skills: List[str], 
                             hours_per_week: int = 10, timeline_weeks: int = 26) -> Dict:
        """Generate optimized learning plan for multiple skills"""
        
        # Calculate ROI for target skills
        skills_df = self.compare_multiple_skills(target_skills, hours_per_week)
        
        # Filter out skills already known
        current_lower = [s.lower() for s in current_skills]
        skills_df = skills_df[~skills_df['skill'].str.lower().isin(current_lower)]
        
        if skills_df.empty:
            return {'error': 'All target skills already known or no valid skills provided'}
        
        # Create learning plan
        total_available_hours = hours_per_week * timeline_weeks
        accumulated_hours = 0
        learning_plan = []
        
        for _, row in skills_df.iterrows():
            skill_hours = row['learning_hours']
            
            # Check if we have time for this skill
            if accumulated_hours + skill_hours <= total_available_hours:
                learning_plan.append({
                    'skill': row['skill'],
                    'priority': len(learning_plan) + 1,
                    'estimated_hours': skill_hours,
                    'estimated_weeks': skill_hours / hours_per_week,
                    'roi_score': row['roi_score'],
                    'salary_impact': row['salary_increase']
                })
                accumulated_hours += skill_hours
        
        # Calculate plan metrics
        if learning_plan:
            total_salary_impact = sum(item['salary_impact'] for item in learning_plan)
            total_learning_weeks = sum(item['estimated_weeks'] for item in learning_plan)
            
            plan_efficiency = (sum(item['roi_score'] for item in learning_plan) / 
                            len(learning_plan)) if learning_plan else 0
            
            return {
                'learning_plan': learning_plan,
                'metrics': {
                    'total_skills': len(learning_plan),
                    'total_weeks': total_learning_weeks,
                    'total_hours': accumulated_hours,
                    'estimated_salary_impact': total_salary_impact,
                    'plan_efficiency_score': plan_efficiency,
                    'timeline_feasibility': 'Feasible' if total_learning_weeks <= timeline_weeks else 'Extended',
                    'completion_date': (datetime.now() + 
                                      timedelta(weeks=total_learning_weeks)).strftime('%B %d, %Y')
                },
                'recommendations': self._generate_plan_recommendations(learning_plan)
            }
        
        return {'error': 'No skills could be fit into the timeline'}
    
    def _generate_plan_recommendations(self, learning_plan: List[Dict]) -> List[str]:
        """Generate recommendations for learning plan"""
        recommendations = []
        
        if learning_plan:
            # Quick wins (skills with low hours, high ROI)
            quick_wins = [item for item in learning_plan 
                         if item['estimated_hours'] <= 30 and item['roi_score'] > 60]
            
            if quick_wins:
                recommendations.append(
                    f"Start with '{quick_wins[0]['skill']}' - quick win with {quick_wins[0]['estimated_weeks']:.1f} weeks to learn"
                )
            
            # High impact skills
            high_impact = sorted(learning_plan, key=lambda x: x['salary_impact'], reverse=True)[:2]
            if len(high_impact) >= 2:
                recommendations.append(
                    f"Focus on '{high_impact[0]['skill']}' and '{high_impact[1]['skill']}' for maximum salary impact"
                )
            
            # Timeline optimization
            total_weeks = sum(item['estimated_weeks'] for item in learning_plan)
            if total_weeks > 26:
                recommendations.append(
                    f"Consider increasing weekly hours to {int(total_weeks / 26 * 10)} to complete in 6 months"
                )
        
        return recommendations