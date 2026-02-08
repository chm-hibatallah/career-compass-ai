"""
Analysis pages for the Streamlit app
"""
import streamlit as st
import pandas as pd
from typing import Dict, List
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from app.components.dashboard import DashboardComponents
from app.utils.helpers import get_cached_data, cache_data, format_currency, format_percentage

def show_skill_analysis_page(market_data: pd.DataFrame, 
                           skill_extractor, 
                           market_engine):
    """Show skill analysis page"""
    st.header("🔍 Skill Analysis")
    
    # Skill search
    col1, col2 = st.columns([2, 1])
    
    with col1:
        skill_query = st.text_input("Search for a skill:", placeholder="e.g., Python, Docker, AWS")
    
    with col2:
        analysis_type = st.selectbox("Analysis Type", ["Demand", "Trend", "Salary Impact"])
    
    if skill_query:
        # Get skill analysis
        skill_demand = market_engine._calculate_skill_demand(skill_query)
        
        # Display metrics
        cols = st.columns(3)
        
        with cols[0]:
            DashboardComponents.metric_card(
                "Demand Level",
                skill_demand['demand_level'].upper(),
                f"{skill_demand['percentage']}% of jobs",
                icon="📈"
            )
        
        with cols[1]:
            DashboardComponents.metric_card(
                "Job Count",
                f"{skill_demand['job_count']:,}",
                "Total postings",
                icon="💼"
            )
        
        with cols[2]:
            # Simulated growth
            growth = "Rising" if skill_demand['percentage'] > 15 else "Stable"
            DashboardComponents.metric_card(
                "Market Trend",
                growth,
                "6-month outlook",
                icon="📊"
            )
        
        # Skill details
        st.subheader("Skill Details")
        
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "🎯 Related Skills", "💰 Salary Impact"])
        
        with tab1:
            # Skill overview
            st.markdown("""
            #### Skill Overview
            This skill is currently in **{}** demand in the job market.
            """.format(skill_demand['demand_level']))
            
            # Create gauge for demand
            demand_score = min(100, skill_demand['percentage'] * 3)
            fig = DashboardComponents.create_gauge_chart(demand_score, "Demand Score")
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Related skills (from ontology)
            st.info("Related skills often appear together in job postings")
            
            # Simulated related skills
            related_skills = {
                "Python": ["Django", "Flask", "FastAPI", "Pandas", "NumPy"],
                "AWS": ["Docker", "Kubernetes", "Terraform", "CI/CD"],
                "Machine Learning": ["TensorFlow", "PyTorch", "scikit-learn", "Statistics"],
                "Docker": ["Kubernetes", "AWS", "CI/CD", "DevOps"],
                "SQL": ["PostgreSQL", "MySQL", "Data Warehousing", "ETL"]
            }
            
            for skill, related in related_skills.items():
                if skill.lower() in skill_query.lower():
                    for related_skill in related:
                        DashboardComponents.skill_card(
                            related_skill,
                            level="intermediate",
                            demand="high",
                            hours=30
                        )
        
        with tab3:
            # Salary impact analysis
            st.markdown("""
            #### Salary Impact
            Estimated salary premium for having this skill:
            """)
            
            # Simulated salary data
            salary_impact = {
                "Entry Level": 10000,
                "Mid Level": 20000,
                "Senior Level": 35000
            }
            
            for level, impact in salary_impact.items():
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**{level}**")
                with col2:
                    st.markdown(f"**+{format_currency(impact)}**")
            
            # ROI calculation
            st.subheader("ROI Calculation")
            
            hours_per_week = st.slider("Hours per week for learning", 5, 40, 10)
            current_salary = st.number_input("Current salary ($)", 50000, 300000, 80000)
            
            if st.button("Calculate ROI", type="primary"):
                # Simplified ROI calculation
                learning_hours = 40  # Estimated
                weeks = learning_hours / hours_per_week
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Weeks to Learn", f"{weeks:.1f}")
                
                with col2:
                    st.metric("Estimated Salary Boost", "+$15,000")
                
                with col3:
                    st.metric("ROI Score", "8.2/10")

def show_career_transition_page(market_data: pd.DataFrame, 
                              transition_simulator):
    """Show career transition page"""
    st.header("🎯 Career Transition Analysis")
    
    # User inputs
    col1, col2 = st.columns(2)
    
    with col1:
        current_role = st.selectbox(
            "Current Role",
            ["Data Analyst", "Software Engineer", "Business Analyst", 
             "DevOps Engineer", "Product Manager", "Other"]
        )
        
        current_experience = st.slider("Years of Experience", 0, 20, 3)
    
    with col2:
        target_role = st.selectbox(
            "Target Role",
            ["Data Scientist", "Machine Learning Engineer", "Data Engineer",
             "MLOps Engineer", "AI Researcher", "Backend Developer"]
        )
        
        timeline_months = st.slider("Target Timeline (months)", 3, 24, 12)
    
    # Skill input
    st.subheader("Your Current Skills")
    current_skills = st.multiselect(
        "Select your current skills:",
        ["Python", "SQL", "JavaScript", "AWS", "Docker", "Machine Learning",
         "Statistics", "Excel", "Tableau", "Git", "Linux", "Networking"],
        default=["Python", "SQL"]
    )
    
    if st.button("Analyze Transition", type="primary"):
        with st.spinner("Analyzing career transition..."):
            # Get transition analysis
            analysis = transition_simulator.analyze_transition(
                current_role, target_role, current_skills
            )
            
            if 'error' not in analysis:
                # Display results
                st.success("Analysis complete!")
                
                # Key metrics
                cols = st.columns(4)
                
                with cols[0]:
                    DashboardComponents.metric_card(
                        "Transition Score",
                        f"{analysis['feasibility']['transition_score']}/100",
                        analysis['feasibility']['difficulty'].title(),
                        icon="🎯"
                    )
                
                with cols[1]:
                    DashboardComponents.metric_card(
                        "Skill Coverage",
                        format_percentage(analysis['transition_analysis']['skill_coverage']),
                        f"{len(analysis['transition_analysis']['missing_core_skills'])} skills to learn",
                        icon="✅"
                    )
                
                with cols[2]:
                    DashboardComponents.metric_card(
                        "Salary Increase",
                        format_currency(analysis['transition_analysis']['salary_increase']),
                        f"{analysis['transition_analysis']['salary_increase_percentage']:.1f}% increase",
                        icon="💰"
                    )
                
                with cols[3]:
                    DashboardComponents.metric_card(
                        "Time Required",
                        f"{analysis['learning_requirements']['estimated_months']} months",
                        f"At {st.session_state.get('hours_per_week', 10)} hours/week",
                        icon="⏱️"
                    )
                
                # Detailed analysis
                st.subheader("Detailed Analysis")
                
                tab1, tab2, tab3 = st.tabs(["📋 Missing Skills", "🗺️ Learning Path", "📈 Market Outlook"])
                
                with tab1:
                    st.markdown("#### Skills You Need to Learn:")
                    for skill in analysis['transition_analysis']['missing_core_skills'][:10]:
                        DashboardComponents.skill_card(skill, level="intermediate", demand="high")
                
                with tab2:
                    # Generate learning path
                    roadmap = transition_simulator.generate_transition_roadmap(
                        current_role, target_role, current_skills, timeline_months
                    )
                    
                    if 'roadmap' in roadmap:
                        st.markdown("#### Learning Roadmap")
                        
                        for phase_name, phase_data in roadmap['roadmap'].items():
                            with st.expander(f"{phase_name.replace('_', ' ').title()} - {phase_data['duration']}"):
                                st.markdown(f"**Focus:** {phase_data['focus']}")
                                st.markdown("**Key Skills:**")
                                for skill in phase_data['skills']:
                                    st.markdown(f"- {skill}")
                                
                                st.markdown("**Milestones:**")
                                for milestone in phase_data['milestones']:
                                    st.markdown(f"✓ {milestone}")
                
                with tab3:
                    st.markdown("#### Market Outlook for Target Role:")
                    
                    market_outlook = {
                        "Demand": analysis['market_opportunity']['target_role_demand'],
                        "Growth Trend": analysis['market_opportunity']['growth_trend'],
                        "Competition": "Medium",  # Simulated
                        "Remote Opportunities": "High"  # Simulated
                    }
                    
                    for metric, value in market_outlook.items():
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.markdown(f"**{metric}:**")
                        with col2:
                            st.markdown(value)
                
                # Recommendations
                st.subheader("🎯 Recommendations")
                
                recommendations = [
                    f"Focus on learning {analysis['transition_analysis']['missing_core_skills'][0]} first",
                    "Build a portfolio project using your target skills",
                    "Network with professionals in your target role",
                    "Consider taking relevant certifications",
                    "Update your LinkedIn profile with new skills"
                ]
                
                for i, recommendation in enumerate(recommendations, 1):
                    st.markdown(f"{i}. {recommendation}")
            
            else:
                st.error(f"Error: {analysis['error']}")

def show_roi_calculator_page(market_data: pd.DataFrame, roi_calculator):
    """Show ROI calculator page"""
    st.header("💰 ROI Calculator")
    
    st.markdown("""
    Calculate the Return on Investment (ROI) for learning new skills.
    This helps you prioritize which skills to learn based on market value.
    """)
    
    # Input section
    col1, col2 = st.columns(2)
    
    with col1:
        skills_to_evaluate = st.multiselect(
            "Skills to Evaluate",
            ["Python", "AWS", "Docker", "Machine Learning", "Kubernetes",
             "TensorFlow", "Spark", "Airflow", "FastAPI", "React"],
            default=["Python", "AWS", "Machine Learning"]
        )
        
        hours_per_week = st.slider("Learning Hours/Week", 5, 40, 10)
    
    with col2:
        current_role = st.selectbox(
            "Your Current Role",
            ["Data Analyst", "Software Engineer", "Student", "Other"],
            key="roi_current_role"
        )
        
        target_role = st.selectbox(
            "Target Role (Optional)",
            ["", "Data Scientist", "ML Engineer", "Data Engineer", "DevOps Engineer"],
            key="roi_target_role"
        )
    
    if st.button("Calculate ROI for All Skills", type="primary"):
        if not skills_to_evaluate:
            st.warning("Please select at least one skill to evaluate")
        else:
            with st.spinner("Calculating ROI for each skill..."):
                # Get ROI comparison
                comparison_df = roi_calculator.compare_multiple_skills(
                    skills_to_evaluate, hours_per_week
                )
                
                if not comparison_df.empty:
                    # Display comparison table
                    st.subheader("ROI Comparison")
                    DashboardComponents.create_comparison_table(comparison_df)
                    
                    # Visualizations
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # ROI Score Chart
                        fig = go.Figure(data=[
                            go.Bar(
                                x=comparison_df['skill'],
                                y=comparison_df['roi_score'],
                                marker_color='#2563EB'
                            )
                        ])
                        
                        fig.update_layout(
                            title="ROI Score by Skill",
                            xaxis_title="Skill",
                            yaxis_title="ROI Score",
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Salary Increase Chart
                        fig = go.Figure(data=[
                            go.Bar(
                                x=comparison_df['skill'],
                                y=comparison_df['salary_increase'],
                                marker_color='#10B981'
                            )
                        ])
                        
                        fig.update_layout(
                            title="Estimated Salary Increase",
                            xaxis_title="Skill",
                            yaxis_title="Annual Salary Increase ($)",
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Recommendations
                    st.subheader("🎯 Skill Investment Strategy")
                    
                    # Sort by ROI score
                    top_skills = comparison_df.nlargest(3, 'roi_score')
                    
                    st.markdown("### Top 3 Skills by ROI:")
                    
                    for idx, row in top_skills.iterrows():
                        col1, col2, col3 = st.columns([1, 2, 1])
                        
                        with col1:
                            st.markdown(f"**#{idx + 1}**")
                        
                        with col2:
                            st.markdown(f"**{row['skill']}**")
                            st.markdown(f"*{row['recommendation']}*")
                        
                        with col3:
                            st.metric("ROI Score", f"{row['roi_score']}/100")
                    
                    # Learning plan
                    if target_role:
                        st.subheader("📚 Optimized Learning Plan")
                        
                        learning_plan = roi_calculator.generate_learning_plan(
                            [],  # Empty list for current skills (simplified)
                            skills_to_evaluate,
                            hours_per_week,
                            timeline_weeks=26  # 6 months
                        )
                        
                        if 'learning_plan' in learning_plan:
                            plan_df = pd.DataFrame(learning_plan['learning_plan'])
                            
                            st.markdown("#### Suggested Learning Order:")
                            for i, item in enumerate(learning_plan['learning_plan'], 1):
                                st.markdown(f"""
                                **{i}. {item['skill']}**
                                - Priority: {item['priority']}
                                - Estimated: {item['estimated_weeks']:.1f} weeks
                                - Salary Impact: +{format_currency(item['salary_impact'])}
                                - ROI Score: {item['roi_score']}/100
                                """)
                            
                            # Plan metrics
                            metrics = learning_plan['metrics']
                            
                            cols = st.columns(3)
                            with cols[0]:
                                st.metric("Total Timeline", f"{metrics['total_weeks']:.1f} weeks")
                            with cols[1]:
                                st.metric("Salary Impact", format_currency(metrics['estimated_salary_impact']))
                            with cols[2]:
                                st.metric("Efficiency Score", f"{metrics['plan_efficiency_score']:.1f}/100")
                else:
                    st.warning("Could not calculate ROI for selected skills")

def show_forecasting_page(market_engine):
    """Show forecasting page"""
    st.header("🔮 Market Forecasting")
    
    st.markdown("""
    Predict which skills and technologies will be in demand in the future.
    This helps you future-proof your career by learning emerging technologies early.
    """)
    
    # Time horizon selection
    forecast_horizon = st.select_slider(
        "Forecast Horizon",
        options=["3 months", "6 months", "1 year", "2 years"],
        value="6 months"
    )
    
    # Get emerging tech analysis
    emerging_tech = market_engine._detect_emerging_tech()
    
    if emerging_tech:
        st.subheader("🚀 Emerging Technologies")
        
        for tech in emerging_tech:
            with st.expander(f"{tech['technology']} - Growth: {tech['growth_rate']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Description:** {tech['description']}")
                    st.markdown(f"**Adoption Score:** {tech['adoption_score']}/100")
                    
                    # Related skills
                    st.markdown("**Related Skills:**")
                    for skill in tech['related_skills']:
                        st.markdown(f"- {skill}")
                
                with col2:
                    # Growth indicator
                    growth_score = tech['adoption_score']
                    fig = DashboardComponents.create_gauge_chart(growth_score, "Adoption")
                    st.plotly_chart(fig, use_container_width=True)
        
        # Skill growth predictions
        st.subheader("📈 Skill Growth Predictions")
        
        # Simulated growth data
        growth_data = {
            "Skill": ["LangChain", "Ray", "Kubernetes", "FastAPI", "MLOps"],
            "Current Demand": [25, 35, 70, 45, 55],
            f"Demand in {forecast_horizon}": [65, 60, 85, 70, 80],
            "Growth": ["+160%", "+71%", "+21%", "+56%", "+45%"]
        }
        
        growth_df = pd.DataFrame(growth_data)
        
        # Create growth chart
        fig = go.Figure(data=[
            go.Bar(name='Current', x=growth_df['Skill'], y=growth_df['Current Demand']),
            go.Bar(name=f'Future ({forecast_horizon})', x=growth_df['Skill'], y=growth_df[f'Demand in {forecast_horizon}'])
        ])
        
        fig.update_layout(
            title=f"Skill Demand Growth Projection",
            barmode='group',
            xaxis_title="Skill",
            yaxis_title="Demand Score",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        st.subheader("🎯 Future-Proofing Recommendations")
        
        recommendations = [
            "Focus on skills with high growth rates (like LangChain)",
            "Learn complementary skills together (e.g., Docker + Kubernetes)",
            "Build projects using emerging technologies",
            "Follow thought leaders in emerging tech fields",
            "Contribute to open-source projects in growing areas"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
    
    else:
        st.info("Forecasting data will be available after more data collection")