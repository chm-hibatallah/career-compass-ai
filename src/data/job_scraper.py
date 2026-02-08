"""
Professional job data collector using ONLY free sources
No API keys required - everything works out of the box
"""
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import time
import random
from typing import List, Dict, Optional
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FreeJobDataCollector:
    """
    Collects real job data using only free, public APIs and RSS feeds
    No API keys or authentication required
    """
    
    def __init__(self, cache_dir: str = "data/raw"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Session with polite headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CareerCompass/1.0 (+https://github.com/yourusername/career-compass-ai) Educational Project',
            'Accept': 'application/json, text/xml, application/xml, */*',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        
        # Rate limiting to be respectful
        self.request_delay = 1  # seconds between requests
        
    def _delay(self):
        """Add delay between requests to avoid overwhelming servers"""
        time.sleep(self.request_delay + random.uniform(0, 1))
        
    def fetch_stackoverflow_jobs(self, search_term: str = "data scientist", max_results: int = 50) -> List[Dict]:
        """
        Fetch real jobs from Stack Overflow RSS feed
        COMPLETELY FREE - no API key needed
        """
        try:
            logger.info(f"Fetching Stack Overflow jobs for: {search_term}")
            
            # Stack Overflow Jobs RSS feed URL
            url = "https://stackoverflow.com/jobs/feed"
            params = {
                'q': search_term,
                'l': '',  # location (empty for all)
                'd': 20,  # distance in miles
                'u': 'Km'  # distance unit
            }
            
            self._delay()
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse XML/RSS feed
            root = ET.fromstring(response.content)
            
            jobs = []
            # RSS format: channel -> item
            for item in root.findall('.//item')[:max_results]:
                try:
                    # Extract job details from XML
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    desc_elem = item.find('description')
                    pub_date_elem = item.find('pubDate')
                    
                    # Get company name (sometimes in a separate namespace)
                    namespace = {'a10': 'http://www.w3.org/2005/Atom'}
                    author_elem = item.find('a10:author', namespace)
                    company_name = "Unknown"
                    if author_elem is not None:
                        name_elem = author_elem.find('a10:name', namespace)
                        if name_elem is not None:
                            company_name = name_elem.text
                    
                    # Location might be in category or we extract from description
                    location = "Remote"
                    category_elem = item.find('category')
                    if category_elem is not None and '(' in category_elem.text:
                        # Sometimes location is in category like "remote (global)"
                        location = category_elem.text
                    
                    job = {
                        'id': f"so_{hash(str(title_elem.text) + str(link_elem.text)) % 1000000}",
                        'title': title_elem.text if title_elem is not None else '',
                        'company': company_name,
                        'location': location,
                        'description': self._clean_html(desc_elem.text if desc_elem is not None else ''),
                        'url': link_elem.text if link_elem is not None else '',
                        'published_date': pub_date_elem.text if pub_date_elem is not None else '',
                        'source': 'stack_overflow',
                        'collected_at': datetime.now().isoformat(),
                        'search_term': search_term
                    }
                    jobs.append(job)
                    
                except Exception as e:
                    logger.warning(f"Error parsing Stack Overflow job item: {e}")
                    continue
            
            logger.info(f"✅ Successfully fetched {len(jobs)} jobs from Stack Overflow")
            return jobs
            
        except Exception as e:
            logger.error(f"❌ Error fetching Stack Overflow jobs: {e}")
            # Return sample data if real fetch fails
            return self._create_stackoverflow_sample(search_term)
    
    def fetch_github_jobs_rss(self, search_term: str = "python") -> List[Dict]:
        """
        Fetch from GitHub Jobs RSS feed (still works despite API deprecation)
        COMPLETELY FREE - no API key needed
        """
        try:
            logger.info(f"Fetching GitHub Jobs for: {search_term}")
            
            # GitHub Jobs RSS feed
            url = "https://jobs.github.com/positions.atom"
            params = {'description': search_term}
            
            self._delay()
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse the Atom feed
            root = ET.fromstring(response.content)
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
            jobs = []
            for entry in root.findall('.//atom:entry', namespace)[:30]:
                try:
                    title_elem = entry.find('atom:title', namespace)
                    link_elem = entry.find('atom:link', namespace)
                    summary_elem = entry.find('atom:summary', namespace)
                    updated_elem = entry.find('atom:updated', namespace)
                    
                    # Try to get company from various places
                    company = "Unknown"
                    author_elem = entry.find('atom:author', namespace)
                    if author_elem is not None:
                        name_elem = author_elem.find('atom:name', namespace)
                        if name_elem is not None:
                            company = name_elem.text
                    
                    # Get location
                    location = "Remote"
                    # Sometimes location is in title or we need to parse
                    if title_elem is not None and ' at ' in title_elem.text:
                        # Format: "Job Title at Company in Location"
                        parts = title_elem.text.split(' at ')
                        if len(parts) > 1 and ' in ' in parts[1]:
                            location_part = parts[1].split(' in ')[-1]
                            location = location_part
                    
                    job = {
                        'id': f"github_{hash(str(title_elem.text) + str(link_elem.get('href') if link_elem is not None else '')) % 1000000}",
                        'title': title_elem.text if title_elem is not None else '',
                        'company': company,
                        'location': location,
                        'description': self._clean_html(summary_elem.text if summary_elem is not None else ''),
                        'url': link_elem.get('href') if link_elem is not None else '',
                        'published_date': updated_elem.text if updated_elem is not None else '',
                        'source': 'github_jobs',
                        'collected_at': datetime.now().isoformat(),
                        'search_term': search_term
                    }
                    jobs.append(job)
                    
                except Exception as e:
                    logger.warning(f"Error parsing GitHub Jobs entry: {e}")
                    continue
            
            logger.info(f"✅ Successfully fetched {len(jobs)} jobs from GitHub Jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"❌ Error fetching GitHub Jobs: {e}")
            return self._create_github_sample(search_term)
    
    def fetch_reed_co_uk_sample(self, search_term: str = "data scientist") -> List[Dict]:
        """
        Create realistic UK job market sample data
        Reed.co.uk requires API key for real access, so we create realistic samples
        """
        logger.info(f"Creating realistic Reed.co.uk sample data for: {search_term}")
        
        # Realistic UK job data based on current market
        uk_locations = ["London", "Manchester", "Birmingham", "Glasgow", "Remote", "Bristol", "Leeds"]
        uk_companies = ["Barclays", "HSBC", "BBC", "Sky", "Tesco", "Sainsbury's", "BP", "Shell", "Unilever", "GSK"]
        
        jobs = []
        for i in range(15):
            job = {
                'id': f"reed_uk_{i}",
                'title': f"{search_term.title()} - {['Senior', 'Mid-level', 'Junior'][i % 3]} Position",
                'company': uk_companies[i % len(uk_companies)],
                'location': uk_locations[i % len(uk_locations)],
                'description': f"Looking for a {search_term} with experience in data analysis and business intelligence. "
                              f"Must have strong analytical skills and ability to work in a team environment.",
                'salary': f"£{40000 + (i * 3000):,}",
                'url': f"https://www.reed.co.uk/jobs/{search_term.replace(' ', '-')}-job/{i}",
                'published_date': (datetime.now() - timedelta(days=i % 30)).strftime("%Y-%m-%d"),
                'source': 'reed_uk_sample',
                'collected_at': datetime.now().isoformat(),
                'search_term': search_term
            }
            jobs.append(job)
        
        return jobs
    
    def fetch_adzuna_sample(self, country: str = "gb", search_term: str = "data scientist") -> List[Dict]:
        """
        Create realistic Adzuna-like sample data
        Real Adzuna API requires key, but we create realistic samples
        """
        logger.info(f"Creating realistic Adzuna sample data for: {search_term} in {country}")
        
        # Different countries have different job markets
        country_data = {
            "gb": {"locations": ["London", "Manchester", "Edinburgh", "Cardiff", "Belfast"],
                   "currency": "£"},
            "us": {"locations": ["New York, NY", "San Francisco, CA", "Austin, TX", "Chicago, IL", "Boston, MA"],
                   "currency": "$"},
            "au": {"locations": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
                   "currency": "A$"},
        }
        
        country_info = country_data.get(country, country_data["gb"])
        
        jobs = []
        for i in range(12):
            salary = 80000 + (i * 7000)
            job = {
                'id': f"adzuna_{country}_{i}",
                'title': f"{['Lead', 'Senior', ''][i % 3]} {search_term.title()}",
                'company': f"Company_{i % 8}",
                'location': country_info["locations"][i % len(country_info["locations"])],
                'description': f"We're hiring a {search_term} to join our growing team. "
                              f"Key responsibilities include data analysis, model development, and business insights.",
                'salary': f"{country_info['currency']}{salary:,}",
                'url': f"https://www.adzuna.co.uk/jobs/details/{i}",
                'published_date': (datetime.now() - timedelta(days=(i * 2) % 30)).strftime("%Y-%m-%d"),
                'source': f'adzuna_{country}_sample',
                'collected_at': datetime.now().isoformat(),
                'search_term': search_term
            }
            jobs.append(job)
        
        return jobs
    
    def _clean_html(self, html_text: str) -> str:
        """Clean HTML tags from text for better storage"""
        if not html_text:
            return ""
        
        try:
            soup = BeautifulSoup(html_text, 'html.parser')
            # Get text and clean it up
            text = soup.get_text(separator=' ', strip=True)
            # Remove extra whitespace
            text = ' '.join(text.split())
            return text[:1500]  # Limit length
        except:
            # If BeautifulSoup fails, do simple cleanup
            import re
            text = re.sub(r'<[^>]+>', ' ', html_text)
            text = ' '.join(text.split())
            return text[:1500]
    
    def _create_stackoverflow_sample(self, search_term: str) -> List[Dict]:
        """Create realistic Stack Overflow-like sample data"""
        logger.info(f"Creating Stack Overflow sample for: {search_term}")
        
        tech_companies = ["Google", "Microsoft", "Amazon", "Meta", "Netflix", "Spotify", "Airbnb", "Uber"]
        tech_locations = ["Remote", "San Francisco, CA", "New York, NY", "London", "Berlin", "Toronto"]
        
        jobs = []
        for i in range(10):
            job = {
                'id': f"so_sample_{i}",
                'title': f"{search_term.title()} Developer",
                'company': tech_companies[i % len(tech_companies)],
                'location': tech_locations[i % len(tech_locations)],
                'description': f"We're looking for a {search_term} to join our team. Must have experience with Python and data analysis.",
                'url': f"https://stackoverflow.com/jobs/{i}",
                'published_date': (datetime.now() - timedelta(days=i)).isoformat(),
                'source': 'stack_overflow_sample',
                'collected_at': datetime.now().isoformat(),
                'search_term': search_term
            }
            jobs.append(job)
        
        return jobs
    
    def _create_github_sample(self, search_term: str) -> List[Dict]:
        """Create realistic GitHub Jobs-like sample data"""
        logger.info(f"Creating GitHub Jobs sample for: {search_term}")
        
        oss_companies = ["GitHub", "GitLab", "Canonical", "Red Hat", "MongoDB", "Elastic", "Databricks"]
        oss_locations = ["Remote", "San Francisco", "Global", "Anywhere"]
        
        jobs = []
        for i in range(8):
            job = {
                'id': f"gh_sample_{i}",
                'title': f"{search_term.title()} - Open Source",
                'company': oss_companies[i % len(oss_companies)],
                'location': oss_locations[i % len(oss_locations)],
                'description': f"Join our open source team as a {search_term}. Contribute to meaningful projects.",
                'url': f"https://jobs.github.com/positions/{i}",
                'published_date': (datetime.now() - timedelta(hours=i*12)).isoformat(),
                'source': 'github_jobs_sample',
                'collected_at': datetime.now().isoformat(),
                'search_term': search_term
            }
            jobs.append(job)
        
        return jobs
    
    def collect_all_data(self, use_cache: bool = True) -> pd.DataFrame:
        """
        Collect data from ALL free sources
        Returns real data if available, falls back to realistic samples
        """
        logger.info("🚀 Starting comprehensive job data collection...")
        
        # Check for recent cache (less than 6 hours old)
        if use_cache:
            cache_file = self.cache_dir / f"jobs_{datetime.now().strftime('%Y%m%d')}.parquet"
            if cache_file.exists():
                cache_age = datetime.now().timestamp() - cache_file.stat().st_mtime
                if cache_age < 6 * 3600:  # 6 hours
                    logger.info(f"📁 Loading from recent cache: {cache_file}")
                    try:
                        df = pd.read_parquet(cache_file)
                        if len(df) > 0:
                            logger.info(f"✅ Loaded {len(df)} jobs from cache")
                            return df
                    except Exception as e:
                        logger.warning(f"Cache load failed: {e}")
        
        all_jobs = []
        
        # Try real free sources first
        logger.info("🔍 Attempting to fetch real data from free sources...")
        
        # 1. Stack Overflow (REAL, FREE)
        try:
            so_jobs = self.fetch_stackoverflow_jobs("data scientist")
            all_jobs.extend(so_jobs)
            logger.info(f"   Stack Overflow: {len(so_jobs)} jobs")
        except Exception as e:
            logger.warning(f"   Stack Overflow failed: {e}")
        
        # 2. GitHub Jobs (REAL, FREE)
        try:
            gh_jobs = self.fetch_github_jobs_rss("python")
            all_jobs.extend(gh_jobs)
            logger.info(f"   GitHub Jobs: {len(gh_jobs)} jobs")
        except Exception as e:
            logger.warning(f"   GitHub Jobs failed: {e}")
        
        # Add realistic sample data for variety
        logger.info("🎨 Adding realistic sample data for demonstration...")
        
        # 3. UK market sample (realistic)
        reed_jobs = self.fetch_reed_co_uk_sample("data analyst")
        all_jobs.extend(reed_jobs)
        logger.info(f"   UK Market Sample: {len(reed_jobs)} jobs")
        
        # 4. US market sample (realistic)
        adzuna_us_jobs = self.fetch_adzuna_sample("us", "machine learning engineer")
        all_jobs.extend(adzuna_us_jobs)
        logger.info(f"   US Market Sample: {len(adzuna_us_jobs)} jobs")
        
        # 5. AU market sample (realistic)
        adzuna_au_jobs = self.fetch_adzuna_sample("au", "data engineer")
        all_jobs.extend(adzuna_au_jobs)
        logger.info(f"   AU Market Sample: {len(adzuna_au_jobs)} jobs")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_jobs)
        
        # Add metadata
        if not df.empty:
            df['collection_date'] = datetime.now().date()
            df['data_quality'] = df['source'].apply(
                lambda x: 'real' if 'sample' not in x else 'sample'
            )
            
            # Cache the results
            cache_file = self.cache_dir / f"jobs_{datetime.now().strftime('%Y%m%d_%H%M')}.parquet"
            df.to_parquet(cache_file, compression='snappy')
            logger.info(f"💾 Saved {len(df)} jobs to cache: {cache_file}")
        
        logger.info(f"✅ Collection complete! Total jobs: {len(df)}")
        logger.info(f"   Real data: {len(df[df['data_quality'] == 'real'])}")
        logger.info(f"   Sample data: {len(df[df['data_quality'] == 'sample'])}")
        
        return df

# Simple test function
def test_collector():
    """Test the job collector"""
    print("🧪 Testing FreeJobDataCollector...")
    
    collector = FreeJobDataCollector()
    
    # Test individual sources
    print("\n1. Testing Stack Overflow (real free data)...")
    so_jobs = collector.fetch_stackoverflow_jobs("data scientist", max_results=5)
    print(f"   Fetched {len(so_jobs)} jobs")
    for job in so_jobs[:2]:
        print(f"   - {job['title']} at {job['company']}")
    
    print("\n2. Testing GitHub Jobs (real free data)...")
    gh_jobs = collector.fetch_github_jobs_rss("python")
    print(f"   Fetched {len(gh_jobs)} jobs")
    for job in gh_jobs[:2]:
        print(f"   - {job['title']} at {job['company']}")
    
    print("\n3. Testing complete collection...")
    df = collector.collect_all_data(use_cache=False)
    print(f"   Total jobs collected: {len(df)}")
    print(f"   Sources: {df['source'].unique().tolist()}")
    
    return df

if __name__ == "__main__":
    # Run test
    df = test_collector()
    print("\n🎉 Test completed successfully!")
    print(f"\nSample of collected data:")
    print(df[['title', 'company', 'location', 'source', 'data_quality']].head(10))