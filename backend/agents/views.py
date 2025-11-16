# agents/views.py

"""
Optimized Agent Response API Views

Enterprise features:
- Async/await for I/O operations
- Efficient error handling with retries
- Request validation and sanitization
- Rate limiting ready
- Comprehensive logging
- Database query optimization
- Response streaming with backpressure
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
from .services.model_router import ModelRouter
from .services.chief_agent import ChiefOfStaffAgent
from .services.quality_gates import QualityGates
from .services.confidence_marker import ConfidenceMarker
from .services.memory_service import get_memory_service

logger = logging.getLogger(__name__)

# Initialize services (singleton pattern)
classifier = QuestionClassifier()
emotional_detector = EmotionalStateDetector()
model_router = ModelRouter()
quality_gates = QualityGates()
confidence_marker = ConfidenceMarker()
memory_service = get_memory_service()


class StreamingError(Exception):
    """Custom exception for streaming errors"""
    pass


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_agent(request):
    """
    Generate AI response (streaming SSE)
    
    POST /api/agents/ask
    {
        "question": "Should we pivot to enterprise?",
        "conversation_id": 123  // optional
    }
    
    Returns: Server-Sent Events stream
    
    Performance targets:
    - First byte: < 500ms
    - Total time: 8-12s
    - Memory: < 50MB per request
    """
    try:
        # Validate input
        question = request.data.get('question', '').strip()
        conversation_id = request.data.get('conversation_id')
        
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
                workspace_id=request.data.get('workspace_id')  # ADD THIS
            ),
            content_type='text/event-stream'
        )
        
        # SSE headers
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        # response['Connection'] = 'keep-alive'
        
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
    Generate streaming SSE response with proper error handling
    
    Yields SSE events in format:
    data: {"type": "...", ...}\n\n
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Run async pipeline
        async_gen = run_agent_pipeline(user, question, conversation_id,  workspace_id)
        
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


async def run_agent_pipeline(
    user,
    question: str,
    conversation_id: Optional[int] = None,
    workspace_id: Optional[int] = None
) -> AsyncGenerator[Dict, None]:
    """
    Complete Week 2 AI pipeline (async) - INTEGRATED VERSION
    
    Pipeline stages:
    0. Link workspace & conversation
    1. Classification (sync)
    2. Emotional detection (sync)
    3. Model selection (sync)
    4. Memory retrieval (sync with cache)
    5. AI generation (async streaming)
    6. Quality validation (sync)
    7. Confidence marking (sync)
    8. Database persistence (sync)
    9. Create conversation messages
    
    Yields SSE events at each stage
    """
    
    agent_response_obj = None
    workspace = None
    conversation = None
    
    try:
        # STAGE 0: Link Workspace & Conversation
        logger.info(f"[Pipeline] Stage 0: Linking workspace/conversation")
        
        if conversation_id:
            # Get conversation and its workspace
            from conversations.models import Conversation
            conversation = await asyncio.to_thread(
                Conversation.objects.select_related('workspace').get,
                id=conversation_id,
                user=user,
                is_archived=False
            )
            workspace = conversation.workspace
            logger.info(f"[Pipeline] Using conversation {conversation_id}, workspace {workspace.id if workspace else 'None'}")
        
        elif workspace_id:
            # Get workspace only (quick chat in workspace)
            from workspaces.models import Workspace
            workspace = await asyncio.to_thread(
                Workspace.objects.get,
                id=workspace_id,
                user=user,
                is_archived=False
            )
            logger.info(f"[Pipeline] Using workspace {workspace_id}, no conversation")
        
        # STAGE 1: Question Classification
        logger.info(f"[Pipeline] Stage 1: Classification")
        
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
            f"[Pipeline] Classification: {classification_result.question_type}, "
            f"{classification_result.complexity}, {classification_result.urgency}"
        )
        
        # STAGE 2: Emotional State Detection
        logger.info(f"[Pipeline] Stage 2: Emotional detection")
        
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
        
        logger.info(f"[Pipeline] Emotional state: {emotional_result.state}")
        
        # STAGE 3: Model Selection
        logger.info(f"[Pipeline] Stage 3: Model selection")
        
        yield {
            'type': 'status',
            'stage': 3,
            'message': 'Selecting AI model...',
            'timestamp': datetime.now().isoformat()
        }
        
        model_selection_result = model_router.select_model(
            question_type=classification_result.question_type,
            domains=classification_result.domains,
            urgency=classification_result.urgency,
            complexity=classification_result.complexity,
            emotional_state=emotional_result.state
        )
        
        # Persist model selection
        model_obj = await asyncio.to_thread(
            ModelSelection.objects.create,
            model_name=model_selection_result.model_name,
            selection_criteria=model_selection_result.selection_criteria,
            estimated_cost=model_selection_result.estimated_cost,
            estimated_latency=model_selection_result.estimated_latency
        )
        
        logger.info(
            f"[Pipeline] Model: {model_selection_result.model_name}, "
            f"est_cost=${model_selection_result.estimated_cost:.4f}"
        )
        
        # STAGE 4: Memory Retrieval
        logger.info(f"[Pipeline] Stage 4: Memory retrieval")
        
        user_memory = await asyncio.to_thread(
            memory_service.get_user_memory,
            user.id
        )
        
        user_context = memory_service.format_for_prompt(user_memory, user=user)
        
        logger.info(
            f"[Pipeline] Memory: {user_memory.interaction_count} interactions"
        )
        
        # Prepare question metadata
        question_metadata = {
            'question_type': classification_result.question_type,
            'domains': classification_result.domains,
            'urgency': classification_result.urgency,
            'complexity': classification_result.complexity
        }
        
        # STAGE 5: Initialize Agent and Create Response Object
        logger.info(f"[Pipeline] Stage 5: AI generation")
        
        yield {
            'type': 'status',
            'stage': 5,
            'message': 'Generating response...',
            'timestamp': datetime.now().isoformat()
        }
        
        api_key = config('ANTHROPIC_API_KEY')
        agent = ChiefOfStaffAgent(
            api_key=api_key,
            model=model_selection_result.model_name,
            max_tokens=2000,
            temperature=0.7
        )
        
        # Create response object WITH workspace/conversation links
        agent_response_obj = await asyncio.to_thread(
            AgentResponse.objects.create,
            user=user,
            workspace=workspace,  # NEW: LINKED
            conversation=conversation,  # UPDATED: LINKED (was conversation_id)
            user_question=question,
            agent_response="",
            classification=classification_obj,
            emotional_state=emotional_obj,
            model_selection=model_obj,
            confidence_level='medium',
            confidence_percentage=50,
            is_streaming=True
        )
        
        logger.info(
            f"[Pipeline] Created AgentResponse {agent_response_obj.id} "
            f"(workspace={workspace.id if workspace else None}, "
            f"conversation={conversation.id if conversation else None})"
        )
        
        await asyncio.to_thread(agent_response_obj.mark_streaming_started)
        
        # Stream AI response
        full_response = ""
        response_metadata = None
        chunk_count = 0
        
        async for event in agent.generate_response(
            user_question=question,
            user_context=user_context,
            emotional_state=emotional_result.state,
            tone_adjustment=emotional_result.tone_adjustment,
            question_metadata=question_metadata
        ):
            if event['type'] == 'start':
                yield {
                    'type': 'start',
                    'response_id': str(agent_response_obj.id),
                    'model': event['model'],
                    'timestamp': datetime.now().isoformat()
                }
            
            elif event['type'] == 'chunk':
                chunk_count += 1
                full_response += event['content']
                
                yield {
                    'type': 'chunk',
                    'content': event['content'],
                    'chunk_number': chunk_count,
                    'timestamp': datetime.now().isoformat()
                }
            
            elif event['type'] == 'complete':
                response_metadata = event['metadata']
                logger.info(
                    f"[Pipeline] AI complete: "
                    f"{response_metadata['total_tokens']} tokens, "
                    f"{response_metadata['response_time']:.2f}s"
                )
            
            elif event['type'] == 'error':
                logger.error(f"[Pipeline] AI error: {event['error']}")
                yield event
                return
        
        # Validate we have response
        if not response_metadata:
            raise StreamingError("No response metadata received from AI")
        
        # STAGE 6: Quality Gates
        logger.info(f"[Pipeline] Stage 6: Quality validation")
        
        quality_passed, failures, checks = quality_gates.validate_response(
            question=question,
            response=full_response,
            user_context=user_context,
            response_time=response_metadata['response_time'],
            question_metadata=question_metadata
        )
        
        # Persist quality check
        quality_obj = await asyncio.to_thread(
            QualityGateCheck.objects.create,
            understands_context=checks['understands_context'],
            addresses_question=checks['addresses_question'],
            within_time_limit=checks['within_time_limit'],
            includes_reasoning=checks['includes_reasoning'],
            empowers_user=checks['empowers_user'],
            overall_passed=quality_passed,
            response_time_seconds=response_metadata['response_time'],
            failure_reasons=failures
        )
        
        if not quality_passed:
            logger.warning(f"[Pipeline] Quality check failed: {failures}")
        
        # STAGE 7: Confidence Marking
        logger.info(f"[Pipeline] Stage 7: Confidence marking")
        
        confidence_level, confidence_pct, confidence_explanation = \
            confidence_marker.calculate_confidence(
                response=full_response,
                question_complexity=classification_result.complexity,
                model_used=model_selection_result.model_name,
                response_time=response_metadata['response_time'],
                question_type=classification_result.question_type
            )
        
        logger.info(
            f"[Pipeline] Confidence: {confidence_level} ({confidence_pct}%)"
        )
        
        # STAGE 8: Persist Final Response
        logger.info(f"[Pipeline] Stage 8: Persisting")

        # Update response object (in memory)
        agent_response_obj.agent_response = full_response
        agent_response_obj.quality_check = quality_obj
        agent_response_obj.confidence_level = confidence_level
        agent_response_obj.confidence_percentage = confidence_pct
        agent_response_obj.confidence_explanation = confidence_explanation
        agent_response_obj.total_tokens = response_metadata['total_tokens']
        agent_response_obj.prompt_tokens = response_metadata['prompt_tokens']
        agent_response_obj.completion_tokens = response_metadata['completion_tokens']
        agent_response_obj.response_time_seconds = response_metadata['response_time']
        agent_response_obj.api_cost = response_metadata['cost']

        # Mark streaming complete and save to DB (async)
        await asyncio.to_thread(agent_response_obj.mark_streaming_completed)
        await asyncio.to_thread(agent_response_obj.save)

        # Update memory with this interaction
        await asyncio.to_thread(
            memory_service.update_after_interaction,
            user.id,
            agent_response_obj
        )

        # Invalidate memory cache (forces refresh on next request)
        await asyncio.to_thread(memory_service.invalidate_cache, user.id)
        
        # STAGE 9: Create Conversation Messages
        if conversation:
            logger.info(f"[Pipeline] Stage 9: Creating messages")
            
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
                content=full_response,
                role='assistant',
                agent_response=agent_response_obj
            )
            
            logger.info(
                f"[Pipeline] Created messages: "
                f"user={user_message.id}, assistant={assistant_message.id}"
            )
        
        # STAGE 10: Complete
        logger.info(
            f"[Pipeline] Complete: response_id={agent_response_obj.id}, "
            f"time={response_metadata['response_time']:.2f}s, "
            f"cost=${response_metadata['cost']:.6f}"
        )
        
        yield {
            'type': 'complete',
            'response_id': str(agent_response_obj.id),
            'workspace_id': str(workspace.id) if workspace else None,
            'conversation_id': str(conversation.id) if conversation else None,
            'confidence': {
                'level': confidence_level,
                'percentage': confidence_pct,
                'explanation': confidence_explanation
            },
            'quality': {
                'passed': quality_passed,
                'checks': checks,
                'failures': failures if failures else None
            },
            'metadata': {
                'response_time': response_metadata['response_time'],
                'total_tokens': response_metadata['total_tokens'],
                'cost': float(response_metadata['cost']),
                'model': model_selection_result.model_name,
                'chunks_sent': chunk_count
            },
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(
            f"[Pipeline] Error: {str(e)}",
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
            'stage': 'pipeline',
            'timestamp': datetime.now().isoformat()
        }

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
            'quality_check'
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
            'quality_check'
        ).get(id=response_id, user=user)
        
        # Full serialization
        data = {
            'id': response_obj.id,
            'question': response_obj.user_question,
            'response': response_obj.agent_response,
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