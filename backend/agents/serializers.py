# agents/serializers.py

from rest_framework import serializers
from .models import (
    QuestionClassification,
    EmotionalState,
    ModelSelection,
    QualityGateCheck,
    AgentResponse
)


class QuestionClassificationSerializer(serializers.ModelSerializer):
    """Serializer for question classification"""
    
    class Meta:
        model = QuestionClassification
        fields = [
            'id',
            'question_type',
            'domains',
            'urgency',
            'complexity',
            'confidence_score',
            'detected_patterns',
            'created_at'
        ]


class EmotionalStateSerializer(serializers.ModelSerializer):
    """Serializer for emotional state detection"""
    
    class Meta:
        model = EmotionalState
        fields = [
            'id',
            'state',
            'confidence_score',
            'detected_patterns',
            'tone_adjustment',
            'created_at'
        ]


class ModelSelectionSerializer(serializers.ModelSerializer):
    """Serializer for model selection"""
    
    class Meta:
        model = ModelSelection
        fields = [
            'id',
            'model_name',
            'selection_criteria',
            'estimated_cost',
            'estimated_latency',
            'created_at'
        ]


class QualityGateCheckSerializer(serializers.ModelSerializer):
    """Serializer for quality gate checks"""
    
    class Meta:
        model = QualityGateCheck
        fields = [
            'id',
            'understands_context',
            'addresses_question',
            'within_time_limit',
            'includes_reasoning',
            'empowers_user',
            'overall_passed',
            'response_time_seconds',
            'failure_reasons',
            'created_at'
        ]


class AgentResponseListSerializer(serializers.ModelSerializer):
    """Serializer for list view of agent responses"""
    
    classification = QuestionClassificationSerializer(read_only=True)
    
    class Meta:
        model = AgentResponse
        fields = [
            'id',
            'user_question',
            'agent_response',
            'confidence_level',
            'confidence_percentage',
            'classification',
            'response_time_seconds',
            'api_cost',
            'created_at'
        ]


class AgentResponseDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed view of agent response"""
    
    classification = QuestionClassificationSerializer(read_only=True)
    emotional_state = EmotionalStateSerializer(read_only=True)
    model_selection = ModelSelectionSerializer(read_only=True)
    quality_check = QualityGateCheckSerializer(read_only=True)
    
    class Meta:
        model = AgentResponse
        fields = [
            'id',
            'user_question',
            'agent_response',
            'confidence_level',
            'confidence_percentage',
            'confidence_explanation',
            'classification',
            'emotional_state',
            'model_selection',
            'quality_check',
            'total_tokens',
            'prompt_tokens',
            'completion_tokens',
            'response_time_seconds',
            'api_cost',
            'streaming_duration',
            'created_at',
            'updated_at'
        ]


class AskAgentSerializer(serializers.Serializer):
    """Serializer for ask agent request"""
    
    question = serializers.CharField(
        required=True,
        max_length=5000,
        help_text="Your question for the AI Chief of Staff"
    )
    conversation_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Optional conversation ID for context"
    )
    
    def validate_question(self, value):
        """Validate question is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Question cannot be empty")
        return value.strip()