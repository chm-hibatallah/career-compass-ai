"""
Reusable dashboard components
"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any

class DashboardComponents:
    """Reusable dashboard components"""
    
    @staticmethod
    def metric_card(title: str, value: Any, change: str = None, 
                   icon: str = "📊", color: str = "blue"):
        """Create a metric card"""
        col1, col2 = st.columns([1, 4])
        
        with col1:
            st.markdown(f"<h1 style='font-size: 2.5rem; color: {color};'>{icon}</h1>", 
                       unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**{title}**")
            st.markdown(f"<h2 style='margin: 0;'>{value}</h2>", unsafe_allow_html=True)
            if change:
                st.caption(change)
    
    @staticmethod
    def skill_card(skill: str, level: str = "intermediate", 
                  demand: str = "high", hours: int = 40):
        """Create a skill card"""
        colors = {
            "beginner": "#3B82F6",
            "intermediate": "#8B5CF6",
            "advanced": "#EF4444"
        }
        
        demand_icons = {
            "very high": "🔥",
            "high": "📈",
            "medium": "📊",
            "low": "📉",
            "niche": "🎯"
        }
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {colors.get(level, '#3B82F6')}20, #ffffff);
            border-left: 4px solid {colors.get(level, '#3B82F6')};
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 0 8px 8px 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0; color: #1F2937;">{skill.title()}</h4>
                    <p style="margin: 0.25rem 0; color: #6B7280; font-size: 0.9rem;">
                        Level: <span style="color: {colors.get(level, '#3B82F6')}; font-weight: bold;">{level.title()}</span>
                    </p>
                </div>
                <div style="text-align: right;">
                    <p style="margin: 0; color: #6B7280; font-size: 0.9rem;">
                        {demand_icons.get(demand, '📊')} {demand.title()} Demand
                    </p>
                    <p style="margin: 0; color: #6B7280; font-size: 0.9rem;">
                        ⏱️ {hours} hours
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def create_gauge_chart(value: float, title: str = "Score", 
                          min_val: float = 0, max_val: float = 100):
        """Create a gauge chart"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': title},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [min_val, max_val]},
                'bar': {'color': "#2563EB"},
                'steps': [
                    {'range': [min_val, max_val * 0.6], 'color': "lightgray"},
                    {'range': [max_val * 0.6, max_val * 0.8], 'color': "gray"},
                    {'range': [max_val * 0.8, max_val], 'color': "darkgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_val * 0.8
                }
            }
        ))
        
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=50, b=20))
        return fig
    
    @staticmethod
    def create_radar_chart(categories: List[str], values: List[float], 
                          title: str = "Skill Profile"):
        """Create a radar chart"""
        fig = go.Figure(data=go.Scatterpolar(
            r=values + [values[0]],  # Close the shape
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(37, 99, 235, 0.3)',
            line_color='rgb(37, 99, 235)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(values) * 1.2]
                )
            ),
            showlegend=False,
            title=title,
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_timeline_chart(milestones: List[Dict]):
        """Create a timeline visualization"""
        fig = go.Figure()
        
        for i, milestone in enumerate(milestones):
            fig.add_trace(go.Scatter(
                x=[i, i],
                y=[0, 1],
                mode='lines+markers+text',
                line=dict(color='#2563EB', width=2),
                marker=dict(size=10, color='#2563EB'),
                text=[f"Month {milestone['month']}", milestone['description']],
                textposition="top center",
                name=milestone['title']
            ))
        
        fig.update_layout(
            title="Learning Timeline",
            xaxis=dict(showticklabels=False, showgrid=False),
            yaxis=dict(showticklabels=False, showgrid=False),
            showlegend=False,
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig
    
    @staticmethod
    def create_comparison_table(data: pd.DataFrame, title: str = "Comparison"):
        """Create a styled comparison table"""
        st.markdown(f"### {title}")
        
        # Style the dataframe
        styled_df = data.style.format({
            'Salary Increase': '${:,.0f}',
            'ROI Score': '{:.1f}',
            'Months to Break Even': '{:.1f}'
        }).background_gradient(subset=['ROI Score'], cmap='RdYlGn')
        
        st.dataframe(styled_df, use_container_width=True)