# src/database/models.py

from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Float, Text, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

# Association table for many-to-many relationship between jobs and skills
job_skills = Table('job_skills', Base.metadata,
    Column('job_id', Integer, ForeignKey('jobs.id')),
    Column('skill_id', Integer, ForeignKey('skills.id'))
)

# Association table for many-to-many relationship between users and skills
user_skills = Table('user_skills', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('skill_id', Integer, ForeignKey('skills.id'))
)

class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    external_id = Column(String, unique=True)  # ID from the source
    title = Column(String)
    company = Column(String)
    location = Column(String)
    description = Column(Text)
    posted_date = Column(DateTime)
    salary_range = Column(String)
    experience_level = Column(String)
    source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    skills = relationship("Skill", secondary=job_skills, back_populates="jobs")

class Skill(Base):
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    category = Column(String)
    description = Column(Text)
    
    jobs = relationship("Job", secondary=job_skills, back_populates="skills")
    users = relationship("User", secondary=user_skills, back_populates="skills")
    trends = relationship("SkillTrend", back_populates="skill")

class Company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    industry = Column(String)
    size = Column(String)
    tech_stack = Column(JSON)  # List of skills

class SkillTrend(Base):
    __tablename__ = 'skill_trends'
    
    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey('skills.id'))
    date = Column(DateTime)
    demand_score = Column(Float)  # Normalized demand (e.g., percentage of job postings)
    
    skill = relationship("Skill", back_populates="trends")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String)
    linkedin_id = Column(String, unique=True)
    github_id = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    skills = relationship("Skill", secondary=user_skills, back_populates="users")
    learning_paths = relationship("LearningPath", back_populates="user")

class LearningPath(Base):
    __tablename__ = 'learning_paths'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    skill_id = Column(Integer, ForeignKey('skills.id'))
    target_level = Column(String)  # beginner, intermediate, advanced
    current_level = Column(String)
    start_date = Column(DateTime)
    target_date = Column(DateTime)
    
    user = relationship("User", back_populates="learning_paths")
    skill = relationship("Skill")

# Create the database engine
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./career_compass.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)