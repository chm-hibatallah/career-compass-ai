"""
Data quality and validation pipeline
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataQualityChecker:
    """Ensure data quality and consistency"""
    
    def __init__(self):
        self.quality_metrics = {}
        
    def check_dataframe(self, df: pd.DataFrame) -> Dict:
        """Run comprehensive data quality checks"""
        logger.info("Running data quality checks...")
        
        metrics = {
            'total_records': len(df),
            'columns': list(df.columns),
            'missing_values': {},
            'duplicates': 0,
            'data_types': {},
            'unique_counts': {},
            'quality_score': 0
        }
        
        # Check for missing values
        for col in df.columns:
            missing = df[col].isnull().sum()
            missing_pct = (missing / len(df)) * 100
            metrics['missing_values'][col] = {
                'count': int(missing),
                'percentage': float(missing_pct)
            }
        
        # Check for duplicates
        duplicates = df.duplicated(subset=['id', 'title', 'company']).sum()
        metrics['duplicates'] = int(duplicates)
        
        # Check data types
        for col in df.columns:
            metrics['data_types'][col] = str(df[col].dtype)
        
        # Check unique values for categorical columns
        categorical_cols = ['source', 'location', 'company']
        for col in categorical_cols:
            if col in df.columns:
                metrics['unique_counts'][col] = int(df[col].nunique())
        
        # Calculate quality score (0-100)
        quality_score = 100
        
        # Penalize for missing values
        total_missing_pct = sum(m['percentage'] for m in metrics['missing_values'].values()) / len(metrics['missing_values'])
        quality_score -= total_missing_pct * 0.5
        
        # Penalize for duplicates
        duplicate_pct = (metrics['duplicates'] / len(df)) * 100
        quality_score -= duplicate_pct
        
        # Ensure score is between 0 and 100
        quality_score = max(0, min(100, quality_score))
        metrics['quality_score'] = round(quality_score, 2)
        
        self.quality_metrics = metrics
        self._log_quality_report(metrics)
        
        return metrics
    
    def _log_quality_report(self, metrics: Dict):
        """Log quality report"""
        logger.info("=" * 50)
        logger.info("📊 DATA QUALITY REPORT")
        logger.info("=" * 50)
        logger.info(f"Total Records: {metrics['total_records']:,}")
        logger.info(f"Quality Score: {metrics['quality_score']}/100")
        logger.info(f"Duplicates: {metrics['duplicates']:,}")
        
        logger.info("\n🔍 Missing Values:")
        for col, stats in metrics['missing_values'].items():
            if stats['percentage'] > 5:  # Highlight significant missing values
                logger.warning(f"  {col}: {stats['percentage']:.1f}% missing ({stats['count']:,})")
        
        logger.info("\n📈 Unique Counts:")
        for col, count in metrics['unique_counts'].items():
            logger.info(f"  {col}: {count:,} unique values")
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the dataframe"""
        logger.info("Cleaning dataframe...")
        
        # Create a copy
        df_clean = df.copy()
        
        # Remove exact duplicates
        initial_count = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['id', 'title', 'company'], keep='first')
        logger.info(f"Removed {initial_count - len(df_clean)} exact duplicates")
        
        # Fill missing values
        if 'location' in df_clean.columns:
            df_clean['location'] = df_clean['location'].fillna('Remote')
        
        if 'description' in df_clean.columns:
            df_clean['description'] = df_clean['description'].fillna('')
        
        # Standardize text columns
        text_columns = ['title', 'company', 'location']
        for col in text_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()
        
        # Parse dates
        date_columns = ['created_at', 'posted_date', 'published']
        for col in date_columns:
            if col in df_clean.columns:
                try:
                    df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                except:
                    pass
        
        # Add derived columns
        if 'description' in df_clean.columns:
            df_clean['description_length'] = df_clean['description'].str.len()
            df_clean['has_description'] = df_clean['description_length'] > 10
        
        # Filter out low-quality entries
        df_clean = df_clean[
            (df_clean['title'].str.len() > 3) &
            (df_clean['company'].str.len() > 2)
        ]
        
        logger.info(f"Cleaned dataframe: {len(df_clean):,} rows ({len(df) - len(df_clean):,} removed)")
        
        return df_clean
    
    def generate_data_profile(self, df: pd.DataFrame) -> Dict:
        """Generate comprehensive data profile"""
        profile = {
            'summary': {
                'total_jobs': len(df),
                'date_range': {},
                'sources_distribution': {},
                'location_distribution': {}
            },
            'temporal_analysis': {},
            'text_analysis': {}
        }
        
        # Date range
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'created' in col.lower()]
        for col in date_cols:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                profile['summary']['date_range'][col] = {
                    'min': df[col].min().strftime('%Y-%m-%d') if not pd.isna(df[col].min()) else None,
                    'max': df[col].max().strftime('%Y-%m-%d') if not pd.isna(df[col].max()) else None
                }
        
        # Source distribution
        if 'source' in df.columns:
            source_counts = df['source'].value_counts().head(10).to_dict()
            profile['summary']['sources_distribution'] = source_counts
        
        # Location distribution
        if 'location' in df.columns:
            location_counts = df['location'].value_counts().head(15).to_dict()
            profile['summary']['location_distribution'] = location_counts
        
        return profile