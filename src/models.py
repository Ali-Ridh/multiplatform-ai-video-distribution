#!/usr/bin/env python3
"""
Database models for Opus system
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base

class User(Base):
    """User model for system administration"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    accounts = relationship("Account", back_populates="user")

class Account(Base):
    """Social media account configuration"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(20), nullable=False)  # 'tiktok', 'youtube', 'instagram'
    username = Column(String(100), nullable=False)
    access_token = Column(String(500), nullable=False)
    refresh_token = Column(String(500))
    client_id = Column(String(255))
    client_secret = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    proxy_config = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="accounts")
    videos = relationship("Video", back_populates="account")
    analytics = relationship("Analytics", back_populates="account")

class Video(Base):
    """Processed video data"""
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    original_url = Column(String(500))
    original_path = Column(String(500), nullable=False)
    processed_path = Column(String(500))
    duration = Column(Float)
    title = Column(String(500))
    description = Column(Text)
    thumbnail_path = Column(String(500))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    status = Column(String(20), default="pending")  # 'pending', 'processing', 'completed', 'failed'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    account = relationship("Account", back_populates="videos")
    analytics = relationship("Analytics", back_populates="video")
    renditions = relationship("VideoRendition", back_populates="video")
    segments = relationship("VideoSegment", back_populates="video")

class VideoRendition(Base):
    """Video variations (rendered versions for each platform)"""
    __tablename__ = "video_renditions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    platform = Column(String(20), nullable=False)  # 'tiktok', 'youtube', 'instagram'
    file_path = Column(String(500), nullable=False)
    resolution = Column(String(20))  # '1080x1920', '720x1280'
    format = Column(String(10))  # 'mp4', 'mov'
    bitrate = Column(Integer)
    size = Column(Integer)  # in bytes
    created_at = Column(DateTime, default=datetime.utcnow)
    
    video = relationship("Video", back_populates="renditions")

class VideoSegment(Base):
    """Viral segments detected in videos"""
    __tablename__ = "video_segments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    duration = Column(Float)
    confidence_score = Column(Float)
    reason = Column(Text)
    selected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    video = relationship("Video", back_populates="segments")

class Analytics(Base):
    """Video analytics data"""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    platform = Column(String(20), nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    posted_at = Column(DateTime)
    last_scraped = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    video = relationship("Video", back_populates="analytics")
    account = relationship("Account", back_populates="analytics")

class Task(Base):
    """Background task tracking"""
    __tablename__ = "tasks"
    
    id = Column(String(100), primary_key=True)
    task_type = Column(String(50), nullable=False)  # 'process', 'render', 'upload', 'analytics'
    status = Column(String(20), default="pending")  # 'pending', 'running', 'completed', 'failed'
    video_id = Column(Integer, ForeignKey("videos.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    result = Column(Text)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    video = relationship("Video")
    account = relationship("Account")

class Schedule(Base):
    """Video upload schedule"""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    platform = Column(String(20), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String(20), default="pending")  # 'pending', 'processed', 'failed'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    video = relationship("Video")
    account = relationship("Account")

class Proxy(Base):
    """Proxy server configuration"""
    __tablename__ = "proxies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(255), nullable=False)  # 'http://192.168.1.1:8080'
    username = Column(String(50))
    password = Column(String(50))
    country = Column(String(50))
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
