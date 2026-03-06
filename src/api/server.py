#!/usr/bin/env python3
"""
FastAPI Backend Server

Provides RESTful API for the Opus dashboard
"""

import os
import logging
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Opus API",
    description="API for Opus Video Pipeline",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (Next.js build output)
static_dir = os.getenv("STATIC_DIR", "./frontend")
if os.path.exists(static_dir):
    # Check if we have an export directory (production) or just the source (development)
    out_dir = os.path.join(static_dir, "out")
    if os.path.exists(out_dir):
        from fastapi.responses import FileResponse
        
        # Serve Next.js static files
        app.mount("/_next", StaticFiles(directory=os.path.join(out_dir, "_next")), name="next_static")
        
        # Serve index.html for root path
        @app.get("/")
        async def serve_index():
            index_path = os.path.join(out_dir, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
            raise HTTPException(status_code=404, detail="Index not found")
    else:
        logger.warning("Frontend export directory not found, skipping static file serving")

# Initialize Opus engine
from src.opus import Opus
opus = Opus()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/process")
async def process_video(url: str):
    """
    Process a video from URL
    
    Args:
        url: Video URL to process
        
    Returns:
        Processing status
    """
    try:
        logger.info(f"Processing video: {url}")
        
        from src.worker.tasks import process_video_task
        task = process_video_task.delay(url)
        
        return {
            "success": True,
            "task_id": task.id,
            "message": "Video processing started"
        }
        
    except Exception as e:
        logger.error(f"Process video failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Get task status
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Task status and result
    """
    try:
        from src.worker.celery_app import app as celery_app
        from celery.result import AsyncResult
        
        result = AsyncResult(task_id, app=celery_app)
        
        response = {
            "task_id": task_id,
            "status": result.status,
            "result": None
        }
        
        if result.successful():
            response["result"] = result.result
        elif result.failed():
            response["error"] = str(result.result)
            
        return response
        
    except Exception as e:
        logger.error(f"Get task status failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Upload video file
    
    Args:
        file: Video file to upload
        
    Returns:
        Upload status
    """
    try:
        logger.info(f"Uploading file: {file.filename}")
        
        upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as f:
            f.write(await file.read())
            
        logger.info(f"File saved: {file_path}")
        
        # Save to database so it appears in the gallery
        from src.database import get_db
        from src.models import Video
        
        db = next(get_db())
        new_video = Video(
            original_url="",
            original_path=file_path,
            title=file.filename,
            status="completed"
        )
        db.add(new_video)
        db.commit()
        db.refresh(new_video)
        
        return {
            "success": True,
            "video": {
                "id": str(new_video.id),
                "filename": new_video.title,
                "path": new_video.original_path,
                "views": 0,
                "likes": 0,
                "created_at": new_video.created_at.isoformat() if new_video.created_at else None
            },
            "message": "File uploaded and saved to database successfully"
        }
        
    except Exception as e:
        logger.error(f"Upload video failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/videos")
async def list_videos():
    """
    List processed videos
    
    Returns:
        List of processed videos
    """
    try:
        from src.database import get_db
        from src.models import Video, Analytics
        from sqlalchemy import func
        
        db = next(get_db())
        
        # Query all videos and calculate their total views and likes across platforms
        videos = db.query(Video).all()
        response_videos = []
        
        for video in videos:
            views = db.query(func.sum(Analytics.views)).filter(Analytics.video_id == video.id).scalar() or 0
            likes = db.query(func.sum(Analytics.likes)).filter(Analytics.video_id == video.id).scalar() or 0
            
            response_videos.append({
                "id": str(video.id),
                "filename": video.title or f"Video {video.id}",
                "path": video.processed_path or video.original_url,
                "size": 0,
                "created_at": video.created_at.isoformat() if video.created_at else None,
                "modified_at": video.updated_at.isoformat() if video.updated_at else None,
                "views": views,
                "likes": likes
            })
                
        # Sort by views descending to show top videos
        response_videos.sort(key=lambda x: x["views"], reverse=True)
                
        return {
            "success": True,
            "videos": response_videos
        }
        
    except Exception as e:
        logger.error(f"List videos failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/videos/{filename}")
async def get_video(filename: str):
    """
    Get video details
    
    Args:
        filename: Video filename
        
    Returns:
        Video details
    """
    try:
        processed_dir = os.path.join(os.getenv("OUTPUT_DIR", "./output"), "processed")
        file_path = os.path.join(processed_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Video not found")
            
        stat = os.stat(file_path)
        
        return {
            "success": True,
            "filename": filename,
            "path": file_path,
            "size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get video failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/render")
async def render_videos(video_path: str, variations: int = Query(3, ge=1, le=10)):
    """
    Render video variations
    
    Args:
        video_path: Path to video file
        variations: Number of variations to generate
        
    Returns:
        Rendering status
    """
    try:
        logger.info(f"Rendering {variations} variations of: {video_path}")
        
        from src.worker.tasks import render_video_task
        task = render_video_task.delay(video_path, variations)
        
        return {
            "success": True,
            "task_id": task.id,
            "message": f"Rendering {variations} variations started"
        }
        
    except Exception as e:
        logger.error(f"Render videos failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-video")
async def upload_processed_video(video_path: str, platform: str = Query("all")):
    """
    Upload video to platforms
    
    Args:
        video_path: Path to video file
        platform: Platform to upload to
        
    Returns:
        Upload status
    """
    try:
        logger.info(f"Uploading to {platform}: {video_path}")
        
        from src.worker.tasks import upload_video_task
        task = upload_video_task.delay(video_path, platform)
        
        return {
            "success": True,
            "task_id": task.id,
            "message": f"Upload to {platform} started"
        }
        
    except Exception as e:
        logger.error(f"Upload video failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schedule")
async def schedule_upload(
    video_path: str,
    platform: str,
    schedule_time: str,
    account_id: Optional[str] = None
):
    """
    Schedule video upload
    
    Args:
        video_path: Path to video file
        platform: Platform to upload to
        schedule_time: ISO datetime string
        account_id: Optional account identifier
        
    Returns:
        Scheduled task information
    """
    try:
        logger.info(f"Scheduling upload for {schedule_time}: {video_path}")
        
        from datetime import datetime
        from src.worker.tasks import schedule_video_upload_task
        
        # Parse schedule time
        scheduled_datetime = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
        
        task = schedule_video_upload_task.delay(
            video_path,
            platform,
            scheduled_datetime.isoformat(),
            account_id
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "scheduled_time": schedule_time,
            "message": f"Upload scheduled for {schedule_time}"
        }
        
    except Exception as e:
        logger.error(f"Schedule upload failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/accounts")
async def get_accounts():
    """
    Get all connected accounts
    
    Returns:
        List of connected accounts
    """
    try:
        from src.database import get_db
        from src.models import Account, Video, Analytics
        from sqlalchemy import func
        
        db = next(get_db())
        accounts = db.query(Account).all()
        
        response_accounts = []
        for account in accounts:
            # Calculate videos count
            posts = db.query(Video).filter(Video.account_id == account.id).count()
            
            # Calculate total views
            views = db.query(func.sum(Analytics.views)).filter(Analytics.account_id == account.id).scalar() or 0
            
            # Calculate engagement (likes + comments) / views * 100
            likes = db.query(func.sum(Analytics.likes)).filter(Analytics.account_id == account.id).scalar() or 0
            comments = db.query(func.sum(Analytics.comments)).filter(Analytics.account_id == account.id).scalar() or 0
            
            engagement = 0.0
            if views > 0:
                engagement = round(((likes + comments) / views) * 100, 2)
                
            response_accounts.append({
                "id": account.id,
                "platform": account.platform,
                "username": account.username,
                "status": "Active" if account.is_active else "Inactive",
                "posts": posts,
                "views": views,
                "engagement": engagement
            })
            
        return {
            "success": True,
            "accounts": response_accounts
        }
        
    except Exception as e:
        logger.error(f"Get accounts failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

import secrets
import urllib.parse
from fastapi.responses import RedirectResponse
import httpx

# OAuth2 Configuration (should ideally come from env vars)
OAUTH_CONFIG = {
    "tiktok": {
        "client_key": os.getenv("TIKTOK_CLIENT_KEY", "placeholder_tiktok_key"),
        "client_secret": os.getenv("TIKTOK_CLIENT_SECRET", "placeholder_tiktok_secret"),
        "auth_url": "https://www.tiktok.com/v2/auth/authorize/",
        "token_url": "https://open.tiktokapis.com/v2/oauth/token/",
        "scopes": "user.info.basic,video.upload,video.publish"
    },
    "youtube": {
        "client_id": os.getenv("YOUTUBE_CLIENT_ID", "placeholder_youtube_id"),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET", "placeholder_youtube_secret"),
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": "https://www.googleapis.com/auth/youtube.upload"
    },
    "instagram": {
        "client_id": os.getenv("INSTAGRAM_CLIENT_ID", "placeholder_instagram_id"),
        "client_secret": os.getenv("INSTAGRAM_CLIENT_SECRET", "placeholder_instagram_secret"),
        "auth_url": "https://api.instagram.com/oauth/authorize",
        "token_url": "https://api.instagram.com/oauth/access_token",
        "scopes": "instagram_basic,instagram_content_publish"
    }
}

REDIRECT_URI = "http://localhost:8000/api/accounts/callback"

@app.get("/api/accounts/auth")
async def get_oauth_url(platform: str):
    """
    Generate the OAuth2 Authorization URL for a specific platform.
    """
    platform = platform.lower()
    if platform not in OAUTH_CONFIG:
        raise HTTPException(status_code=400, detail="Unsupported platform")
        
    config = OAUTH_CONFIG[platform]
    state = secrets.token_urlsafe(16)
    
    # Store state somewhere secure in a real app (e.g. Redis or signed cookie) to prevent CSRF
    
    params = {}
    if platform == "tiktok":
        code_verifier = secrets.token_urlsafe(32)
        import hashlib
        import base64
        digest = hashlib.sha256(code_verifier.encode('ascii')).digest()
        code_challenge = base64.urlsafe_b64encode(digest).decode('ascii').rstrip('=')
        
        params = {
            "client_key": config["client_key"],
            "response_type": "code",
            "scope": config["scopes"],
            "redirect_uri": REDIRECT_URI,
            "state": f"{platform}:{state}:{code_verifier}",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
    else:
        # Standard OAuth2 (Google, Instagram)
        params = {
            "client_id": config.get("client_id", ""),
            "response_type": "code",
            "scope": config["scopes"],
            "redirect_uri": REDIRECT_URI,
            "state": f"{platform}:{state}"
        }
        
        if platform == "youtube":
            params["access_type"] = "offline" # Required for refresh token Google
            params["prompt"] = "consent"
            
    auth_url = f"{config['auth_url']}?{urllib.parse.urlencode(params)}"
    return {"success": True, "auth_url": auth_url}

@app.get("/api/accounts/callback")
async def oauth_callback(code: str, state: str, error: str = None):
    """
    Handle the OAuth2 callback from platforms, exchange code for tokens, and save the account.
    """
    if error:
        return RedirectResponse(url=f"http://localhost:3000?error={error}")
        
    if not code or not state:
        return RedirectResponse(url="http://localhost:3000?error=missing_parameters")
        
    # Extract platform from state mapping
    try:
        platform, original_state = state.split(":", 1)
    except ValueError:
        return RedirectResponse(url="http://localhost:3000?error=invalid_state")
        
    if platform not in OAUTH_CONFIG:
        return RedirectResponse(url="http://localhost:3000?error=unsupported_platform")

    config = OAUTH_CONFIG[platform]
    
    # Normally we would do an async httpx.post to the token_url here to exchange the `code` for actual tokens.
    # Since we don't have real app credentials in sandbox mode, we simulate the token exchange response:
    
    access_token = f"mock_access_token_{secrets.token_hex(8)}"
    refresh_token = f"mock_refresh_token_{secrets.token_hex(8)}"
    # Mocking getting user profile info during token exchange
    username = f"{platform}_user_{secrets.token_hex(4)}"

    try:
        from src.database import get_db
        from src.models import Account
        db = next(get_db())
        
        # Upsert account (if an account with same platform/username exists, update tokens)
        account = db.query(Account).filter(Account.platform == platform, Account.username == username).first()
        
        if not account:
            account = Account(
                platform=platform,
                username=username,
                access_token=access_token,
                refresh_token=refresh_token,
                is_active=True
            )
            db.add(account)
        else:
            account.access_token = access_token
            account.refresh_token = refresh_token
            account.is_active = True
            
        db.commit()
        db.refresh(account)
        
        # Redirect back to frontend dashboard with success
        return RedirectResponse(url="http://localhost:3000?account_connected=true")
        
    except Exception as e:
        logger.error(f"Callback account save failed: {str(e)}", exc_info=True)
        return RedirectResponse(url="http://localhost:3000?error=database_error")

@app.get("/api/analytics/timeseries")
async def get_analytics_timeseries(days: int = Query(7, ge=1, le=90)):
    """
    Get timeseries analytics data for the given number of days
    """
    try:
        from src.database import get_db
        from src.models import Analytics
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        db = next(get_db())
        
        # Calculate start date
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days-1)
        
        # We need data grouped by day
        # For simplicity in SQLite/Postgres compatibility, we fetch raw records and aggregate in Python
        recent_analytics = db.query(Analytics).filter(Analytics.created_at >= start_date).all()
        
        # Initialize map with zero values for the past N days
        daily_stats = {}
        for i in range(days):
            day = (start_date + timedelta(days=i)).strftime("%a") # Mon, Tue, etc.
            # Using date string as key to handle multiple weeks safely, though we'll just format it to day name
            date_key = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            daily_stats[date_key] = {
                "name": day,
                "views": 0,
                "likes": 0,
                "comments": 0
            }
            
        # Aggregate analytics by day
        for row in recent_analytics:
            if row.created_at:
                date_key = row.created_at.strftime("%Y-%m-%d")
                if date_key in daily_stats:
                    daily_stats[date_key]["views"] += (row.views or 0)
                    daily_stats[date_key]["likes"] += (row.likes or 0)
                    daily_stats[date_key]["comments"] += (row.comments or 0)
                    
        # Convert dictionary to ordered list
        result = list(daily_stats.values())
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Get timeseries failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
async def get_analytics(platform: str = Query("all")):
    """
    Get analytics data
    
    Args:
        platform: Platform to get analytics for
        
    Returns:
        Analytics data
    """
    try:
        logger.info(f"Getting analytics for: {platform}")
        
        # Get real analytics from database
        from src.database import get_db
        from src.models import Analytics, Video
        from sqlalchemy import func
        
        db = next(get_db())
        
        # Calculate totals using SQL functions
        total_views = db.query(func.sum(Analytics.views)).filter(
            Analytics.platform == platform if platform != "all" and platform in ["tiktok", "youtube", "instagram"] else True
        ).scalar() or 0
        
        total_likes = db.query(func.sum(Analytics.likes)).filter(
            Analytics.platform == platform if platform != "all" and platform in ["tiktok", "youtube", "instagram"] else True
        ).scalar() or 0
        
        total_comments = db.query(func.sum(Analytics.comments)).filter(
            Analytics.platform == platform if platform != "all" and platform in ["tiktok", "youtube", "instagram"] else True
        ).scalar() or 0
        
        # Get video count
        video_count = db.query(Video).count()
        
        return {
            "success": True,
            "platform": platform,
            "data": {
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "video_count": video_count
            }
        }
        
    except Exception as e:
        logger.error(f"Get analytics failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/templates")
async def get_templates():
    """
    Get available templates
    
    Returns:
        List of available templates
    """
    try:
        from src.templater import VideoTemplateEngine
        engine = VideoTemplateEngine()
        
        return {
            "success": True,
            "templates": list(engine.templates.keys())
        }
        
    except Exception as e:
        logger.error(f"Get templates failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
