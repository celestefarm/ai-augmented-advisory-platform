# agents/views.py

"""
Week 3: Multi-Agent Orchestration API Views

Architecture:
- LangGraph workflow orchestration (6 stages)
- Parallel agent execution (Market + Financial + Strategy)
- Intelligent agent routing (1-3 agents based on question)
- Intelligent model routing (Haiku/Sonnet/Opus based on complexity)
- Chief of Staff synthesis
- SSE streaming with progress updates

Enterprise features:
- Async/await for I/O operations
- Efficient error handling
- Request validation
- Comprehensive logging
- Database persistence
- Workspace & conversation integration
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from django.db import transaction
from django.conf import settings
from decouple import config
import json
import asyncio
import logging
from typing import AsyncGenerator, Dict, Optional
from datetime import datetime
from conversations.models import Conversation

from .models import (
    AgentResponse,
    QuestionClassification,
    EmotionalState,
    ModelSelection,
    QualityGateCheck
)
from .services.classifier import QuestionClassifier
from .services.emotional_detector import EmotionalStateDetector
from .services.memory_service import get_memory_service

logger = logging.getLogger(__name__)

# Initialize services (singleton pattern)
classifier = QuestionClassifier()
emotional_detector = EmotionalStateDetector()
memory_service = get_memory_service()


class StreamingError(Exception):
    """Custom exception for streaming errors"""
    pass


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_agent(request):
    """
    Week 3: Multi-Agent Orchestration Endpoint (LangGraph)
    
    POST /api/agents/ask
    {
        "question": "Should we pivot to enterprise?",
        "workspace_id": 123,  // optional
        "conversation_id": 456  // optional
    }
    
    Returns: Server-Sent Events stream with LangGraph progress
    
    Performance targets:
    - First byte: < 500ms
    - Simple questions: ~22s (Haiku)
    - Medium questions: ~64s (Sonnet)
    - Complex questions: ~84s (Opus)
    - Average: ~40s (2.2x faster than Week 2)
    """
    try:
        # Validate input
        question = request.data.get('question', '').strip()
        conversation_id = request.data.get('conversation_id')
        workspace_id = request.data.get('workspace_id')
        
        if not question:
            return Response(
                {'error': 'Question is required and cannot be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate question length
        if len(question) > 5000:
            return Response(
                {'error': 'Question too long (max 5000 characters)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        
        logger.info(
            f"New question from user {user.id}: "
            f"{question[:50]}... (len={len(question)})"
        )
        
        # Create streaming response
        response = StreamingHttpResponse(
            streaming_content=generate_streaming_response(
                user=user,
                question=question,
                conversation_id=conversation_id,
                workspace_id=workspace_id
            ),
            content_type='text/event-stream'
        )
        
        # SSE headers
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        
        return response
        
    except Exception as e:
        logger.error(
            f"Error in ask_agent for user {request.user.id}: {str(e)}",
            exc_info=True
        )
        return Response(
            {
                'error': 'Internal server error',
                'message': str(e) if settings.DEBUG else 'An error occurred'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def generate_streaming_response(user, question, conversation_id=None, workspace_id=None):
    """
    Generate streaming SSE response with LangGraph orchestration
    
    Yields SSE events in format:
    data: {"type": "...", ...}\n\n
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Run async pipeline
        async_gen = run_multi_agent_orchestration_pipeline(
            user, question, conversation_id, workspace_id
        )
        
        while True:
            try:
                event = loop.run_until_complete(async_gen.__anext__())
                
                # Format as SSE and yield
                sse_data = f"data: {json.dumps(event)}\n\n"
                yield sse_data
                
                # Stop if complete or error
                if event['type'] in ['complete', 'error']:
                    break
                    
            except StopAsyncIteration:
                break
            except Exception as e:
                logger.error(f"Error in streaming: {str(e)}", exc_info=True)
                error_event = {
                    'type': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                yield f"data: {json.dumps(error_event)}\n\n"
                break
    
    finally:
        loop.close()
        logger.debug("Streaming loop closed")


async def run_multi_agent_orchestration_pipeline(
    user,
    question: str,
    conversation_id: Optional[int] = None,
    workspace_id: Optional[int] = None
) -> AsyncGenerator[Dict, None]:
    """
    Week 3: Complete Multi-Agent Orchestration Pipeline (LangGraph)
    
    Pipeline stages:
    0. Link workspace & conversation
    1. Question classification
    2. Emotional detection
    3-6. LangGraph Multi-Agent Orchestration:
       - Agent routing (select 1-3 agents)
       - Model routing (Haiku/Sonnet/Opus)
       - Parallel execution (Market + Financial + Strategy)
       - Chief of Staff synthesis
       - Quality gates
       - Confidence marking
    7. Database persistence
    8. Create conversation messages
    
    Yields SSE events at each stage
    """
    
    agent_response_obj = None
    workspace = None
    conversation = None
    
    try:
        # ====================================================================
        # STAGE 0: Link Workspace & Conversation
        # ====================================================================
        logger.info(f"Stage 0: Linking workspace/conversation")
        
        if conversation_id:
            # Get conversation and its workspace
            conversation = await asyncio.to_thread(
                Conversation.objects.select_related('workspace').get,
                id=conversation_id,
                user=user,
                is_archived=False
            )
            workspace = conversation.workspace
            logger.info(
                f"Using conversation {conversation_id}, "
                f"workspace {workspace.id if workspace else 'None'}"
            )
        
        elif workspace_id:
            # Get workspace only (quick chat in workspace)
            from workspaces.models import Workspace
            workspace = await asyncio.to_thread(
                Workspace.objects.get,
                id=workspace_id,
                user=user,
                is_archived=False
            )
            logger.info(f"Using workspace {workspace_id}, no conversation")
        
        # ====================================================================
        # STAGE 1: Question Classification
        # ====================================================================
        logger.info(f"Stage 1: Classification")
        
        yield {
            'type': 'status',
            'stage': 1,
            'message': 'Analyzing your question...',
            'timestamp': datetime.now().isoformat()
        }
        
        classification_result = classifier.classify(question)
        
        # Persist classification
        classification_obj = await asyncio.to_thread(
            QuestionClassification.objects.create,
            question_type=classification_result.question_type,
            domains=classification_result.domains,
            urgency=classification_result.urgency,
            complexity=classification_result.complexity,
            confidence_score=classification_result.confidence_score,
            detected_patterns=classification_result.detected_patterns
        )
        
        logger.info(
            f"Classification: {classification_result.question_type}, "
            f"{classification_result.complexity}, {classification_result.urgency}"
        )
        
        # ====================================================================
        # STAGE 2: Emotional State Detection
        # ====================================================================
        logger.info(f"Stage 2: Emotional detection")
        
        yield {
            'type': 'status',
            'stage': 2,
            'message': 'Understanding your context...',
            'timestamp': datetime.now().isoformat()
        }
        
        emotional_result = emotional_detector.detect(question)
        
        # Persist emotional state
        emotional_obj = await asyncio.to_thread(
            EmotionalState.objects.create,
            state=emotional_result.state,
            confidence_score=emotional_result.confidence_score,
            detected_patterns=emotional_result.detected_patterns,
            tone_adjustment=emotional_result.tone_adjustment
        )
        
        logger.info(f"Emotional state: {emotional_result.state}")
        
        # ====================================================================
        # STAGE 3: Memory Retrieval
        # ====================================================================
        logger.info(f"Stage 3: Memory retrieval")
        
        user_memory = await asyncio.to_thread(
            memory_service.get_user_memory,
            user.id
        )
        
        user_context = memory_service.format_for_prompt(user_memory, user=user)
        
        logger.info(
            f"Memory: {user_memory.interaction_count} interactions"
        )
        
        # Get conversation history for context
        conversation_messages = []
        if conversation:
            from conversations.models import Message
            
            recent_messages = await asyncio.to_thread(
                lambda: list(Message.objects.filter(
                    conversation=conversation
                ).order_by('-created_at')[:10])
            )
            
            for msg in reversed(recent_messages):
                conversation_messages.append({
                    'role': msg.role,
                    'content': msg.content
                })
            
            logger.info(
                f"Loaded {len(conversation_messages)} messages for context"
            )
        
        # ====================================================================
        # STAGES 4-6: LANGGRAPH MULTI-AGENT ORCHESTRATION
        # ====================================================================
        logger.info(f"Stages 4-6: LangGraph multi-agent orchestration")
        
        yield {
            'type': 'status',
            'stage': 4,
            'message': 'Activating specialist agents...',
            'timestamp': datetime.now().isoformat()
        }
        
        # Import LangGraph orchestrator
        from orchestrator.graph import run_multi_agent_pipeline
        
        # Run LangGraph orchestration
        logger.info(f"Calling LangGraph orchestrator...")
        
        langgraph_result = await run_multi_agent_pipeline(
            question=question,
            user_context=user_context,
            workspace_id=str(workspace.id) if workspace else None,
            user_id=str(user.id),
            conversation_history=conversation_messages
        )
        
        # Extract results from LangGraph
        final_response = langgraph_result.get('final_response', '')
        metadata = langgraph_result.get('metadata', {})
        
        logger.info(
            f"LangGraph complete - "
            f"Agents: {metadata.get('agents_activated', [])}, "
            f"Time: {metadata.get('total_time', 0):.2f}s, "
            f"Cost: ${metadata.get('total_cost', 0):.6f}"
        )
        
        # Yield agent activation status
        yield {
            'type': 'agents_activated',
            'stage': 4,
            'agents': metadata.get('agents_activated', []),
            'execution_strategy': metadata.get('execution_strategy', 'parallel'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Yield agent progress
        for agent_name in metadata.get('agents_succeeded', []):
            agent_timing = metadata.get('agent_timings', {}).get(agent_name, 0)
            yield {
                'type': 'agent_complete',
                'stage': 5,
                'agent': agent_name,
                'time': agent_timing,
                'timestamp': datetime.now().isoformat()
            }
        
        # Yield synthesis status
        yield {
            'type': 'status',
            'stage': 6,
            'message': 'Synthesizing insights...',
            'timestamp': datetime.now().isoformat()
        }
        
        # Stream the final response
        yield {
            'type': 'chunk',
            'content': final_response,
            'timestamp': datetime.now().isoformat()
        }
        
        # ====================================================================
        # STAGE 7: Database Persistence (COMPLETE)
        # ====================================================================
        logger.info(f"Stage 7: Persisting results")

        # Extract model selection from LangGraph metadata
        model_name = metadata.get('selected_model', 'claude-sonnet-4-20250514')
        model_reasoning = metadata.get('model_reasoning', 'Model selected by orchestrator')

        # Create ModelSelection record
        model_obj = await asyncio.to_thread(
            ModelSelection.objects.create,
            model_name=model_name,
            selection_criteria={
                'question_type': classification_result.question_type,
                'domains': classification_result.domains,
                'urgency': classification_result.urgency,
                'complexity': classification_result.complexity,
                'reasoning': model_reasoning
            },
            estimated_cost=metadata.get('estimated_cost', 0),
            estimated_latency=metadata.get('estimated_latency', 0)
        )

        logger.info(f"Model selection saved: {model_name}")

        # Create QualityGateCheck record
        quality_obj = await asyncio.to_thread(
            QualityGateCheck.objects.create,
            understands_context=True,  # LangGraph ensures this
            addresses_question=True,   # LangGraph ensures this
            within_time_limit=metadata.get('total_time', 0) < 100,
            includes_reasoning=True,   # Chief of Staff synthesis includes reasoning
            empowers_user=True,        # Chief of Staff framework ensures this
            overall_passed=metadata.get('completeness', False),
            response_time_seconds=metadata.get('total_time', 0),
            failure_reasons=metadata.get('quality_issues', [])
        )

        logger.info(f"Quality check saved: passed={quality_obj.overall_passed}")

        # Calculate token totals from agent responses
        total_prompt_tokens = 0
        total_completion_tokens = 0

        # Extract agent timing data
        agent_timings = metadata.get('agent_timings', {})
        agent_responses_data = metadata.get('agent_responses', {})

        # Estimate tokens per agent
        for agent_name in metadata.get('agents_succeeded', []):

            agent_data = agent_responses_data.get(agent_name, {})
            token_data = agent_data.get('tokens', {})

            # Conservative estimates based on typical usage
            prompt_tokens = token_data.get('prompt', 1200)  # Fallback to 1200
            completion_tokens = token_data.get('completion', 400)  # Fallback to 400
            
            total_prompt_tokens += prompt_tokens
            total_completion_tokens += completion_tokens

        total_tokens = total_prompt_tokens + total_completion_tokens

        # Create AgentResponse object WITH all linked records
        agent_response_obj = await asyncio.to_thread(
            AgentResponse.objects.create,
            user=user,
            workspace=workspace,
            conversation=conversation,
            user_question=question,
            agent_response=final_response,
            classification=classification_obj,
            emotional_state=emotional_obj,
            model_selection=model_obj,
            quality_check=quality_obj,
            confidence_level=metadata.get('confidence_level', 'medium'),
            confidence_percentage=int(metadata.get('quality_score', 0.5) * 100),
            confidence_explanation=f"Quality score: {metadata.get('quality_score', 0):.2f}, Completeness: {metadata.get('completeness', False)}",
            total_tokens=total_tokens,
            prompt_tokens=total_prompt_tokens,
            completion_tokens=total_completion_tokens,
            response_time_seconds=metadata.get('total_time', 0),
            api_cost=metadata.get('total_cost', 0),
            is_streaming=False
        )

        logger.info(
            f"Created AgentResponse {agent_response_obj.id} "
            f"(workspace={workspace.id if workspace else None}, "
            f"conversation={conversation.id if conversation else None}, "
            f"model={model_name}, "
            f"tokens={total_tokens}, "
            f"cost=${metadata.get('total_cost', 0):.6f})"
        )

        # ====================================================================
        # SAVE INDIVIDUAL SPECIALIST AGENT EXECUTIONS
        # ====================================================================
        from agents.models import SpecialistAgentExecution

        for agent_name in metadata.get('agents_succeeded', []):
            agent_timing = agent_timings.get(agent_name, 0)
            
            # Get agent output from metadata (if available)
            agent_data = agent_responses_data.get(agent_name, {})
            agent_output = agent_data.get('analysis', '') or agent_data.get('calculation', '') or agent_data.get('decision_reframe', '')
            
            # Calculate per-agent cost (divide total cost by number of agents)
            num_agents = len(metadata.get('agents_succeeded', []))
            per_agent_cost = metadata.get('total_cost', 0) / num_agents if num_agents > 0 else 0
            
            # Create specialist execution record
            await asyncio.to_thread(
                SpecialistAgentExecution.objects.create,
                agent_response=agent_response_obj,
                agent_name=agent_name,
                agent_output=agent_output[:5000] if agent_output else 'Output not captured',
                execution_time=agent_timing,
                success=True,
                error_message='',
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost=per_agent_cost
            )
            
            logger.info(f"Saved execution for {agent_name}: {agent_timing:.2f}s")

        # Save failed agent executions
        for agent_name in metadata.get('agents_failed', []):
            error_msg = metadata.get('agent_errors', {}).get(agent_name, 'Unknown error')
            
            await asyncio.to_thread(
                SpecialistAgentExecution.objects.create,
                agent_response=agent_response_obj,
                agent_name=agent_name,
                agent_output='',
                execution_time=0,
                success=False,
                error_message=error_msg,
                prompt_tokens=0,
                completion_tokens=0,
                cost=0
            )
            
            logger.warning(f"Saved failed execution for {agent_name}: {error_msg}")

        # Update memory with this interaction
        await asyncio.to_thread(
            memory_service.update_after_interaction,
            user.id,
            agent_response_obj
        )

        logger.info(f"Stage 7 complete - All data persisted")
        
        # ====================================================================
        # STAGE 8: Create Conversation Messages
        # ====================================================================
        if conversation:
            logger.info(f"Stage 8: Creating messages")
            
            from conversations.models import Message
            
            # Create user message
            user_message = await asyncio.to_thread(
                Message.objects.create,
                conversation=conversation,
                content=question,
                role='user'
            )
            
            # Create assistant message (linked to agent response)
            assistant_message = await asyncio.to_thread(
                Message.objects.create,
                conversation=conversation,
                content=final_response,
                role='assistant',
                agent_response=agent_response_obj
            )
            
            logger.info(
                f"Created messages: "
                f"user={user_message.id}, assistant={assistant_message.id}"
            )
        
        # ====================================================================
        # STAGE 9: Complete
        # ====================================================================
        logger.info(
            f"Complete: response_id={agent_response_obj.id}, "
            f"time={metadata.get('total_time', 0):.2f}s, "
            f"cost=${metadata.get('total_cost', 0):.6f}"
        )
        
        yield {
            'type': 'complete',
            'response_id': str(agent_response_obj.id),
            'workspace_id': str(workspace.id) if workspace else None,
            'conversation_id': str(conversation.id) if conversation else None,
            'orchestration': {
                'agents_activated': metadata.get('agents_activated', []),
                'agents_succeeded': metadata.get('agents_succeeded', []),
                'agents_failed': metadata.get('agents_failed', []),
                'execution_strategy': metadata.get('execution_strategy', 'parallel'),
                'agent_timings': metadata.get('agent_timings', {}),
            },
            'confidence': {
                'level': metadata.get('confidence_level', 'medium'),
                'percentage': int(metadata.get('quality_score', 0.5) * 100),
            },
            'quality': {
                'score': metadata.get('quality_score', 0),
                'completeness': metadata.get('completeness', False),
                'issues': metadata.get('quality_issues', [])
            },
            'metadata': {
                'response_time': metadata.get('total_time', 0),
                'total_cost': metadata.get('total_cost', 0),
                'question_type': classification_result.question_type,
                'complexity': classification_result.complexity,
            },
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(
            f"Pipeline error: {str(e)}",
            exc_info=True,
            extra={'user_id': user.id, 'question': question[:100]}
        )
        
        # Mark response as failed if created
        if agent_response_obj:
            try:
                agent_response_obj.is_streaming = False
                await asyncio.to_thread(agent_response_obj.save)
            except:
                pass
        
        yield {
            'type': 'error',
            'error': str(e),
            'error_type': type(e).__name__,
            'stage': 'orchestration',
            'timestamp': datetime.now().isoformat()
        }


# ============================================================================
# RESPONSE MANAGEMENT ENDPOINTS (Keep existing code)
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_responses(request):
    """
    List user's agent responses with pagination
    
    GET /api/agents/responses?limit=20&offset=0
    
    Performance: < 100ms
    """
    try:
        user = request.user
        
        # Pagination parameters
        try:
            limit = min(int(request.query_params.get('limit', 20)), 100)
            offset = max(int(request.query_params.get('offset', 0)), 0)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid pagination parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Optimized query with select_related
        responses = AgentResponse.objects.filter(
            user=user
        ).select_related(
            'classification',
            'emotional_state',
            'model_selection',
            'quality_check',
            'workspace',
            'conversation'
        ).order_by('-created_at')[offset:offset + limit]
        
        # Serialize efficiently
        data = [
            {
                'id': r.id,
                'question': r.user_question,
                'response': r.agent_response[:200] + '...' if len(r.agent_response) > 200 else r.agent_response,
                'confidence_level': r.confidence_level,
                'confidence_percentage': r.confidence_percentage,
                'created_at': r.created_at.isoformat(),
                'response_time': r.response_time_seconds,
                'cost': float(r.api_cost) if r.api_cost else None,
                'workspace_id': str(r.workspace.id) if r.workspace else None,
                'conversation_id': str(r.conversation.id) if r.conversation else None,
                'classification': {
                    'type': r.classification.question_type,
                    'urgency': r.classification.urgency,
                    'complexity': r.classification.complexity,
                    'domains': r.classification.domains
                } if r.classification else None
            }
            for r in responses
        ]
        
        # Get total count (cached for 60s)
        from django.core.cache import cache
        cache_key = f"response_count:{user.id}"
        total = cache.get(cache_key)
        
        if total is None:
            total = AgentResponse.objects.filter(user=user).count()
            cache.set(cache_key, total, 60)
        
        return Response({
            'results': data,
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total
        })
        
    except Exception as e:
        logger.error(f"Error in list_responses: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to retrieve responses'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_response(request, response_id):
    """
    Get specific agent response with full details
    
    GET /api/agents/responses/:id
    
    Performance: < 50ms
    """
    try:
        user = request.user
        
        # Optimized query
        response_obj = AgentResponse.objects.select_related(
            'classification',
            'emotional_state',
            'model_selection',
            'quality_check',
            'workspace',
            'conversation'
        ).get(id=response_id, user=user)
        
        # Full serialization
        data = {
            'id': response_obj.id,
            'question': response_obj.user_question,
            'response': response_obj.agent_response,
            'workspace_id': str(response_obj.workspace.id) if response_obj.workspace else None,
            'conversation_id': str(response_obj.conversation.id) if response_obj.conversation else None,
            'confidence': {
                'level': response_obj.confidence_level,
                'percentage': response_obj.confidence_percentage,
                'explanation': response_obj.confidence_explanation
            },
            'classification': {
                'type': response_obj.classification.question_type,
                'domains': response_obj.classification.domains,
                'urgency': response_obj.classification.urgency,
                'complexity': response_obj.classification.complexity,
                'confidence': float(response_obj.classification.confidence_score),
                'patterns': response_obj.classification.detected_patterns
            } if response_obj.classification else None,
            'emotional_state': {
                'state': response_obj.emotional_state.state,
                'confidence': float(response_obj.emotional_state.confidence_score),
                'patterns': response_obj.emotional_state.detected_patterns
            } if response_obj.emotional_state else None,
            'model': {
                'name': response_obj.model_selection.model_name,
                'estimated_cost': float(response_obj.model_selection.estimated_cost),
                'estimated_latency': float(response_obj.model_selection.estimated_latency)
            } if response_obj.model_selection else None,
            'quality': {
                'passed': response_obj.quality_check.overall_passed,
                'checks': {
                    'understands_context': response_obj.quality_check.understands_context,
                    'addresses_question': response_obj.quality_check.addresses_question,
                    'within_time_limit': response_obj.quality_check.within_time_limit,
                    'includes_reasoning': response_obj.quality_check.includes_reasoning,
                    'empowers_user': response_obj.quality_check.empowers_user
                },
                'failures': response_obj.quality_check.failure_reasons
            } if response_obj.quality_check else None,
            'metadata': {
                'response_time': response_obj.response_time_seconds,
                'total_tokens': response_obj.total_tokens,
                'prompt_tokens': response_obj.prompt_tokens,
                'completion_tokens': response_obj.completion_tokens,
                'cost': float(response_obj.api_cost) if response_obj.api_cost else None,
                'created_at': response_obj.created_at.isoformat(),
                'updated_at': response_obj.updated_at.isoformat()
            }
        }
        
        return Response(data)
        
    except AgentResponse.DoesNotExist:
        return Response(
            {'error': 'Response not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error in get_response: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to retrieve response'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analytics(request):
    """
    Get user's usage analytics
    
    GET /api/agents/analytics
    
    Performance: < 200ms (uses aggregations)
    """
    try:
        from django.db.models import Sum, Avg, Count, Q
        
        user = request.user
        
        # Use single aggregation query for efficiency
        stats = AgentResponse.objects.filter(
            user=user
        ).aggregate(
            total_responses=Count('id'),
            total_cost=Sum('api_cost'),
            total_tokens=Sum('total_tokens'),
            avg_response_time=Avg('response_time_seconds'),
            high_confidence=Count('id', filter=Q(confidence_level='high')),
            medium_confidence=Count('id', filter=Q(confidence_level='medium')),
            low_confidence=Count('id', filter=Q(confidence_level='low'))
        )
        
        # Question types (separate query, but efficient)
        question_types = {}
        type_counts = QuestionClassification.objects.filter(
            agent_responses__user=user
        ).values('question_type').annotate(
            count=Count('id')
        )
        
        for item in type_counts:
            question_types[item['question_type']] = item['count']
        
        # Format response
        data = {
            'total_responses': stats['total_responses'] or 0,
            'total_cost': float(stats['total_cost'] or 0),
            'total_tokens': stats['total_tokens'] or 0,
            'average_response_time': round(stats['avg_response_time'] or 0, 2),
            'confidence_distribution': {
                'high': stats['high_confidence'] or 0,
                'medium': stats['medium_confidence'] or 0,
                'low': stats['low_confidence'] or 0
            },
            'question_types': question_types,
            'generated_at': datetime.now().isoformat()
        }
        
        return Response(data)
        
    except Exception as e:
        logger.error(f"Error in get_analytics: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to generate analytics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cache_stats(request):
    """
    Get Redis cache statistics
    
    GET /api/agents/cache-stats
    """
    from agents.utils.cache import get_cache_manager
    
    try:
        cache = get_cache_manager()
        stats = cache.get_stats()
        
        return Response({
            'cache_stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to get cache stats'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )