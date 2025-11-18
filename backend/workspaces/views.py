from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.db.models import Count, Q, Max
import logging

from .models import Workspace, Artifact
from .serializers import (
    WorkspaceListSerializer,
    WorkspaceDetailSerializer,
    CreateWorkspaceSerializer,
    UpdateWorkspaceSerializer,
    ArtifactSerializer,
)

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination class"""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class WorkspaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Workspace CRUD operations
    
    list: Get all workspaces for authenticated user
    retrieve: Get single workspace with details
    create: Create new workspace
    update/partial_update: Update workspace
    destroy: Archive workspace (soft delete)
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter workspaces by user"""
        return Workspace.objects.for_user(self.request.user).with_counts()
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return WorkspaceListSerializer
        elif self.action == 'create':
            return CreateWorkspaceSerializer
        elif self.action in ['update', 'partial_update']:
            return UpdateWorkspaceSerializer
        return WorkspaceDetailSerializer
    
    def perform_create(self, serializer):
        """Create workspace for authenticated user"""
        serializer.save(user=self.request.user)
        logger.info(f"Workspace created: {serializer.instance.id} by user {self.request.user.id}")
    
    def perform_destroy(self, instance):
        """Soft delete - archive workspace"""
        instance.is_archived = True
        instance.save(update_fields=['is_archived'])
        logger.info(f"Workspace archived: {instance.id} by user {self.request.user.id}")
    
    @action(detail=True, methods=['get'])
    def conversations(self, request, pk=None):
        """
        Get conversations in a workspace
        GET /api/workspaces/:id/conversations/
        """
        workspace = self.get_object()
        
        # Import here to avoid circular imports
        from conversations.models import Conversation
        from conversations.serializers import ConversationListSerializer
        
        # Get conversations for this workspace
        conversations = Conversation.objects.filter(
            workspace=workspace,
            is_archived=False
        ).with_counts()
        
        # Serialize and return
        serializer = ConversationListSerializer(conversations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        """Pin/unpin workspace"""
        workspace = self.get_object()
        workspace.is_pinned = not workspace.is_pinned
        workspace.save(update_fields=['is_pinned'])
        
        return Response({
            'message': 'Workspace pinned' if workspace.is_pinned else 'Workspace unpinned',
            'is_pinned': workspace.is_pinned
        })
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore archived workspace"""
        workspace = self.get_object()
        
        if not workspace.is_archived:
            return Response(
                {'message': 'Workspace is not archived'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        workspace.is_archived = False
        workspace.save(update_fields=['is_archived'])
        
        logger.info(f"Workspace restored: {workspace.id} by user {request.user.id}")
        
        return Response({
            'message': 'Workspace restored successfully',
            'workspace': WorkspaceDetailSerializer(workspace).data
        })
    
    @action(detail=False, methods=['get'])
    def archived(self, request):
        """Get archived workspaces"""
        archived_workspaces = Workspace.objects.filter(
            user=request.user,
            is_archived=True
        ).with_counts()
        
        serializer = WorkspaceListSerializer(archived_workspaces, many=True)
        return Response(serializer.data)


class ArtifactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Artifact CRUD operations
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ArtifactSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter artifacts by user's workspaces"""
        return Artifact.objects.filter(
            workspace__user=self.request.user,
            is_archived=False
        )
    
    def perform_destroy(self, instance):
        """Soft delete - archive artifact"""
        instance.is_archived = True
        instance.save(update_fields=['is_archived'])
        logger.info(f"Artifact archived: {instance.id} by user {self.request.user.id}")