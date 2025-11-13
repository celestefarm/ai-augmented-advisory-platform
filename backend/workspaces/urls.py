from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet, ArtifactViewSet

router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')
router.register(r'artifacts', ArtifactViewSet, basename='artifact')

app_name = 'workspaces'

urlpatterns = [
    path('', include(router.urls)),
]