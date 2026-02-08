# src/data/github_jobs.py

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict
from ..database.models import SessionLocal, Job, Skill

class GitHubJobsCollector:
    BASE_URL = "https://jobs.github.com/positions.json"
    
    def __init__(self):
        self.session = SessionLocal()
    
    def fetch_jobs(self, search_term: str = "data scientist") -> List[Dict]:
        params = {"description": search_term}
        response = requests.get(self.BASE_URL, params=params)
        jobs = response.json()
        
        processed_jobs = []
        for job in jobs:
            processed_job = {
                "external_id": job.get("id"),
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "description": job.get("description"),
                "posted_date": datetime.strptime(job.get("created_at"), "%a %b %d %H:%M:%S UTC %Y"),
                "source": "github_jobs"
            }
            processed_jobs.append(processed_job)
        
        return processed_jobs
    
    def extract_skills(self, description: str) -> List[str]:
        # Use the SkillExtractor from earlier
        from ..features.skill_extractor import SkillExtractor
        extractor = SkillExtractor()
        return extractor.extract_skills(description)
    
    def save_jobs(self, jobs: List[Dict]):
        for job_data in jobs:
            # Check if job already exists
            existing_job = self.session.query(Job).filter(Job.external_id == job_data["external_id"]).first()
            if existing_job:
                continue
            
            # Extract skills
            skill_names = self.extract_skills(job_data["description"])
            skills = []
            for name in skill_names:
                skill = self.session.query(Skill).filter(Skill.name == name).first()
                if not skill:
                    skill = Skill(name=name)
                    self.session.add(skill)
                skills.append(skill)
            
            job = Job(
                external_id=job_data["external_id"],
                title=job_data["title"],
                company=job_data["company"],
                location=job_data["location"],
                description=job_data["description"],
                posted_date=job_data["posted_date"],
                source=job_data["source"],
                skills=skills
            )
            self.session.add(job)
        
        self.session.commit()
    
    def run(self):
        print("Fetching jobs from GitHub Jobs...")
        jobs = self.fetch_jobs()
        print(f"Found {len(jobs)} jobs")
        self.save_jobs(jobs)
        self.session.close()