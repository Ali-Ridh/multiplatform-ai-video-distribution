#!/usr/bin/env python3
"""
Video Reframer Module

Implements 9:16 aspect ratio reframing with face tracking using MediaPipe
"""

import os
import logging
import cv2
import mediapipe as mp
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

class VideoReframer:
    """
    Handles video reframing with face tracking for 9:16 aspect ratio
    """
    
    def __init__(self):
        """Initialize the video reframer"""
        logger.info("Initializing video reframer...")
        
        # Output directory
        self.output_dir = os.getenv("OUTPUT_DIR", "./output")
        self.processed_dir = os.path.join(self.output_dir, "processed")
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # Initialize MediaPipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 0 for short range, 1 for full range
            min_detection_confidence=0.5
        )
        
        logger.info("MediaPipe Face Detection initialized")
        
    def reframe(self, video_path: str, segments: list = None) -> str:
        """
        Reframe video to 9:16 aspect ratio with face tracking
        
        Args:
            video_path: Path to source video
            segments: Optional list of segments to reframe
            
        Returns:
            Path to reframed video
            
        Raises:
            Exception: If reframing fails
        """
        logger.info(f"Reframing video: {video_path}")
        
        try:
            # Open video file
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise Exception(f"Could not open video: {video_path}")
                
            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            logger.info(f"Video properties: {width}x{height} @ {fps:.1f} FPS")
            
            # Calculate 9:16 aspect ratio dimensions
            target_aspect = 9 / 16
            
            # Determine reframed dimensions
            if width / height > target_aspect:
                # Video is wider than target aspect
                new_height = height
                new_width = int(height * target_aspect)
            else:
                # Video is taller than target aspect
                new_width = width
                new_height = int(width / target_aspect)
                
            logger.info(f"Reframed dimensions: {new_width}x{new_height}")
            
            # Output file path
            filename = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.processed_dir, f"{filename}_reframed.mp4")
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (new_width, new_height))
            
            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                
                if not ret:
                    break
                    
                # Process frame
                processed_frame = self._reframe_frame(frame, new_width, new_height)
                out.write(processed_frame)
                
                frame_count += 1
                if frame_count % 100 == 0:
                    logger.info(f"Processed frame {frame_count}/{total_frames}")
                    
            # Release resources
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            
            logger.info(f"Video reframed successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Video reframing failed: {str(e)}", exc_info=True)
            raise
            
    def _reframe_frame(self, frame: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
        """
        Reframe a single frame to target dimensions with face tracking
        
        Args:
            frame: Input frame
            target_width: Target width
            target_height: Target height
            
        Returns:
            Processed frame
        """
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        results = self.face_detection.process(rgb_frame)
        
        if results.detections:
            # Get face bounding box
            detection = results.detections[0]
            bbox = detection.location_data.relative_bounding_box
            
            # Calculate face center
            face_center_x = bbox.xmin + bbox.width / 2
            face_center_y = bbox.ymin + bbox.height / 2
            
            # Calculate crop coordinates to keep face centered
            cropped = self._center_crop(frame, face_center_x, face_center_y, target_width, target_height)
        else:
            # No face detected, crop from center
            cropped = self._center_crop(frame, 0.5, 0.5, target_width, target_height)
            
        return cropped
        
    def _center_crop(self, frame: np.ndarray, center_x: float, center_y: float, target_width: int, target_height: int) -> np.ndarray:
        """
        Crop frame around specified center
        
        Args:
            frame: Input frame
            center_x: Normalized x-coordinate of center (0-1)
            center_y: Normalized y-coordinate of center (0-1)
            target_width: Target width
            target_height: Target height
            
        Returns:
            Cropped frame
        """
        frame_height, frame_width = frame.shape[:2]
        
        # Calculate crop dimensions
        crop_width = target_width
        crop_height = target_height
        
        # Calculate top-left corner coordinates
        center_x_px = int(center_x * frame_width)
        center_y_px = int(center_y * frame_height)
        
        x1 = center_x_px - crop_width // 2
        y1 = center_y_px - crop_height // 2
        x2 = x1 + crop_width
        y2 = y1 + crop_height
        
        # Adjust if crop goes out of bounds
        if x1 < 0:
            x1 = 0
            x2 = crop_width
        if y1 < 0:
            y1 = 0
            y2 = crop_height
        if x2 > frame_width:
            x2 = frame_width
            x1 = frame_width - crop_width
        if y2 > frame_height:
            y2 = frame_height
            y1 = frame_height - crop_height
            
        # Perform crop
        cropped = frame[y1:y2, x1:x2]
        
        # Resize if dimensions don't match exactly (due to integer calculations)
        if cropped.shape[1] != target_width or cropped.shape[0] != target_height:
            cropped = cv2.resize(cropped, (target_width, target_height))
            
        return cropped
        
    def reframe_segment(self, video_path: str, start_time: float, end_time: float) -> str:
        """
        Reframe a specific segment of a video
        
        Args:
            video_path: Path to source video
            start_time: Start time of segment
            end_time: End time of segment
            
        Returns:
            Path to reframed segment
            
        Raises:
            Exception: If reframing fails
        """
        logger.info(f"Reframing segment {start_time:.1f}-{end_time:.1f} from {video_path}")
        
        try:
            # Use FFmpeg to extract and reframe segment
            import subprocess
            
            filename = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.processed_dir, f"{filename}_segment_{start_time:.1f}-{end_time:.1f}.mp4")
            
            # First extract the segment
            temp_path = os.path.join(self.processed_dir, f"temp_segment_{start_time:.1f}-{end_time:.1f}.mp4")
            
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-ss", str(start_time),
                "-i", video_path,
                "-t", str(end_time - start_time),
                "-c", "copy",
                temp_path
            ]
            
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
            
            # Then reframe the segment
            reframed_path = self.reframe(temp_path)
            
            # Rename to final output
            final_path = os.path.join(self.processed_dir, f"{filename}_segment_{start_time:.1f}-{end_time:.1f}_reframed.mp4")
            os.rename(reframed_path, final_path)
            
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            logger.info(f"Segment reframed successfully: {final_path}")
            return final_path
            
        except Exception as e:
            logger.error(f"Segment reframing failed: {str(e)}", exc_info=True)
            raise
