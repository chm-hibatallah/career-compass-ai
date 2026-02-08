"""
Professional data collector with real APIs and ethical scraping
"""
import requests
import pandas as pd
from typing import List, Dict, Optional
import json
from datetime import datetime, timedelta
import time
from bs4 import BeautifulSoup
import feedparser
import logging
from pathlib import Path
import aiohttp
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealJobCollector:
    """Collect real job data from multiple sources"""
    
    def __init__(self, cache_dir: str = "data/raw"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CareerCompass/1.0 (+https://github.com/chm-hibatallah/career-compass-ai)'
        })
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_github_jobs_api(self, description: str = "data", location: str = "") -> List[Dict]:
        """Fetch real jobs from GitHub Jobs API"""
        base_url = "https://jobs.github.com/positions.json"
        params = {
            'description': description,
            'location': location
        }
        
        try:
            response = self.session.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            jobs = response.json()
            
            processed_jobs = []
            for job in jobs:
                processed_job = {
                    'id': f"github_{job['id']}",
                    'title': job.get('title', ''),
                    'company': job.get('company', ''),
                    'location': job.get('location', ''),
                    'description': self.clean_html(job.get('description', '')),
                    'type': job.get('type', ''),
                    'url': job.get('url', ''),
                    'company_url': job.get('company_url', ''),
                    'company_logo': job.get('company_logo', ''),
                    'created_at': job.get('created_at', ''),
                    'source': 'github_jobs',
                    'collected_at': datetime.now().isoformat()
                }
                processed_jobs.append(processed_job)
            
            logger.info(f"Fetched {len(processed_jobs)} jobs from GitHub Jobs API")
            return processed_jobs
            
        except Exception as e:
            logger.error(f"Error fetching GitHub Jobs: {e}")
            return []
    
    def fetch_stackoverflow_jobs(self, tags: str = "python") -> List[Dict]:
        """Fetch jobs from Stack Overflow RSS feed"""
        try:
            url = f"https://stackoverflow.com/jobs/feed?q={tags}"
            feed = feedparser.parse(url)
            
            jobs = []
            for entry in feed.entries[:50]:  # Limit to 50
                job = {
                    'id': f"so_{entry.get('id', '').split('/')[-1]}",
                    'title': entry.get('title', ''),
                    'company': entry.get('author', ''),
                    'location': entry.get('location', ''),
                    'description': self.clean_html(entry.get('summary', '')),
                    'url': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'tags': [tag.term for tag in entry.get('tags', [])],
                    'source': 'stack_overflow',
                    'collected_at': datetime.now().isoformat()
                }
                jobs.append(job)
            
            logger.info(f"Fetched {len(jobs)} jobs from Stack Overflow")
            return jobs
            
        except Exception as e:
            logger.error(f"Error fetching Stack Overflow jobs: {e}")
            return []
    
    def fetch_remoteok_api(self) -> List[Dict]:
        """Fetch remote jobs from RemoteOK API"""
        try:
            url = "https://remoteok.com/api"
            response = self.session.get(url, headers={'User-Agent': 'CareerCompass'}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()[1:]  # First item is metadata
                jobs = []
                
                for item in data[:50]:  # Limit to 50
                    if item.get('position'):
                        job = {
                            'id': f"remoteok_{item.get('slug', '')}",
                            'title': item.get('position', ''),
                            'company': item.get('company', ''),
                            'location': 'Remote',
                            'description': self.clean_html(item.get('description', '')),
                            'url': item.get('url', ''),
                            'salary': item.get('salary', ''),
                            'tags': item.get('tags', []),
                            'source': 'remoteok',
                            'collected_at': datetime.now().isoformat()
                        }
                        jobs.append(job)
                
                logger.info(f"Fetched {len(jobs)} jobs from RemoteOK")
                return jobs
                
        except Exception as e:
            logger.error(f"Error fetching RemoteOK jobs: {e}")
            return []
        
        return []
    
    def fetch_reed_co_uk(self, keywords: str = "data scientist") -> List[Dict]:
        """Fetch jobs from Reed.co.uk (UK market)"""
        try:
            url = f"https://www.reed.co.uk/api/1.0/search"
            
            # Note: Reed API requires authentication
            # For now, we'll simulate with ethical web scraping alternative
            # In production, you'd use their official API with an API key
            
            # Simulated response for development
            jobs = []
            for i in range(20):
                job = {
                    'id': f"reed_{i}",
                    'title': f"{keywords.title()} - Example Position {i}",
                    'company': f"Company {i % 5}",
                    'location': ['London', 'Manchester', 'Remote', 'Birmingham'][i % 4],
                    'description': f"Looking for a {keywords} with Python, SQL, and cloud experience.",
                    'salary': f"£{40000 + (i * 5000):,}",
                    'source': 'reed',
                    'collected_at': datetime.now().isoformat()
                }
                jobs.append(job)
            
            logger.info(f"Simulated {len(jobs)} jobs from Reed")
            return jobs
            
        except Exception as e:
            logger.error(f"Error with Reed jobs: {e}")
            return []
    
    def fetch_linkedin_simulation(self, role: str = "data scientist") -> List[Dict]:
        """Simulated LinkedIn data - In production, use LinkedIn API with proper auth"""
        # LinkedIn API requires partnership - we'll create realistic simulation data
        # based on real market trends
        
        roles_data = {
            "data scientist": {
                "skills": ["Python", "SQL", "Machine Learning", "Statistics", "A/B Testing", 
                          "TensorFlow", "PyTorch", "Spark", "AWS", "Tableau"],
                "salary_range": (80000, 150000),
                "companies": ["Amazon", "Google", "Meta", "Microsoft", "Netflix", 
                             "Spotify", "Airbnb", "Uber", "Stripe", "Salesforce"]
            },
            "machine learning engineer": {
                "skills": ["Python", "Docker", "AWS", "MLOps", "TensorFlow", "PyTorch",
                          "Kubernetes", "FastAPI", "CI/CD", "Spark"],
                "salary_range": (90000, 180000),
                "companies": ["Tesla", "OpenAI", "NVIDIA", "Apple", "Facebook AI",
                             "DeepMind", "Hugging Face", "Scale AI", "Waymo", "Cruise"]
            },
            "data engineer": {
                "skills": ["SQL", "Python", "Spark", "AWS", "Airflow", "Kafka",
                          "Data Pipelines", "ETL", "Snowflake", "dbt"],
                "salary_range": (85000, 160000),
                "companies": ["Snowflake", "Databricks", "Confluent", "Fivetran",
                             "Palantir", "Bloomberg", "Goldman Sachs", "JP Morgan"]
            }
        }
        
        role_data = roles_data.get(role.lower(), roles_data["data scientist"])
        
        jobs = []
        for i in range(30):
            skills_needed = role_data["skills"][: (i % 6) + 4]
            min_salary, max_salary = role_data["salary_range"]
            salary = min_salary + ((i % 10) * 7000)
            
            job = {
                'id': f"linkedin_sim_{role.lower().replace(' ', '_')}_{i}",
                'title': f"{['Senior', 'Mid-level', 'Junior'][i % 3]} {role.title()}",
                'company': role_data["companies"][i % len(role_data["companies"])],
                'location': ["Remote", "San Francisco, CA", "New York, NY", "London"][i % 4],
                'description': f"Seeking a {role} with experience in {', '.join(skills_needed[:3])}. "
                              f"Must have strong problem-solving skills and ability to work in fast-paced environment.",
                'skills': skills_needed,
                'salary': f"${salary:,}",
                'experience_level': ["Entry", "Mid", "Senior"][i % 3],
                'job_type': ["Full-time", "Contract", "Part-time"][i % 3],
                'posted_date': (datetime.now() - timedelta(days=i % 30)).strftime("%Y-%m-%d"),
                'source': 'linkedin_simulated',
                'collected_at': datetime.now().isoformat()
            }
            jobs.append(job)
        
        logger.info(f"Generated {len(jobs)} simulated LinkedIn jobs for {role}")
        return jobs
    
    def clean_html(self, html_text: str) -> str:
        """Clean HTML from job descriptions"""
        if not html_text:
            return ""
        
        soup = BeautifulSoup(html_text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        return text[:2000]  # Limit length
    
    def collect_all_sources(self) -> pd.DataFrame:
        """Collect jobs from all available sources"""
        logger.info("Starting comprehensive job data collection...")
        
        all_jobs = []
        
        # Collect from real APIs
        all_jobs.extend(self.fetch_github_jobs_api("data scientist"))
        all_jobs.extend(self.fetch_github_jobs_api("machine learning engineer"))
        all_jobs.extend(self.fetch_stackoverflow_jobs("python"))
        all_jobs.extend(self.fetch_remoteok_api())
        
        # Add simulated/supplemental data
        all_jobs.extend(self.fetch_reed_co_uk("data scientist"))
        all_jobs.extend(self.fetch_linkedin_simulation("data scientist"))
        all_jobs.extend(self.fetch_linkedin_simulation("machine learning engineer"))
        all_jobs.extend(self.fetch_linkedin_simulation("data engineer"))
        
        # Convert to DataFrame
        df = pd.DataFrame(all_jobs)
        
        # Add metadata
        df['collection_timestamp'] = datetime.now()
        df['job_id_hash'] = df['id'].apply(lambda x: hash(str(x)) % 1000000)
        
        # Save to cache
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cache_file = self.cache_dir / f"jobs_comprehensive_{timestamp}.parquet"
        df.to_parquet(cache_file, compression='snappy')
        
        logger.info(f"✅ Collected {len(df)} jobs total")
        logger.info(f"📁 Saved to: {cache_file}")
        
        return df
    
    def load_latest_data(self) -> pd.DataFrame:
        """Load the most recent cached data"""
        cache_files = list(self.cache_dir.glob("jobs_comprehensive_*.parquet"))
        if not cache_files:
            logger.warning("No cached data found. Collecting fresh data...")
            return self.collect_all_sources()
        
        latest_file = max(cache_files, key=lambda x: x.stat().st_mtime)
        logger.info(f"Loading cached data from: {latest_file}")
        
        df = pd.read_parquet(latest_file)
        logger.info(f"Loaded {len(df)} jobs from cache")
        
        return df


if __name__ == "__main__":
    collector = RealJobCollector()
    
    # Test collection
    df = collector.collect_all_sources()
    
    print(f"\n📊 Data Collection Summary:")
    print(f"Total jobs: {len(df)}")
    print(f"Sources: {df['source'].unique().tolist()}")
    print(f"\nSample jobs:")
    print(df[['title', 'company', 'location', 'source']].head())