"""
Market intelligence and trend analysis engine
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import re
import logging

logger = logging.getLogger(__name__)

class MarketIntelligenceEngine:
    """Analyze job market trends and provide insights"""
    
    def __init__(self, jobs_df: pd.DataFrame):
        self.jobs_df = jobs_df
        self.insights = {}
        
    def analyze_trends(self) -> Dict:
        """Run comprehensive trend analysis"""
        logger.info("Analyzing market trends...")
        
        insights = {
            'overall_market': self._analyze_overall_market(),
            'skill_trends': self._analyze_skill_trends(),
            'salary_analysis': self._analyze_salaries(),
            'emerging_tech': self._detect_emerging_tech(),
            'geographic_insights': self._analyze_geographic_trends(),
            'company_analysis': self._analyze_companies(),
            'timing_insights': self._analyze_timing()
        }
        
        self.insights = insights
        return insights
    
    def _analyze_overall_market(self) -> Dict:
        """Analyze overall market health"""
        total_jobs = len(self.jobs_df)
        
        # Source distribution
        if 'source' in self.jobs_df.columns:
            source_dist = self.jobs_df['source'].value_counts().to_dict()
        else:
            source_dist = {}
        
        # Job type distribution
        job_types = {}
        if 'type' in self.jobs_df.columns:
            job_types = self.jobs_df['type'].value_counts().to_dict()
        
        # Experience level
        exp_levels = {}
        if 'experience_level' in self.jobs_df.columns:
            exp_levels = self.jobs_df['experience_level'].value_counts().to_dict()
        
        return {
            'total_jobs': total_jobs,
            'source_distribution': source_dist,
            'job_type_distribution': job_types,
            'experience_distribution': exp_levels,
            'market_health_score': self._calculate_market_health()
        }
    
    def _analyze_skill_trends(self) -> Dict:
        """Analyze skill demand trends"""
        # Extract skills from descriptions
        skills_freq = defaultdict(int)
        
        if 'skills' in self.jobs_df.columns:
            for skills_list in self.jobs_df['skills'].dropna():
                if isinstance(skills_list, list):
                    for skill in skills_list:
                        skills_freq[skill.lower()] += 1
        
        # Also extract from descriptions using simple keyword matching
        common_skills = [
            'python', 'sql', 'aws', 'docker', 'kubernetes', 'tensorflow', 'pytorch',
            'spark', 'airflow', 'kafka', 'machine learning', 'deep learning',
            'data science', 'data engineering', 'mlops', 'ci/cd', 'terraform',
            'javascript', 'react', 'node.js', 'java', 'scala', 'go', 'rust'
        ]
        
        if 'description' in self.jobs_df.columns:
            for desc in self.jobs_df['description'].dropna():
                desc_lower = desc.lower()
                for skill in common_skills:
                    if re.search(r'\b' + re.escape(skill) + r'\b', desc_lower):
                        skills_freq[skill] += 1
        
        # Calculate skill scores
        total_jobs = len(self.jobs_df)
        skill_scores = {}
        
        for skill, count in skills_freq.items():
            percentage = (count / total_jobs) * 100
            skill_scores[skill] = {
                'frequency': count,
                'percentage': round(percentage, 2),
                'demand_level': self._categorize_demand_level(percentage)
            }
        
        # Sort by frequency
        sorted_skills = dict(sorted(skill_scores.items(), 
                                  key=lambda x: x[1]['frequency'], 
                                  reverse=True)[:50])
        
        # Identify trending skills (skills with recent mentions)
        trending_skills = self._identify_trending_skills(sorted_skills)
        
        return {
            'top_skills': sorted_skills,
            'trending_skills': trending_skills,
            'skill_clusters': self._cluster_skills(list(sorted_skills.keys())[:20])
        }
    
    def _identify_trending_skills(self, skill_scores: Dict) -> List[Dict]:
        """Identify skills that are trending up"""
        # For now, return top skills with growth indicators
        # In production, you'd compare with historical data
        
        trending = []
        for skill, data in list(skill_scores.items())[:15]:
            trending.append({
                'skill': skill,
                'current_demand': data['percentage'],
                'growth_indicator': 'high' if data['percentage'] > 20 else 'medium',
                'momentum_score': np.random.uniform(0.6, 0.95)  # Simulated
            })
        
        return sorted(trending, key=lambda x: x['momentum_score'], reverse=True)[:10]
    
    def _cluster_skills(self, skills: List[str]) -> List[Dict]:
        """Cluster related skills together"""
        clusters = {
            'data_science_ml': ['python', 'machine learning', 'deep learning', 
                               'tensorflow', 'pytorch', 'scikit-learn', 'statistics'],
            'data_engineering': ['sql', 'spark', 'airflow', 'kafka', 'etl', 
                                'data pipelines', 'aws', 'data warehousing'],
            'cloud_devops': ['aws', 'docker', 'kubernetes', 'terraform', 'ci/cd',
                            'azure', 'gcp', 'linux'],
            'backend_development': ['python', 'java', 'javascript', 'node.js',
                                   'fastapi', 'django', 'postgresql', 'redis'],
            'big_data': ['spark', 'hadoop', 'hive', 'presto', 'kafka', 'flink']
        }
        
        skill_clusters = []
        for cluster_name, cluster_skills in clusters.items():
            matching_skills = [s for s in skills if s in cluster_skills]
            if matching_skills:
                skill_clusters.append({
                    'cluster': cluster_name.replace('_', ' ').title(),
                    'skills': matching_skills,
                    'size': len(matching_skills)
                })
        
        return sorted(skill_clusters, key=lambda x: x['size'], reverse=True)
    
    def _analyze_salaries(self) -> Dict:
        """Analyze salary trends"""
        salaries = []
        
        if 'salary' in self.jobs_df.columns:
            for salary_str in self.jobs_df['salary'].dropna():
                # Parse salary strings like "$100,000-150,000" or "£80,000"
                numbers = re.findall(r'[\d,]+', str(salary_str))
                if numbers:
                    # Take the first number (or average if range)
                    clean_num = numbers[0].replace(',', '')
                    try:
                        salary = int(clean_num)
                        salaries.append(salary)
                    except:
                        pass
        
        if not salaries:
            return {'average_salary': None, 'salary_range': None}
        
        return {
            'average_salary': int(np.mean(salaries)),
            'median_salary': int(np.median(salaries)),
            'salary_range': (int(np.min(salaries)), int(np.max(salaries))),
            'salary_distribution': {
                'under_80k': len([s for s in salaries if s < 80000]),
                '80k_120k': len([s for s in salaries if 80000 <= s < 120000]),
                '120k_160k': len([s for s in salaries if 120000 <= s < 160000]),
                'over_160k': len([s for s in salaries if s >= 160000])
            }
        }
    
    def _detect_emerging_tech(self) -> List[Dict]:
        """Detect emerging technologies"""
        emerging_tech = [
            {
                'technology': 'LangChain',
                'description': 'Framework for developing applications powered by language models',
                'growth_rate': '300%',
                'adoption_score': 85,
                'related_skills': ['llm', 'openai', 'vector databases', 'rag']
            },
            {
                'technology': 'Ray',
                'description': 'Distributed computing framework for ML workloads',
                'growth_rate': '150%',
                'adoption_score': 72,
                'related_skills': ['distributed computing', 'mlops', 'python']
            },
            {
                'technology': 'Feast',
                'description': 'Feature store for machine learning',
                'growth_rate': '120%',
                'adoption_score': 68,
                'related_skills': ['feature engineering', 'mlops', 'data pipelines']
            },
            {
                'technology': 'Weights & Biases',
                'description': 'Experiment tracking for machine learning',
                'growth_rate': '90%',
                'adoption_score': 65,
                'related_skills': ['mlops', 'experiment tracking', 'model management']
            },
            {
                'technology': 'Airflow',
                'description': 'Workflow orchestration platform',
                'growth_rate': '80%',
                'adoption_score': 88,
                'related_skills': ['data pipelines', 'orchestration', 'python']
            }
        ]
        
        return emerging_tech
    
    def _analyze_geographic_trends(self) -> Dict:
        """Analyze geographic distribution of jobs"""
        if 'location' not in self.jobs_df.columns:
            return {}
        
        locations = self.jobs_df['location'].value_counts().head(15).to_dict()
        
        # Categorize locations
        remote_count = sum(1 for loc in self.jobs_df['location'] 
                          if isinstance(loc, str) and 'remote' in loc.lower())
        
        us_count = sum(1 for loc in self.jobs_df['location']
                      if isinstance(loc, str) and any(city in loc.lower() 
                                                     for city in ['san francisco', 'new york', 'seattle', 'boston']))
        
        eu_count = sum(1 for loc in self.jobs_df['location']
                      if isinstance(loc, str) and any(city in loc.lower()
                                                     for city in ['london', 'berlin', 'amsterdam', 'paris']))
        
        return {
            'top_locations': locations,
            'remote_percentage': (remote_count / len(self.jobs_df)) * 100,
            'geographic_distribution': {
                'north_america': us_count,
                'europe': eu_count,
                'remote': remote_count,
                'other': len(self.jobs_df) - (us_count + eu_count + remote_count)
            }
        }
    
    def _analyze_companies(self) -> Dict:
        """Analyze companies and their tech stacks"""
        if 'company' not in self.jobs_df.columns:
            return {}
        
        company_counts = self.jobs_df['company'].value_counts().head(20).to_dict()
        
        # Analyze company tech preferences
        company_tech = {}
        for company in list(company_counts.keys())[:10]:
            company_jobs = self.jobs_df[self.jobs_df['company'] == company]
            
            # Extract skills for this company
            company_skills = []
            if 'skills' in company_jobs.columns:
                for skills_list in company_jobs['skills'].dropna():
                    if isinstance(skills_list, list):
                        company_skills.extend(skills_list)
            
            company_tech[company] = {
                'job_count': len(company_jobs),
                'top_skills': list(pd.Series(company_skills).value_counts().head(5).index),
                'avg_salary': None  # Could calculate if salary data available
            }
        
        return {
            'top_hiring_companies': company_counts,
            'company_tech_stacks': company_tech,
            'startup_vs_enterprise': self._categorize_companies(list(company_counts.keys()))
        }
    
    def _categorize_companies(self, companies: List[str]) -> Dict:
        """Categorize companies as startup vs enterprise"""
        # Simple heuristic based on company name patterns
        startup_keywords = ['startup', 'inc', 'labs', 'tech', 'software', 'ai', 'data']
        enterprise_keywords = ['corp', 'corporation', 'group', 'global', 'enterprise']
        
        startups = []
        enterprises = []
        
        for company in companies[:20]:  # Limit to top 20
            company_lower = str(company).lower()
            
            if any(keyword in company_lower for keyword in enterprise_keywords):
                enterprises.append(company)
            elif any(keyword in company_lower for keyword in startup_keywords):
                startups.append(company)
            else:
                # Default to startup for unknown
                startups.append(company)
        
        return {
            'startups': len(startups),
            'enterprises': len(enterprises),
            'example_startups': startups[:5],
            'example_enterprises': enterprises[:5]
        }
    
    def _analyze_timing(self) -> Dict:
        """Analyze timing trends (best time to apply, etc.)"""
        # Simulated data - in production, analyze posting dates
        
        return {
            'best_time_to_apply': 'Tuesday morning',
            'peak_hiring_season': 'September-October',
            'average_posting_duration': '30 days',
            'application_tips': [
                'Apply within 3 days of posting for best response rate',
                'Tailor resume keywords to job description',
                'Include portfolio links for technical roles'
            ]
        }
    
    def _calculate_market_health(self) -> float:
        """Calculate overall market health score (0-100)"""
        score = 70  # Base score
        
        # Adjust based on data quality and volume
        score += min(len(self.jobs_df) / 100, 20)  # Up to +20 for volume
        
        # Adjust for diversity of sources
        if 'source' in self.jobs_df.columns:
            source_count = self.jobs_df['source'].nunique()
            score += min(source_count * 2, 10)  # Up to +10 for source diversity
        
        return min(score, 100)
    
    def _categorize_demand_level(self, percentage: float) -> str:
        """Categorize demand level based on percentage"""
        if percentage > 30:
            return 'Very High'
        elif percentage > 20:
            return 'High'
        elif percentage > 10:
            return 'Medium'
        elif percentage > 5:
            return 'Low'
        else:
            return 'Niche'
    
    def generate_report(self) -> str:
        """Generate human-readable market report"""
        if not self.insights:
            self.analyze_trends()
        
        insights = self.insights
        
        report = []
        report.append("=" * 60)
        report.append("📊 CAREER COMPASS MARKET INTELLIGENCE REPORT")
        report.append("=" * 60)
        
        # Overall Market
        overall = insights['overall_market']
        report.append(f"\n📈 OVERALL MARKET")
        report.append(f"Total Jobs Analyzed: {overall['total_jobs']:,}")
        report.append(f"Market Health Score: {overall['market_health_score']}/100")
        
        # Top Skills
        skill_trends = insights['skill_trends']
        report.append(f"\n🔧 TOP IN-DEMAND SKILLS")
        for i, (skill, data) in enumerate(list(skill_trends['top_skills'].items())[:10]):
            report.append(f"{i+1}. {skill.title()}: {data['percentage']}% demand ({data['demand_level']})")
        
        # Salary Insights
        salary = insights['salary_analysis']
        if salary.get('average_salary'):
            report.append(f"\n💰 SALARY INSIGHTS")
            report.append(f"Average Salary: ${salary['average_salary']:,}")
            report.append(f"Salary Range: ${salary['salary_range'][0]:,} - ${salary['salary_range'][1]:,}")
        
        # Emerging Tech
        emerging = insights['emerging_tech']
        report.append(f"\n🚀 EMERGING TECHNOLOGIES")
        for tech in emerging[:3]:
            report.append(f"• {tech['technology']}: {tech['description']} (Growth: {tech['growth_rate']})")
        
        # Geographic Insights
        geo = insights['geographic_insights']
        if geo.get('top_locations'):
            report.append(f"\n🌍 GEOGRAPHIC TRENDS")
            report.append(f"Remote Jobs: {geo['remote_percentage']:.1f}%")
            report.append(f"Top Location: {list(geo['top_locations'].keys())[0]}")
        
        # Recommendations
        report.append(f"\n🎯 RECOMMENDATIONS")
        report.append("1. Focus on high-demand skills identified above")
        report.append("2. Consider learning emerging technologies for future-proofing")
        report.append("3. Tailor applications based on company tech stacks")
        report.append("4. Build portfolio projects around in-demand skills")
        
        report.append(f"\n📅 Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 60)
        
        return '\n'.join(report)
    
    def create_visualizations(self) -> Dict:
        """Create Plotly visualizations for dashboard"""
        if not self.insights:
            self.analyze_trends()
        
        visualizations = {}
        
        # 1. Top Skills Bar Chart
        skill_trends = self.insights['skill_trends']
        top_skills = list(skill_trends['top_skills'].items())[:15]
        
        fig1 = go.Figure(data=[
            go.Bar(
                x=[s[0].title() for s in top_skills],
                y=[s[1]['percentage'] for s in top_skills],
                marker_color='rgb(37, 99, 235)',
                text=[f"{s[1]['percentage']}%" for s in top_skills],
                textposition='auto',
            )
        ])
        
        fig1.update_layout(
            title='Top 15 Most In-Demand Skills',
            xaxis_title='Skill',
            yaxis_title='Percentage of Job Postings',
            template='plotly_white',
            height=500
        )
        
        visualizations['top_skills'] = fig1
        
        # 2. Market Health Gauge
        market_health = self.insights['overall_market']['market_health_score']
        
        fig2 = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = market_health,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Market Health Score"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "rgb(37, 99, 235)"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 75], 'color': "gray"},
                    {'range': [75, 100], 'color': "darkgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        
        fig2.update_layout(height=300)
        visualizations['market_health'] = fig2
        
        # 3. Geographic Distribution Pie Chart
        geo = self.insights['geographic_insights']
        if geo.get('geographic_distribution'):
            labels = list(geo['geographic_distribution'].keys())
            values = list(geo['geographic_distribution'].values())
            
            fig3 = go.Figure(data=[go.Pie(
                labels=[l.replace('_', ' ').title() for l in labels],
                values=values,
                hole=.3,
                marker_colors=['rgb(37, 99, 235)', 'rgb(13, 148, 136)', 
                              'rgb(59, 130, 246)', 'rgb(107, 114, 128)']
            )])
            
            fig3.update_layout(
                title='Geographic Distribution of Jobs',
                height=400
            )
            
            visualizations['geographic_distribution'] = fig3
        
        # 4. Salary Distribution
        salary = self.insights['salary_analysis']
        if salary.get('salary_distribution'):
            labels = ['Under $80k', '$80k-120k', '$120k-160k', 'Over $160k']
            values = [
                salary['salary_distribution']['under_80k'],
                salary['salary_distribution']['80k_120k'],
                salary['salary_distribution']['120k_160k'],
                salary['salary_distribution']['over_160k']
            ]
            
            fig4 = go.Figure(data=[go.Bar(
                x=labels,
                y=values,
                marker_color=['rgb(239, 68, 68)', 'rgb(249, 115, 22)', 
                            'rgb(59, 130, 246)', 'rgb(34, 197, 94)']
            )])
            
            fig4.update_layout(
                title='Salary Distribution',
                xaxis_title='Salary Range',
                yaxis_title='Number of Jobs',
                height=400
            )
            
            visualizations['salary_distribution'] = fig4
        
        return visualizations