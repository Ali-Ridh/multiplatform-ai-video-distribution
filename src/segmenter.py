#!/usr/bin/env python3
"""
Viral Segment Detector Module

Uses GPT-4o to analyze transcripts and identify viral segments
"""

import os
import json
import logging
import openai

# Configure logging
logger = logging.getLogger(__name__)

class ViralSegmentDetector:
    """
    Uses GPT-4o to analyze transcripts and identify viral segments
    """
    
    def __init__(self):
        """Initialize the viral segment detector"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise Exception("OPENAI_API_KEY environment variable is not set")
            
        openai.api_key = self.api_key
        
        logger.info("Viral segment detector initialized")
        
    def detect(self, video_path: str, transcript_path: str) -> list:
        """
        Detect viral segments in a video
        
        Args:
            video_path: Path to video file
            transcript_path: Path to transcript file
            
        Returns:
            List of viral segments with start/end times
            
        Raises:
            Exception: If detection fails
        """
        logger.info(f"Detecting viral segments in: {video_path}")
        
        try:
            # Read transcript
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript = json.load(f)
                
            # Prepare prompt
            prompt = self._prepare_prompt(transcript)
            
            # Call GPT-4o
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a viral content detection expert. Your task is to analyze video transcripts and identify segments that have high potential to go viral on platforms like TikTok, YouTube Shorts, and Instagram Reels."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse response
            segments = self._parse_response(response)
            
            logger.info(f"Found {len(segments)} viral segments")
            
            # Save segments
            self._save_segments(video_path, segments)
            
            return segments
            
        except Exception as e:
            logger.error(f"Viral segment detection failed: {str(e)}", exc_info=True)
            raise
            
    def _prepare_prompt(self, transcript: dict) -> str:
        """
        Prepare prompt for GPT-4o
        
        Args:
            transcript: Transcript data
            
        Returns:
            Formatted prompt
        """
        # Build transcript text
        transcript_text = ""
        for segment in transcript["segments"]:
            start = segment["start"]
            end = segment["end"]
            text = segment["text"].strip()
            
            transcript_text += f"[{start:.1f}-{end:.1f}]: {text}\n"
            
        prompt = (
            "Analyze the following video transcript and identify 3-5 viral segments that are likely to perform well on short-form video platforms. "
            "Viral segments typically have:\n"
            "1. Strong emotional hooks (surprise, curiosity, anger, joy)\n"
            "2. Clear actionable information or advice\n"
            "3. Controversial or thought-provoking statements\n"
            "4. Relatable or aspirational content\n"
            "5. High information density in a short time\n"
            "\n"
            "Transcript:\n"
            f"{transcript_text}\n"
            "\n"
            "For each viral segment, provide:\n"
            "1. start_time: the start time in seconds\n"
            "2. end_time: the end time in seconds\n"
            "3. reasoning: why this segment has viral potential\n"
            "4. hook: a catchy 2-3 word description of the segment\n"
            "\n"
            "Return the results as a JSON array without any additional text. Example format:\n"
            "[\n"
            "    {\n"
            "        \"start_time\": 12.3,\n"
            "        \"end_time\": 25.6,\n"
            "        \"reasoning\": \"Strong emotional hook about money management that resonates with young viewers\",\n"
            "        \"hook\": \"Money Secrets\"\n"
            "    }\n"
            "]"
        )
        
        return prompt
        
    def _parse_response(self, response) -> list:
        """
        Parse GPT-4o response
        
        Args:
            response: OpenAI response object
            
        Returns:
            List of viral segments
        """
        try:
            content = response['choices'][0]['message']['content']
            
            # Extract JSON from response (handle cases where there's extra text)
            if '[' in content and ']' in content:
                start = content.find('[')
                end = content.rfind(']') + 1
                json_str = content[start:end]
                
                return json.loads(json_str)
            else:
                logger.warning("No valid JSON array found in response, trying to parse directly")
                return json.loads(content)
                
        except Exception as e:
            logger.error(f"Failed to parse GPT response: {str(e)}", exc_info=True)
            raise
            
    def _save_segments(self, video_path: str, segments: list):
        """
        Save viral segments to JSON file
        
        Args:
            video_path: Path to source video
            segments: List of viral segments
        """
        output_dir = os.getenv("OUTPUT_DIR", "./output")
        segments_dir = os.path.join(output_dir, "segments")
        os.makedirs(segments_dir, exist_ok=True)
        
        filename = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(segments_dir, f"{filename}_segments.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Segments saved to: {output_path}")
