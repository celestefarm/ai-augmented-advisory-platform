# memory/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import UserMemory, InteractionSession


@admin.register(UserMemory)
class UserMemoryAdmin(admin.ModelAdmin):

    list_display = [
        'user_email',
        'expertise_level',
        'decision_style',
        'interaction_count',
        'last_interaction',
        'common_domains_display',
        'sync_status',
    ]
    
    list_filter = [
        'expertise_level',
        'decision_style',
        'last_interaction_at',
    ]
    
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
    ]
    
    readonly_fields = [
        'id',
        'user',
        'interaction_count',
        'last_interaction_at',
        'created_at',
        'updated_at',
        'recent_interactions_display',
        'common_domains_display',
        'common_question_types_display',
        'firebase_doc_id',
        'last_synced_at',
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('id', 'user', 'created_at', 'updated_at')
        }),
        ('Learning Profile', {
            'fields': ('expertise_level', 'decision_style'),
            'description': 'User expertise and decision-making style (learned from interactions)'
        }),
        ('Interaction Stats', {
            'fields': (
                'interaction_count',
                'last_interaction_at',
            )
        }),
        ('Detected Patterns', {
            'fields': (
                'common_domains_display',
                'common_question_types_display',
            ),
            'description': 'Patterns detected from user questions'
        }),
        ('Recent Interactions', {
            'fields': ('recent_interactions_display',),
            'classes': ('collapse',),
        }),
        ('Firebase Sync (Week 5+)', {
            'fields': ('firebase_doc_id', 'last_synced_at'),
            'classes': ('collapse',),
        }),
    )
    
    def user_email(self, obj):
        """Display user email with link to user admin"""
        url = reverse('admin:authentication_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def last_interaction(self, obj):
        """Display last interaction time in human-readable format"""
        if obj.last_interaction_at:
            from django.utils.timesince import timesince
            return f"{timesince(obj.last_interaction_at)} ago"
        return "Never"
    last_interaction.short_description = 'Last Interaction'
    last_interaction.admin_order_field = 'last_interaction_at'
    
    def common_domains_display(self, obj):
        """Display common domains as badges"""
        if not obj.common_domains:
            return "—"
        
        badges = []
        colors = {
            'market': '#4CAF50',
            'strategy': '#2196F3',
            'finance': '#FF9800',
            'people': '#9C27B0',
            'execution': '#F44336',
        }
        
        for domain in obj.common_domains[:3]:  # Show top 3
            color = colors.get(domain, '#757575')
            badges.append(
                f'<span style="background-color:{color};color:white;'
                f'padding:2px 8px;border-radius:3px;margin-right:4px;">'
                f'{domain}</span>'
            )
        
        return mark_safe(''.join(badges))
    common_domains_display.short_description = 'Common Topics'
    
    def common_question_types_display(self, obj):
        """Display common question types"""
        if not obj.common_question_types:
            return "—"
        return ", ".join(obj.common_question_types)
    common_question_types_display.short_description = 'Question Types'
    
    def recent_interactions_display(self, obj):
        """Display recent interactions in a formatted table"""
        if not obj.recent_interactions:
            return "No interactions yet"
        
        html = ['<table style="width:100%;border-collapse:collapse;">']
        html.append(
            '<tr style="background-color:#f5f5f5;">'
            '<th style="padding:8px;text-align:left;">Question</th>'
            '<th style="padding:8px;text-align:left;">Type</th>'
            '<th style="padding:8px;text-align:left;">Domains</th>'
            '<th style="padding:8px;text-align:left;">Confidence</th>'
            '<th style="padding:8px;text-align:left;">Time</th>'
            '</tr>'
        )
        
        for interaction in obj.recent_interactions[:5]:  # Show last 5
            question = interaction.get('question', 'Unknown')
            if len(question) > 80:
                question = question[:80] + '...'
            
            qtype = interaction.get('question_type', '—')
            domains = ', '.join(interaction.get('domains', [])) or '—'
            confidence = f"{interaction.get('confidence_percentage', 0)}%"
            timestamp = interaction.get('timestamp', '—')
            
            # Confidence color
            conf_pct = interaction.get('confidence_percentage', 0)
            if conf_pct >= 80:
                conf_color = '#4CAF50'
            elif conf_pct >= 60:
                conf_color = '#FF9800'
            else:
                conf_color = '#F44336'
            
            html.append(
                f'<tr style="border-bottom:1px solid #ddd;">'
                f'<td style="padding:8px;">{question}</td>'
                f'<td style="padding:8px;">{qtype}</td>'
                f'<td style="padding:8px;">{domains}</td>'
                f'<td style="padding:8px;color:{conf_color};font-weight:bold;">{confidence}</td>'
                f'<td style="padding:8px;font-size:0.9em;">{timestamp[:10]}</td>'
                f'</tr>'
            )
        
        html.append('</table>')
        
        if len(obj.recent_interactions) > 5:
            html.append(
                f'<p style="margin-top:10px;color:#666;font-style:italic;">'
                f'Showing 5 of {len(obj.recent_interactions)} interactions'
                f'</p>'
            )
        
        return mark_safe(''.join(html))
    recent_interactions_display.short_description = 'Recent Interactions'
    
    def sync_status(self, obj):
        """Display Firebase sync status"""
        if obj.last_synced_at:
            return format_html(
                '<span style="color:green;">✓ Synced</span>'
            )
        elif obj.firebase_doc_id:
            return format_html(
                '<span style="color:orange;">⚠ Pending</span>'
            )
        return format_html(
            '<span style="color:gray;">— Not synced</span>'
        )
    sync_status.short_description = 'Firebase Sync'
    
    def has_add_permission(self, request):
        """Disable manual creation (auto-created via get_or_create)"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion only for superusers"""
        return request.user.is_superuser


@admin.register(InteractionSession)
class InteractionSessionAdmin(admin.ModelAdmin):
    """
    Admin interface for InteractionSession
    
    Features:
    - View session analytics
    - Filter by date and duration
    - Track questions per session
    """
    
    list_display = [
        'session_id_short',
        'user_email',
        'session_start',
        'duration_display',
        'questions_asked',
        'average_confidence',
        'topics_display',
    ]
    
    list_filter = [
        'session_start',
        'session_end',
    ]
    
    search_fields = [
        'user_memory__user__email',
        'id',
    ]
    
    readonly_fields = [
        'id',
        'user_memory',
        'session_start',
        'session_end',
        'duration_display',
        'questions_asked',
        'average_confidence',
        'topics_discussed',
    ]
    
    fieldsets = (
        ('Session Info', {
            'fields': ('id', 'user_memory', 'session_start', 'session_end', 'duration_display')
        }),
        ('Session Stats', {
            'fields': ('questions_asked', 'average_confidence', 'topics_discussed')
        }),
    )
    
    def session_id_short(self, obj):
        """Display shortened session ID"""
        return str(obj.id)[:8] + '...'
    session_id_short.short_description = 'Session ID'
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user_memory.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user_memory__user__email'
    
    def duration_display(self, obj):
        """Display session duration"""
        if obj.duration:
            minutes = int(obj.duration / 60)
            seconds = int(obj.duration % 60)
            return f"{minutes}m {seconds}s"
        return "In progress..." if not obj.session_end else "0s"
    duration_display.short_description = 'Duration'
    
    def topics_display(self, obj):
        """Display topics as comma-separated list"""
        if not obj.topics_discussed:
            return "—"
        return ", ".join(obj.topics_discussed[:3])
    topics_display.short_description = 'Topics'
    
    def has_add_permission(self, request):
        """Disable manual creation"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Read-only (sessions are auto-managed)"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion only for superusers"""
        return request.user.is_superuser


# Optional: Inline for viewing sessions in UserMemory admin
class InteractionSessionInline(admin.TabularInline):
    """
    Display recent sessions inline in UserMemory admin
    """
    model = InteractionSession
    extra = 0
    max_num = 5
    can_delete = False
    
    fields = [
        'session_start',
        'questions_asked',
        'average_confidence',
    ]
    
    readonly_fields = fields
    
    def has_add_permission(self, request, obj=None):
        return False


# Optionally add inline to UserMemoryAdmin
UserMemoryAdmin.inlines = [InteractionSessionInline]