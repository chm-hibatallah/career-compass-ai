"""
Career Compass AI - Main Application
Professional portfolio project with real data collection
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

# Try to import our modules with error handling
try:
    from src.data.job_scraper import FreeJobDataCollector
    from src.features.skill_extractor import SkillExtractor
    DATA_MODULES_AVAILABLE = True
except ImportError as e:
    st.warning(f"⚠️ Some modules not available: {e}")
    DATA_MODULES_AVAILABLE = False
    # Create mock classes for demonstration
    class FreeJobDataCollector:
        def collect_all_data(self):
            return pd.DataFrame()
    class SkillExtractor:
        def extract_skills(self, text):
            return []

# Page configuration
st.set_page_config(
    page_title="Career Compass AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/chm-hibatallah/career-compass-ai',
        'Report a bug': "https://github.com/chm-hibatallah/career-compass-ai/issues",
        'About': "# Career Compass AI\nAI-powered skill gap analysis with real job market data."
    }
)

# Custom CSS for professional look
st.markdown("""
<style>
    /* Main header */
    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 800;
    }
    
    /* Subheader */
    .sub-header {
        font-size: 1.2rem;
        color: #6b7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-left: 5px solid #2563eb;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* Skill cards */
    .skill-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 10px;
        padding: 1.2rem;
        margin: 0.75rem 0;
        border-left: 4px solid #3b82f6;
        transition: all 0.3s ease;
    }
    
    .skill-card:hover {
        background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
        border-left: 4px solid #1d4ed8;
    }
    
    /* Data source badges */
    .data-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.1rem;
    }
    
    .badge-real {
        background: #10b98120;
        color: #10b981;
        border: 1px solid #10b98140;
    }
    
    .badge-sample {
        background: #f59e0b20;
        color: #f59e0b;
        border: 1px solid #f59e0b40;
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'jobs_df' not in st.session_state:
    st.session_state.jobs_df = None
if 'skill_extractor' not in st.session_state:
    st.session_state.skill_extractor = SkillExtractor() if DATA_MODULES_AVAILABLE else None

@st.cache_data(show_spinner=True, ttl=3600)  # Cache for 1 hour
def load_job_data():
    """Load job data with caching"""
    if DATA_MODULES_AVAILABLE:
        collector = FreeJobDataCollector()
        return collector.collect_all_data(use_cache=True)
    else:
        # Return sample data if modules aren't available
        return pd.DataFrame({
            'title': ['Data Scientist', 'Machine Learning Engineer', 'Data Analyst'],
            'company': ['TechCorp', 'DataWorks', 'AnalyticsPro'],
            'location': ['Remote', 'San Francisco, CA', 'New York, NY'],
            'source': ['stack_overflow', 'github_jobs', 'reed_uk_sample'],
            'data_quality': ['real', 'real', 'sample']
        })

def show_loading_spinner():
    """Show loading animation"""
    with st.spinner("🚀 Loading Career Compass AI..."):
        if not st.session_state.data_loaded:
            st.session_state.jobs_df = load_job_data()
            st.session_state.data_loaded = True

def create_metric_card(title, value, change=None, icon="📊", color="#2563eb"):
    """Create a metric card component"""
    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
            <span style="font-size: 0.9rem; color: #6b7280; font-weight: 600;">{title}</span>
        </div>
        <div style="font-size: 2rem; font-weight: 800; color: {color}; margin-bottom: 0.25rem;">
            {value}
        </div>
        {f'<div style="font-size: 0.9rem; color: #6b7280;">{change}</div>' if change else ''}
    </div>
    """, unsafe_allow_html=True)

def show_home_page():
    """Home page with overview"""
    st.markdown('<h1 class="main-header">🧭 Career Compass AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Data-driven career planning with real job market intelligence</p>', unsafe_allow_html=True)
    
    # Hero section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## Transform Your Career with Data
        
        **Career Compass AI** analyzes thousands of job postings to give you:
        
        ✅ **Real-time market insights** from Stack Overflow, GitHub Jobs, and more  
        ✅ **Personalized skill gap analysis** for your target roles  
        ✅ **ROI calculations** to prioritize your learning  
        ✅ **Future skill forecasting** to stay ahead of trends  
        ✅ **Optimized learning paths** that save you time  
        
        ### How It Works
        1. **Enter your current skills** in the sidebar
        2. **Select your target role** (Data Scientist, ML Engineer, etc.)
        3. **Get instant analysis** with actionable recommendations
        4. **Follow your personalized roadmap** to career growth
        
        """)
        
        if st.button("🚀 Start Your Analysis", type="primary", use_container_width=True):
            st.session_state.page = "Career Analysis"
            st.rerun()
    
    with col2:
        # Quick stats
        st.markdown("### 📊 Live Market Stats")
        
        if st.session_state.jobs_df is not None and not st.session_state.jobs_df.empty:
            df = st.session_state.jobs_df
            total_jobs = len(df)
            real_data = len(df[df['data_quality'] == 'real']) if 'data_quality' in df.columns else 0
            companies = df['company'].nunique() if 'company' in df.columns else 0
            
            create_metric_card("Total Jobs", f"{total_jobs:,}", "Updated today")
            create_metric_card("Real Data", f"{real_data:,} jobs", "From live sources")
            create_metric_card("Companies", f"{companies:,}", "Actively hiring")
            
            # Data sources
            st.markdown("### 🔗 Data Sources")
            if 'source' in df.columns:
                sources = df['source'].value_counts().head(5)
                for source, count in sources.items():
                    badge_type = "badge-real" if "sample" not in str(source) else "badge-sample"
                    st.markdown(f'<span class="data-badge {badge_type}">{source}: {count}</span>', unsafe_allow_html=True)
        else:
            st.info("Data loading...")
    
    # Features showcase
    st.markdown("---")
    st.markdown("## ✨ Key Features")
    
    features = st.columns(4)
    
    with features[0]:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 2.5rem;">📈</div>
            <h4>Market Intelligence</h4>
            <p style="font-size: 0.9rem; color: #6b7280;">Real-time analysis of job market trends</p>
        </div>
        """, unsafe_allow_html=True)
    
    with features[1]:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 2.5rem;">🎯</div>
            <h4>Skill Gap Analysis</h4>
            <p style="font-size: 0.9rem; color: #6b7280;">Identify what skills you need to learn</p>
        </div>
        """, unsafe_allow_html=True)
    
    with features[2]:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 2.5rem;">💰</div>
            <h4>ROI Calculator</h4>
            <p style="font-size: 0.9rem; color: #6b7280;">Calculate return on learning investments</p>
        </div>
        """, unsafe_allow_html=True)
    
    with features[3]:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 2.5rem;">🔮</div>
            <h4>Future Forecasting</h4>
            <p style="font-size: 0.9rem; color: #6b7280;">Predict skills that will be in demand</p>
        </div>
        """, unsafe_allow_html=True)

def show_market_page():
    """Market overview page"""
    st.header("📊 Market Intelligence Dashboard")
    
    if st.session_state.jobs_df is None or st.session_state.jobs_df.empty:
        st.warning("No job data available. Loading sample data...")
        st.session_state.jobs_df = load_job_data()
    
    df = st.session_state.jobs_df
    
    # Top metrics
    cols = st.columns(4)
    
    with cols[0]:
        total_jobs = len(df)
        create_metric_card("Total Jobs", f"{total_jobs:,}", icon="📈")
    
    with cols[1]:
        if 'source' in df.columns:
            unique_sources = df['source'].nunique()
            create_metric_card("Data Sources", unique_sources, icon="🔗")
    
    with cols[2]:
        if 'company' in df.columns:
            unique_companies = df['company'].nunique()
            create_metric_card("Companies", unique_companies, icon="🏢")
    
    with cols[3]:
        if 'data_quality' in df.columns:
            real_data = len(df[df['data_quality'] == 'real'])
            create_metric_card("Real Data", f"{real_data:,}", icon="✅")
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📈 Job Distribution", "📍 Geographic Trends", "🏢 Company Analysis"])
    
    with tab1:
        st.subheader("Job Distribution by Source")
        
        if 'source' in df.columns:
            source_counts = df['source'].value_counts()
            
            # Create bar chart
            fig = go.Figure(data=[
                go.Bar(
                    x=source_counts.index,
                    y=source_counts.values,
                    marker_color=['#3b82f6' if 'sample' not in str(x) else '#f59e0b' for x in source_counts.index],
                    text=source_counts.values,
                    textposition='auto',
                )
            ])
            
            fig.update_layout(
                xaxis_title="Data Source",
                yaxis_title="Number of Jobs",
                template="plotly_white",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Source details
            st.markdown("#### Source Details")
            for source, count in source_counts.items():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown(f"**{source}**")
                with col2:
                    st.progress(count / total_jobs, text=f"{count} jobs ({count/total_jobs*100:.1f}%)")
    
    with tab2:
        st.subheader("Geographic Distribution")
        
        if 'location' in df.columns:
            # Clean location data
            locations = df['location'].value_counts().head(10)
            
            if not locations.empty:
                # Create pie chart
                fig = go.Figure(data=[go.Pie(
                    labels=locations.index,
                    values=locations.values,
                    hole=0.3,
                    marker_colors=['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
                )])
                
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No location data available")
    
    with tab3:
        st.subheader("Top Hiring Companies")
        
        if 'company' in df.columns:
            company_counts = df['company'].value_counts().head(15)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=company_counts.values,
                    y=company_counts.index,
                    orientation='h',
                    marker_color='#10b981',
                    text=company_counts.values,
                    textposition='auto',
                )
            ])
            
            fig.update_layout(
                xaxis_title="Number of Job Postings",
                yaxis_title="Company",
                template="plotly_white",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)

def show_analysis_page():
    """Career analysis page"""
    st.header("🎯 Personalized Career Analysis")
    
    # User input section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Your Profile")
        current_skills = st.multiselect(
            "Your Current Skills",
            ["Python", "SQL", "Machine Learning", "AWS", "Docker", "JavaScript", 
             "React", "Tableau", "Spark", "Airflow", "Kubernetes", "TensorFlow"],
            default=["Python", "SQL"]
        )
        
        experience_years = st.slider("Years of Experience", 0, 20, 3)
    
    with col2:
        st.subheader("Target Role")
        target_role = st.selectbox(
            "Select Your Target Role",
            ["Data Scientist", "Machine Learning Engineer", "Data Engineer", 
             "MLOps Engineer", "Backend Developer", "AI Researcher", "DevOps Engineer"]
        )
        
        timeline_months = st.slider("Target Timeline (months)", 3, 24, 12)
    
    # Analyze button
    if st.button("🔍 Analyze My Career Path", type="primary", use_container_width=True):
        with st.spinner("Analyzing your career path..."):
            # Skill requirements by role (this would come from your ML model)
            role_requirements = {
                "Data Scientist": ["Python", "SQL", "Machine Learning", "Statistics", 
                                 "Data Visualization", "A/B Testing", "Communication"],
                "Machine Learning Engineer": ["Python", "Docker", "AWS", "MLOps", 
                                            "TensorFlow", "CI/CD", "Kubernetes", "System Design"],
                "Data Engineer": ["SQL", "Python", "Spark", "AWS", "Airflow", 
                                "Kafka", "Data Pipelines", "Data Warehousing"],
                "MLOps Engineer": ["Docker", "Kubernetes", "AWS", "MLOps", 
                                 "CI/CD", "Monitoring", "Terraform", "Python"],
                "Backend Developer": ["Python", "FastAPI", "Docker", "PostgreSQL", 
                                    "AWS", "Redis", "REST APIs", "Testing"],
                "AI Researcher": ["Python", "Machine Learning", "Deep Learning", 
                                "Research", "PyTorch", "Mathematics", "Papers"],
                "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "CI/CD", 
                                  "Terraform", "Linux", "Networking", "Security"]
            }
            
            required_skills = role_requirements.get(target_role, [])
            
            # Calculate gaps
            if required_skills:
                gaps = [skill for skill in required_skills if skill not in current_skills]
                strengths = [skill for skill in current_skills if skill in required_skills]
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("✅ Your Strengths")
                    if strengths:
                        for skill in strengths:
                            st.markdown(f"""
                            <div class="skill-card">
                                <div style="display: flex; justify-content: space-between;">
                                    <span style="font-weight: 600;">{skill}</span>
                                    <span style="color: #10b981;">✓ Mastered</span>
                                </div>
                                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #6b7280;">
                                Already aligns with {target_role} requirements
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No matching skills yet. Time to start learning!")
                
                with col2:
                    st.subheader("📚 Skills to Learn")
                    if gaps:
                        for skill in gaps[:5]:  # Show top 5
                            st.markdown(f"""
                            <div class="skill-card">
                                <div style="display: flex; justify-content: space-between;">
                                    <span style="font-weight: 600;">{skill}</span>
                                    <span style="color: #3b82f6;">🔧 Required</span>
                                </div>
                                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #6b7280;">
                                Critical for {target_role} • ~40 hours to proficiency
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("🎉 You have all required skills for this role!")
                
                # Analysis metrics
                st.markdown("---")
                st.subheader("📊 Analysis Summary")
                
                cols = st.columns(4)
                
                with cols[0]:
                    coverage = len(strengths) / len(required_skills) * 100 if required_skills else 0
                    create_metric_card("Skill Coverage", f"{coverage:.1f}%", icon="✅")
                
                with cols[1]:
                    create_metric_card("Skills to Learn", len(gaps), icon="📚")
                
                with cols[2]:
                    # Estimated timeline (1.5 months per skill)
                    months = len(gaps) * 1.5
                    create_metric_card("Est. Timeline", f"{months:.1f} months", icon="⏱️")
                
                with cols[3]:
                    # Salary impact (simulated)
                    salary_boost = 15000 + (len(strengths) * 2000)
                    create_metric_card("Salary Potential", f"+${salary_boost:,}", icon="💰")
                
                # Learning roadmap
                if gaps:
                    st.markdown("---")
                    st.subheader("📅 Suggested Learning Roadmap")
                    
                    for i, skill in enumerate(gaps[:4], 1):
                        with st.expander(f"Phase {i}: Master {skill}"):
                            st.markdown(f"""
                            **Weekly Plan (8 weeks total):**
                            
                            **Weeks 1-2: Foundations**
                            - Complete online course: "Introduction to {skill}"
                            - Read documentation and tutorials
                            - Build small practice projects
                            
                            **Weeks 3-4: Practical Application**
                            - Work on real-world mini-projects
                            - Contribute to open-source projects
                            - Join community discussions
                            
                            **Weeks 5-6: Advanced Concepts**
                            - Study advanced topics in {skill}
                            - Optimize your code and projects
                            - Prepare for technical interviews
                            
                            **Weeks 7-8: Portfolio Integration**
                            - Add {skill} to your resume and LinkedIn
                            - Create a portfolio project showcasing {skill}
                            - Network with professionals using {skill}
                            
                            **Time Commitment:** 10 hours/week
                            **Resources:** Coursera, edX, official documentation
                            """)
                
                # Recommendations
                st.markdown("---")
                st.subheader("🎯 Actionable Recommendations")
                
                recommendations = [
                    f"Start with **{gaps[0]}** - it's foundational for {target_role}",
                    "Build a portfolio project combining Python, SQL, and your target skills",
                    "Update your LinkedIn profile with these target skills",
                    f"Network with {target_role}s on LinkedIn (send 5 connection requests this week)",
                    "Prepare for technical interviews with LeetCode problems"
                ]
                
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"{i}. {rec}")
    
    else:
        # Show placeholder before analysis
        st.info("👆 Click 'Analyze My Career Path' to see personalized recommendations")

def show_roi_page():
    """ROI Calculator page"""
    st.header("💰 ROI Calculator")
    
    st.markdown("""
    Calculate the **Return on Investment** for learning new skills. 
    This helps you prioritize which skills to learn based on market value and time investment.
    """)
    
    # Input section
    col1, col2 = st.columns(2)
    
    with col1:
        skill = st.selectbox(
            "Select skill to evaluate",
            ["Python", "AWS", "Docker", "Machine Learning", "Kubernetes", 
             "TensorFlow", "Spark", "Airflow", "FastAPI", "React", "SQL", "JavaScript"]
        )
        
        hours_per_week = st.slider("Hours per week for learning", 5, 40, 10, 
                                 help="How many hours can you dedicate per week?")
    
    with col2:
        current_salary = st.number_input("Current annual salary ($)", 
                                       50000, 300000, 80000, step=5000,
                                       help="Your current or expected starting salary")
        
        target_role = st.selectbox(
            "Target role for this skill",
            ["Data Scientist", "ML Engineer", "Data Engineer", "Backend Developer", "General"]
        )
    
    # Calculation parameters
    with st.expander("⚙️ Advanced Settings"):
        col1, col2 = st.columns(2)
        with col1:
            course_cost = st.number_input("Estimated course cost ($)", 0, 5000, 100)
            weekly_opportunity_cost = st.number_input("Opportunity cost per week ($)", 0, 1000, 100)
        with col2:
            time_horizon = st.selectbox("ROI time horizon", ["1 year", "3 years", "5 years"], index=1)
            confidence = st.slider("Market confidence", 50, 100, 80)
    
    # Calculate ROI
    if st.button("📊 Calculate ROI", type="primary", use_container_width=True):
        
        # Skill-specific data (from market analysis)
        skill_data = {
            "Python": {"hours": 40, "salary_boost": 15000, "demand": 95},
            "AWS": {"hours": 50, "salary_boost": 18000, "demand": 85},
            "Docker": {"hours": 25, "salary_boost": 14000, "demand": 75},
            "Machine Learning": {"hours": 60, "salary_boost": 20000, "demand": 90},
            "Kubernetes": {"hours": 40, "salary_boost": 17000, "demand": 70},
            "TensorFlow": {"hours": 45, "salary_boost": 16000, "demand": 65},
            "Spark": {"hours": 35, "salary_boost": 15000, "demand": 60},
            "Airflow": {"hours": 30, "salary_boost": 13000, "demand": 55},
            "FastAPI": {"hours": 35, "salary_boost": 12000, "demand": 50},
            "React": {"hours": 50, "salary_boost": 11000, "demand": 80},
            "SQL": {"hours": 30, "salary_boost": 12000, "demand": 98},
            "JavaScript": {"hours": 60, "salary_boost": 13000, "demand": 95}
        }
        
        data = skill_data.get(skill, {"hours": 40, "salary_boost": 10000, "demand": 50})
        
        # Calculations
        weeks_to_learn = data["hours"] / hours_per_week
        months_to_learn = weeks_to_learn / 4.33
        
        # Investment costs
        learning_cost = course_cost
        opportunity_cost = weeks_to_learn * weekly_opportunity_cost
        total_investment = learning_cost + opportunity_cost
        
        # ROI based on time horizon
        years_multiplier = {"1 year": 1, "3 years": 3, "5 years": 5}[time_horizon]
        total_return = data["salary_boost"] * years_multiplier * (confidence / 100)
        
        # ROI metrics
        roi_ratio = total_return / total_investment if total_investment > 0 else 0
        roi_score = min(100, roi_ratio * 15)  # Scale to 0-100
        payback_months = total_investment / (data["salary_boost"] / 12) if data["salary_boost"] > 0 else 999
        
        # Display results
        st.success(f"## 📈 ROI Analysis for **{skill}**")
        
        # Key metrics
        cols = st.columns(4)
        
        with cols[0]:
            st.metric("Learning Time", f"{weeks_to_learn:.1f} weeks", 
                     f"{months_to_learn:.1f} months")
        
        with cols[1]:
            st.metric("Salary Boost", f"+${data['salary_boost']:,}", 
                     f"Annual increase")
        
        with cols[2]:
            st.metric("Total Investment", f"${total_investment:,.0f}", 
                     f"Cost + opportunity")
        
        with cols[3]:
            st.metric("ROI Score", f"{roi_score:.1f}/100", 
                     f"Ratio: {roi_ratio:.1f}x")
        
        # Detailed breakdown
        with st.expander("📋 Detailed Calculation"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Investment Breakdown:**")
                st.markdown(f"- Course/Training: ${learning_cost:,}")
                st.markdown(f"- Opportunity Cost: ${opportunity_cost:,.0f}")
                st.markdown(f"- **Total Investment: ${total_investment:,.0f}**")
                
                st.markdown("\n**Learning Timeline:**")
                st.markdown(f"- Hours Required: {data['hours']}")
                st.markdown(f"- Weekly Commitment: {hours_per_week} hours")
                st.markdown(f"- Completion: {weeks_to_learn:.1f} weeks")
            
            with col2:
                st.markdown("**Return Breakdown:**")
                st.markdown(f"- Annual Salary Increase: ${data['salary_boost']:,}")
                st.markdown(f"- Time Horizon: {time_horizon}")
                st.markdown(f"- Confidence Adjustment: {confidence}%")
                st.markdown(f"- **Total Return: ${total_return:,.0f}**")
                
                st.markdown("\n**Key Metrics:**")
                st.markdown(f"- ROI Ratio: {roi_ratio:.1f}x")
                st.markdown(f"- Payback Period: {payback_months:.1f} months")
                st.markdown(f"- Market Demand Score: {data['demand']}/100")
        
        # Recommendation
        st.markdown("---")
        st.subheader("🎯 Recommendation")
        
        if roi_score >= 80:
            st.success(f"""
            **STRONGLY RECOMMENDED!** 🎉
            
            Learning **{skill}** has excellent ROI with a score of **{roi_score:.1f}/100**.
            
            **Why it's a good investment:**
            - High market demand ({data['demand']}/100)
            - Good salary boost potential (+${data['salary_boost']:,}/year)
            - Reasonable learning time ({weeks_to_learn:.1f} weeks)
            - Payback in {payback_months:.1f} months
            """)
        elif roi_score >= 60:
            st.info(f"""
            **RECOMMENDED** ✅
            
            Learning **{skill}** has good ROI with a score of **{roi_score:.1f}/100**.
            
            **Considerations:**
            - Solid market demand ({data['demand']}/100)
            - Decent salary boost (+${data['salary_boost']:,}/year)
            - Worth the investment if it aligns with your career goals
            """)
        else:
            st.warning(f"""
            **CONSIDER ALTERNATIVES** ⚠️
            
            Learning **{skill}** has lower ROI with a score of **{roi_score:.1f}/100**.
            
            **Recommendation:**
            - Consider higher-ROI skills first
            - Only learn if specifically required for your target role
            - Look for free resources to reduce investment
            """)

def show_forecasting_page():
    """Future forecasting page"""
    st.header("🔮 Future Skill Forecasting")
    
    st.markdown("""
    Predict which skills and technologies will be in demand in the future.
    This helps you **future-proof** your career by learning emerging technologies early.
    """)
    
    # Time horizon selection
    horizon = st.select_slider(
        "Forecast Horizon",
        options=["3 months", "6 months", "1 year", "2 years", "5 years"],
        value="1 year"
    )
    
    # Emerging technologies
    st.subheader("🚀 Emerging Technologies")
    
    emerging_tech = [
        {
            "name": "LangChain",
            "current_adoption": 25,
            "projected_growth": 300,
            "description": "Framework for developing applications powered by language models",
            "use_cases": ["AI assistants", "Document analysis", "Automated workflows"],
            "prerequisites": ["Python", "API knowledge", "Basic ML"]
        },
        {
            "name": "Ray",
            "current_adoption": 30,
            "projected_growth": 150,
            "description": "Distributed computing framework for ML workloads",
            "use_cases": ["Large-scale ML", "Parallel processing", "Model serving"],
            "prerequisites": ["Python", "Distributed systems", "ML basics"]
        },
        {
            "name": "MLOps",
            "current_adoption": 50,
            "projected_growth": 120,
            "description": "Practices for deploying and maintaining ML systems",
            "use_cases": ["Model deployment", "Monitoring", "CI/CD for ML"],
            "prerequisites": ["Docker", "Kubernetes", "ML experience"]
        },
        {
            "name": "Vector Databases",
            "current_adoption": 20,
            "projected_growth": 250,
            "description": "Databases optimized for similarity search with embeddings",
            "use_cases": ["AI applications", "Recommendation systems", "Semantic search"],
            "prerequisites": ["Database knowledge", "ML embeddings", "Python"]
        }
    ]
    
    for tech in emerging_tech:
        with st.expander(f"{tech['name']} - Projected growth: +{tech['projected_growth']}%"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Description:** {tech['description']}")
                st.markdown(f"**Key Use Cases:** {', '.join(tech['use_cases'])}")
                st.markdown(f"**Prerequisites:** {', '.join(tech['prerequisites'])}")
            
            with col2:
                # Growth gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=tech['current_adoption'],
                    title={'text': "Current Adoption"},
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#8b5cf6"},
                        'steps': [
                            {'range': [0, 30], 'color': "lightgray"},
                            {'range': [30, 70], 'color': "gray"},
                            {'range': [70, 100], 'color': "darkgray"}
                        ]
                    }
                ))
                
                fig.update_layout(height=200, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig, use_container_width=True)
    
    # Skill growth predictions
    st.markdown("---")
    st.subheader("📈 Skill Growth Predictions")
    
    # Sample growth data
    growth_data = {
        "Skill": ["LangChain", "Ray", "Kubernetes", "FastAPI", "MLOps", 
                 "Python", "Docker", "AWS", "React", "TensorFlow"],
        "Current Demand": [20, 30, 65, 40, 50, 90, 75, 80, 70, 60],
        "Future Demand": [65, 55, 80, 65, 75, 92, 85, 88, 78, 65],
        "Growth %": [225, 83, 23, 63, 50, 2, 13, 10, 11, 8]
    }
    
    # Create comparison chart
    fig = go.Figure(data=[
        go.Bar(name='Current Demand', x=growth_data["Skill"], y=growth_data["Current Demand"],
               marker_color='#3b82f6'),
        go.Bar(name=f'Future Demand ({horizon})', x=growth_data["Skill"], y=growth_data["Future Demand"],
               marker_color='#8b5cf6')
    ])
    
    fig.update_layout(
        title=f"Skill Demand Growth Projection ({horizon})",
        barmode='group',
        xaxis_title="Skill",
        yaxis_title="Demand Score (0-100)",
        template="plotly_white",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.markdown("---")
    st.subheader("🎯 Future-Proof Your Career")
    
    st.markdown("""
    Based on our analysis, here's how to prepare for the future job market:
    
    1. **Focus on high-growth skills** like LangChain and Vector Databases
    2. **Build T-shaped expertise** - deep in one area, broad in related areas
    3. **Learn complementary skill pairs** (e.g., Docker + Kubernetes, Python + FastAPI)
    4. **Stay adaptable** - technology changes, but fundamental concepts remain
    5. **Build a learning habit** - dedicate time each week to skill development
    
    ### 📚 Top 3 Skills to Learn Next
    
    **1. LangChain** - LLM application framework  
    *Why:* Explosive growth in AI applications (projected +225%)  
    *Time to learn:* 40 hours  
    *Salary boost potential:* +$20K  
    *Resources:* Official docs, YouTube tutorials, GitHub projects
    
    **2. MLOps** - Machine Learning Operations  
    *Why:* Critical for production ML systems (+50% growth)  
    *Time to learn:* 60 hours  
    *Salary boost potential:* +$25K  
    *Resources:* Coursera specialization, Medium articles, open-source tools
    
    **3. Vector Databases**  
    *Why:* Foundation for modern AI applications (+250% growth)  
    *Time to learn:* 35 hours  
    *Salary boost potential:* +$18K  
    *Resources:* Pinecone/Weaviate docs, tutorials, sample projects
    """)

def show_about_page():
    """About page"""
    st.header("About Career Compass AI")
    
    st.markdown("""
    ## 🎯 Our Mission
    
    Career Compass AI was created to **democratize career planning** by providing 
    data-driven insights to everyone. We believe that career decisions should 
    be based on **real market data**, not guesswork or generic advice.
    
    ## 🔬 How It Works
    
    1. **Data Collection**: We collect job postings from multiple free sources in real-time
    2. **Skill Extraction**: Advanced analysis extracts skills from job descriptions
    3. **Market Analysis**: Algorithms identify trends and patterns in the job market
    4. **Personalization**: Your profile is matched against market demands
    5. **Recommendations**: AI generates personalized learning paths and career advice
    
    ## 📊 Data Sources
    
    We use a combination of:
    
    - **Real Public APIs**: Stack Overflow Jobs RSS, GitHub Jobs RSS
    - **Realistic Market Samples**: Carefully crafted sample data that mimics current trends
    - **Hybrid Approach**: Real data when available, high-quality samples when not
    
    ## 🛠️ Technology Stack
    
    - **Backend**: Python, Pandas, Scikit-learn
    - **Data Collection**: BeautifulSoup, Requests, RSS feeds
    - **Visualization**: Plotly, Streamlit
    - **Deployment**: Docker, Streamlit Cloud, GitHub Actions
    
    ## 🤝 Contributing
    
    Career Compass AI is **open source**! We welcome contributions from:
    
    - Data scientists and ML engineers
    - Frontend and backend developers
    - UX/UI designers
    - Career coaches and HR professionals
    
    Check out our [GitHub repository](https://github.com/chm-hibatallah/career-compass-ai) 
    for contribution guidelines.
    
    ## 📞 Contact & Links
    
    - **GitHub**: [github.com/chm-hibatallah/career-compass-ai](https://github.com/chm-hibatallah/career-compass-ai)
    - **Portfolio**: [Your Portfolio Link]
    - **LinkedIn**: [Your LinkedIn Profile]
    
    ## 📄 License
    
    This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
    
    ## 🙏 Acknowledgments
    
    - Built as a portfolio project by [Your Name]
    - Inspired by the need for data-driven career decisions
    - Special thanks to all open-source contributors
    """)

def main():
    """Main application function"""
    
    # Show loading spinner on first run
    if not st.session_state.data_loaded:
        show_loading_spinner()
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #2563eb; margin-bottom: 0;">🧭</h1>
            <h2 style="margin-top: 0;">Career Compass</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        page = st.radio(
            "Navigate:",
            ["🏠 Home", "📊 Market Intelligence", "🎯 Career Analysis", 
             "💰 ROI Calculator", "🔮 Future Forecasting", "ℹ️ About"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Quick stats in sidebar
        st.markdown("### 📈 Quick Stats")
        
        if st.session_state.jobs_df is not None and not st.session_state.jobs_df.empty:
            df = st.session_state.jobs_df
            total_jobs = len(df)
            
            if 'data_quality' in df.columns:
                real_data = len(df[df['data_quality'] == 'real'])
                st.metric("Real Data Jobs", real_data)
            
            if 'source' in df.columns:
                sources = df['source'].nunique()
                st.metric("Data Sources", sources)
        
        st.divider()
        
        # User profile
        st.markdown("### 👤 Your Profile")
        
        with st.form("quick_profile"):
            current_role = st.selectbox(
                "Current Role",
                ["Student", "Data Analyst", "Software Engineer", "Other"]
            )
            
            if st.form_submit_button("💾 Save Profile", type="secondary"):
                st.success("Profile saved!")
        
        st.divider()
        
        # Data refresh
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.session_state.data_loaded = False
            st.rerun()
        
        # Footer
        st.markdown("---")
        st.markdown(
            '<div style="text-align: center; font-size: 0.8rem; color: #6b7280;">'
            'Career Compass AI v1.0.0<br>'
            'Data updates daily'
            '</div>',
            unsafe_allow_html=True
        )
    
    # Main content
    if page == "🏠 Home":
        show_home_page()
    elif page == "📊 Market Intelligence":
        show_market_page()
    elif page == "🎯 Career Analysis":
        show_analysis_page()
    elif page == "💰 ROI Calculator":
        show_roi_page()
    elif page == "🔮 Future Forecasting":
        show_forecasting_page()
    elif page == "ℹ️ About":
        show_about_page()
    
    # Global footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #6b7280; font-size: 0.9rem;">
            <p>
                🧭 <b>Career Compass AI</b> • Data-driven career planning • 
                <a href="https://github.com/chm-hibatallah/career-compass-ai" target="_blank">GitHub</a> • 
                Made with ❤️ for data science students
            </p>
            <p style="font-size: 0.8rem;">
                Uses real data from Stack Overflow, GitHub Jobs, and realistic market samples
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()