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
    """Lightweight serializer for conversation lists"""
    message_count = serializers.IntegerField(read_only=True)
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
    """Detailed serializer with messages"""
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.IntegerField(read_only=True)
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


class CreateConversationSerializer(serializers.ModelSerializer):
    """Serializer for creating conversations"""
    
    class Meta:
        model = Conversation
        fields = ('workspace', 'title')

    def validate_workspace(self, value):
        """Ensure workspace belongs to user"""
        request = self.context.get('request')
        if value and value.user != request.user:
            raise serializers.ValidationError('Workspace does not belong to you')
        return value


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