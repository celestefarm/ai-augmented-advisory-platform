from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    # Main endpoint - Ask the AI agent
    path('ask', views.ask_agent, name='ask'),
    
    # Response management
    path('responses', views.list_responses, name='list-responses'),
    path('responses/<int:response_id>', views.get_response, name='get-response'),
    
    # Analytics
    path('analytics', views.get_analytics, name='analytics'),

    # cache management
    path('cache-stats', views.get_cache_stats, name='cache-stats'),
]