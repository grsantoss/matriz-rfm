"""Centralized prompts configuration for AI operations."""

from typing import Dict

class PromptTemplates:
    # System prompts define the AI's role
    SYSTEM_PROMPTS = {
        "analyst": "You are an expert in customer behavior analysis and marketing strategy, specializing in RFM (Recency, Frequency, Monetary) analysis. You provide detailed, actionable insights based on customer data.",
        "marketer": "You are an expert marketing strategist specializing in customer segmentation and personalized marketing. You create engaging, conversion-focused content tailored to specific customer segments.",
        "copywriter": "You are a professional copywriter specializing in marketing communications. You create compelling, personalized content that resonates with specific customer segments while maintaining brand voice and marketing best practices."
    }

    # Segment analysis prompts
    SEGMENT_ANALYSIS = {
        "default": """
        Analyze the following customer segment data and provide detailed insights:

        Segment: {segment_name}
        
        Metrics:
        - Average Recency Score: {avg_recency}
        - Average Frequency Score: {avg_frequency}
        - Average Monetary Score: {avg_monetary}
        - Segment Size: {size} customers
        - Percentage of Total: {percentage}%

        Please provide:
        1. Key characteristics of this segment
        2. Behavioral patterns
        3. Potential opportunities
        4. Risk factors
        5. Recommended focus areas
        """,
        
        "champions": """
        Analyze our Champions segment - our most valuable customers:

        Metrics:
        {metrics}

        Focus on:
        1. What makes these customers so valuable
        2. How to maintain their loyalty
        3. How to create more customers like them
        4. Early warning signs of potential churn
        5. Premium service opportunities
        """,
        
        "at_risk": """
        Analyze our At-Risk customers who need immediate attention:

        Metrics:
        {metrics}

        Focus on:
        1. Common reasons for decreased engagement
        2. Reactivation opportunities
        3. Immediate action steps
        4. Value retention strategies
        5. Churn prevention tactics
        """
    }

    # Marketing suggestion prompts
    MARKETING_SUGGESTIONS = {
        "default": """
        Generate marketing suggestions for the following customer segment:

        Segment: {segment_name}
        
        Metrics:
        {metrics}

        Please provide:
        1. Email Template: A personalized email template for this segment
        2. Campaign Ideas: 3 specific marketing campaign ideas
        3. Action Points: 5 immediate actions to engage this segment

        Format the response as:
        EMAIL TEMPLATE:
        [Template here]

        CAMPAIGN IDEAS:
        1. [Idea 1]
        2. [Idea 2]
        3. [Idea 3]

        ACTION POINTS:
        1. [Action 1]
        2. [Action 2]
        etc.
        """,
        
        "reactivation": """
        Create a reactivation campaign for dormant customers:

        Segment Data:
        {metrics}

        Focus on:
        1. Re-engagement email sequence
        2. Special comeback offers
        3. Personalized incentives
        4. Trust-building messages
        5. Value proposition reminder

        Include specific subject lines and call-to-action phrases.
        """,
        
        "loyalty_program": """
        Design a loyalty program campaign for high-value customers:

        Segment Data:
        {metrics}

        Include:
        1. Program structure
        2. Tier benefits
        3. Exclusive offers
        4. VIP perks
        5. Communication strategy

        Provide specific examples of rewards and recognition elements.
        """
    }

    # Marketplace content prompts
    MARKETPLACE_CONTENT = {
        "product_description": """
        Create a compelling product description for:
        {product_name}

        Key Features:
        {features}

        Target Segment:
        {segment}

        Include:
        1. Unique value proposition
        2. Key benefits
        3. Technical specifications
        4. Use cases
        5. Call to action
        """,
        
        "email_campaign": """
        Generate an email campaign for:
        Product: {product_name}
        Segment: {segment_name}
        Campaign Type: {campaign_type}

        Include:
        1. Subject line options (3)
        2. Email body
        3. Call-to-action buttons
        4. Follow-up email template
        5. A/B testing variants
        """,
        
        "social_media": """
        Create social media content for:
        Platform: {platform}
        Product: {product_name}
        Target: {segment}

        Deliverables:
        1. Post copy (3 variants)
        2. Hashtag suggestions
        3. Call-to-action options
        4. Engagement prompts
        5. Content calendar suggestions
        """
    }

    @classmethod
    def get_system_prompt(cls, role: str) -> str:
        """Get system prompt for a specific AI role."""
        return cls.SYSTEM_PROMPTS.get(role, cls.SYSTEM_PROMPTS["analyst"])

    @classmethod
    def get_segment_prompt(cls, segment_type: str, **kwargs) -> str:
        """Get segment analysis prompt with formatted parameters."""
        prompt_template = cls.SEGMENT_ANALYSIS.get(segment_type, cls.SEGMENT_ANALYSIS["default"])
        return prompt_template.format(**kwargs)

    @classmethod
    def get_marketing_prompt(cls, campaign_type: str, **kwargs) -> str:
        """Get marketing suggestion prompt with formatted parameters."""
        prompt_template = cls.MARKETING_SUGGESTIONS.get(campaign_type, cls.MARKETING_SUGGESTIONS["default"])
        return prompt_template.format(**kwargs)

    @classmethod
    def get_marketplace_prompt(cls, content_type: str, **kwargs) -> str:
        """Get marketplace content prompt with formatted parameters."""
        prompt_template = cls.MARKETPLACE_CONTENT.get(content_type, cls.MARKETPLACE_CONTENT["product_description"])
        return prompt_template.format(**kwargs) 