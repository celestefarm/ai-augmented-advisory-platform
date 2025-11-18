from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    
    class Meta:
        model = Message
        fields = (
            'id',
            'conversation',
            'role',
            'content',
            'tokens',
            'model',
            'is_streaming',
            'created_at',
        )
        read_only_fields = ('id', 'created_at', 'tokens')


class ConversationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for conversation lists
    FIXED: Uses annotation-compatible field names
    """
    # This will use the annotation 'total_messages' if available
    message_count = serializers.IntegerField(source='total_messages', read_only=True, default=0)
    is_quick_chat = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Conversation
        fields = (
            'id',
            'workspace',
            'title',
            'summary',
            'is_pinned',
            'is_quick_chat',
            'message_count',
            'last_message_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'last_message_at')


class ConversationDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer with messages
    FIXED: Uses SerializerMethodField for flexibility
    """
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    is_quick_chat = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Conversation
        fields = (
            'id',
            'workspace',
            'title',
            'summary',
            'is_pinned',
            'is_archived',
            'is_quick_chat',
            'message_count',
            'messages',
            'last_message_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'last_message_at')
    
    def get_message_count(self, obj):
        """
        Get message count - uses annotation if available, otherwise counts
        This matches the property behavior in the model
        """
        if hasattr(obj, 'total_messages'):
            return obj.total_messages
        return obj.messages.count()


class CreateConversationSerializer(serializers.ModelSerializer):
    """Serializer for creating conversations"""
    workspace_id = serializers.UUIDField(required=False, allow_null=True, write_only=True)
    
    class Meta:
        model = Conversation
        fields = ('workspace_id', 'title')

    def validate_workspace_id(self, value):
        """Ensure workspace belongs to user"""
        if not value:
            return None
            
        request = self.context.get('request')
        try:
            from workspaces.models import Workspace
            workspace = Workspace.objects.get(id=value, user=request.user, is_archived=False)
            return workspace.id
        except Workspace.DoesNotExist:
            raise serializers.ValidationError('Workspace does not exist or does not belong to you')
    
    def create(self, validated_data):
        """Create conversation with workspace"""
        workspace_id = validated_data.pop('workspace_id', None)
        
        conversation = Conversation.objects.create(
            workspace_id=workspace_id,
            **validated_data
        )
        return conversation
    
class CreateMessageSerializer(serializers.ModelSerializer):
    """Serializer for creating messages"""
    
    class Meta:
        model = Message
        fields = ('conversation', 'role', 'content')

    def validate_conversation(self, value):
        """Ensure conversation belongs to user"""
        request = self.context.get('request')
        if value.user != request.user:
            raise serializers.ValidationError('Conversation does not belong to you')
        return value