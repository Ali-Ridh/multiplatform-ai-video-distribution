#!/usr/bin/env python3
"""
Opus - Core Engine

Main class orchestrating the entire video processing pipeline
"""

import os
import logging
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Opus:
    """
    Main Opus engine class that orchestrates the entire video processing pipeline
    """
    
    def __init__(self):
        """Initialize the Opus engine"""
        logger.info("Initializing Opus engine...")
        
        # Configuration
        self.upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
        self.output_dir = os.getenv("OUTPUT_DIR", "./output")
        self.fps = int(os.getenv("FPS", "30"))
        
        # Create directories if they don't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize modules
        self._init_modules()
        
    def _init_modules(self):
        """Initialize all processing modules"""
        logger.info("Initializing processing modules...")
        
        # Import modules dynamically to handle dependencies
        try:
            from src.downloader import VideoDownloader
            from src.transcriber import VideoTranscriber
            from src.segmenter import ViralSegmentDetector
            from src.reframer import VideoReframer
            from src.templater import VideoTemplateEngine
            from src.distributor import VideoDistributor
            from src.renderer import VideoRenderer
            
            self.downloader = VideoDownloader()
            self.transcriber = VideoTranscriber()
            self.segmenter = ViralSegmentDetector()
            self.reframer = VideoReframer()
            self.templater = VideoTemplateEngine()
            self.distributor = VideoDistributor()
            self.renderer = VideoRenderer()
            
            logger.info("All modules initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize modules: {str(e)}", exc_info=True)
            raise
            
    def process_video(self, url: str) -> str:
        """
        Process a single video from URL
        
        Args:
            url: Video URL to process
            
        Returns:
            Path to processed video
        """
        logger.info(f"Processing video: {url}")
        
        try:
            # Step 1: Download video
            logger.info("Step 1: Downloading video...")
            video_path = self.downloader.download(url)
            
            # Step 2: Transcribe video
            logger.info("Step 2: Transcribing video...")
            transcript_path = self.transcriber.transcribe(video_path)
            
            # Step 3: Detect viral segments
            logger.info("Step 3: Detecting viral segments...")
            segments = self.segmenter.detect(video_path, transcript_path)
            
            # Step 4: Reframe video (9:16 with face tracking)
            logger.info("Step 4: Reframing video...")
            reframed_path = self.reframer.reframe(video_path, segments)
            
            # Step 5: Apply visual templates
            logger.info("Step 5: Applying visual templates...")
            templated_path = self.templater.apply(reframed_path, transcript_path)
            
            logger.info("Video processing completed successfully")
            return templated_path
            
        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}", exc_info=True)
            raise
            
    def render_videos(self):
        """Render processed videos for distribution"""
        logger.info("Rendering videos for distribution...")
        
        try:
            # Get all processed videos
            processed_videos = self._get_processed_videos()
            
            for video_path in processed_videos:
                logger.info(f"Rendering: {video_path}")
                
                # Render variations for distribution
                variations = self.renderer.render(video_path)
                
                logger.info(f"Generated {len(variations)} video variations")
                
        except Exception as e:
            logger.error(f"Video rendering failed: {str(e)}", exc_info=True)
            raise
            
    def upload_videos(self):
        """Upload rendered videos to social media platforms"""
        logger.info("Uploading videos to social media platforms...")
        
        try:
            # Get all rendered videos
            rendered_videos = self._get_rendered_videos()
            
            for video_path in rendered_videos:
                logger.info(f"Uploading: {video_path}")
                
                # Upload to platforms
                self.distributor.upload(video_path)
                
        except Exception as e:
            logger.error(f"Video upload failed: {str(e)}", exc_info=True)
            raise
            
    def _get_processed_videos(self):
        """Get list of processed videos"""
        processed_dir = os.path.join(self.output_dir, "processed")
        os.makedirs(processed_dir, exist_ok=True)
        
        videos = []
        for file in os.listdir(processed_dir):
            if file.endswith(('.mp4', '.avi', '.mov')):
                videos.append(os.path.join(processed_dir, file))
                
        return videos
        
    def _get_rendered_videos(self):
        """Get list of rendered videos"""
        rendered_dir = os.path.join(self.output_dir, "rendered")
        os.makedirs(rendered_dir, exist_ok=True)
        
        videos = []
        for file in os.listdir(rendered_dir):
            if file.endswith(('.mp4', '.avi', '.mov')):
                videos.append(os.path.join(rendered_dir, file))
                
        return videos
