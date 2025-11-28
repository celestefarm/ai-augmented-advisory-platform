from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel, BaseModelManager

User = get_user_model()


class QuestionClassification(BaseModel):
    """
    Stores question classification metadata for analytics and routing
    """
    QUESTION_TYPES = [
        ('decision', _('Decision')),
        ('validation', _('Validation')),
        ('exploration', _('Exploration')),
        ('crisis', _('Crisis')),
    ]
    
    DOMAINS = [
        ('market', _('Market')),
        ('strategy', _('Strategy')),
        ('finance', _('Finance')),
        ('people', _('People')),
        ('execution', _('Execution')),
    ]
    
    URGENCY_LEVELS = [
        ('routine', _('Routine')),
        ('important', _('Important')),
        ('urgent', _('Urgent')),
        ('crisis', _('Crisis')),
    ]
    
    COMPLEXITY_LEVELS = [
        ('simple', _('Simple')),
        ('medium', _('Medium')),
        ('complex', _('Complex')),
    ]
    
    
    # Classification results
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, db_index=True)
    domains = models.JSONField(
        default=list,
        help_text=_('List of relevant domains (can be multiple)')
    )
    urgency = models.CharField(max_length=20, choices=URGENCY_LEVELS, db_index=True)
    complexity = models.CharField(max_length=20, choices=COMPLEXITY_LEVELS, db_index=True)
    
    # Classification confidence
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text=_('Classification confidence (0-1)')
    )
    
    # Detected patterns
    detected_patterns = models.JSONField(
        default=list,
        help_text=_('Keywords and patterns that influenced classification')
    )
    
    objects = BaseModelManager()
    
    class Meta(BaseModel.Meta): 
        db_table = 'question_classifications'
        verbose_name = _('question classification')
        verbose_name_plural = _('question classifications')
        indexes = [
            models.Index(fields=['question_type', 'urgency']),
            models.Index(fields=['complexity', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.question_type} - {self.urgency} - {self.complexity}"


class EmotionalState(BaseModel):
    """
    Tracks detected emotional state from user's language patterns
    """
    EMOTIONAL_STATES = [
        ('anxiety', _('Anxiety')),
        ('confidence', _('Confidence')),
        ('uncertainty', _('Uncertainty')),
        ('urgency', _('Urgency')),
        ('exploration', _('Exploration')),
    ]
  
    state = models.CharField(max_length=20, choices=EMOTIONAL_STATES, db_index=True)
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text=_('Detection confidence (0-1)')
    )
    detected_patterns = models.JSONField(
        default=list,
        help_text=_('Language patterns that indicated this emotional state')
    )
    tone_adjustment = models.JSONField(
        default=dict,
        help_text=_('How response tone was adjusted based on emotional state')
    )
    
    objects = BaseModelManager()
    
    class Meta(BaseModel.Meta):
        db_table = 'emotional_states'
        verbose_name = _('emotional state')
        verbose_name_plural = _('emotional states')
    
    def __str__(self):
        return f"{self.state} (confidence: {self.confidence_score:.2f})"


class ModelSelection(BaseModel):
    """Records which model was selected and why"""
    MODELS = [
        ('claude-sonnet-4-20250514', _('Claude Sonnet 4')),
        ('claude-opus-4-20250514', _('Claude Opus 4')),
        ('gemini-2.0-flash-exp', _('Gemini 2.0 Flash')),
        ('gemini-2.0-pro', _('Gemini 2.0 Pro')),
    ]
    
    
    model_name = models.CharField(max_length=100, choices=MODELS, db_index=True)
    selection_criteria = models.JSONField(
        default=dict,
        help_text=_('Criteria used for model selection')
    )
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        help_text=_('Estimated API cost in USD')
    )
    estimated_latency = models.FloatField(
        null=True,
        blank=True,
        help_text=_('Estimated response time in seconds')
    )
    
    objects = BaseModelManager() 
    
    class Meta(BaseModel.Meta):
        db_table = 'model_selections'
        verbose_name = _('model selection')
        verbose_name_plural = _('model selections')
    
    def __str__(self):
        return f"{self.model_name} - ${self.estimated_cost}"


class QualityGateCheck(BaseModel):
    """Records quality gate validation results before response delivery"""
    
    
    understands_context = models.BooleanField(
        default=False,
        help_text=_('Response references user situation')
    )
    addresses_question = models.BooleanField(
        default=False,
        help_text=_('Response directly addresses the question')
    )
    within_time_limit = models.BooleanField(
        default=False,
        help_text=_('Response generated within 12 seconds')
    )
    includes_reasoning = models.BooleanField(
        default=False,
        help_text=_('Response includes evidence/reasoning')
    )
    empowers_user = models.BooleanField(
        default=False,
        help_text=_('Response empowers user to decide (not prescriptive)')
    )
    overall_passed = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_('All quality gates passed')
    )
    response_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text=_('Actual response time')
    )
    failure_reasons = models.JSONField(
        default=list,
        help_text=_('Reasons for quality gate failures')
    )
    
    objects = BaseModelManager()
    
    class Meta(BaseModel.Meta):
        db_table = 'quality_gate_checks'
        verbose_name = _('quality gate check')
        verbose_name_plural = _('quality gate checks')
        indexes = [
            models.Index(fields=['overall_passed', 'created_at']),
        ]
    
    def __str__(self):
        return f"QualityCheck - {'Passed' if self.overall_passed else 'Failed'}"


class AgentResponse(BaseModel):
    """
    Stores complete agent response with all metadata
    This is the main model that ties everything together
    """
    CONFIDENCE_LEVELS = [
        ('high', _('High (85%+)')),
        ('medium', _('Medium (65-85%)')),
        ('low', _('Low (50-65%)')),
        ('speculative', _('Speculative (30-50%)')),
    ]
    
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='agent_responses',
        db_index=True
    )
    conversation = models.ForeignKey(
        'conversations.Conversation',
        on_delete=models.CASCADE,
        related_name='agent_responses',
        db_index=True,
        null=True,
        blank=True
    )
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='agent_responses',
        null=True,
        blank=True
    )
    user_question = models.TextField(help_text=_('Original user question'))
    agent_response = models.TextField(help_text=_('Generated agent response'))
    
    classification = models.ForeignKey(
        QuestionClassification,
        on_delete=models.CASCADE,
        related_name='agent_responses',
        null=True,
        blank=True
    )
    emotional_state = models.ForeignKey(
        EmotionalState,
        on_delete=models.CASCADE,
        related_name='agent_responses',
        null=True,
        blank=True
    )
    model_selection = models.ForeignKey(
        ModelSelection,
        on_delete=models.CASCADE,
        related_name='agent_responses',
        null=True,
        blank=True
    )
    quality_check = models.ForeignKey(
        QualityGateCheck,
        on_delete=models.CASCADE,
        related_name='agent_responses',
        null=True,
        blank=True
    )
    
    confidence_level = models.CharField(
        max_length=20,
        choices=CONFIDENCE_LEVELS,
        db_index=True
    )
    confidence_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Confidence percentage (0-100)')
    )
    confidence_explanation = models.TextField(
        blank=True,
        help_text=_('Explanation of confidence level')
    )
    
    total_tokens = models.IntegerField(default=0)
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    
    response_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text=_('Total response generation time')
    )
    api_cost = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        help_text=_('Actual API cost in USD')
    )
    
    is_streaming = models.BooleanField(
        default=False,
        help_text=_('Response is currently streaming')
    )
    streaming_started_at = models.DateTimeField(null=True, blank=True)
    streaming_completed_at = models.DateTimeField(null=True, blank=True)
    
    objects = BaseModelManager()
    
    class Meta(BaseModel.Meta):
        db_table = 'agent_responses'
        verbose_name = _('agent response')
        verbose_name_plural = _('agent responses')
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['confidence_level', 'created_at']),
            models.Index(fields=['is_streaming']),
        ]
    
    def __str__(self):
        return f"Response to: {self.user_question[:50]}... ({self.confidence_level})"
    
    @property
    def streaming_duration(self):
        """Calculate streaming duration if completed"""
        if self.streaming_started_at and self.streaming_completed_at:
            delta = self.streaming_completed_at - self.streaming_started_at
            return delta.total_seconds()
        return None
    
    def mark_streaming_started(self):
        """Mark response streaming as started"""
        self.is_streaming = True
        self.streaming_started_at = timezone.now()
        self.save(update_fields=['is_streaming', 'streaming_started_at'])
    
    def mark_streaming_completed(self):
        """Mark response streaming as completed"""
        self.is_streaming = False
        self.streaming_completed_at = timezone.now()
        self.save(update_fields=['is_streaming', 'streaming_completed_at'])
    
    def calculate_cost(self):
        """Calculate API cost using accurate pricing"""
        if not self.model_selection:
            return 0.0
        
        from agents.services.pricing import PricingCalculator
        
        calc = PricingCalculator()
        costs = calc.calculate_cost(
            model=self.model_selection.model_name,
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            cache_creation_tokens=0,
            cache_read_tokens=0
        )
        
        return float(costs['total_cost'])
    

class SpecialistAgentExecution(BaseModel):
    """
    Records individual specialist agent executions within orchestration
    """
    AGENT_TYPES = [
        ('market_compass', _('Market Compass')),
        ('financial_guardian', _('Financial Guardian')),
        ('strategy_analyst', _('Strategy Analyst')),
    ]
    
    agent_response = models.ForeignKey(
        AgentResponse,
        on_delete=models.CASCADE,
        related_name='specialist_executions'
    )
    agent_name = models.CharField(max_length=50, choices=AGENT_TYPES, db_index=True)
    agent_output = models.TextField()
    execution_time = models.FloatField()
    success = models.BooleanField(default=True, db_index=True)
    error_message = models.TextField(blank=True)
    
    # Token usage for this specific agent
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    
    objects = BaseModelManager()
    
    class Meta(BaseModel.Meta):
        db_table = 'specialist_agent_executions'
        verbose_name = _('specialist agent execution')
        verbose_name_plural = _('specialist agent executions')
        indexes = [
            models.Index(fields=['agent_response', 'created_at']),
            models.Index(fields=['agent_name', 'success']),
        ]
    
    def __str__(self):  # ✅ ADD THIS
        return f"{self.agent_name} - {self.execution_time:.2f}s ({'✓' if self.success else '✗'})"