# memory/models.py

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

User = get_user_model()


class BaseModel(models.Model):
    """Abstract base model with common fields"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModelManager(models.Manager):
    """Base manager with common query methods"""
    pass


class UserMemoryManager(BaseModelManager):
    """Custom manager for UserMemory"""
    
    def get_or_create_for_user(self, user):
        """Get or create memory for user with defaults"""
        memory, created = self.get_or_create(
            user=user,
            defaults={
                'expertise_level': 'novice',
                'decision_style': 'balanced',
                'interaction_count': 0,
            }
        )
        return memory, created
    
    def increment_interaction(self, user):
        """Increment interaction count for user"""
        memory = self.get_or_create_for_user(user)[0]
        memory.interaction_count += 1
        memory.last_interaction_at = timezone.now()
        memory.save(update_fields=['interaction_count', 'last_interaction_at'])
        return memory


class UserMemory(BaseModel):
    """
    Layer 1: Interaction Memory
    Stores user context and recent interaction history
    """
    EXPERTISE_LEVELS = [
        ('novice', _('Novice')),
        ('intermediate', _('Intermediate')),
        ('advanced', _('Advanced')),
        ('expert', _('Expert')),
    ]
    
    DECISION_STYLES = [
        ('analytical', _('Analytical')),
        ('intuitive', _('Intuitive')),
        ('balanced', _('Balanced')),
        ('collaborative', _('Collaborative')),
    ]
    
    # User relationship
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='memory',
        db_index=True
    )
    
    # User profile (learned from interactions)
    expertise_level = models.CharField(
        max_length=20,
        choices=EXPERTISE_LEVELS,
        default='novice',
        db_index=True,
        help_text=_('User expertise level (estimated from questions)')
    )
    decision_style = models.CharField(
        max_length=20,
        choices=DECISION_STYLES,
        default='balanced',
        db_index=True,
        help_text=_('Preferred decision-making approach')
    )
    
    # Interaction tracking
    interaction_count = models.IntegerField(
        default=0,
        help_text=_('Total number of interactions')
    )
    last_interaction_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_('Last time user interacted')
    )
    
    # Recent interactions (stored as JSON for Layer 1)
    recent_interactions = models.JSONField(
        default=list,
        help_text=_('Last 20 interactions with full metadata')
    )
    
    # Detected patterns
    common_domains = models.JSONField(
        default=list,
        help_text=_('Most common domains user asks about')
    )
    common_question_types = models.JSONField(
        default=list,
        help_text=_('Most common question types')
    )
    
    # Firebase sync (for later - Week 5+)
    firebase_doc_id = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Firestore document ID for sync (Week 5+)')
    )
    last_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Last time synced with Firestore (Week 5+)')
    )
    
    objects = UserMemoryManager()
    
    class Meta:
        db_table = 'user_memories'
        verbose_name = _('user memory')
        verbose_name_plural = _('user memories')
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'expertise_level']),
            models.Index(fields=['last_interaction_at']),
        ]
    
    def __str__(self):
        return f"Memory for {self.user.email} ({self.expertise_level})"
    
    def add_interaction(self, agent_response):
        """
        Add new interaction to recent_interactions
        Keep only last 20 interactions
        
        Args:
            agent_response: AgentResponse instance
        """
        interaction = {
            'response_id': str(agent_response.id),
            'question': agent_response.user_question,
            'response': agent_response.agent_response,
            'question_type': agent_response.classification.question_type if agent_response.classification else None,
            'domains': agent_response.classification.domains if agent_response.classification else [],
            'urgency': agent_response.classification.urgency if agent_response.classification else None,
            'complexity': agent_response.classification.complexity if agent_response.classification else None,
            'emotional_state': agent_response.emotional_state.state if agent_response.emotional_state else None,
            'confidence_level': agent_response.confidence_level,
            'confidence_percentage': agent_response.confidence_percentage,
            'timestamp': agent_response.created_at.isoformat(),
        }
        
        # Add to beginning of list
        self.recent_interactions.insert(0, interaction)
        
        # Keep only last 20
        self.recent_interactions = self.recent_interactions[:20]
        
        # Update interaction count
        self.interaction_count += 1
        self.last_interaction_at = timezone.now()
        
        # Update expertise level based on complexity
        self._update_expertise_level()
        
        # Update common patterns
        self._update_common_patterns()
        
        self.save()
    
    def _update_expertise_level(self):
        """
        Estimate expertise level based on recent question complexity
        Algorithm: Count complex questions in last 10 interactions
        - 0-2 complex: novice
        - 3-5 complex: intermediate
        - 6-8 complex: advanced
        - 9-10 complex: expert
        """
        if not self.recent_interactions:
            return
        
        last_10 = self.recent_interactions[:10]
        complex_count = sum(1 for i in last_10 if i.get('complexity') == 'complex')
        
        if complex_count >= 9:
            self.expertise_level = 'expert'
        elif complex_count >= 6:
            self.expertise_level = 'advanced'
        elif complex_count >= 3:
            self.expertise_level = 'intermediate'
        else:
            self.expertise_level = 'novice'
    
    def _update_common_patterns(self):
        """
        Update common domains and question types from recent interactions
        """
        if not self.recent_interactions:
            return
        
        # Count domains
        domain_counts = {}
        question_type_counts = {}
        
        for interaction in self.recent_interactions:
            # Count domains
            for domain in interaction.get('domains', []):
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            # Count question types
            qtype = interaction.get('question_type')
            if qtype:
                question_type_counts[qtype] = question_type_counts.get(qtype, 0) + 1
        
        # Sort by frequency and keep top 3
        self.common_domains = sorted(
            domain_counts.keys(),
            key=lambda x: domain_counts[x],
            reverse=True
        )[:3]
        
        self.common_question_types = sorted(
            question_type_counts.keys(),
            key=lambda x: question_type_counts[x],
            reverse=True
        )[:3]
    
    def get_context_for_prompt(self):
        """
        Generate context string for AI prompt personalization
        Returns formatted context about user
        """
        context_parts = []
        
        # Expertise level
        context_parts.append(f"User expertise: {self.expertise_level}")
        
        # Decision style
        context_parts.append(f"Decision style: {self.decision_style}")
        
        # Common domains
        if self.common_domains:
            domains_str = ', '.join(self.common_domains)
            context_parts.append(f"Common topics: {domains_str}")
        
        # Recent interaction summary
        if self.recent_interactions:
            recent_count = len(self.recent_interactions)
            context_parts.append(f"Recent interactions: {recent_count}")
            
            # Get last interaction context
            last_interaction = self.recent_interactions[0]
            if last_interaction.get('question'):
                context_parts.append(f"Last question was about: {last_interaction['question'][:100]}...")
        
        return "\n".join(context_parts)
    
    def sync_to_firestore(self):
        """
        Sync to Firestore (only in production - Week 5+)
        For local dev, this is a no-op
        """
        if not getattr(settings, 'USE_FIRESTORE', False):
            # Skip Firestore sync in local development
            return
        
        # Week 5+: Implement Firestore sync
        # from firebase_admin import firestore
        # db = firestore.client()
        # db.collection('user_memories').document(str(self.user.id)).set(self.to_firestore_dict())
        pass
    
    def to_firestore_dict(self):
        """Convert to Firestore-compatible dictionary (for Week 5+)"""
        return {
            'user_id': str(self.user.id),
            'expertise_level': self.expertise_level,
            'decision_style': self.decision_style,
            'interaction_count': self.interaction_count,
            'last_interaction_at': self.last_interaction_at.isoformat() if self.last_interaction_at else None,
            'recent_interactions': self.recent_interactions,
            'common_domains': self.common_domains,
            'common_question_types': self.common_question_types,
            'updated_at': self.updated_at.isoformat(),
        }


class InteractionSession(BaseModel):
    """
    Tracks individual interaction sessions for analytics
    """
    
    user_memory = models.ForeignKey(
        UserMemory,
        on_delete=models.CASCADE,
        related_name='sessions',
        db_index=True
    )
    
    # Session metadata
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)
    
    # Interaction counts
    questions_asked = models.IntegerField(default=0)
    average_confidence = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    
    # Topics covered
    topics_discussed = models.JSONField(
        default=list,
        help_text=_('Domains and topics covered in session')
    )
    
    objects = BaseModelManager()
    
    class Meta:
        db_table = 'interaction_sessions'
        verbose_name = _('interaction session')
        verbose_name_plural = _('interaction sessions')
        ordering = ['-session_start']
        indexes = [
            models.Index(fields=['user_memory', 'session_start']),
        ]
    
    def __str__(self):
        return f"Session {self.id} - {self.questions_asked} questions"
    
    @property
    def duration(self):
        """Calculate session duration if ended"""
        if self.session_end:
            return (self.session_end - self.session_start).total_seconds()
        return None