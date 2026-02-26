#!/usr/bin/env python3
"""
Video Downloader Module

Handles downloading videos from URLs using pytube
"""

import os
import logging
import tempfile
from pytube import YouTube
from pytube.exceptions import VideoUnavailable

# Configure logging
logger = logging.getLogger(__name__)

class VideoDownloader:
    """
    Downloads videos from URLs using pytube
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the video downloader
        
        Args:
            output_dir: Directory to save downloaded videos
        """
        self.output_dir = output_dir or os.getenv("UPLOAD_DIR", "./uploads")
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"Video downloader initialized, saving to: {self.output_dir}")
        
    def download(self, url: str) -> str:
        """
        Download a video from URL
        
        Args:
            url: Video URL to download
            
        Returns:
            Path to downloaded video file
            
        Raises:
            Exception: If download fails
        """
        logger.info(f"Downloading video: {url}")
        
        try:
            # Create YouTube object
            yt = YouTube(url)
            
            # Print video information
            logger.info(f"Video title: {yt.title}")
            logger.info(f"Video duration: {yt.length} seconds")
            logger.info(f"Video views: {yt.views}")
            
            # Get the highest resolution stream available
            stream = yt.streams.get_highest_resolution()
            
            logger.info(f"Downloading stream: {stream}")
            
            # Download the video
            output_path = stream.download(output_path=self.output_dir)
            
            logger.info(f"Video downloaded successfully: {output_path}")
            
            return output_path
            
        except VideoUnavailable as e:
            logger.error(f"Video unavailable: {str(e)}")
            raise Exception(f"Video unavailable: {str(e)}")
            
        except Exception as e:
            logger.error(f"Download failed: {str(e)}", exc_info=True)
            raise Exception(f"Download failed: {str(e)}")
            
    def download_audio(self, url: str) -> str:
        """
        Download only the audio track from a video
        
        Args:
            url: Video URL to download audio from
            
        Returns:
            Path to downloaded audio file
            
        Raises:
            Exception: If download fails
        """
        logger.info(f"Downloading audio from: {url}")
        
        try:
            yt = YouTube(url)
            
            # Get audio stream
            stream = yt.streams.get_audio_only()
            
            logger.info(f"Downloading audio stream: {stream}")
            
            output_path = stream.download(output_path=self.output_dir)
            
            logger.info(f"Audio downloaded successfully: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Audio download failed: {str(e)}", exc_info=True)
            raise
            
    def clean_up(self, file_path: str):
        """
        Clean up downloaded file
        
        Args:
            file_path: Path to file to remove
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}", exc_info=True)
