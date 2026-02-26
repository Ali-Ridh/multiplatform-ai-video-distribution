#!/usr/bin/env python3
"""
Video Template Engine Module

Applies visual templates to videos using MoviePy
"""

import os
import logging
import json
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.drawing import color_gradient

# Configure logging
logger = logging.getLogger(__name__)

class VideoTemplateEngine:
    """
    Applies visual templates to videos using MoviePy
    """
    
    def __init__(self):
        """Initialize the video template engine"""
        logger.info("Initializing video template engine...")
        
        # Output directory
        self.output_dir = os.getenv("OUTPUT_DIR", "./output")
        self.processed_dir = os.path.join(self.output_dir, "processed")
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # Available templates
        self.templates = {
            "minimalist": self._apply_minimalist_template,
            "hormozi": self._apply_hormozi_template,
            "gaming": self._apply_gaming_template
        }
        
        logger.info(f"Available templates: {list(self.templates.keys())}")
        
    def apply(self, video_path: str, transcript_path: str = None, template_name: str = "minimalist") -> str:
        """
        Apply a visual template to a video
        
        Args:
            video_path: Path to source video
            transcript_path: Path to transcript file (optional)
            template_name: Template to apply
            
        Returns:
            Path to templated video
            
        Raises:
            Exception: If template application fails
        """
        logger.info(f"Applying {template_name} template to: {video_path}")
        
        try:
            # Check if template exists
            if template_name not in self.templates:
                raise Exception(f"Unknown template: {template_name}")
                
            # Load video
            video = VideoFileClip(video_path)
            
            # Load transcript if available
            transcript = None
            if transcript_path and os.path.exists(transcript_path):
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    transcript = json.load(f)
                    
            # Apply template
            templated_video = self.templates[template_name](video, transcript)
            
            # Save output
            filename = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.processed_dir, f"{filename}_{template_name}.mp4")
            templated_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
            
            logger.info(f"Template applied successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Template application failed: {str(e)}", exc_info=True)
            raise
            
    def _apply_minimalist_template(self, video, transcript=None):
        """
        Apply minimalist template
        
        Args:
            video: VideoFileClip object
            transcript: Transcript data (optional)
            
        Returns:
            CompositeVideoClip with minimalist template
        """
        # Add subtle background gradient
        gradient = color_gradient(
            (video.w, video.h),
            (255, 255, 255),
            (245, 245, 245)
        )
        gradient = gradient.to_ImageClip()
        
        # Create composite
        composite = CompositeVideoClip([gradient, video])
        
        # Add subtitle text if transcript available
        if transcript:
            subtitles = self._create_subtitles(video, transcript, fontsize=48)
            composite = CompositeVideoClip([composite, subtitles])
            
        return composite
        
    def _apply_hormozi_template(self, video, transcript=None):
        """
        Apply Hormozi-style template
        
        Args:
            video: VideoFileClip object
            transcript: Transcript data (optional)
            
        Returns:
            CompositeVideoClip with Hormozi template
        """
        # Add dark background with border
        from moviepy.video.fx.all import resize
        
        # Create background with gradient
        gradient = color_gradient(
            (video.w + 40, video.h + 40),
            (0, 0, 0),
            (30, 30, 30)
        )
        gradient = gradient.to_ImageClip()
        
        # Resize video
        resized_video = video.fx(resize, 0.9)
        
        # Center video on background
        x_pos = (gradient.w - resized_video.w) // 2
        y_pos = (gradient.h - resized_video.h) // 2
        positioned_video = resized_video.set_position((x_pos, y_pos))
        
        composite = CompositeVideoClip([gradient, positioned_video])
        
        # Add subtitle text if transcript available
        if transcript:
            subtitles = self._create_subtitles(composite, transcript, fontsize=56, color="#FFD700")
            composite = CompositeVideoClip([composite, subtitles])
            
        return composite
        
    def _apply_gaming_template(self, video, transcript=None):
        """
        Apply gaming-style template
        
        Args:
            video: VideoFileClip object
            transcript: Transcript data (optional)
            
        Returns:
            CompositeVideoClip with gaming template
        """
        # Add dynamic background with neon effect
        gradient = color_gradient(
            (video.w, video.h),
            (0, 0, 255),
            (0, 0, 0)
        )
        gradient = gradient.to_ImageClip()
        
        # Create composite
        composite = CompositeVideoClip([gradient, video])
        
        # Add subtitle text if transcript available
        if transcript:
            subtitles = self._create_subtitles(video, transcript, fontsize=52, color="#00FFFF")
            composite = CompositeVideoClip([composite, subtitles])
            
        return composite
        
    def _create_subtitles(self, video, transcript, fontsize=48, color="#000000"):
        """
        Create subtitle text clips from transcript
        
        Args:
            video: VideoFileClip object
            transcript: Transcript data
            fontsize: Font size
            color: Text color
            
        Returns:
            CompositeVideoClip of subtitles
        """
        subtitle_clips = []
        
        for segment in transcript["segments"]:
            text = segment["text"].strip()
            start_time = segment["start"]
            end_time = segment["end"]
            
            # Create text clip
            text_clip = TextClip(
                text,
                fontsize=fontsize,
                color=color,
                font="Arial-Bold",
                stroke_color="white",
                stroke_width=2,
                bg_color="rgba(0,0,0,0.5)",
                method="caption",
                size=(video.w - 40, None)
            )
            
            # Position at bottom center
            text_clip = text_clip.set_position(("center", "bottom"))
            
            # Set duration
            text_clip = text_clip.set_start(start_time).set_end(end_time)
            
            subtitle_clips.append(text_clip)
            
        return CompositeVideoClip(subtitle_clips)
        
    def apply_all_templates(self, video_path: str, transcript_path: str = None) -> list:
        """
        Apply all available templates to a video
        
        Args:
            video_path: Path to source video
            transcript_path: Path to transcript file (optional)
            
        Returns:
            List of paths to templated videos
        """
        logger.info(f"Applying all templates to: {video_path}")
        
        results = []
        for template_name in self.templates.keys():
            try:
                output_path = self.apply(video_path, transcript_path, template_name)
                results.append(output_path)
            except Exception as e:
                logger.error(f"Failed to apply {template_name} template: {str(e)}")
                
        logger.info(f"Applied {len(results)} out of {len(self.templates)} templates")
        return results
