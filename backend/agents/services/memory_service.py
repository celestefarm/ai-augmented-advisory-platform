# agents/services/memory_service.py

"""
Memory Service - Layer 1 Interface

Provides clean interface between API views and memory app.
Handles caching, context formatting, and memory updates.
"""

import logging
from typing import Optional, Dict, Any
from django.core.cache import cache
from django.contrib.auth import get_user_model

from memory.models import UserMemory, InteractionSession

logger = logging.getLogger(__name__)

User = get_user_model()


class MemoryService:
    """
    Service layer for memory operations
    
    Responsibilities:
    - Get/create user memory
    - Format memory for AI prompts
    - Update memory after interactions
    - Cache management
    """
    
    CACHE_TIMEOUT = 300  # 5 minutes
    
    def __init__(self):
        self.cache_prefix = "user_memory:"
    
    def get_user_memory(self, user_id: int) -> UserMemory:
        """
        Get user memory with caching
        
        Args:
            user_id: User ID
            
        Returns:
            UserMemory instance
        """
        # Try cache first
        cache_key = f"{self.cache_prefix}{user_id}"
        memory = cache.get(cache_key)
        
        if memory is not None:
            logger.debug(f"Memory cache HIT for user {user_id}")
            return memory
        
        # Cache miss - fetch from DB
        logger.debug(f"Memory cache MISS for user {user_id}")
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error(f"User {user_id} not found")
            raise
        
        # Get or create memory
        memory, created = UserMemory.objects.get_or_create_for_user(user)
        
        if created:
            logger.info(f"Created new memory for user {user_id}")
        
        # Cache it
        cache.set(cache_key, memory, self.CACHE_TIMEOUT)
        
        return memory
    
    def format_for_prompt(self, memory: UserMemory, user=None) -> str:
        """
        Format memory as context string for AI prompt
        
        Args:
            memory: UserMemory instance
            
        Returns:
            Formatted context string
        """
        if user is None:
            user = memory.user
        
        # Build context sections
        context_parts = [
            "=== User Context ===",
            "",
            "Profile:",
            f"- Name: {user.get_full_name() or user.email}",
            f"- Industry: {getattr(user, 'industry', 'Not specified')}",
            f"- Region: {getattr(user, 'region', 'Not specified')}",
            "",
            "Learning Profile:",
            f"- Expertise Level: {memory.get_expertise_level_display()}",
            f"- Decision Style: {memory.get_decision_style_display()}",
            f"- Total Interactions: {memory.interaction_count}",
        ]
        
        # Add common topics if available
        if memory.common_domains:
            domains_str = ', '.join(memory.common_domains)
            context_parts.extend([
                "",
                "Common Topics:",
                f"- {domains_str}"
            ])
        
        # Add recent interaction context
        if memory.recent_interactions:
            recent = memory.recent_interactions[0]  # Most recent
            
            context_parts.extend([
                "",
                "Recent Context:",
                f"- Last interaction: {recent.get('timestamp', 'Unknown')}",
                f"- Last question type: {recent.get('question_type', 'Unknown')}",
                f"- Last complexity: {recent.get('complexity', 'Unknown')}",
            ])
            
            # Add last question preview (first 100 chars)
            if recent.get('question'):
                preview = recent['question'][:100]
                if len(recent['question']) > 100:
                    preview += "..."
                context_parts.append(f"- Last question: \"{preview}\"")
        
        context_parts.append("")
        context_parts.append("=== End User Context ===")
        
        return "\n".join(context_parts)
    
    def update_after_interaction(
        self,
        user_id: int,
        agent_response
    ) -> None:
        """
        Update memory after an interaction
        
        Args:
            user_id: User ID
            agent_response: AgentResponse instance
        """
        try:
            memory = self.get_user_memory(user_id)
            
            # Add interaction to memory
            memory.add_interaction(agent_response)
            
            logger.info(
                f"Updated memory for user {user_id}: "
                f"interaction #{memory.interaction_count}"
            )
            
            # Invalidate cache to force refresh
            self.invalidate_cache(user_id)
            
        except Exception as e:
            logger.error(
                f"Error updating memory for user {user_id}: {str(e)}",
                exc_info=True
            )
            # Don't raise - memory updates shouldn't break the flow
    
    def invalidate_cache(self, user_id: int) -> None:
        """
        Invalidate cache for user memory
        
        Args:
            user_id: User ID
        """
        cache_key = f"{self.cache_prefix}{user_id}"
        cache.delete(cache_key)
        logger.debug(f"Invalidated memory cache for user {user_id}")
    
    def get_interaction_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get interaction statistics for user
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with stats
        """
        try:
            memory = self.get_user_memory(user_id)
            
            return {
                'total_interactions': memory.interaction_count,
                'expertise_level': memory.expertise_level,
                'decision_style': memory.decision_style,
                'common_domains': memory.common_domains,
                'common_question_types': memory.common_question_types,
                'last_interaction_at': memory.last_interaction_at.isoformat() if memory.last_interaction_at else None,
                'recent_interactions_count': len(memory.recent_interactions)
            }
            
        except Exception as e:
            logger.error(f"Error getting stats for user {user_id}: {str(e)}")
            return {}
    
    def create_session(self, user_id: int) -> InteractionSession:
        """
        Create new interaction session
        
        Args:
            user_id: User ID
            
        Returns:
            InteractionSession instance
        """
        memory = self.get_user_memory(user_id)
        
        session = InteractionSession.objects.create(
            user_memory=memory
        )
        
        logger.info(f"Created session {session.id} for user {user_id}")
        
        return session
    
    def end_session(
        self,
        session_id: str,
        questions_asked: int,
        average_confidence: float,
        topics: list
    ) -> None:
        """
        End interaction session with stats
        
        Args:
            session_id: Session UUID
            questions_asked: Number of questions in session
            average_confidence: Average confidence level
            topics: List of topics discussed
        """
        try:
            from django.utils import timezone
            
            session = InteractionSession.objects.get(id=session_id)
            session.session_end = timezone.now()
            session.questions_asked = questions_asked
            session.average_confidence = average_confidence
            session.topics_discussed = topics
            session.save()
            
            logger.info(
                f"Ended session {session_id}: "
                f"{questions_asked} questions, "
                f"avg confidence {average_confidence}%"
            )
            
        except InteractionSession.DoesNotExist:
            logger.error(f"Session {session_id} not found")
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {str(e)}")


# Singleton instance
_memory_service = None


def get_memory_service() -> MemoryService:
    """Get singleton memory service instance"""
    global _memory_service
    
    if _memory_service is None:
        _memory_service = MemoryService()
    
    return _memory_service


# Example usage
if __name__ == '__main__':
    """Test memory service"""
    import django
    import os
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    service = get_memory_service()
    
    # Test with user ID 1
    print("Testing Memory Service...")
    
    try:
        memory = service.get_user_memory(1)
        print(f"✅ Got memory: {memory}")
        
        context = service.format_for_prompt(memory)
        print("\n" + "=" * 80)
        print("FORMATTED CONTEXT:")
        print("=" * 80)
        print(context)
        
        stats = service.get_interaction_stats(1)
        print("\n" + "=" * 80)
        print("STATS:")
        print("=" * 80)
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n✅ Memory service working!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")