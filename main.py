#!/usr/bin/env python3
"""
Opus - High-Performance Video Pipeline for Content Creation and Distribution

Main entry point for the Opus system
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('opus.log')
    ]
)
logger = logging.getLogger(__name__)

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.opus import Opus

def main():
    """Main function to start the Opus system"""
    logger.info("🎬 Starting Opus system...")
    
    try:
        # Initialize Opus engine
        opus = Opus()
        
        # Parse command-line arguments
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == "process":
                # Process a single video
                if len(sys.argv) > 2:
                    url = sys.argv[2]
                    logger.info(f"Processing video: {url}")
                    opus.process_video(url)
                else:
                    logger.error("Please provide a video URL to process")
                    sys.exit(1)
                    
            elif command == "render":
                # Render processed videos
                logger.info("Rendering videos...")
                opus.render_videos()
                
            elif command == "upload":
                # Upload rendered videos
                logger.info("Uploading videos...")
                opus.upload_videos()
                
            elif command == "dashboard":
                # Start the dashboard server
                logger.info("Starting dashboard server...")
                from src.api.server import app
                import uvicorn
                uvicorn.run(app, host="0.0.0.0", port=8000)
                
            elif command == "worker":
                # Start Celery worker
                logger.info("Starting Celery worker...")
                import subprocess
                subprocess.run([
                    "celery", "-A", "src.worker.celery_app", "worker", 
                    "--loglevel=info", "--concurrency=4"
                ])
                
            elif command == "flower":
                # Start Flower monitoring
                logger.info("Starting Flower monitoring...")
                import subprocess
                subprocess.run([
                    "celery", "-A", "src.worker.celery_app", "flower",
                    "--port=5555"
                ])
                
            else:
                logger.error(f"Unknown command: {command}")
                logger.info("Available commands: process, render, upload, dashboard, worker, flower")
                sys.exit(1)
        else:
            # Show help
            logger.info("Opus - High-Performance Video Pipeline")
            logger.info("Usage: python main.py [command] [args]")
            logger.info("\nAvailable commands:")
            logger.info("  process <url>  - Process a single video")
            logger.info("  render         - Render processed videos")
            logger.info("  upload         - Upload rendered videos")
            logger.info("  dashboard      - Start the dashboard server")
            logger.info("  worker         - Start Celery worker")
            logger.info("  flower         - Start Flower monitoring")
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
