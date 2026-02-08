import os 
from pathlib import Path 
 
BASE_DIR = Path(__file__).resolve().parent.parent 
DATA_DIR = BASE_DIR / "data" 
LOG_DIR = BASE_DIR / "logs" 
 
for dir_path in [DATA_DIR, LOG_DIR]: 
    dir_path.mkdir(exist_ok=True) 
 
class Settings: 
    APP_NAME = "Career Compass AI" 
    VERSION = "1.0.0" 
    DEBUG = os.getenv("DEBUG", "True").lower() == "true" 
    ENABLE_REAL_API_CALLS = False 
    DEFAULT_HOURS_PER_WEEK = 10 
    DEFAULT_TIMELINE_MONTHS = 6 
 
settings = Settings() 
