# workspaces/serializers.py

from rest_framework import serializers
from .models import Workspace, Artifact


class ArtifactSerializer(serializers.ModelSerializer):
    """Serializer for Artifact model"""
    
    class Meta:
        model = Artifact
        fields = (
            'id',
            'workspace',
            'name',
            'file_type',
            'file_url',
            'file_size',
            'mime_type',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class WorkspaceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for workspace lists"""
    conversation_count = serializers.IntegerField(source='total_conversations', read_only=True, default=0)
    artifact_count = serializers.IntegerField(source='total_artifacts', read_only=True, default=0)
    last_activity = serializers.DateTimeField(source='latest_activity', read_only=True)
    
    class Meta:
        model = Workspace
        fields = (
            'id',
            'name',
            'description',
            'icon',
            'color',
            'is_pinned',
            'conversation_count',
            'artifact_count',
            'last_activity',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class CreateWorkspaceSerializer(serializers.ModelSerializer):
    """Serializer for creating workspaces"""
    
    class Meta:
        model = Workspace
        fields = ('name', 'description', 'icon', 'color')

    def validate_name(self, value):
        """Validate workspace name"""
        if not value or not value.strip():
            raise serializers.ValidationError('Workspace name cannot be empty')
        return value.strip()


class UpdateWorkspaceSerializer(serializers.ModelSerializer):
    """Serializer for updating workspaces"""
    
    class Meta:
        model = Workspace
        fields = ('name', 'description', 'icon', 'color', 'is_pinned', 'order')

    def validate_name(self, value):
        """Validate workspace name"""
        if not value or not value.strip():
            raise serializers.ValidationError('Workspace name cannot be empty')
        return value.strip()
    

class WorkspaceDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with artifacts"""
    artifacts = ArtifactSerializer(many=True, read_only=True)
    conversation_count = serializers.IntegerField(source='total_conversations', read_only=True, default=0)
    artifact_count = serializers.IntegerField(source='total_artifacts', read_only=True, default=0)
    last_activity = serializers.DateTimeField(source='latest_activity', read_only=True)
    
    class Meta:
        model = Workspace
        fields = (
            'id',
            'name',
            'description',
            'icon',
            'color',
            'order',
            'is_pinned',
            'is_archived',
            'conversation_count',
            'artifact_count',
            'last_activity',
            'artifacts',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        """Validate workspace creation"""
        request = self.context.get('request')
        if request and not self.instance:  # Only on creation
            user = request.user
            workspace_count = Workspace.objects.filter(
                user=user,
                is_archived=False
            ).count()
            
            if workspace_count >= user.workspace_limit:
                raise serializers.ValidationError(
                    f'You have reached your workspace limit of {user.workspace_limit}'
                )
        
        return attrs