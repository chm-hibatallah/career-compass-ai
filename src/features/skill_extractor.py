"""
Skill extraction from job descriptions
"""
import re
from typing import List, Set, Dict
import pandas as pd
from collections import Counter


class SkillExtractor:
    """Extract and normalize skills from job descriptions"""
    
    def __init__(self):
        # Custom skill ontology - THIS IS WHERE YOU ADD VALUE
        self.skill_ontology = {
            # Programming Languages
            "python": ["python", "python3", "python 3", "py"],
            "r": ["r", "r language", "r programming"],
            "java": ["java", "java 8", "java 11", "java 17"],
            "javascript": ["javascript", "js", "es6", "node.js"],
            "sql": ["sql", "postgresql", "mysql", "sqlite", "nosql"],
            
            # Data Science & ML
            "machine learning": ["machine learning", "ml", "ai", "artificial intelligence"],
            "deep learning": ["deep learning", "neural networks", "cnn", "rnn"],
            "tensorflow": ["tensorflow", "tf"],
            "pytorch": ["pytorch", "torch"],
            "scikit-learn": ["scikit-learn", "sklearn"],
            
            # Data Engineering
            "spark": ["spark", "apache spark", "pyspark"],
            "hadoop": ["hadoop", "hdfs", "mapreduce"],
            "airflow": ["airflow", "apache airflow"],
            "kafka": ["kafka", "apache kafka"],
            
            # Cloud & DevOps
            "aws": ["aws", "amazon web services", "s3", "ec2", "lambda"],
            "docker": ["docker", "containerization"],
            "kubernetes": ["kubernetes", "k8s"],
            "terraform": ["terraform", "iac"],
            
            # Soft Skills
            "communication": ["communication", "communicate", "presentation"],
            "leadership": ["leadership", "lead", "mentor"],
            "problem solving": ["problem solving", "critical thinking"],
        }
        
        # Reverse mapping for quick lookup
        self.skill_mapping = {}
        for canonical, variants in self.skill_ontology.items():
            for variant in variants:
                self.skill_mapping[variant] = canonical
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using ontology"""
        if not isinstance(text, str):
            return []
        
        text_lower = text.lower()
        found_skills = set()
        
        # Look for skills in ontology
        for variant, canonical in self.skill_mapping.items():
            if re.search(r'\b' + re.escape(variant) + r'\b', text_lower):
                found_skills.add(canonical)
        
        return list(found_skills)
    
    def extract_skills_from_dataframe(self, df: pd.DataFrame, text_column: str = "description") -> pd.DataFrame:
        """Extract skills for all job postings"""
        print(f"Extracting skills from {len(df)} job postings...")
        
        # Extract skills
        df["extracted_skills"] = df[text_column].apply(self.extract_skills)
        
        # Combine with existing skills if available
        if "skills" in df.columns:
            df["all_skills"] = df.apply(
                lambda row: list(set(row["skills"] + row["extracted_skills"])) 
                if isinstance(row["skills"], list) 
                else row["extracted_skills"],
                axis=1
            )
        else:
            df["all_skills"] = df["extracted_skills"]
        
        # Create skill frequency analysis
        all_skills_flat = [skill for skills in df["all_skills"] for skill in skills]
        skill_freq = Counter(all_skills_flat)
        
        print(f"Found {len(skill_freq)} unique skills")
        print(f"Top 10 skills: {skill_freq.most_common(10)}")
        
        return df, skill_freq
    
    def get_skill_categories(self) -> Dict[str, List[str]]:
        """Get skills grouped by category for visualization"""
        categories = {}
        for skill, variants in self.skill_ontology.items():
            # Simple category assignment based on skill type
            if skill in ["python", "r", "java", "javascript", "sql"]:
                category = "Programming"
            elif skill in ["machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn"]:
                category = "ML/AI"
            elif skill in ["spark", "hadoop", "airflow", "kafka"]:
                category = "Data Engineering"
            elif skill in ["aws", "docker", "kubernetes", "terraform"]:
                category = "Cloud/DevOps"
            else:
                category = "Soft Skills"
            
            if category not in categories:
                categories[category] = []
            categories[category].append(skill)
        
        return categories


if __name__ == "__main__":
    # Test the skill extractor
    extractor = SkillExtractor()
    
    test_text = "Looking for a Data Scientist with Python, SQL, and machine learning experience. AWS and Docker knowledge is a plus."
    
    skills = extractor.extract_skills(test_text)
    print(f"Extracted skills: {skills}")