"""
Content filtering utilities for NSFW mode and content safety
"""

from typing import Dict, Any
from utils.database import MessageDatabase

class ContentFilter:
    """Handles content filtering based on user settings"""
    
    def __init__(self, db: MessageDatabase):
        self.db = db
        
        # Define content filter prompts for different levels
        self.filter_prompts = {
            'strict': {
                'system_addition': "\n\nIMPORTANT CONTENT GUIDELINES:\n"
                                 "- You must maintain strict content filtering\n"
                                 "- Avoid any sexual, violent, or inappropriate content\n"
                                 "- Decline requests for NSFW content politely\n"
                                 "- Keep all responses family-friendly and appropriate\n"
                                 "- If asked about mature topics, provide educational information only\n"
                                 "- Do not generate, describe, or discuss explicit content",
                'decline_message': "I'm configured to maintain family-friendly content. I can't assist with that request, but I'd be happy to help with something else!"
            },
            'moderate': {
                'system_addition': "\n\nCONTENT GUIDELINES:\n"
                                 "- You can discuss mature topics in an educational or informational context\n"
                                 "- Avoid explicit sexual content or graphic violence\n"
                                 "- You may discuss relationships, health topics, and social issues appropriately\n"
                                 "- Keep responses tasteful and informative\n"
                                 "- Decline requests for explicit content politely",
                'decline_message': "I can discuss mature topics in an educational context, but I can't provide explicit content. Let me know if you'd like information on this topic in an appropriate way."
            },
            'minimal': {
                'system_addition': "\n\nCONTENT GUIDELINES (NSFW MODE ACTIVE):\n"
                                 "- NSFW mode is enabled for this user\n"
                                 "- You may discuss mature and adult content when requested\n"
                                 "- Still maintain respect and avoid harmful content\n"
                                 "- You can provide information on adult topics, relationships, and sexuality\n"
                                 "- Always prioritize user safety and well-being\n"
                                 "- Follow Discord's Terms of Service and community guidelines\n"
                                 "- Be helpful while remaining responsible",
                'decline_message': "While NSFW mode is enabled, I still need to prioritize safety and follow platform guidelines. Let me know if you'd like to discuss this topic in a different way."
            }
        }
    
    async def get_user_content_settings(self, user_id: str) -> Dict[str, Any]:
        """Get user's content filtering settings"""
        try:
            settings = await self.db.get_user_settings(user_id)
            return {
                'nsfw_mode': settings.get('nsfw_mode', False),
                'content_filter_level': settings.get('content_filter_level', 'strict'),
                'user_id': user_id
            }
        except Exception as e:
            print(f"Error getting user content settings: {e}")
            # Return safe defaults on error
            return {
                'nsfw_mode': False,
                'content_filter_level': 'strict',
                'user_id': user_id
            }
    
    def get_system_prompt_addition(self, content_settings: Dict[str, Any]) -> str:
        """Get the system prompt addition based on user's content settings"""
        filter_level = content_settings.get('content_filter_level', 'strict')
        nsfw_mode = content_settings.get('nsfw_mode', False)
        
        # If NSFW mode is disabled, always use strict filtering
        if not nsfw_mode and filter_level in ['moderate', 'minimal']:
            filter_level = 'strict'
        
        # If NSFW mode is enabled but filter level is minimal, use minimal
        if nsfw_mode and filter_level == 'minimal':
            filter_level = 'minimal'
        elif nsfw_mode and filter_level in ['strict', 'moderate']:
            # User has NSFW enabled but chose a more restrictive filter
            filter_level = filter_level
        
        return self.filter_prompts.get(filter_level, self.filter_prompts['strict'])['system_addition']
    
    def get_decline_message(self, content_settings: Dict[str, Any]) -> str:
        """Get appropriate decline message based on user's content settings"""
        filter_level = content_settings.get('content_filter_level', 'strict')
        nsfw_mode = content_settings.get('nsfw_mode', False)
        
        # If NSFW mode is disabled, always use strict filtering
        if not nsfw_mode:
            filter_level = 'strict'
        
        return self.filter_prompts.get(filter_level, self.filter_prompts['strict'])['decline_message']
    
    def should_allow_nsfw_content(self, content_settings: Dict[str, Any]) -> bool:
        """Check if NSFW content should be allowed for this user"""
        nsfw_mode = content_settings.get('nsfw_mode', False)
        filter_level = content_settings.get('content_filter_level', 'strict')
        
        # NSFW content is only allowed if:
        # 1. NSFW mode is explicitly enabled
        # 2. Content filter level is set to minimal
        return nsfw_mode and filter_level == 'minimal'
    
    def get_content_warning_message(self, content_settings: Dict[str, Any]) -> str:
        """Get content warning message if applicable"""
        if self.should_allow_nsfw_content(content_settings):
            return "⚠️ **NSFW Mode Active** - Content filtering is minimal. Please use responsibly.\n\n"
        return ""
    
    async def check_and_filter_content(self, user_id: str, content: str) -> Dict[str, Any]:
        """
        Check content against user's filtering settings
        Returns dict with 'allowed', 'filtered_content', 'warning_message'
        """
        content_settings = await self.get_user_content_settings(user_id)
        
        # For now, we'll rely on the AI model's built-in filtering
        # and the system prompt modifications
        # This method can be extended with custom content analysis if needed
        
        return {
            'allowed': True,  # Let the AI handle filtering based on system prompt
            'filtered_content': content,
            'warning_message': self.get_content_warning_message(content_settings),
            'content_settings': content_settings
        }
    
    def get_filter_status_emoji(self, content_settings: Dict[str, Any]) -> str:
        """Get emoji representing current filter status"""
        if self.should_allow_nsfw_content(content_settings):
            return "🔞"
        elif content_settings.get('content_filter_level') == 'moderate':
            return "🛡️"
        else:
            return "✅"
    
    def get_filter_status_text(self, content_settings: Dict[str, Any]) -> str:
        """Get text description of current filter status"""
        nsfw_mode = content_settings.get('nsfw_mode', False)
        filter_level = content_settings.get('content_filter_level', 'strict')
        
        if nsfw_mode and filter_level == 'minimal':
            return "NSFW Mode (Minimal Filtering)"
        elif nsfw_mode and filter_level == 'moderate':
            return "NSFW Mode (Moderate Filtering)"
        elif nsfw_mode and filter_level == 'strict':
            return "NSFW Mode (Strict Filtering)"
        elif filter_level == 'moderate':
            return "Moderate Filtering"
        else:
            return "Strict Filtering"

# Utility function for easy access
async def get_content_filter_for_user(user_id: str, db: MessageDatabase = None) -> ContentFilter:
    """Get a ContentFilter instance for a specific user"""
    if db is None:
        db = MessageDatabase("data/bot_messages.db")
    
    return ContentFilter(db)
