#!/usr/bin/env python3
"""
Staggered Scheduler Module

Implements a drip-feed scheduling system for video uploads
"""

import os
import logging
import time
from datetime import datetime, timedelta
import random
from typing import Optional
from src.worker.tasks import upload_video_task

# Configure logging
logger = logging.getLogger(__name__)

class StaggeredScheduler:
    """
    Manages staggered video upload scheduling with drip-feed functionality
    """
    
    def __init__(self):
        """Initialize the scheduler"""
        logger.info("Initializing staggered scheduler...")
        
        # Configuration
        self.base_delay = int(os.getenv("BASE_DELAY", "300"))  # 5 minutes
        self.max_random_delay = int(os.getenv("MAX_RANDOM_DELAY", "300"))  # 5 minutes
        
        # Active schedules
        self.scheduled_tasks = {}
        
        logger.info(f"Scheduler initialized with base delay: {self.base_delay} seconds, max random delay: {self.max_random_delay} seconds")
        
    def schedule_upload(self, video_path: str, platform: str, schedule_time: datetime, account_id: Optional[str] = None) -> str:
        """
        Schedule a video for upload
        
        Args:
            video_path: Path to video file
            platform: Platform to upload to
            schedule_time: Scheduled upload time
            account_id: Optional account identifier
            
        Returns:
            Unique task ID
            
        Raises:
            Exception: If scheduling fails
        """
        logger.info(f"Scheduling upload for {schedule_time} to {platform}: {video_path}")
        
        try:
            # Generate unique task ID
            task_id = self._generate_task_id()
            
            # Calculate delay from now
            now = datetime.now()
            delay = (schedule_time - now).total_seconds()
            
            if delay < 0:
                logger.warning(f"Schedule time {schedule_time} is in the past, scheduling for now")
                delay = 0
                
            # Create task configuration
            task_config = {
                "task_id": task_id,
                "video_path": video_path,
                "platform": platform,
                "schedule_time": schedule_time,
                "account_id": account_id,
                "delay": delay,
                "status": "scheduled"
            }
            
            # Store in memory (for now - should use database)
            self.scheduled_tasks[task_id] = task_config
            
            logger.info(f"Task scheduled: {task_id}, delay: {delay:.0f} seconds")
            
            # Schedule the Celery task with countdown
            result = upload_video_task.apply_async(
                args=[video_path, platform],
                countdown=delay,
                task_id=task_id
            )
            
            logger.info(f"Celery task scheduled: {result.id}")
            
            task_config["celery_task_id"] = result.id
            task_config["status"] = "celery_scheduled"
            
            return task_id
            
        except Exception as e:
            logger.error(f"Schedule upload failed: {str(e)}", exc_info=True)
            raise
            
    def schedule_batch_uploads(self, video_paths: list, platform: str, start_time: datetime, account_ids: list = None) -> list:
        """
        Schedule batch of videos with staggered delays
        
        Args:
            video_paths: List of video paths
            platform: Platform to upload to
            start_time: Start time for first video
            account_ids: List of account identifiers
            
        Returns:
            List of scheduled task IDs
        """
        logger.info(f"Scheduling batch of {len(video_paths)} videos for {platform}")
        
        if account_ids is None:
            account_ids = [None] * len(video_paths)
            
        if len(account_ids) < len(video_paths):
            account_ids.extend([None] * (len(video_paths) - len(account_ids)))
            
        scheduled_task_ids = []
        
        for i, (video_path, account_id) in enumerate(zip(video_paths, account_ids)):
            # Calculate delay for each video
            base_offset = i * self.base_delay
            random_offset = random.randint(0, self.max_random_delay)
            total_offset = base_offset + random_offset
            
            schedule_time = start_time + timedelta(seconds=total_offset)
            
            logger.info(f"Video {i+1}: Scheduled for {schedule_time}, offset: {total_offset} seconds")
            
            try:
                task_id = self.schedule_upload(video_path, platform, schedule_time, account_id)
                scheduled_task_ids.append(task_id)
            except Exception as e:
                logger.error(f"Failed to schedule video {i+1}: {str(e)}")
                
        logger.info(f"Batch scheduling completed: {len(scheduled_task_ids)} out of {len(video_paths)} videos scheduled")
        
        return scheduled_task_ids
        
    def schedule_distribution_cycle(self, video_path: str, platforms: list, account_ids: list, start_time: datetime) -> list:
        """
        Schedule a complete distribution cycle across platforms and accounts
        
        Args:
            video_path: Path to video file
            platforms: List of platforms to upload to
            account_ids: List of account identifiers per platform
            start_time: Start time
            
        Returns:
            List of scheduled task IDs
        """
        logger.info(f"Scheduling distribution cycle for {video_path}")
        
        scheduled_task_ids = []
        
        for platform in platforms:
            if platform not in account_ids:
                logger.warning(f"No account IDs configured for platform: {platform}")
                continue
                
            # Create platform-specific video variations if needed
            platform_video_path = video_path
            if platform == "instagram":
                # Instagram might need specific format
                platform_video_path = self._prepare_instagram_version(video_path)
            elif platform == "tiktok":
                # TikTok might need specific format
                platform_video_path = self._prepare_tiktok_version(video_path)
                
            # Schedule for each account
            for account_id in account_ids[platform]:
                task_id = self.schedule_upload(platform_video_path, platform, start_time, account_id)
                scheduled_task_ids.append(task_id)
                
                # Stagger each account's upload
                start_time += timedelta(seconds=self.base_delay + random.randint(0, self.max_random_delay))
                
        return scheduled_task_ids
        
    def _prepare_instagram_version(self, video_path: str) -> str:
        """
        Prepare video for Instagram Reels
        
        Args:
            video_path: Path to source video
            
        Returns:
            Path to Instagram-optimized video
        """
        logger.info("Preparing video for Instagram")
        
        try:
            # In a real implementation, this would apply Instagram-specific optimizations
            return video_path
            
        except Exception as e:
            logger.error(f"Failed to prepare Instagram version: {str(e)}", exc_info=True)
            return video_path
            
    def _prepare_tiktok_version(self, video_path: str) -> str:
        """
        Prepare video for TikTok
        
        Args:
            video_path: Path to source video
            
        Returns:
            Path to TikTok-optimized video
        """
        logger.info("Preparing video for TikTok")
        
        try:
            # In a real implementation, this would apply TikTok-specific optimizations
            return video_path
            
        except Exception as e:
            logger.error(f"Failed to prepare TikTok version: {str(e)}", exc_info=True)
            return video_path
            
    def get_scheduled_tasks(self, platform: str = None, status: str = None) -> list:
        """
        Get scheduled tasks
        
        Args:
            platform: Optional platform filter
            status: Optional status filter
            
        Returns:
            List of scheduled tasks
        """
        tasks = list(self.scheduled_tasks.values())
        
        if platform:
            tasks = [t for t in tasks if t.get("platform") == platform]
            
        if status:
            tasks = [t for t in tasks if t.get("status") == status]
            
        return tasks
        
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a scheduled task
        
        Args:
            task_id: Task ID to cancel
            
        Returns:
            True if cancelled successfully, False otherwise
        """
        logger.info(f"Cancelling task: {task_id}")
        
        try:
            if task_id in self.scheduled_tasks:
                task_config = self.scheduled_tasks[task_id]
                
                # Cancel Celery task if it exists
                if "celery_task_id" in task_config:
                    from src.worker.celery_app import app
                    from celery.result import AsyncResult
                    
                    result = AsyncResult(task_config["celery_task_id"], app=app)
                    
                    try:
                        result.revoke(terminate=True)
                        logger.info(f"Celery task revoked: {task_config['celery_task_id']}")
                    except Exception as e:
                        logger.error(f"Failed to revoke Celery task: {str(e)}")
                        
                # Remove from scheduled tasks
                del self.scheduled_tasks[task_id]
                logger.info(f"Task cancelled: {task_id}")
                return True
                
            logger.warning(f"Task not found: {task_id}")
            return False
            
        except Exception as e:
            logger.error(f"Cancel task failed: {str(e)}", exc_info=True)
            return False
            
    def _generate_task_id(self) -> str:
        """Generate a unique task ID"""
        import uuid
        return str(uuid.uuid4())
