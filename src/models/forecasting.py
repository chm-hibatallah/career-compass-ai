# src/models/forecasting.py

import pandas as pd
from prophet import Prophet
from ..database.models import SessionLocal, SkillTrend, Skill

class SkillForecaster:
    def __init__(self):
        self.session = SessionLocal()
    
    def prepare_data(self, skill_id: int):
        # Get historical trend data for the skill
        trends = self.session.query(SkillTrend).filter(SkillTrend.skill_id == skill_id).order_by(SkillTrend.date).all()
        
        data = pd.DataFrame([{
            'ds': trend.date,
            'y': trend.demand_score
        } for trend in trends])
        
        return data
    
    def forecast(self, skill_id: int, periods: int = 30):
        data = self.prepare_data(skill_id)
        if data.empty:
            return None
        
        model = Prophet()
        model.fit(data)
        
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
    
    def forecast_all_skills(self):
        skills = self.session.query(Skill).all()
        forecasts = {}
        for skill in skills:
            forecast = self.forecast(skill.id)
            if forecast is not None:
                forecasts[skill.name] = forecast
        return forecasts