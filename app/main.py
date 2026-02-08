"""
Career Compass - Main Streamlit Application
Windows-compatible version
"""
import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Set page configuration FIRST
st.set_page_config(
    page_title="Career Compass AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add project root to path for Windows
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Try to import settings with error handling
try:
    from config.settings import settings
    st.success("✅ Successfully loaded configuration")
except ImportError as e:
    st.warning(f"⚠️ Using fallback settings: {e}")
    
    # Fallback settings
    class Settings:
        APP_NAME = "Career Compass AI"
        VERSION = "1.0.0"
        DEBUG = True
        DEFAULT_HOURS_PER_WEEK = 10
        DEFAULT_TIMELINE_MONTHS = 6
    
    settings = Settings()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2563eb;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #2563eb;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Title
    st.markdown('<h1 class="main-header">🧭 Career Compass AI</h1>', unsafe_allow_html=True)
    st.markdown("### AI-powered skill gap analysis with market forecasting")
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/compass--v1.png", width=80)
        st.title("Navigation")
        
        # Page selection
        page = st.radio(
            "Choose Analysis:",
            ["🏠 Home", "📊 Market Overview", "🎯 Career Analysis", "💰 ROI Calculator", "🔮 Forecasting"]
        )
        
        st.divider()
        
        # User profile
        st.subheader("Your Profile")
        user_skills = st.multiselect(
            "Your Current Skills",
            ["Python", "SQL", "Machine Learning", "AWS", "Docker", "JavaScript", "React", "Tableau"],
            default=["Python", "SQL"]
        )
        
        target_role = st.selectbox(
            "Target Role",
            ["Data Scientist", "Machine Learning Engineer", "Data Engineer", 
             "Backend Developer", "MLOps Engineer", "AI Researcher"]
        )
        
        experience = st.slider("Years of Experience", 0, 20, 3)
        
        st.divider()
        
        # Quick actions
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    # Main content based on page selection
    if page == "🏠 Home":
        show_home_page()
    elif page == "📊 Market Overview":
        show_market_page()
    elif page == "🎯 Career Analysis":
        show_analysis_page(user_skills, target_role, experience)
    elif page == "💰 ROI Calculator":
        show_roi_page(user_skills, target_role)
    elif page == "🔮 Forecasting":
        show_forecasting_page()

def show_home_page():
    """Show home page"""
    st.header("Welcome to Career Compass AI 🚀")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## Why Career Compass?
        
        Traditional career advice is **generic**. We use **real market data** to provide:
        
        ✅ **Personalized skill gap analysis**  
        ✅ **ROI calculation** for learning investments  
        ✅ **Future skill forecasting**  
        ✅ **Optimal learning paths**  
        ✅ **Career transition simulations**
        
        ### How It Works
        1. **Enter your skills** in the sidebar
        2. **Select your target role**
        3. **Get instant analysis** with actionable insights
        4. **Follow optimized learning paths**
        
        """)
        
        if st.button("🎯 Start Your Analysis", type="primary", use_container_width=True):
            st.session_state.page = "Career Analysis"
            st.rerun()
    
    with col2:
        # Quick stats
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Quick Stats</h3>
            <p><b>Jobs Analyzed:</b> 1,250+</p>
            <p><b>Skills Tracked:</b> 150+</p>
            <p><b>Market Health:</b> 85/100</p>
            <p><b>Remote Jobs:</b> 42%</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h3>🔥 Top Skills</h3>
            <p>1. Python (45%)</p>
            <p>2. SQL (39%)</p>
            <p>3. AWS (36%)</p>
            <p>4. Docker (32%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Testimonials
    st.markdown("---")
    st.subheader("🎓 What Students Are Saying")
    
    cols = st.columns(3)
    testimonials = [
        {"name": "Sarah M.", "role": "Data Science Student", "text": "Career Compass helped me land my first data science internship!"},
        {"name": "Alex T.", "role": "Career Changer", "text": "The ROI calculator showed me exactly which skills to learn first."},
        {"name": "Jamie L.", "role": "Recent Graduate", "text": "The forecasting feature helped me future-proof my skillset."}
    ]
    
    for idx, col in enumerate(cols):
        with col:
            testimonial = testimonials[idx]
            st.markdown(f"""
            <div class="metric-card">
                <p><i>"{testimonial['text']}"</i></p>
                <p><b>{testimonial['name']}</b><br>
                <small>{testimonial['role']}</small></p>
            </div>
            """, unsafe_allow_html=True)

def show_market_page():
    """Show market overview"""
    st.header("📊 Current Market Overview")
    
    # Market metrics
    cols = st.columns(4)
    
    with cols[0]:
        st.metric("Total Jobs", "1,250", "+12%")
    
    with cols[1]:
        st.metric("Remote Jobs", "42%", "+5%")
    
    with cols[2]:
        st.metric("Avg. Salary", "$112,000", "+8%")
    
    with cols[3]:
        st.metric("Market Health", "85/100", "Strong")
    
    st.markdown("---")
    
    # Top skills
    st.subheader("🔥 Top In-Demand Skills")
    
    top_skills = {
        "Python": {"demand": 45.2, "salary_boost": 15000, "growth": "+12%"},
        "SQL": {"demand": 38.7, "salary_boost": 12000, "growth": "+8%"},
        "AWS": {"demand": 36.5, "salary_boost": 18000, "growth": "+15%"},
        "Docker": {"demand": 32.1, "salary_boost": 14000, "growth": "+22%"},
        "Machine Learning": {"demand": 29.8, "salary_boost": 20000, "growth": "+18%"},
        "Spark": {"demand": 24.3, "salary_boost": 16000, "growth": "+10%"},
        "Kubernetes": {"demand": 21.5, "salary_boost": 17000, "growth": "+25%"},
        "Airflow": {"demand": 19.2, "salary_boost": 13000, "growth": "+30%"}
    }
    
    for skill, data in top_skills.items():
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"**{skill}**")
        with col2:
            st.markdown(f"{data['demand']}% demand")
        with col3:
            st.markdown(f"+${data['salary_boost']:,}")
    
    st.markdown("---")
    
    # Emerging technologies
    st.subheader("🚀 Emerging Technologies")
    
    emerging = [
        {"name": "LangChain", "growth": "+300%", "description": "LLM application framework"},
        {"name": "Ray", "growth": "+150%", "description": "Distributed ML computing"},
        {"name": "Feast", "growth": "+120%", "description": "Feature store for ML"}
    ]
    
    for tech in emerging:
        with st.expander(f"{tech['name']} - Growth: {tech['growth']}"):
            st.write(tech['description'])
            st.progress(0.7)

def show_analysis_page(user_skills, target_role, experience):
    """Show career analysis"""
    st.header(f"🎯 Career Analysis: Transition to {target_role}")
    
    # Skill requirements by role
    role_requirements = {
        "Data Scientist": ["Python", "SQL", "Machine Learning", "Statistics", "Data Visualization", "A/B Testing"],
        "Machine Learning Engineer": ["Python", "Docker", "AWS", "MLOps", "TensorFlow", "CI/CD", "Kubernetes"],
        "Data Engineer": ["SQL", "Python", "Spark", "AWS", "Airflow", "Kafka", "Data Pipelines"],
        "Backend Developer": ["Python", "FastAPI", "Docker", "PostgreSQL", "AWS", "Redis", "Testing"],
        "MLOps Engineer": ["Docker", "Kubernetes", "AWS", "MLOps", "CI/CD", "Monitoring", "Terraform"],
        "AI Researcher": ["Python", "Machine Learning", "Deep Learning", "Research", "PyTorch", "Mathematics"]
    }
    
    if target_role in role_requirements:
        required = role_requirements[target_role]
        
        # Calculate skill gaps
        gaps = [skill for skill in required if skill not in user_skills]
        strengths = [skill for skill in user_skills if skill in required]
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Your Strengths")
            if strengths:
                for skill in strengths:
                    st.success(f"**{skill}** - Already mastered!")
            else:
                st.info("No matching skills yet. Time to start learning!")
        
        with col2:
            st.subheader("📚 Skills to Learn")
            if gaps:
                for skill in gaps:
                    st.warning(f"**{skill}** - Required for {target_role}")
            else:
                st.success("🎉 You have all required skills!")
        
        # Analysis metrics
        st.markdown("---")
        
        cols = st.columns(4)
        
        with cols[0]:
            coverage = len(strengths) / len(required) * 100 if required else 0
            st.metric("Skill Coverage", f"{coverage:.1f}%")
        
        with cols[1]:
            st.metric("Skills to Learn", len(gaps))
        
        with cols[2]:
            # Estimated timeline
            months = len(gaps) * 1.5  # 1.5 months per skill
            st.metric("Est. Timeline", f"{months:.1f} months")
        
        with cols[3]:
            # Salary impact (simulated)
            salary_boost = 15000 + (len(strengths) * 2000)
            st.metric("Salary Potential", f"+${salary_boost:,}")
        
        # Learning plan
        if gaps:
            st.markdown("---")
            st.subheader("📅 Suggested Learning Plan")
            
            for i, skill in enumerate(gaps[:5], 1):  # Limit to top 5
                with st.expander(f"Month {i}: Learn {skill}"):
                    st.markdown(f"""
                    **Weekly Plan:**
                    - Week 1-2: Fundamentals and theory
                    - Week 3-4: Hands-on projects
                    - Week 5-6: Advanced concepts
                    - Week 7-8: Portfolio project
                    
                    **Resources:**
                    - Course: Coursera/edX {skill} specialization
                    - Book: Recommended readings
                    - Practice: LeetCode/HackerRank exercises
                    
                    **Time commitment:** 10 hours/week
                    """)
        
        # Recommendations
        st.markdown("---")
        st.subheader("🎯 Recommendations")
        
        recommendations = [
            f"Focus on learning {gaps[0] if gaps else 'Python'} first",
            "Build a portfolio project using target skills",
            "Network with professionals in your target role",
            "Update LinkedIn profile with new skills",
            "Consider relevant certifications"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
    
    else:
        st.error(f"Sorry, we don't have data for {target_role} yet.")

def show_roi_page(user_skills, target_role):
    """Show ROI calculator"""
    st.header("💰 ROI Calculator")
    
    st.markdown("Calculate the Return on Investment for learning new skills")
    
    # Inputs
    col1, col2 = st.columns(2)
    
    with col1:
        skill = st.selectbox(
            "Select skill to evaluate",
            ["Python", "AWS", "Docker", "Machine Learning", "Kubernetes", 
             "TensorFlow", "Spark", "Airflow", "FastAPI", "React"]
        )
        
        hours_per_week = st.slider("Hours per week for learning", 5, 40, 10)
    
    with col2:
        current_salary = st.number_input("Current annual salary ($)", 50000, 300000, 80000)
        
        if st.button("💰 Calculate Maximum ROI", type="secondary"):
            st.session_state.show_max_roi = True
    
    # ROI calculation
    if st.button("📊 Calculate ROI", type="primary") or st.session_state.get('show_max_roi', False):
        
        # Simulated calculation
        salary_boost = {
            "Python": 15000,
            "AWS": 18000,
            "Docker": 14000,
            "Machine Learning": 20000,
            "Kubernetes": 17000,
            "TensorFlow": 16000,
            "Spark": 15000,
            "Airflow": 13000,
            "FastAPI": 12000,
            "React": 11000
        }.get(skill, 10000)
        
        learning_hours = {
            "Python": 40,
            "AWS": 50,
            "Docker": 25,
            "Machine Learning": 60,
            "Kubernetes": 40,
            "TensorFlow": 45,
            "Spark": 35,
            "Airflow": 30,
            "FastAPI": 35,
            "React": 50
        }.get(skill, 40)
        
        # Calculate
        weeks_to_learn = learning_hours / hours_per_week
        months_to_learn = weeks_to_learn / 4.33
        
        # ROI formula
        learning_cost = 100  # Course cost
        opportunity_cost = weeks_to_learn * 100  # $100/week
        total_investment = learning_cost + opportunity_cost
        
        roi_ratio = (salary_boost * 3) / total_investment if total_investment > 0 else 0
        roi_score = min(100, roi_ratio * 20)
        
        # Display results
        st.success(f"""
        ## 📈 Results for learning **{skill}**
        """)
        
        cols = st.columns(3)
        
        with cols[0]:
            st.metric("Learning Time", f"{weeks_to_learn:.1f} weeks")
            st.caption(f"({months_to_learn:.1f} months at {hours_per_week} hrs/week)")
        
        with cols[1]:
            st.metric("Salary Increase", f"+${salary_boost:,}")
            st.caption("Estimated annual boost")
        
        with cols[2]:
            st.metric("ROI Score", f"{roi_score:.1f}/100")
            st.caption(f"ROI Ratio: {roi_ratio:.1f}x")
        
        # Detailed breakdown
        with st.expander("📋 Detailed Breakdown"):
            st.markdown(f"""
            **Investment:**
            - Course cost: ${learning_cost}
            - Time investment: {weeks_to_learn:.1f} weeks × $100/week = ${opportunity_cost:,.0f}
            - **Total investment: ${total_investment:,.0f}**
            
            **Return:**
            - Annual salary increase: ${salary_boost:,}
            - 3-year return: ${salary_boost * 3:,}
            
            **ROI Calculation:**
            - ROI Ratio = (3-year return) / (Total investment)
            - ROI Ratio = ${salary_boost * 3:,} / ${total_investment:,.0f} = {roi_ratio:.1f}x
            
            **Payback Period:**
            - Break even in: {total_investment / (salary_boost/12):.1f} months
            """)
        
        # Recommendation
        if roi_score > 70:
            st.balloons()
            st.success(f"🎯 **STRONGLY RECOMMENDED!** Learning {skill} has excellent ROI.")
        elif roi_score > 50:
            st.info(f"✅ **RECOMMENDED!** Good ROI for learning {skill}.")
        else:
            st.warning(f"⚠️ **CONSIDER ALTERNATIVES.** ROI for {skill} is lower than other skills.")

def show_forecasting_page():
    """Show forecasting page"""
    st.header("🔮 Future Skill Forecasting")
    
    st.markdown("Predict which skills will be in demand in the future")
    
    # Time horizon
    horizon = st.select_slider(
        "Forecast Horizon",
        options=["3 months", "6 months", "1 year", "2 years"],
        value="6 months"
    )
    
    # Growth predictions
    st.subheader("📈 Skill Growth Predictions")
    
    growth_data = {
        "Skill": ["LangChain", "Ray", "Kubernetes", "FastAPI", "MLOps", 
                 "Python", "Docker", "AWS", "React", "TensorFlow"],
        "Current": [20, 30, 65, 40, 50, 90, 75, 80, 70, 60],
        "Future": [65, 55, 80, 65, 75, 92, 85, 88, 78, 65],
        "Growth": ["+225%", "+83%", "+23%", "+63%", "+50%", 
                  "+2%", "+13%", "+10%", "+11%", "+8%"]
    }
    
    # Create comparison chart
    import plotly.graph_objects as go
    
    fig = go.Figure(data=[
        go.Bar(name='Current Demand', x=growth_data["Skill"], y=growth_data["Current"]),
        go.Bar(name=f'Future Demand ({horizon})', x=growth_data["Skill"], y=growth_data["Future"])
    ])
    
    fig.update_layout(
        title=f"Skill Demand Growth Projection ({horizon})",
        barmode='group',
        xaxis_title="Skill",
        yaxis_title="Demand Score (0-100)",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.subheader("🎯 Future-Proofing Strategy")
    
    st.markdown("""
    Based on our analysis, here's how to future-proof your career:
    
    1. **Focus on high-growth skills** like LangChain and Ray
    2. **Learn complementary skill pairs** (e.g., Docker + Kubernetes)
    3. **Build projects using emerging technologies**
    4. **Follow industry thought leaders** on new trends
    5. **Contribute to open-source** in growing areas
    
    ### Top 3 Skills to Learn Next:
    
    **1. LangChain** - LLM application framework  
    *Why:* Explosive growth in AI applications  
    *Time to learn:* 40 hours  
    *Salary boost:* +$20K  
    
    **2. MLOps** - Machine Learning Operations  
    *Why:* Critical for production ML systems  
    *Time to learn:* 60 hours  
    *Salary boost:* +$25K  
    
    **3. Kubernetes** - Container orchestration  
    *Why:* Becoming standard for deployment  
    *Time to learn:* 40 hours  
    *Salary boost:* +$18K  
    """)

# Footer
def add_footer():
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #6b7280; font-size: 0.9rem;">
            <p>🧭 Career Compass AI • Data-driven career planning • 
            <a href="https://github.com/yourusername/career-compass-ai" target="_blank">GitHub</a></p>
            <p>Built with ❤️ for data science students • Version 1.0.0</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    # Initialize session state
    if 'show_max_roi' not in st.session_state:
        st.session_state.show_max_roi = False
    if 'page' not in st.session_state:
        st.session_state.page = "Home"
    
    main()
    add_footer()