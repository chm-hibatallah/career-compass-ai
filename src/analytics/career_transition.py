"""
Career transition simulation and analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import networkx as nx
import logging

logger = logging.getLogger(__name__)

class CareerTransitionSimulator:
    """Simulate career transitions and analyze feasibility"""
    
    def __init__(self, market_data: pd.DataFrame, ontology):
        self.market_data = market_data
        self.ontology = ontology
        
        # Career role definitions
        self.role_definitions = {
            'data_analyst': {
                'description': 'Analyzes data to provide business insights',
                'core_skills': ['sql', 'excel', 'tableau', 'statistics', 'python'],
                'average_salary': 85000,
                'seniority_path': ['Junior Analyst', 'Analyst', 'Senior Analyst', 'Lead Analyst']
            },
            'data_scientist': {
                'description': 'Builds machine learning models for prediction and insight',
                'core_skills': ['python', 'machine learning', 'statistics', 'sql', 'data visualization'],
                'average_salary': 120000,
                'seniority_path': ['Junior Data Scientist', 'Data Scientist', 'Senior Data Scientist', 'Principal Data Scientist']
            },
            'machine_learning_engineer': {
                'description': 'Builds and deploys machine learning systems at scale',
                'core_skills': ['python', 'machine learning', 'docker', 'aws', 'mlops'],
                'average_salary': 140000,
                'seniority_path': ['ML Engineer', 'Senior ML Engineer', 'ML Architect', 'Head of ML']
            },
            'data_engineer': {
                'description': 'Builds and maintains data pipelines and infrastructure',
                'core_skills': ['sql', 'python', 'spark', 'aws', 'airflow'],
                'average_salary': 130000,
                'seniority_path': ['Data Engineer', 'Senior Data Engineer', 'Data Architect', 'Director of Data Engineering']
            },
            'mlops_engineer': {
                'description': 'Focuses on ML deployment, monitoring, and automation',
                'core_skills': ['docker', 'kubernetes', 'aws', 'mlops', 'ci/cd'],
                'average_salary': 150000,
                'seniority_path': ['MLOps Engineer', 'Senior MLOps Engineer', 'MLOps Architect']
            }
        }
        
        # Transition feasibility matrix
        self.transition_matrix = {
            'data_analyst': {
                'data_scientist': {'difficulty': 'medium', 'common_path': True, 'success_rate': 0.65},
                'data_engineer': {'difficulty': 'medium', 'common_path': True, 'success_rate': 0.60},
                'machine_learning_engineer': {'difficulty': 'hard', 'common_path': False, 'success_rate': 0.40},
                'mlops_engineer': {'difficulty': 'hard', 'common_path': False, 'success_rate': 0.35}
            },
            'data_scientist': {
                'machine_learning_engineer': {'difficulty': 'medium', 'common_path': True, 'success_rate': 0.70},
                'data_engineer': {'difficulty': 'medium', 'common_path': True, 'success_rate': 0.65},
                'mlops_engineer': {'difficulty': 'medium', 'common_path': True, 'success_rate': 0.60}
            },
            'data_engineer': {
                'mlops_engineer': {'difficulty': 'medium', 'common_path': True, 'success_rate': 0.75},
                'machine_learning_engineer': {'difficulty': 'hard', 'common_path': False, 'success_rate': 0.50},
                'data_scientist': {'difficulty': 'hard', 'common_path': False, 'success_rate': 0.45}
            }
        }
    
    def analyze_transition(self, current_role: str, target_role: str, 
                         current_skills: List[str]) -> Dict:
        """Analyze feasibility of career transition"""
        
        # Normalize role names
        current_role_key = self._normalize_role_name(current_role)
        target_role_key = self._normalize_role_name(target_role)
        
        if current_role_key not in self.role_definitions:
            return {'error': f'Unknown current role: {current_role}'}
        
        if target_role_key not in self.role_definitions:
            return {'error': f'Unknown target role: {target_role}'}
        
        # Get role definitions
        current_role_def = self.role_definitions[current_role_key]
        target_role_def = self.role_definitions[target_role_key]
        
        # Calculate skill overlap
        current_lower = [s.lower() for s in current_skills]
        target_core_lower = [s.lower() for s in target_role_def['core_skills']]
        
        overlapping_skills = [s for s in current_lower if s in target_core_lower]
        missing_skills = [s for s in target_core_lower if s not in current_lower]
        
        # Calculate metrics
        skill_coverage = len(overlapping_skills) / len(target_core_lower) * 100
        salary_increase = target_role_def['average_salary'] - current_role_def['average_salary']
        
        # Get transition feasibility
        transition_info = self._get_transition_feasibility(current_role_key, target_role_key)
        
        # Generate learning path for missing skills
        learning_path = []
        total_hours = 0
        
        for skill in missing_skills[:5]:  # Limit to top 5
            path_info = self.ontology.find_learning_path(current_lower, skill)
            if 'error' not in path_info:
                learning_path.append({
                    'skill': skill,
                    'path_length': path_info['total_steps'],
                    'total_hours': path_info['total_hours']
                })
                total_hours += path_info['total_hours']
        
        # Calculate timeline
        estimated_months = total_hours / (10 * 4.33)  # 10 hours/week
        
        # Generate transition score
        transition_score = self._calculate_transition_score(
            skill_coverage, 
            transition_info['success_rate'],
            salary_increase,
            estimated_months
        )
        
        return {
            'transition_analysis': {
                'from': current_role_def['description'],
                'to': target_role_def['description'],
                'skill_coverage': round(skill_coverage, 1),
                'missing_core_skills': missing_skills,
                'salary_increase': salary_increase,
                'salary_increase_percentage': (salary_increase / current_role_def['average_salary']) * 100
            },
            'feasibility': {
                'difficulty': transition_info['difficulty'],
                'common_path': transition_info['common_path'],
                'success_rate': transition_info['success_rate'],
                'transition_score': transition_score,
                'recommendation': self._generate_transition_recommendation(transition_score, skill_coverage)
            },
            'learning_requirements': {
                'missing_skills_count': len(missing_skills),
                'estimated_total_hours': total_hours,
                'estimated_months': round(estimated_months, 1),
                'learning_path': learning_path
            },
            'market_opportunity': {
                'current_role_demand': self._calculate_role_demand(current_role_key),
                'target_role_demand': self._calculate_role_demand(target_role_key),
                'growth_trend': self._analyze_role_growth(target_role_key)
            }
        }
    
    def _normalize_role_name(self, role: str) -> str:
        """Normalize role name to key"""
        role_lower = role.lower().replace(' ', '_')
        
        # Map common variations
        role_mapping = {
            'data_analyst': 'data_analyst',
            'data_scientist': 'data_scientist',
            'machine_learning_engineer': 'machine_learning_engineer',
            'ml_engineer': 'machine_learning_engineer',
            'data_engineer': 'data_engineer',
            'mlops_engineer': 'mlops_engineer',
            'mlops': 'mlops_engineer'
        }
        
        for key, value in role_mapping.items():
            if key in role_lower:
                return value
        
        # Try direct match
        if role_lower in self.role_definitions:
            return role_lower
        
        # Default to data_scientist
        return 'data_scientist'
    
    def _get_transition_feasibility(self, from_role: str, to_role: str) -> Dict:
        """Get transition feasibility information"""
        if from_role in self.transition_matrix and to_role in self.transition_matrix[from_role]:
            return self.transition_matrix[from_role][to_role]
        
        # Default if no specific transition data
        return {
            'difficulty': 'unknown',
            'common_path': False,
            'success_rate': 0.5
        }
    
    def _calculate_transition_score(self, skill_coverage: float, success_rate: float,
                                  salary_increase: float, estimated_months: float) -> float:
        """Calculate overall transition score (0-100)"""
        
        # Weighted components
        skill_score = min(100, skill_coverage * 1.5)  # 0-100
        success_score = success_rate * 100  # 0-100
        
        # Salary score (normalize)
        salary_score = min(100, salary_increase / 50000 * 100)  # $50k increase = 100
        
        # Time score (shorter is better)
        time_score = max(0, 100 - (estimated_months * 5))  # 20 months = 0
        
        # Weighted average
        weights = {
            'skill': 0.4,
            'success': 0.3,
            'salary': 0.2,
            'time': 0.1
        }
        
        total_score = (
            skill_score * weights['skill'] +
            success_score * weights['success'] +
            salary_score * weights['salary'] +
            time_score * weights['time']
        )
        
        return round(total_score, 1)
    
    def _generate_transition_recommendation(self, score: float, skill_coverage: float) -> str:
        """Generate recommendation based on transition score"""
        if score >= 80:
            return 'HIGHLY RECOMMENDED - Strong alignment with target role'
        elif score >= 60:
            return 'RECOMMENDED - Good transition opportunity'
        elif score >= 40:
            return 'FEASIBLE - Requires significant upskilling'
        elif score >= 20:
            return 'CHALLENGING - Major skill gap to overcome'
        else:
            return 'NOT RECOMMENDED - Consider different target role'
    
    def _calculate_role_demand(self, role_key: str) -> float:
        """Calculate demand for role in market data"""
        if 'description' not in self.market_data.columns:
            return 50  # Default
        
        # Search for role in descriptions
        role_terms = {
            'data_analyst': ['data analyst', 'business analyst'],
            'data_scientist': ['data scientist', 'data science'],
            'machine_learning_engineer': ['machine learning engineer', 'ml engineer'],
            'data_engineer': ['data engineer'],
            'mlops_engineer': ['mlops', 'ml ops']
        }
        
        terms = role_terms.get(role_key, [role_key.replace('_', ' ')])
        
        count = 0
        for desc in self.market_data['description'].astype(str).str.lower():
            if any(term in desc for term in terms):
                count += 1
        
        percentage = (count / len(self.market_data)) * 100
        return round(percentage, 2)
    
    def _analyze_role_growth(self, role_key: str) -> str:
        """Analyze growth trend for role"""
        # Simulated growth analysis
        growth_trends = {
            'data_analyst': 'Stable',
            'data_scientist': 'Growing',
            'machine_learning_engineer': 'Rapidly Growing',
            'data_engineer': 'High Growth',
            'mlops_engineer': 'Explosive Growth'
        }
        
        return growth_trends.get(role_key, 'Growing')
    
    def compare_multiple_transitions(self, current_role: str, 
                                   target_roles: List[str], 
                                   current_skills: List[str]) -> pd.DataFrame:
        """Compare multiple potential career transitions"""
        results = []
        
        for target_role in target_roles:
            analysis = self.analyze_transition(current_role, target_role, current_skills)
            
            if 'error' not in analysis:
                results.append({
                    'target_role': target_role,
                    'skill_coverage': analysis['transition_analysis']['skill_coverage'],
                    'missing_skills': len(analysis['transition_analysis']['missing_core_skills']),
                    'salary_increase': analysis['transition_analysis']['salary_increase'],
                    'estimated_months': analysis['learning_requirements']['estimated_months'],
                    'transition_score': analysis['feasibility']['transition_score'],
                    'difficulty': analysis['feasibility']['difficulty'],
                    'recommendation': analysis['feasibility']['recommendation']
                })
        
        if results:
            df = pd.DataFrame(results)
            df = df.sort_values('transition_score', ascending=False)
            df['rank'] = range(1, len(df) + 1)
            return df
        
        return pd.DataFrame()
    
    def generate_transition_roadmap(self, current_role: str, target_role: str,
                                  current_skills: List[str], timeline_months: int = 12) -> Dict:
        """Generate detailed transition roadmap"""
        
        analysis = self.analyze_transition(current_role, target_role, current_skills)
        
        if 'error' in analysis:
            return analysis
        
        # Create phased roadmap
        roadmap = {
            'phase_1_foundation': {
                'duration': 'Months 1-3',
                'focus': 'Build core missing skills',
                'skills': analysis['transition_analysis']['missing_core_skills'][:3],
                'activities': [
                    'Complete foundational courses',
                    'Build small projects',
                    'Join relevant communities'
                ],
                'milestones': [
                    'Complete 2-3 online courses',
                    'Build portfolio project 1',
                    'Network with 5 professionals in target role'
                ]
            },
            'phase_2_application': {
                'duration': 'Months 4-6',
                'focus': 'Apply skills to real projects',
                'skills': analysis['transition_analysis']['missing_core_skills'][3:6],
                'activities': [
                    'Contribute to open source',
                    'Freelance projects',
                    'Internal projects at current job'
                ],
                'milestones': [
                    'Complete 2-3 substantial projects',
                    'Get first client/freelance work',
                    'Update LinkedIn profile with new skills'
                ]
            },
            'phase_3_transition': {
                'duration': 'Months 7-9',
                'focus': 'Job search preparation',
                'skills': ['Interview preparation', 'Portfolio polish', 'Networking'],
                'activities': [
                    'Mock interviews',
                    'Portfolio website',
                    'Targeted networking'
                ],
                'milestones': [
                    'Complete 10+ mock interviews',
                    'Launch portfolio website',
                    'Apply to 50+ target positions'
                ]
            },
            'phase_4_placement': {
                'duration': 'Months 10-12',
                'focus': 'Secure target role',
                'skills': ['Negotiation', 'Onboarding', 'Continued learning'],
                'activities': [
                    'Interview process',
                    'Offer negotiation',
                    'Planning first 90 days'
                ],
                'milestones': [
                    'Receive job offer',
                    'Successfully negotiate salary',
                    'Start new role in target position'
                ]
            }
        }
        
        # Add success metrics
        success_metrics = {
            'target_timeline': f'{timeline_months} months',
            'estimated_salary_increase': f'${analysis["transition_analysis"]["salary_increase"]:,}',
            'success_probability': f'{analysis["feasibility"]["success_rate"] * 100:.0f}%',
            'key_risks': [
                'Market conditions changing',
                'Learning slower than expected',
                'Competition for roles'
            ],
            'mitigation_strategies': [
                'Continuous market monitoring',
                'Adjust learning pace as needed',
                'Build strong network for referrals'
            ]
        }
        
        return {
            'roadmap': roadmap,
            'success_metrics': success_metrics,
            'original_analysis': analysis
        }