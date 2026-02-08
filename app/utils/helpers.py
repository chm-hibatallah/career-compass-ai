"""
Utility functions for the application
"""
import json
import yaml
import pickle
import hashlib
from typing import Any, Dict, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

def cache_data(data: Any, key: str, expiration_hours: int = 24) -> None:
    """Cache data to Streamlit session state"""
    if 'cache' not in st.session_state:
        st.session_state.cache = {}
    
    cache_entry = {
        'data': data,
        'timestamp': datetime.now(),
        'expires': datetime.now() + timedelta(hours=expiration_hours)
    }
    st.session_state.cache[key] = cache_entry

def get_cached_data(key: str) -> Any:
    """Get cached data if not expired"""
    if 'cache' not in st.session_state:
        return None
    
    if key not in st.session_state.cache:
        return None
    
    cache_entry = st.session_state.cache[key]
    
    if datetime.now() > cache_entry['expires']:
        del st.session_state.cache[key]
        return None
    
    return cache_entry['data']

def calculate_hash(data: Any) -> str:
    """Calculate hash of data for caching"""
    if isinstance(data, pd.DataFrame):
        data_str = data.to_string()
    elif isinstance(data, dict):
        data_str = json.dumps(data, sort_keys=True)
    else:
        data_str = str(data)
    
    return hashlib.md5(data_str.encode()).hexdigest()

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division with default value on zero denominator"""
    if denominator == 0:
        return default
    return numerator / denominator

def format_currency(amount: float) -> str:
    """Format number as currency"""
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount/1_000:.1f}K"
    else:
        return f"${amount:,.0f}"

def format_percentage(value: float) -> str:
    """Format as percentage"""
    return f"{value:.1f}%"

def create_progress_bar(value: float, total: float = 100) -> str:
    """Create a text-based progress bar"""
    width = 20
    filled = int((value / total) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"|{bar}| {value:.1f}%"

def load_yaml_file(filepath: Path) -> Dict:
    """Load YAML file"""
    try:
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}

def save_yaml_file(data: Dict, filepath: Path) -> None:
    """Save data to YAML file"""
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

def get_color_for_score(score: float) -> str:
    """Get color based on score (0-100)"""
    if score >= 80:
        return "#10B981"  # Green
    elif score >= 60:
        return "#F59E0B"  # Yellow
    elif score >= 40:
        return "#EF4444"  # Red
    else:
        return "#6B7280"  # Gray

def validate_user_input(user_data: Dict) -> List[str]:
    """Validate user input and return error messages"""
    errors = []
    
    if 'skills' in user_data and not user_data['skills']:
        errors.append("Please add at least one skill")
    
    if 'target_role' in user_data and not user_data['target_role']:
        errors.append("Please select a target role")
    
    return errors

def time_it(func):
    """Decorator to measure execution time"""
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result
    return wrapper