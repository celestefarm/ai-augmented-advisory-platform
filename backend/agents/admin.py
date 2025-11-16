from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Avg, Sum
from .models import (
    AgentResponse,
    QuestionClassification,
    EmotionalState,
    ModelSelection,
    QualityGateCheck
)


@admin.register(AgentResponse)
class AgentResponseAdmin(admin.ModelAdmin):
    """
    Main admin interface for Agent Responses
    
    Features:
    - View all responses with key metrics
    - Filter by confidence, quality, date
    - Search by question content
    - Detailed response view with all metadata
    """
    
    list_display = [
        'response_id_short',
        'user_email',
        'question_preview',
        'confidence_badge',
        'quality_badge',
        'response_time_display',
        'cost_display',
        'created_date',
    ]
    
    list_filter = [
        'confidence_level',
        'is_streaming',
        'created_at',
    ]
    
    search_fields = [
        'user_question',
        'agent_response',
        'user__email',
    ]
    
    readonly_fields = [
        'id',
        'user',
        'conversation',
        'user_question',
        'agent_response_display',
        'classification_display',
        'emotional_state_display',
        'model_selection_display',
        'quality_check_display',
        'confidence_display',
        'tokens_display',
        'streaming_info',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Response Info', {
            'fields': ('id', 'user', 'conversation', 'created_at', 'updated_at')
        }),
        ('Question', {
            'fields': ('user_question',)
        }),
        ('AI Response', {
            'fields': ('agent_response_display',),
            'classes': ('wide',)
        }),
        ('Classification', {
            'fields': ('classification_display',)
        }),
        ('Emotional State', {
            'fields': ('emotional_state_display',)
        }),
        ('Model Selection', {
            'fields': ('model_selection_display',)
        }),
        ('Quality Check', {
            'fields': ('quality_check_display',)
        }),
        ('Confidence', {
            'fields': ('confidence_display',)
        }),
        ('Performance Metrics', {
            'fields': ('tokens_display', 'streaming_info')
        }),
    )
    
    def response_id_short(self, obj):
        """Display shortened UUID"""
        return str(obj.id)[:8] + '...'
    response_id_short.short_description = 'ID'
    
    def user_email(self, obj):
        """Display user email with link"""
        url = reverse('admin:authentication_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def question_preview(self, obj):
        """Display question preview"""
        preview = obj.user_question[:60]
        if len(obj.user_question) > 60:
            preview += '...'
        return preview
    question_preview.short_description = 'Question'
    
    def confidence_badge(self, obj):
        """Display confidence as colored badge"""
        colors = {
            'high': '#4CAF50',
            'medium': '#FF9800',
            'low': '#F44336',
            'speculative': '#9E9E9E',
        }
        color = colors.get(obj.confidence_level, '#9E9E9E')
        return format_html(
            '<span style="background-color:{};color:white;'
            'padding:4px 8px;border-radius:3px;font-weight:bold;">'
            '{} ({}%)</span>',
            color,
            obj.confidence_level.upper(),
            obj.confidence_percentage
        )
    confidence_badge.short_description = 'Confidence'
    confidence_badge.admin_order_field = 'confidence_level'
    
    def quality_badge(self, obj):
        """Display quality status"""
        if not obj.quality_check:
            return format_html('<span style="color:#999;">—</span>')
        
        if obj.quality_check.overall_passed:
            return format_html(
                '<span style="color:#4CAF50;font-weight:bold;">✓ PASS</span>'
            )
        return format_html(
            '<span style="color:#F44336;font-weight:bold;">✗ FAIL</span>'
        )
    quality_badge.short_description = 'Quality'
    
    def response_time_display(self, obj):
        """Display response time"""
        if obj.response_time_seconds:
            time = obj.response_time_seconds
            if time <= 12:
                color = '#4CAF50'  # Green (target met)
            elif time <= 15:
                color = '#FF9800'  # Orange
            else:
                color = '#F44336'  # Red
            
            # Format the time FIRST, then pass to format_html
            time_str = f'{time:.1f}s'
            return format_html(
                '<span style="color:{};">{}</span>',
                color, time_str
            )
        return '—'
    response_time_display.short_description = 'Time'
    response_time_display.admin_order_field = 'response_time_seconds'
    
    def cost_display(self, obj):
        """Display API cost"""
        if obj.api_cost:
            return f'${obj.api_cost:.4f}'
        return '—'
    cost_display.short_description = 'Cost'
    cost_display.admin_order_field = 'api_cost'
    
    def created_date(self, obj):
        """Display creation date"""
        from django.utils.timesince import timesince
        return f"{timesince(obj.created_at)} ago"
    created_date.short_description = 'Created'
    created_date.admin_order_field = 'created_at'
    
    # Detailed displays
    
    def classification_display(self, obj):
        if not obj.classification:
            return '—'
        
        c = obj.classification
        domains = ', '.join(c.domains) if c.domains else '—'
        return f"Type: {c.question_type} | Domains: {domains} | Urgency: {c.urgency} | Complexity: {c.complexity} | Confidence: {c.confidence_score:.0%}"

    def emotional_state_display(self, obj):
        if not obj.emotional_state:
            return '—'
        
        e = obj.emotional_state
        patterns = ', '.join(e.detected_patterns) if e.detected_patterns else '—'
        return f"State: {e.state} | Confidence: {e.confidence_score:.0%} | Patterns: {patterns}"

    def model_selection_display(self, obj):
        if not obj.model_selection:
            return '—'
        
        m = obj.model_selection
        return f"Model: {m.model_name} | Est. Cost: ${m.estimated_cost:.4f} | Est. Latency: {m.estimated_latency:.1f}s"

    def quality_check_display(self, obj):
        if not obj.quality_check:
            return '—'
        
        q = obj.quality_check
        status = 'PASS ✓' if q.overall_passed else 'FAIL ✗'
        return f"Context: {'✓' if q.understands_context else '✗'} | Question: {'✓' if q.addresses_question else '✗'} | Time: {'✓' if q.within_time_limit else '✗'} | Reasoning: {'✓' if q.includes_reasoning else '✗'} | Empowers: {'✓' if q.empowers_user else '✗'} | Overall: {status}"

    def confidence_display(self, obj):
        explanation = obj.confidence_explanation or '—'
        return f"Level: {obj.confidence_level} | Percentage: {obj.confidence_percentage}% | Explanation: {explanation}"

    def tokens_display(self, obj):
        cost = f"${obj.api_cost:.4f}" if obj.api_cost else "$0.0000"
        return f"Prompt: {obj.prompt_tokens:,} | Completion: {obj.completion_tokens:,} | Total: {obj.total_tokens:,} | Cost: {cost}"

    def streaming_info(self, obj):
        if not obj.streaming_started_at:
            return 'Not streamed'
        
        duration = obj.streaming_duration
        if duration:
            started = obj.streaming_started_at.strftime('%H:%M:%S')
            completed = obj.streaming_completed_at.strftime('%H:%M:%S') if obj.streaming_completed_at else '—'
            return f"Started: {started} | Completed: {completed} | Duration: {duration:.2f}s"
        return 'In progress...'

    def agent_response_display(self, obj):
        return obj.agent_response  # Just show the text, no HTML
        def has_add_permission(self, request):
            """Disable manual creation"""
            return False
        
        def has_delete_permission(self, request, obj=None):
            """Allow deletion only for superusers"""
            return request.user.is_superuser


@admin.register(QuestionClassification)
class QuestionClassificationAdmin(admin.ModelAdmin):
    """Admin for question classifications"""
    
    list_display = [
        'id_short',
        'question_type',
        'domains_display',
        'urgency',
        'complexity',
        'confidence_display',
        'created',
    ]
    
    list_filter = ['question_type', 'urgency', 'complexity', 'created_at']
    
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def domains_display(self, obj):
        if not obj.domains:
            return '—'
        return ', '.join(obj.domains[:3])
    domains_display.short_description = 'Domains'
    
    def confidence_display(self, obj):
        return f'{obj.confidence_score:.0%}'
    confidence_display.short_description = 'Confidence'
    
    def created(self, obj):
        from django.utils.timesince import timesince
        return f"{timesince(obj.created_at)} ago"
    created.short_description = 'Created'
    
    def has_add_permission(self, request):
        return False


@admin.register(EmotionalState)
class EmotionalStateAdmin(admin.ModelAdmin):
    """Admin for emotional states"""
    
    list_display = ['id_short', 'state', 'confidence_display', 'created']
    list_filter = ['state', 'created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def confidence_display(self, obj):
        return f'{obj.confidence_score:.0%}'
    confidence_display.short_description = 'Confidence'
    
    def created(self, obj):
        from django.utils.timesince import timesince
        return f"{timesince(obj.created_at)} ago"
    created.short_description = 'Created'
    
    def has_add_permission(self, request):
        return False


@admin.register(ModelSelection)
class ModelSelectionAdmin(admin.ModelAdmin):
    """Admin for model selections"""
    
    list_display = [
        'id_short',
        'model_name',
        'estimated_cost_display',
        'estimated_latency_display',
        'created',
    ]
    
    list_filter = ['model_name', 'created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def estimated_cost_display(self, obj):
        return f'${obj.estimated_cost:.4f}'
    estimated_cost_display.short_description = 'Est. Cost'
    
    def estimated_latency_display(self, obj):
        return f'{obj.estimated_latency:.1f}s'
    estimated_latency_display.short_description = 'Est. Time'
    
    def created(self, obj):
        from django.utils.timesince import timesince
        return f"{timesince(obj.created_at)} ago"
    created.short_description = 'Created'
    
    def has_add_permission(self, request):
        return False


@admin.register(QualityGateCheck)
class QualityGateCheckAdmin(admin.ModelAdmin):
    """Admin for quality gate checks"""
    
    list_display = [
        'id_short',
        'overall_status',
        'checks_summary',
        'response_time_display',
        'created',
    ]
    
    list_filter = ['overall_passed', 'created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def overall_status(self, obj):
        if obj.overall_passed:
            return format_html('<span style="color:#4CAF50;font-weight:bold;">✓ PASS</span>')
        return format_html('<span style="color:#F44336;font-weight:bold;">✗ FAIL</span>')
    overall_status.short_description = 'Status'
    
    def checks_summary(self, obj):
        passed = sum([
            obj.understands_context,
            obj.addresses_question,
            obj.within_time_limit,
            obj.includes_reasoning,
            obj.empowers_user,
        ])
        return f'{passed}/5'
    checks_summary.short_description = 'Checks'
    
    def response_time_display(self, obj):
        if obj.response_time_seconds:
            return f'{obj.response_time_seconds:.1f}s'
        return '—'
    response_time_display.short_description = 'Time'
    
    def created(self, obj):
        from django.utils.timesince import timesince
        return f"{timesince(obj.created_at)} ago"
    created.short_description = 'Created'
    
    def has_add_permission(self, request):
        return False