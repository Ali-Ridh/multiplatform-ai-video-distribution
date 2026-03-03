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
    # Check if we have a build directory (production) or just the source (development)
    build_dir = os.path.join(static_dir, "build")
    if os.path.exists(build_dir):
        app.mount("/", StaticFiles(directory=build_dir, html=True), name="static")
    else:
        logger.warning("Frontend build directory not found, skipping static file serving")

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
        
        return {
            "success": True,
            "file_path": file_path,
            "filename": file.filename,
            "message": "File uploaded successfully"
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
        processed_dir = os.path.join(os.getenv("OUTPUT_DIR", "./output"), "processed")
        os.makedirs(processed_dir, exist_ok=True)
        
        videos = []
        
        for filename in os.listdir(processed_dir):
            if filename.endswith(('.mp4', '.avi', '.mov')):
                file_path = os.path.join(processed_dir, filename)
                stat = os.stat(file_path)
                
                videos.append({
                    "filename": filename,
                    "path": file_path,
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
                
        return {
            "success": True,
            "videos": videos
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
        
        results = opus.distributor.scrape_analytics(platform)
        
        return {
            "success": True,
            "platform": platform,
            "data": results
        }
        
    except Exception as e:
        logger.error(f"Get analytics failed: {str(e)}", exc_info=True)
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
