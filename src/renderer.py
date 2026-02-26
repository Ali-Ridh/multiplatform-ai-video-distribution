#!/usr/bin/env python3
"""
Video Renderer Module

Handles final video rendering with visual fingerprinting and audio hashing
"""

import os
import logging
import random
import subprocess
import tempfile

# Configure logging
logger = logging.getLogger(__name__)

class VideoRenderer:
    """
    Handles final video rendering with visual fingerprinting and audio hashing
    """
    
    def __init__(self):
        """Initialize the video renderer"""
        logger.info("Initializing video renderer...")
        
        # Output directory
        self.output_dir = os.getenv("OUTPUT_DIR", "./output")
        self.rendered_dir = os.path.join(self.output_dir, "rendered")
        os.makedirs(self.rendered_dir, exist_ok=True)
        
        # Configuration
        self.fps = int(os.getenv("FPS", "30"))
        
    def render(self, video_path: str, variations: int = 3) -> list:
        """
        Render video variations with fingerprinting
        
        Args:
            video_path: Path to source video
            variations: Number of variations to generate
            
        Returns:
            List of rendered video paths
            
        Raises:
            Exception: If rendering fails
        """
        logger.info(f"Rendering {variations} variations of: {video_path}")
        
        try:
            rendered_paths = []
            
            for i in range(variations):
                # Apply random fingerprinting
                variation_path = self._apply_fingerprinting(video_path, i + 1)
                rendered_paths.append(variation_path)
                
            logger.info(f"Generated {len(rendered_paths)} video variations")
            return rendered_paths
            
        except Exception as e:
            logger.error(f"Video rendering failed: {str(e)}", exc_info=True)
            raise
            
    def _apply_fingerprinting(self, video_path: str, variation_number: int) -> str:
        """
        Apply visual fingerprinting and audio hashing to create unique video variation
        
        Args:
            video_path: Path to source video
            variation_number: Variation number
            
        Returns:
            Path to fingerprinted video
        """
        logger.info(f"Creating variation {variation_number} for: {video_path}")
        
        # Generate output filename
        filename = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(self.rendered_dir, f"{filename}_v{variation_number}.mp4")
        
        # Temporary files
        temp_audio_path = None
        
        try:
            # Step 1: Apply visual fingerprinting
            temp_video_path = tempfile.mktemp(suffix=".mp4")
            self._apply_visual_fingerprinting(video_path, temp_video_path, variation_number)
            
            # Step 2: Apply audio hashing
            temp_audio_path = tempfile.mktemp(suffix=".mp3")
            self._apply_audio_hashing(video_path, temp_audio_path, variation_number)
            
            # Step 3: Mux audio and video
            self._mux_audio_video(temp_video_path, temp_audio_path, output_path)
            
            logger.info(f"Fingerprinting completed: {output_path}")
            
            return output_path
            
        finally:
            # Clean up temporary files
            if 'temp_video_path' in locals() and os.path.exists(temp_video_path):
                try:
                    os.remove(temp_video_path)
                except:
                    pass
            if temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.remove(temp_audio_path)
                except:
                    pass
                    
    def _apply_visual_fingerprinting(self, input_path: str, output_path: str, variation: int):
        """
        Apply visual fingerprinting using FFmpeg filters
        
        Args:
            input_path: Input video path
            output_path: Output video path
            variation: Variation number
            
        Raises:
            Exception: If FFmpeg command fails
        """
        # Random parameters based on variation number
        random.seed(variation)
        
        # Apply subtle color grading
        hue = random.randint(-5, 5)
        saturation = 1.0 + random.randint(-10, 10) / 100
        brightness = 1.0 + random.randint(-5, 5) / 100
        
        # Apply subtle blur to background
        blur_strength = random.randint(0, 2)
        
        # Apply subtle vignette
        vignette_strength = random.randint(0, 20)
        
        # Generate FFmpeg filters
        filters = []
        
        if hue != 0:
            filters.append(f"hue=h={hue}")
            
        if saturation != 1.0 or brightness != 1.0:
            filters.append(f"eq=saturation={saturation}:brightness={brightness}")
            
        if blur_strength > 0:
            filters.append(f"gblur=sigma={blur_strength * 0.5}")
            
        if vignette_strength > 0:
            filters.append(f"vignette=strength={vignette_strength/100}:angle=0")
            
        filter_complex = ",".join(filters) if filters else None
        
        # Build FFmpeg command
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
        ]
        
        if filter_complex:
            cmd.extend([
                "-vf", filter_complex
            ])
            
        cmd.extend([
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "fast",
            "-c:a", "copy",  # Copy audio temporarily, will replace later
            output_path
        ])
        
        # Run FFmpeg
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg visual fingerprinting failed: {e.stderr}")
            raise
            
    def _apply_audio_hashing(self, input_path: str, output_path: str, variation: int):
        """
        Apply audio hashing (subtle pitch/speed adjustments)
        
        Args:
            input_path: Input video path
            output_path: Output audio path
            variation: Variation number
            
        Raises:
            Exception: If FFmpeg command fails
        """
        # Random parameters based on variation number
        random.seed(variation + 1000)
        
        # Subtle speed/pitch adjustment (±0.5% to ±1.5%)
        speed_change = 1.0 + random.randint(-15, 15) / 1000
        
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-filter:a", f"atempo={speed_change}",
            "-c:a", "aac",
            "-b:a", "128k",
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg audio hashing failed: {e.stderr}")
            raise
            
    def _mux_audio_video(self, video_path: str, audio_path: str, output_path: str):
        """
        Mux audio and video tracks
        
        Args:
            video_path: Video file path
            audio_path: Audio file path
            output_path: Output file path
            
        Raises:
            Exception: If FFmpeg command fails
        """
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "128k",
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg muxing failed: {e.stderr}")
            raise
            
    def render_segment(self, video_path: str, start_time: float, end_time: float) -> str:
        """
        Render a specific video segment
        
        Args:
            video_path: Path to source video
            start_time: Start time of segment
            end_time: End time of segment
            
        Returns:
            Path to rendered segment
            
        Raises:
            Exception: If rendering fails
        """
        logger.info(f"Rendering segment {start_time:.1f}-{end_time:.1f} from: {video_path}")
        
        filename = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(self.rendered_dir, f"{filename}_segment_{start_time:.1f}-{end_time:.1f}.mp4")
        
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_time),
            "-i", video_path,
            "-t", str(end_time - start_time),
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "fast",
            "-c:a", "aac",
            "-b:a", "128k",
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Segment rendered successfully: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg segment rendering failed: {e.stderr}")
            raise
