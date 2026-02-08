"""
Simple, ethical job data collector for Career Compass
"""
import requests
import pandas as pd
from typing import List, Dict
import time
from datetime import datetime
import json
from pathlib import Path


class JobDataCollector:
    """Collect job posting data from public APIs"""
    
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def fetch_github_jobs(self, search_term: str = "data scientist") -> List[Dict]:
        """Fetch job postings from GitHub Jobs RSS"""
        print(f"Fetching GitHub Jobs for: {search_term}")
        
        # Simulated data for initial development
        # In production, replace with actual API calls
        
        sample_jobs = [
            {
                "id": f"gh_{i}",
                "title": f"Senior {search_term.title()}",
                "company": ["TechCorp", "DataWorks", "AIStartup"][i % 3],
                "location": "Remote",
                "description": f"Looking for a {search_term} with Python, SQL, and ML experience. Must know {['TensorFlow', 'PyTorch', 'AWS'][i % 3]}.",
                "skills": ["Python", "SQL", "Machine Learning", ["TensorFlow", "PyTorch", "AWS"][i % 3]],
                "posted_date": datetime.now().strftime("%Y-%m-%d"),
                "source": "github_jobs"
            }
            for i in range(10)
        ]
        
        return sample_jobs
    
    def fetch_simulated_linkedin(self, role: str = "data scientist") -> List[Dict]:
        """Simulated LinkedIn job data"""
        print(f"Fetching simulated LinkedIn data for: {role}")
        
        skills_pool = {
            "data scientist": ["Python", "SQL", "Machine Learning", "Statistics", "A/B Testing", "TensorFlow", "PyTorch", "Spark"],
            "ml engineer": ["Python", "Docker", "AWS", "MLOps", "FastAPI", "TensorFlow", "Kubernetes", "CI/CD"],
            "data engineer": ["SQL", "Python", "Spark", "AWS", "Airflow", "Kafka", "Data Pipelines", "ETL"],
            "backend engineer": ["Python", "FastAPI", "Docker", "PostgreSQL", "AWS", "Redis", "REST APIs", "Testing"]
        }
        
        roles = list(skills_pool.keys())
        jobs = []
        
        for i in range(20):
            role_key = roles[i % len(roles)]
            job = {
                "id": f"li_{i}",
                "title": f"{['Senior', 'Mid-level', 'Junior'][i % 3]} {role_key.title()}",
                "company": f"Company_{i % 10}",
                "location": ["Remote", "San Francisco, CA", "New York, NY"][i % 3],
                "description": f"Seeking a {role_key} with experience in various technologies.",
                "skills": skills_pool[role_key][: (i % 4) + 3],  # Varying number of skills
                "posted_date": (datetime.now().replace(day=(i % 28) + 1)).strftime("%Y-%m-%d"),
                "salary_range": f"${(80000 + (i * 5000)):,}-${(120000 + (i * 10000)):,}",
                "experience_level": ["Entry", "Mid", "Senior"][i % 3],
                "source": "linkedin_simulated"
            }
            jobs.append(job)
        
        return jobs
    
    def collect_all_jobs(self) -> pd.DataFrame:
        """Collect jobs from all sources"""
        print("Starting job data collection...")
        
        all_jobs = []
        
        # Collect from different sources
        all_jobs.extend(self.fetch_github_jobs("data scientist"))
        all_jobs.extend(self.fetch_github_jobs("machine learning engineer"))
        all_jobs.extend(self.fetch_simulated_linkedin())
        
        # Convert to DataFrame
        df = pd.DataFrame(all_jobs)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.data_dir / f"jobs_{timestamp}.json"
        
        df.to_json(output_path, orient="records", indent=2)
        print(f"Saved {len(df)} jobs to {output_path}")
        
        return df


if __name__ == "__main__":
    collector = JobDataCollector()
    jobs_df = collector.collect_all_jobs()
    print(f"\nSample job data:\n")
    print(jobs_df[["title", "company", "skills"]].head())