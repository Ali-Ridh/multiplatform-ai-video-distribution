#!/usr/bin/env python3
"""
Video Transcriber Module

Generates word-level timestamped transcripts using Faster-Whisper
"""

import os
import logging
import json
from faster_whisper import WhisperModel

# Configure logging
logger = logging.getLogger(__name__)

class VideoTranscriber:
    """
    Generates word-level timestamped transcripts using Faster-Whisper
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize the video transcriber
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        logger.info(f"Initializing Whisper model: {model_size}")
        self.model = WhisperModel(model_size, device="auto", compute_type="default")
        
        # Output directories
        self.output_dir = os.getenv("OUTPUT_DIR", "./output")
        self.transcript_dir = os.path.join(self.output_dir, "transcripts")
        os.makedirs(self.transcript_dir, exist_ok=True)
        
    def transcribe(self, video_path: str) -> str:
        """
        Transcribe a video file
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to transcript file
            
        Raises:
            Exception: If transcription fails
        """
        logger.info(f"Transcribing video: {video_path}")
        
        try:
            # Transcribe the video with word-level timestamps
            segments, info = self.model.transcribe(
                video_path,
                beam_size=5,
                word_timestamps=True
            )
            
            logger.info(f"Detected language: {info.language} ({info.language_probability:.2f})")
            
            # Convert segments to JSON format
            transcript = {
                "language": info.language,
                "language_probability": info.language_probability,
                "segments": []
            }
            
            for segment in segments:
                segment_data = {
                    "id": segment.id,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                    "words": []
                }
                
                # Add word-level timestamps
                if segment.words:
                    for word in segment.words:
                        segment_data["words"].append({
                            "word": word.word,
                            "start": word.start,
                            "end": word.end,
                            "probability": word.probability
                        })
                
                transcript["segments"].append(segment_data)
                
            # Save transcript
            transcript_path = self._save_transcript(video_path, transcript)
            
            logger.info(f"Transcript generated: {transcript_path}")
            
            # Generate SRT file
            srt_path = self._save_srt(video_path, transcript)
            logger.info(f"SRT file generated: {srt_path}")
            
            return transcript_path
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}", exc_info=True)
            raise
            
    def _save_transcript(self, video_path: str, transcript: dict) -> str:
        """
        Save transcript to JSON file
        
        Args:
            video_path: Path to source video
            transcript: Transcript data
            
        Returns:
            Path to saved transcript file
        """
        filename = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(self.transcript_dir, f"{filename}.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, ensure_ascii=False, indent=2, default=str)
            
        return output_path
        
    def _save_srt(self, video_path: str, transcript: dict) -> str:
        """
        Save transcript to SRT file
        
        Args:
            video_path: Path to source video
            transcript: Transcript data
            
        Returns:
            Path to saved SRT file
        """
        filename = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(self.transcript_dir, f"{filename}.srt")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(transcript["segments"], 1):
                # Format timestamps
                start = self._format_timestamp(segment["start"])
                end = self._format_timestamp(segment["end"])
                
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{segment['text'].strip()}\n\n")
                
        return output_path
        
    def _format_timestamp(self, seconds: float) -> str:
        """
        Format timestamp for SRT file
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted timestamp (HH:MM:SS,mmm)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"
        
    def generate_word_level_srt(self, video_path: str) -> str:
        """
        Generate word-level SRT file
        
        Args:
            video_path: Path to source video
            
        Returns:
            Path to word-level SRT file
        """
        logger.info(f"Generating word-level SRT for: {video_path}")
        
        try:
            # Transcribe with word-level timestamps
            segments, info = self.model.transcribe(
                video_path,
                beam_size=5,
                word_timestamps=True
            )
            
            filename = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.transcript_dir, f"{filename}_words.srt")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                word_count = 1
                
                for segment in segments:
                    if segment.words:
                        for word in segment.words:
                            start = self._format_timestamp(word.start)
                            end = self._format_timestamp(word.end)
                            
                            f.write(f"{word_count}\n")
                            f.write(f"{start} --> {end}\n")
                            f.write(f"{word.word.strip()}\n\n")
                            
                            word_count += 1
                            
            logger.info(f"Word-level SRT generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Word-level SRT generation failed: {str(e)}", exc_info=True)
            raise
