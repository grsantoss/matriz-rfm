"""OpenAI integration for RFM insights and text generation."""

import openai
from typing import Dict, List, Any
import os
from datetime import datetime
import json
import logging
from .prompts import PromptTemplates

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self, api_key: str):
        """Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
        """
        openai.api_key = api_key
        self.model = "gpt-4"  # Using GPT-4 for better analysis

    async def generate_segment_insights(
        self,
        segment_data: Dict[str, Any],
        segment_name: str
    ) -> str:
        """Generate insights for a specific customer segment.
        
        Args:
            segment_data: Dictionary containing segment metrics
            segment_name: Name of the segment
            
        Returns:
            Generated insights text
        """
        try:
            # Get appropriate prompt based on segment type
            segment_type = segment_name.lower().replace(" ", "_")
            prompt = PromptTemplates.get_segment_prompt(
                segment_type,
                segment_name=segment_name,
                **segment_data
            )

            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": PromptTemplates.get_system_prompt("analyst")},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating segment insights: {str(e)}")
            return "Unable to generate insights at this time."

    async def generate_marketing_suggestions(
        self,
        segment_name: str,
        segment_metrics: Dict[str, Any],
        campaign_type: str = "default"
    ) -> Dict[str, str]:
        """Generate marketing suggestions for a segment.
        
        Args:
            segment_name: Name of the customer segment
            segment_metrics: Segment performance metrics
            campaign_type: Type of campaign to generate
            
        Returns:
            Dictionary containing different marketing suggestions
        """
        try:
            prompt = PromptTemplates.get_marketing_prompt(
                campaign_type,
                segment_name=segment_name,
                metrics=json.dumps(segment_metrics, indent=2)
            )

            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": PromptTemplates.get_system_prompt("marketer")},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            suggestions = self._parse_marketing_suggestions(response.choices[0].message.content)
            return suggestions
        except Exception as e:
            logger.error(f"Error generating marketing suggestions: {str(e)}")
            return {
                "email_template": "Unable to generate email template.",
                "campaign_ideas": "Unable to generate campaign ideas.",
                "action_points": "Unable to generate action points."
            }

    async def generate_marketplace_content(
        self,
        content_type: str,
        **kwargs
    ) -> str:
        """Generate marketplace content.
        
        Args:
            content_type: Type of content to generate
            **kwargs: Additional parameters for the prompt
            
        Returns:
            Generated content
        """
        try:
            prompt = PromptTemplates.get_marketplace_prompt(content_type, **kwargs)
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": PromptTemplates.get_system_prompt("copywriter")},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating marketplace content: {str(e)}")
            return "Unable to generate content at this time."

    def _parse_marketing_suggestions(self, response_text: str) -> Dict[str, str]:
        """Parse the marketing suggestions from the response text."""
        sections = response_text.split("\n\n")
        result = {
            "email_template": "",
            "campaign_ideas": "",
            "action_points": ""
        }
        
        current_section = None
        for section in sections:
            if "EMAIL TEMPLATE:" in section:
                current_section = "email_template"
                result[current_section] = section.replace("EMAIL TEMPLATE:", "").strip()
            elif "CAMPAIGN IDEAS:" in section:
                current_section = "campaign_ideas"
                result[current_section] = section.replace("CAMPAIGN IDEAS:", "").strip()
            elif "ACTION POINTS:" in section:
                current_section = "action_points"
                result[current_section] = section.replace("ACTION POINTS:", "").strip()
            elif current_section:
                result[current_section] += "\n" + section.strip()
                
        return result 