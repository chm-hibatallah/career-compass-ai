"""
Career Compass AI - Main Application Package
"""
__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Make key components available at package level
from app.main import main
from app.components.dashboard import DashboardComponents

__all__ = ['main', 'DashboardComponents']