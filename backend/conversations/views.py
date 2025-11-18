# conversations/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import logging
from rest_framework.pagination import PageNumberPagination

from .models import Conversation, Message
from .serializers import (
    ConversationListSerializer,
    ConversationDetailSerializer,
    CreateConversationSerializer,
    MessageSerializer,
    CreateMessageSerializer,
)

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination class"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversation CRUD operations
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter conversations by user"""
        return Conversation.objects.for_user(self.request.user).with_counts()
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return ConversationListSerializer
        elif self.action == 'create':
            return CreateConversationSerializer
        return ConversationDetailSerializer
    
    def perform_create(self, serializer):
        """Create conversation for authenticated user"""
        serializer.save(user=self.request.user)
        logger.info(f"Conversation created: {serializer.instance.id} by user {self.request.user.id}")
    
    def perform_destroy(self, instance):
        """Soft delete - archive conversation"""
        instance.is_archived = True
        instance.save(update_fields=['is_archived'])
        logger.info(f"Conversation archived: {instance.id} by user {self.request.user.id}")
    
    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        """Pin/unpin conversation"""
        conversation = self.get_object()
        conversation.is_pinned = not conversation.is_pinned
        conversation.save(update_fields=['is_pinned'])
        
        return Response({
            'message': 'Conversation pinned' if conversation.is_pinned else 'Conversation unpinned',
            'is_pinned': conversation.is_pinned
        })
    
    @action(detail=False, methods=['get'])
    def quick_chats(self, request):
        """Get quick chats (conversations without workspace)"""
        quick_chats = Conversation.objects.quick_chats(request.user).with_counts()
        serializer = ConversationListSerializer(quick_chats, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Message CRUD operations
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter messages by user's conversations"""
        return Message.objects.filter(
            conversation__user=self.request.user
        ).select_related('conversation').order_by('created_at')
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return CreateMessageSerializer
        return MessageSerializer
    
    @action(detail=False, methods=['get'])
    def conversation(self, request):
        """Get messages for a specific conversation"""
        conversation_id = request.query_params.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {'message': 'conversation_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        messages = self.get_queryset().filter(conversation_id=conversation_id)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)