from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("authentication.urls",)),
    path("api/", include("workspaces.urls",)),
    path('api/', include('conversations.urls')),
    path('api/agents/', include('agents.urls')),
]
