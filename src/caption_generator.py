#!/usr/bin/env python3
"""
Caption Variation Generator Module

Generates unique caption variations from a master caption using GPT-4o
"""

import os
import logging
import openai

# Configure logging
logger = logging.getLogger(__name__)

class CaptionVariationGenerator:
    """
    Generates unique caption variations using GPT-4o
    """
    
    def __init__(self):
        """Initialize the caption generator"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise Exception("OPENAI_API_KEY environment variable is not set")
            
        openai.api_key = self.api_key
        
        logger.info("Caption variation generator initialized")
        
    def generate(self, master_caption: str, count: int = 5) -> list:
        """
        Generate caption variations from a master caption
        
        Args:
            master_caption: Original master caption
            count: Number of variations to generate
            
        Returns:
            List of unique caption variations
            
        Raises:
            Exception: If generation fails
        """
        logger.info(f"Generating {count} caption variations")
        
        try:
            prompt = self._prepare_prompt(master_caption, count)
            
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert social media caption writer. Your task is to generate unique, engaging caption variations that are SEO-friendly and avoid repetition for short-form video platforms like TikTok, YouTube Shorts, and Instagram Reels."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            variations = self._parse_response(response, count)
            
            logger.info(f"Generated {len(variations)} valid caption variations")
            return variations
            
        except Exception as e:
            logger.error(f"Caption variation generation failed: {str(e)}", exc_info=True)
            raise
            
    def _prepare_prompt(self, master_caption: str, count: int) -> str:
        """
        Prepare prompt for GPT-4o
        
        Args:
            master_caption: Original caption
            count: Number of variations to generate
            
        Returns:
            Formatted prompt
        """
        prompt = (
            "Generate {count} unique and engaging caption variations from the following master caption. "
            "Each variation should:\n"
            "1. Maintain the core message and intent of the original\n"
            "2. Use different wording, phrasing, and sentence structures\n"
            "3. Include relevant emojis naturally\n"
            "4. Be engaging and optimized for short-form video platforms\n"
            "5. Have different opening and closing lines\n"
            "6. Avoid repetition between variations\n"
            "7. Include hashtags relevant to the topic\n"
            "\n"
            "Master Caption:\n"
            f"{master_caption}\n"
            "\n"
            "Requirements:\n"
            "- Each variation should be between 30-150 characters\n"
            "- Include 3-5 relevant hashtags at the end\n"
            "- Use varied emoji combinations\n"
            "- Make each variation feel unique and authentic\n"
            "\n"
            "Return the variations as a JSON array where each item contains:\n"
            "- \"caption\": the variation text\n"
            "- \"hashtags\": array of hashtags used\n"
            "- \"tone\": the emotional tone (e.g., upbeat, inspirational, humorous)\n"
            "\n"
            "Example format:\n"
            "[\n"
            "    {\n"
            "        \"caption\": \"Discover the secrets to financial freedom! 💸 Learn how to save more and spend wisely. #MoneyTips #FinancialFreedom\",\n"
            "        \"hashtags\": [\"MoneyTips\", \"FinancialFreedom\", \"SaveMoney\"],\n"
            "        \"tone\": \"inspirational\"\n"
            "    },\n"
            "    {\n"
            "        \"caption\": \"Want to improve your finances? 🌟 These simple tips will transform your money habits! #PersonalFinance #Savings\",\n"
            "        \"hashtags\": [\"PersonalFinance\", \"Savings\", \"MoneyManagement\"],\n"
            "        \"tone\": \"upbeat\"\n"
            "    }\n"
            "]"
        ).format(count=count)
        
        return prompt
        
    def _parse_response(self, response, expected_count: int) -> list:
        """
        Parse GPT-4o response
        
        Args:
            response: OpenAI response object
            expected_count: Number of variations expected
            
        Returns:
            List of caption variations
        """
        try:
            content = response['choices'][0]['message']['content']
            
            # Extract JSON from response
            if '[' in content and ']' in content:
                start = content.find('[')
                end = content.rfind(']') + 1
                json_str = content[start:end]
                
                variations = []
                try:
                    variations = eval(json_str)  # Using eval for quick parsing, consider json.loads
                except:
                    import json
                    variations = json.loads(json_str)
                    
                # Filter and validate variations
                valid_variations = []
                for variation in variations:
                    if (
                        isinstance(variation, dict) and
                        'caption' in variation and
                        isinstance(variation['caption'], str) and
                        len(variation['caption']) > 20
                    ):
                        valid_variations.append(variation)
                        
                # If less than expected, try to extract more or handle
                if len(valid_variations) < expected_count:
                    logger.warning(f"Only found {len(valid_variations)} valid variations (expected {expected_count})")
                    
                return valid_variations
                
            else:
                logger.error("No valid JSON array found in response")
                raise Exception("Response format invalid")
                
        except Exception as e:
            logger.error(f"Failed to parse GPT response: {str(e)}", exc_info=True)
            raise
            
    def generate_metadata(self, caption: str) -> dict:
        """
        Generate metadata (titles, descriptions, hashtags) from a caption
        
        Args:
            caption: Base caption
            
        Returns:
            Metadata dictionary with title, description, and hashtags
        """
        logger.info("Generating metadata for caption")
        
        try:
            prompt = (
                "Generate comprehensive metadata for a short-form video from the following caption:\n"
                f"{caption}\n"
                "\n"
                "Provide:\n"
                "1. A catchy title (50-100 characters)\n"
                "2. A detailed description (150-300 characters)\n"
                "3. 10-15 relevant hashtags separated by commas\n"
                "\n"
                "Return as JSON with keys: 'title', 'description', 'hashtags'\n"
            )
            
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert social media metadata optimizer. Your task is to create compelling titles, detailed descriptions, and relevant hashtags for maximum engagement and search visibility."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.6,
                max_tokens=500
            )
            
            metadata = self._parse_metadata_response(response)
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata generation failed: {str(e)}", exc_info=True)
            raise
            
    def _parse_metadata_response(self, response) -> dict:
        """
        Parse metadata response
        
        Args:
            response: OpenAI response object
            
        Returns:
            Metadata dictionary
        """
        try:
            content = response['choices'][0]['message']['content']
            
            if '{' in content and '}' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
                
                import json
                return json.loads(json_str)
                
            else:
                logger.error("No valid JSON object found in response")
                raise Exception("Metadata response format invalid")
                
        except Exception as e:
            logger.error(f"Failed to parse metadata response: {str(e)}", exc_info=True)
            raise
