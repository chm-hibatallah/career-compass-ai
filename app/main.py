"""
Career Compass - Streamlit Dashboard
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from features.skill_extractor import SkillExtractor
from data.collector import JobDataCollector

# Page configuration
st.set_page_config(
    page_title="Career Compass AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2563eb;
        text-align: center;
        margin-bottom: 2rem;
    }
    .skill-card {
        background-color: #f8fafc;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #2563eb;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🧭 Career Compass AI</h1>', unsafe_allow_html=True)
st.markdown("### AI-powered skill gap analysis with market forecasting")

# Initialize session state
if 'jobs_data' not in st.session_state:
    st.session_state.jobs_data = None
if 'skill_freq' not in st.session_state:
    st.session_state.skill_freq = None

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/compass--v1.png", width=100)
    st.title("Navigation")
    
    menu = st.selectbox(
        "Choose Analysis",
        ["📊 Market Overview", "🔍 Skill Analysis", "🎯 Personal Gap Analysis", "🔮 Forecasting"]
    )
    
    st.divider()
    
    st.subheader("Data Controls")
    if st.button("🔄 Refresh Job Data", type="secondary"):
        with st.spinner("Collecting latest job data..."):
            collector = JobDataCollector()
            jobs_df = collector.collect_all_jobs()
            extractor = SkillExtractor()
            jobs_with_skills, skill_freq = extractor.extract_skills_from_dataframe(jobs_df)
            
            st.session_state.jobs_data = jobs_with_skills
            st.session_state.skill_freq = skill_freq
            st.success(f"Loaded {len(jobs_with_skills)} jobs with {len(skill_freq)} unique skills!")
    
    st.divider()
    
    # Sample user profile
    st.subheader("Your Profile")
    user_skills = st.multiselect(
        "Your Current Skills",
        ["Python", "SQL", "Machine Learning", "AWS", "Docker", "Spark", "Tableau", "R", "Java", "JavaScript"],
        default=["Python", "SQL"]
    )
    
    target_role = st.selectbox(
        "Target Role",
        ["Data Scientist", "Machine Learning Engineer", "Data Engineer", "Backend Developer", "MLOps Engineer"]
    )

# Main content based on menu selection
if menu == "📊 Market Overview":
    st.header("Job Market Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 Total Jobs</h3>
            <h2>1,234</h2>
            <p>+12% from last month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>💼 Top Companies</h3>
            <h2>45</h2>
            <p>actively hiring</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🚀 Emerging Skills</h3>
            <h2>8</h2>
            <p>new technologies detected</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Top skills visualization
    st.subheader("Top In-Demand Skills")
    
    if st.session_state.skill_freq:
        top_skills = dict(st.session_state.skill_freq.most_common(10))
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(top_skills.keys()),
                y=list(top_skills.values()),
                marker_color='rgb(37, 99, 235)',
                text=list(top_skills.values()),
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            xaxis_title="Skill",
            yaxis_title="Number of Job Postings",
            template="plotly_white",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Click 'Refresh Job Data' to load current market data")

elif menu == "🔍 Skill Analysis":
    st.header("Skill Analysis & Trends")
    
    tab1, tab2, tab3 = st.tabs(["📊 By Role", "🏢 By Company", "📈 Trends"])
    
    with tab1:
        st.subheader("Skills by Role")
        
        # Sample role-skills matrix
        role_skills = {
            "Data Scientist": ["Python", "SQL", "Machine Learning", "Statistics", "A/B Testing"],
            "ML Engineer": ["Python", "Docker", "AWS", "MLOps", "TensorFlow"],
            "Data Engineer": ["SQL", "Python", "Spark", "AWS", "Airflow"],
            "Backend Dev": ["Python", "FastAPI", "Docker", "PostgreSQL", "AWS"]
        }
        
        # Create heatmap data
        all_skills = list({skill for skills in role_skills.values() for skill in skills})
        heatmap_data = []
        
        for role, skills in role_skills.items():
            row = [1 if skill in skills else 0 for skill in all_skills]
            heatmap_data.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=all_skills,
            y=list(role_skills.keys()),
            colorscale='Blues',
            showscale=False
        ))
        
        fig.update_layout(
            title="Skill Requirements by Role",
            xaxis_title="Skills",
            yaxis_title="Roles",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Company Tech Stacks")
        
        # Sample company analysis
        companies = ["Netflix", "Spotify", "Airbnb", "Uber", "Stripe"]
        tech_stacks = {
            "Netflix": ["Java", "AWS", "Spark", "Python", "React"],
            "Spotify": ["Python", "Java", "AWS", "Kafka", "TensorFlow"],
            "Airbnb": ["Ruby", "React", "AWS", "Airflow", "Python"],
            "Uber": ["Go", "Python", "Java", "Kafka", "MySQL"],
            "Stripe": ["Ruby", "Go", "React", "AWS", "Kafka"]
        }
        
        # Create radar chart
        categories = list({tech for stack in tech_stacks.values() for tech in stack})[:8]
        
        fig = go.Figure()
        
        for company, stack in tech_stacks.items():
            values = [1 if tech in stack else 0 for tech in categories]
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=company
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            title="Company Tech Stack Comparison",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)

elif menu == "🎯 Personal Gap Analysis":
    st.header("Personal Skill Gap Analysis")
    
    if user_skills and target_role:
        # Sample role requirements
        role_requirements = {
            "Data Scientist": ["Python", "SQL", "Machine Learning", "Statistics", "A/B Testing", "Communication"],
            "Machine Learning Engineer": ["Python", "Docker", "AWS", "MLOps", "TensorFlow", "CI/CD"],
            "Data Engineer": ["SQL", "Python", "Spark", "AWS", "Airflow", "Kafka"],
            "Backend Developer": ["Python", "FastAPI", "Docker", "PostgreSQL", "AWS", "Testing"],
            "MLOps Engineer": ["Docker", "Kubernetes", "AWS", "MLOps", "CI/CD", "Monitoring"]
        }
        
        required = role_requirements.get(target_role, [])
        current = user_skills
        
        # Calculate gaps
        gaps = [skill for skill in required if skill not in current]
        strengths = [skill for skill in current if skill in required]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Your Strengths")
            for skill in strengths:
                st.markdown(f"""
                <div class="skill-card">
                    <b>{skill}</b> - Already mastered!
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("📚 Skills to Learn")
            for skill in gaps:
                st.markdown(f"""
                <div class="skill-card">
                    <b>{skill}</b> - Required for {target_role}
                    <br><small>⏱️ Estimated: 40 hours to proficiency</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Gap visualization
        fig = go.Figure(data=[
            go.Bar(name='Required', x=required, y=[1]*len(required)),
            go.Bar(name='You Have', x=current, y=[0.7]*len(current))
        ])
        
        fig.update_layout(
            title=f"Skill Gap for {target_role}",
            barmode='overlay',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ROI Calculator
        st.subheader("💰 Learning ROI Calculator")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            skill_to_learn = st.selectbox("Select skill to evaluate", gaps)
        
        with col2:
            hours_per_week = st.slider("Hours per week", 5, 40, 10)
        
        with col3:
            current_salary = st.number_input("Current Salary ($)", 60000, 200000, 80000)
        
        if st.button("Calculate ROI"):
            # Simplified ROI calculation
            salary_boost = 15000  # Simplified
            learning_time = 40  # hours
            weeks_to_learn = learning_time / hours_per_week
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Weeks to Learn", f"{weeks_to_learn:.1f}")
            
            with col2:
                st.metric("Salary Boost", f"${salary_boost:,.0f}")
            
            with col3:
                roi = (salary_boost * 5) / (weeks_to_learn * 100)  # Simplified
                st.metric("ROI Score", f"{roi:.1f}x")

elif menu == "🔮 Forecasting":
    st.header("Skill Forecasting & Trends")
    
    st.info("""
    **Coming Soon:** Predictive analytics showing which skills will be in demand 
    in the next 6-12 months based on current trends and adoption rates.
    """)
    
    # Sample forecasting visualization
    skills_forecast = {
        "Skill": ["Python", "TensorFlow", "Docker", "Kubernetes", "FastAPI", "LangChain"],
        "Current Demand": [95, 70, 85, 60, 40, 20],
        "6 Month Forecast": [96, 65, 88, 70, 55, 45],
        "Growth": ["+1%", "-5%", "+3%", "+10%", "+15%", "+25%"]
    }
    
    df_forecast = pd.DataFrame(skills_forecast)
    
    fig = go.Figure(data=[
        go.Bar(name='Current', x=df_forecast['Skill'], y=df_forecast['Current Demand']),
        go.Bar(name='6 Month Forecast', x=df_forecast['Skill'], y=df_forecast['6 Month Forecast'])
    ])
    
    fig.update_layout(
        title="Skill Demand Forecast (Next 6 Months)",
        barmode='group',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Emerging technologies
    st.subheader("🚀 Emerging Technologies to Watch")
    
    emerging = [
        {"name": "LangChain", "description": "LLM application framework", "growth": "+300%"},
        {"name": "Ray", "description": "Distributed computing for ML", "growth": "+150%"},
        {"name": "Feast", "description": "Feature store for ML", "growth": "+120%"},
        {"name": "Weights & Biases", "description": "ML experiment tracking", "growth": "+90%"},
    ]
    
    for tech in emerging:
        with st.expander(f"{tech['name']} - Growth: {tech['growth']}"):
            st.write(tech['description'])
            st.progress(0.7 if "LangChain" in tech['name'] else 0.5)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>🧭 Career Compass AI • Data-driven career planning • Built with ❤️ by [Your Name]</p>
    <p>Note: This is a prototype. Real-time data and advanced forecasting coming soon!</p>
</div>
""", unsafe_allow_html=True)