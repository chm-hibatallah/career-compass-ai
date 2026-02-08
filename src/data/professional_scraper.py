"""
Professional, ethical web scraper for job market data.
Includes rate limiting, caching, and polite headers.
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict
from datetime import datetime
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfessionalJobScraper:
    """Main scraper class with ethical scraping practices"""
    
    def __init__(self, cache_dir="data/raw"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Polite headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Rate limiting: wait 2-5 seconds between requests
        self.min_delay = 2
        self.max_delay = 5
        
    def _delay(self):
        """Add random delay between requests to be polite"""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)
        
    def fetch_stackoverflow_rss(self, search_term="data scientist", max_results=50) -> List[Dict]:
        """
        Fetch jobs from Stack Overflow RSS feed (public and allowed)
        RSS is a public feed - no scraping needed!
        """
        logger.info(f"Fetching Stack Overflow jobs for: {search_term}")
        
        try:
            # Stack Overflow Jobs RSS feed
            url = f"https://stackoverflow.com/jobs/feed"
            params = {
                'q': search_term,
                'l': '',  # location (empty for all)
                'u': 'Miles',
                'd': 20   # distance
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse RSS/XML
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')[:max_results]
            
            jobs = []
            for item in items:
                job = {
                    'id': f"so_{item.find('guid').text if item.find('guid') else item.find('link').text}",
                    'title': item.find('title').text if item.find('title') else '',
                    'company': item.find('name').text if item.find('name') else '',
                    'location': item.find('location').text if item.find('location') else 'Remote',
                    'description': self._clean_html(item.find('description').text if item.find('description') else ''),
                    'url': item.find('link').text if item.find('link') else '',
                    'published_date': item.find('pubDate').text if item.find('pubDate') else '',
                    'source': 'stack_overflow',
                    'collected_at': datetime.now().isoformat()
                }
                jobs.append(job)
                
            logger.info(f"Successfully fetched {len(jobs)} jobs from Stack Overflow")
            return jobs
            
        except Exception as e:
            logger.error(f"Error fetching Stack Overflow jobs: {e}")
            return []
    
    def fetch_github_jobs_rss(self, search_term="python") -> List[Dict]:
        """
        Fetch from GitHub Jobs RSS (still available despite API deprecation)
        """
        logger.info(f"Fetching GitHub jobs for: {search_term}")
        
        try:
            url = f"https://jobs.github.com/positions.atom"
            params = {'description': search_term}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            entries = soup.find_all('entry')[:30]
            
            jobs = []
            for entry in entries:
                job = {
                    'id': f"github_{entry.find('id').text if entry.find('id') else ''}",
                    'title': entry.find('title').text if entry.find('title') else '',
                    'company': entry.find('name').text if entry.find('name') else '',
                    'location': entry.find('location').text if entry.find('location') else 'Remote',
                    'description': self._clean_html(entry.find('summary').text if entry.find('summary') else ''),
                    'url': entry.find('link')['href'] if entry.find('link') else '',
                    'published_date': entry.find('updated').text if entry.find('updated') else '',
                    'source': 'github_jobs',
                    'collected_at': datetime.now().isoformat()
                }
                jobs.append(job)
                
            logger.info(f"Successfully fetched {len(jobs)} jobs from GitHub Jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"Error fetching GitHub Jobs: {e}")
            return []
    
    def fetch_remoteok_api(self) -> List[Dict]:
        """
        Fetch from RemoteOK API (public JSON API)
        """
        logger.info("Fetching RemoteOK jobs")
        
        try:
            url = "https://remoteok.com/api"
            response = self.session.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                jobs = []
                
                # First item is metadata
                for item in data[1:21]:  # Limit to 20 jobs
                    if item.get('position'):
                        job = {
                            'id': f"remoteok_{item.get('slug', '')}",
                            'title': item.get('position', ''),
                            'company': item.get('company', ''),
                            'location': 'Remote',
                            'description': self._clean_html(item.get('description', '')),
                            'url': item.get('url', ''),
                            'salary': item.get('salary', ''),
                            'tags': item.get('tags', []),
                            'source': 'remoteok',
                            'collected_at': datetime.now().isoformat()
                        }
                        jobs.append(job)
                        
                logger.info(f"Successfully fetched {len(jobs)} jobs from RemoteOK")
                return jobs
                
        except Exception as e:
            logger.error(f"Error fetching RemoteOK: {e}")
            return []
        
        return []
    
    def _clean_html(self, html_text: str) -> str:
        """Clean HTML tags from text"""
        if not html_text:
            return ""
        
        soup = BeautifulSoup(html_text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return ' '.join(text.split())[:1000]  # Limit length
    
    def collect_all_sources(self, use_cache=True) -> pd.DataFrame:
        """
        Collect from all sources with caching
        """
        cache_file = self.cache_dir / f"jobs_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Use cache if exists and less than 24 hours old
        if use_cache and cache_file.exists():
            cache_age = datetime.now().timestamp() - cache_file.stat().st_mtime
            if cache_age < 86400:  # 24 hours in seconds
                logger.info(f"Loading cached data from {cache_file}")
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                return pd.DataFrame(cached_data)
        
        logger.info("Starting fresh data collection...")
        
        all_jobs = []
        
        # Collect from each source with delays
        sources = [
            ("Stack Overflow", self.fetch_stackoverflow_rss, "data scientist"),
            ("Stack Overflow", self.fetch_stackoverflow_rss, "machine learning"),
            ("GitHub Jobs", self.fetch_github_jobs_rss, "python"),
            ("RemoteOK", self.fetch_remoteok_api, None)
        ]
        
        for source_name, method, param in sources:
            self._delay()
            if param:
                jobs = method(param)
            else:
                jobs = method()
            all_jobs.extend(jobs)
            logger.info(f"Collected {len(jobs)} jobs from {source_name}")
        
        # Create DataFrame
        df = pd.DataFrame(all_jobs)
        
        # Save to cache
        if not df.empty:
            df.to_json(cache_file, orient='records', indent=2)
            logger.info(f"Saved {len(df)} jobs to cache: {cache_file}")
        
        # If no real data, use sample fallback
        if len(df) < 10:
            logger.warning("Insufficient real data, using enhanced sample data")
            df = self._create_sample_dataset()
        
        return df
    
    def _create_sample_dataset(self) -> pd.DataFrame:
        """
        Create a realistic sample dataset when real data is unavailable
        This ensures the app always works
        """
        logger.info("Creating enhanced sample dataset")
        
        # Realistic job data based on current market trends
        sample_jobs = []
        roles = [
            ("Data Scientist", ["Python", "SQL", "Machine Learning", "Statistics", "AWS"]),
            ("ML Engineer", ["Python", "Docker", "Kubernetes", "TensorFlow", "MLOps"]),
            ("Data Engineer", ["SQL", "Python", "Spark", "Airflow", "AWS"]),
            ("Backend Developer", ["Python", "FastAPI", "Docker", "PostgreSQL", "AWS"])
        ]
        
        companies = ["TechCorp", "DataWorks", "AI Innovations", "CloudSystems", "AnalyticsPro"]
        locations = ["Remote", "San Francisco, CA", "New York, NY", "London, UK", "Berlin, Germany"]
        
        for i in range(50):
            role_idx = i % len(roles)
            role_name, skills = roles[role_idx]
            
            job = {
                'id': f"sample_{i}",
                'title': f"{['Senior', 'Mid-level', 'Junior'][i % 3]} {role_name}",
                'company': companies[i % len(companies)],
                'location': locations[i % len(locations)],
                'description': f"Looking for a {role_name} with experience in {', '.join(skills[:3])}. "
                              f"Must have strong problem-solving skills and ability to work in a fast-paced environment.",
                'skills': skills,
                'salary_range': f"${80000 + (i * 5000):,}-${120000 + (i * 10000):,}",
                'experience_level': ["Entry", "Mid", "Senior"][i % 3],
                'job_type': ["Full-time", "Contract", "Part-time"][i % 3],
                'posted_date': (datetime.now().replace(day=(i % 28) + 1)).strftime("%Y-%m-%d"),
                'source': 'sample_dataset',
                'collected_at': datetime.now().isoformat()
            }
            sample_jobs.append(job)
        
        return pd.DataFrame(sample_jobs)

# Quick test
if __name__ == "__main__":
    scraper = ProfessionalJobScraper()
    df = scraper.collect_all_sources()
    print(f"Collected {len(df)} jobs")
    print(f"Sources: {df['source'].unique()}")
    print(df[['title', 'company', 'location', 'source']].head())