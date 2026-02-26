#!/usr/bin/env python3
"""
Celery Tasks

Defines all async tasks for the Opus system
"""

import os
import logging
from celery import shared_task
from src.opus import Opus

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Opus engine
opus = None

def get_opus_engine():
    """Get or create Opus engine instance"""
    global opus
    if opus is None:
        opus = Opus()
    return opus

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_video_task(self, video_url: str):
    """
    Process a single video from URL
    
    Args:
        video_url: Video URL to process
        
    Returns:
        Path to processed video
    """
    logger.info(f"Processing video task: {video_url}")
    
    try:
        opus = get_opus_engine()
        processed_path = opus.process_video(video_url)
        logger.info(f"Video processing task completed: {processed_path}")
        return processed_path
        
    except Exception as e:
        logger.error(f"Video processing task failed: {str(e)}", exc_info=True)
        raise self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def render_video_task(self, processed_video_path: str):
    """
    Render processed video for distribution
    
    Args:
        processed_video_path: Path to processed video
        
    Returns:
        Path to rendered video
    """
    logger.info(f"Rendering video task: {processed_video_path}")
    
    try:
        opus = get_opus_engine()
        rendered_path = opus.render_videos(processed_video_path)
        logger.info(f"Video rendering task completed: {rendered_path}")
        return rendered_path
        
    except Exception as e:
        logger.error(f"Video rendering task failed: {str(e)}", exc_info=True)
        raise self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def upload_video_task(self, video_path: str, platform: str = "all"):
    """
    Upload video to social media platforms
    
    Args:
        video_path: Path to video file
        platform: Platform to upload to (all, tiktok, youtube, instagram)
        
    Returns:
        Dictionary of upload results per platform
    """
    logger.info(f"Uploading video task to {platform}: {video_path}")
    
    try:
        opus = get_opus_engine()
        results = opus.distributor.upload(video_path, platform)
        logger.info(f"Video upload task completed: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Video upload task failed: {str(e)}", exc_info=True)
        raise self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def scrape_analytics_task(self, platform: str = "all"):
    """
    Scrape analytics from social media platforms
    
    Args:
        platform: Platform to scrape (all, tiktok, youtube, instagram)
        
    Returns:
        Dictionary of analytics data per platform
    """
    logger.info(f"Scraping analytics task for {platform}")
    
    try:
        opus = get_opus_engine()
        results = opus.distributor.scrape_analytics(platform)
        logger.info(f"Analytics scraping task completed: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Analytics scraping task failed: {str(e)}", exc_info=True)
        raise self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_and_upload_task(self, video_url: str, platform: str = "all"):
    """
    Complete process: download -> transcribe -> detect -> reframe -> template -> upload
    
    Args:
        video_url: Video URL to process
        platform: Platform to upload to
        
    Returns:
        Dictionary of final results
    """
    logger.info(f"Complete process task: {video_url} -> {platform}")
    
    try:
        opus = get_opus_engine()
        
        # Step 1: Process video
        processed_path = opus.process_video(video_url)
        
        # Step 2: Render video
        rendered_path = opus.render_videos(processed_path)
        
        # Step 3: Upload video
        upload_results = opus.distributor.upload(rendered_path, platform)
        
        logger.info(f"Complete process task completed: {upload_results}")
        
        return {
            "processed_path": processed_path,
            "rendered_path": rendered_path,
            "upload_results": upload_results
        }
        
    except Exception as e:
        logger.error(f"Complete process task failed: {str(e)}", exc_info=True)
        raise self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_caption_variations_task(self, master_caption: str, count: int = 5):
    """
    Generate caption variations from a master caption
    
    Args:
        master_caption: Original caption
        count: Number of variations to generate
        
    Returns:
        List of caption variations
    """
    logger.info(f"Generating {count} caption variations")
    
    try:
        from src.caption_generator import CaptionVariationGenerator
        
        generator = CaptionVariationGenerator()
        variations = generator.generate(master_caption, count)
        
        logger.info(f"Generated {len(variations)} caption variations")
        return variations
        
    except Exception as e:
        logger.error(f"Caption generation task failed: {str(e)}", exc_info=True)
        raise self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def schedule_video_upload_task(self, video_path: str, platform: str, schedule_time: str):
    """
    Schedule a video for future upload
    
    Args:
        video_path: Path to video file
        platform: Platform to upload to
        schedule_time: ISO datetime string for scheduled time
        
    Returns:
        Scheduled task information
    """
    logger.info(f"Scheduling video upload for {schedule_time}: {video_path}")
    
    try:
        from datetime import datetime
        from src.scheduler import StaggeredScheduler
        
        scheduler = StaggeredScheduler()
        
        # Convert string to datetime
        scheduled_datetime = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
        
        # Schedule the upload
        task_id = scheduler.schedule_upload(
            video_path,
            platform,
            scheduled_datetime
        )
        
        logger.info(f"Video upload scheduled: {task_id}")
        return {"task_id": task_id, "scheduled_time": schedule_time}
        
    except Exception as e:
        logger.error(f"Schedule upload task failed: {str(e)}", exc_info=True)
        raise self.retry(exc=e)
