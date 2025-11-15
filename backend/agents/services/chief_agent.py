# agents/services/chief_agent.py

"""
Chief of Staff Agent - Core AI Implementation

Integrates with Anthropic's Claude API to generate intelligent, streaming responses.
This is the heart of the Week 2 implementation.

Key Responsibilities:
1. Build personalized prompts using ChiefOfStaffPromptBuilder
2. Call Anthropic API with streaming
3. Track performance metrics (tokens, timing, cost)
4. Handle errors with graceful fallbacks
5. Yield response chunks for SSE streaming
"""

import time
import asyncio
from typing import AsyncGenerator, Dict, Optional, Tuple
from anthropic import AsyncAnthropic
from anthropic.types import Message, MessageStreamEvent
import logging

from ..prompts.chief_of_staff import get_chief_of_staff_prompt

logger = logging.getLogger(__name__)


class ChiefOfStaffAgent:
    """
    Chief of Staff AI Agent
    
    Orchestrates the complete AI interaction:
    - Prompt personalization
    - API streaming
    - Performance tracking
    - Error handling
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 2000,
        temperature: float = 0.7
    ):
        """
        Initialize Chief of Staff Agent
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
        """
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        logger.info(
            f"ChiefOfStaffAgent initialized with model={model}, "
            f"max_tokens={max_tokens}, temperature={temperature}"
        )
    
    async def generate_response(
        self,
        user_question: str,
        user_context: str,
        emotional_state: str,
        tone_adjustment: Dict[str, str],
        question_metadata: Dict[str, any],
        conversation_history: Optional[list] = None
    ) -> AsyncGenerator[Dict[str, any], None]:
        """
        Generate streaming response from Claude API
        
        Args:
            user_question: User's question
            user_context: User profile and recent interactions
            emotional_state: Detected emotional state
            tone_adjustment: Tone adjustment instructions
            question_metadata: Question classification metadata
            conversation_history: Optional previous messages for context
            
        Yields:
            Dict with response chunks and metadata:
            {
                'type': 'start' | 'chunk' | 'complete' | 'error',
                'content': str (for chunks),
                'metadata': dict (for complete)
            }
        """
        start_time = time.time()
        total_content = ""
        
        try:
            # 1. Build personalized system prompt
            logger.info("Building personalized Chief of Staff prompt")
            system_prompt = get_chief_of_staff_prompt(
                user_context=user_context,
                emotional_state=emotional_state,
                tone_adjustment=tone_adjustment,
                question_metadata=question_metadata
            )
            
            # 2. Build messages array
            messages = self._build_messages(user_question, conversation_history)
            
            # 3. Log request details
            logger.info(
                f"Calling Anthropic API - model={self.model}, "
                f"prompt_tokens~{len(system_prompt.split()) * 1.3:.0f}"
            )
            
            # Yield start event
            yield {
                'type': 'start',
                'timestamp': time.time(),
                'model': self.model
            }
            
            # 4. Call Anthropic API with streaming
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=messages
            ) as stream:
                # Track tokens as we stream
                async for event in stream:
                    # Handle different event types
                    if event.type == 'content_block_delta':
                        # This is a text chunk
                        if hasattr(event.delta, 'text'):
                            chunk_text = event.delta.text
                            total_content += chunk_text
                            
                            # Yield chunk
                            yield {
                                'type': 'chunk',
                                'content': chunk_text,
                                'timestamp': time.time()
                            }
                    
                    elif event.type == 'message_stop':
                        # Stream completed
                        logger.info("Stream completed successfully")
                        break
            
            # 5. Calculate performance metrics
            end_time = time.time()
            response_time = end_time - start_time
            
            # Get final message with usage data
            try:
                final_message = await stream.get_final_message()
                
                # Extract token usage
                usage = final_message.usage
                prompt_tokens = usage.input_tokens
                completion_tokens = usage.output_tokens
                total_tokens = prompt_tokens + completion_tokens
            except Exception as stream_error:
                # Stream was interrupted, estimate tokens from content
                logger.warning(f"Stream interrupted, estimating tokens: {str(stream_error)}")
                prompt_tokens = int(len(system_prompt.split()) * 1.3)
                completion_tokens = int(len(total_content.split()) * 1.3)
                total_tokens = prompt_tokens + completion_tokens
            
            # Calculate cost
            cost = self._calculate_cost(prompt_tokens, completion_tokens)
            
            # 6. Yield completion event with metadata
            metadata = {
                'response_time': round(response_time, 2),
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens,
                'cost': round(cost, 6),
                'model': self.model,
                'full_response': total_content,
                'success': True
            }
            
            logger.info(
                f"Response generated successfully - "
                f"time={response_time:.2f}s, "
                f"tokens={total_tokens}, "
                f"cost=${cost:.6f}"
            )
            
            yield {
                'type': 'complete',
                'metadata': metadata,
                'timestamp': time.time()
            }
            
        except Exception as e:
            # Handle errors
            error_time = time.time() - start_time
            logger.error(
                f"Error generating response: {str(e)}",
                exc_info=True
            )
            
            # Yield error event
            yield {
                'type': 'error',
                'error': str(e),
                'error_type': type(e).__name__,
                'timestamp': time.time(),
                'response_time': round(error_time, 2)
            }
    
    async def generate_response_simple(
        self,
        user_question: str,
        user_context: str,
        emotional_state: str,
        tone_adjustment: Dict[str, str],
        question_metadata: Dict[str, any],
        conversation_history: Optional[list] = None
    ) -> Tuple[str, Dict[str, any]]:
        """
        Generate non-streaming response (for testing or non-SSE contexts)
        
        Args:
            Same as generate_response
            
        Returns:
            Tuple of (response_text, metadata_dict)
        """
        start_time = time.time()
        
        try:
            # 1. Build personalized system prompt
            system_prompt = get_chief_of_staff_prompt(
                user_context=user_context,
                emotional_state=emotional_state,
                tone_adjustment=tone_adjustment,
                question_metadata=question_metadata
            )
            
            # 2. Build messages array
            messages = self._build_messages(user_question, conversation_history)
            
            # 3. Call Anthropic API (non-streaming)
            logger.info(f"Calling Anthropic API (non-streaming) - model={self.model}")
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=messages
            )
            
            # 4. Extract response text
            response_text = response.content[0].text
            
            # 5. Calculate metrics
            end_time = time.time()
            response_time = end_time - start_time
            
            # Extract token usage
            usage = response.usage
            prompt_tokens = usage.input_tokens
            completion_tokens = usage.output_tokens
            total_tokens = prompt_tokens + completion_tokens
            
            # Calculate cost
            cost = self._calculate_cost(prompt_tokens, completion_tokens)
            
            # 6. Build metadata
            metadata = {
                'response_time': round(response_time, 2),
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens,
                'cost': round(cost, 6),
                'model': self.model,
                'success': True
            }
            
            logger.info(
                f"Response generated - "
                f"time={response_time:.2f}s, "
                f"tokens={total_tokens}, "
                f"cost=${cost:.6f}"
            )
            
            return response_text, metadata
            
        except Exception as e:
            logger.error(f"Error in simple generation: {str(e)}", exc_info=True)
            raise
    
    def _build_messages(
        self,
        user_question: str,
        conversation_history: Optional[list] = None
    ) -> list:
        """
        Build messages array for API call
        
        Args:
            user_question: Current user question
            conversation_history: Previous messages [{'role': 'user'|'assistant', 'content': str}]
            
        Returns:
            Messages array in Anthropic format
        """
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        # Add current question
        messages.append({
            'role': 'user',
            'content': user_question
        })
        
        return messages
    

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Calculate API cost based on tokens using accurate December 2024 pricing
        
        Args:
            prompt_tokens: Input tokens
            completion_tokens: Output tokens
            
        Returns:
            Cost in USD
        """
        from .pricing import PricingCalculator
        
        calc = PricingCalculator()
        costs = calc.calculate_cost(
            model=self.model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cache_creation_tokens=0,
            cache_read_tokens=0
        )
        
        return float(costs['total_cost'])
    
    
    async def test_connection(self) -> bool:
        """
        Test Anthropic API connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info("Testing Anthropic API connection...")
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=50,
                messages=[
                    {
                        'role': 'user',
                        'content': 'Hello! Just testing the connection. Reply with OK.'
                    }
                ]
            )
            
            logger.info("✅ Anthropic API connection successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Anthropic API connection failed: {str(e)}")
            return False


# Example usage and testing
if __name__ == '__main__':
    """Test the Chief of Staff Agent"""
    from decouple import config
    
    async def test_agent():
        """Test agent with sample data"""
        
        # Get API key
        api_key = config('ANTHROPIC_API_KEY', default=None)
        if not api_key:
            print("❌ ERROR: ANTHROPIC_API_KEY not found in environment")
            print("Please set ANTHROPIC_API_KEY in your .env file")
            return
        
        # Initialize agent
        agent = ChiefOfStaffAgent(
            api_key=api_key,
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0.7
        )
        
        # Test connection
        print("\n" + "=" * 80)
        print("TESTING ANTHROPIC API CONNECTION")
        print("=" * 80)
        
        connection_ok = await agent.test_connection()
        if not connection_ok:
            print("❌ Connection test failed. Check your API key.")
            return
        
        # Test data
        test_question = "Whoare you?"
        
        test_context = """
User Profile:
- Expertise Level: Intermediate
- Decision Style: Analytical
- Industry: Technology/SaaS
- Role: VP Strategy
- Recent Interactions: 5
- Common Topics: Strategy, Finance
- Last Question: "How to price our new product?"
"""
        
        test_tone = {
            'approach': 'validate_then_challenge',
            'opening': 'acknowledge_concern',
            'style': 'reassuring_but_realistic',
            'structure': 'validate → provide_context → reframe_positively'
        }
        
        test_metadata = {
            'question_type': 'decision',
            'domains': ['strategy', 'finance'],
            'urgency': 'important',
            'complexity': 'complex'
        }
        
        # Test streaming response
        print("\n" + "=" * 80)
        print("TESTING STREAMING RESPONSE")
        print("=" * 80)
        print(f"\nQuestion: {test_question}\n")
        print("Response (streaming):")
        print("-" * 80)
        
        full_response = ""
        metadata = None
        
        try:
            async for event in agent.generate_response(
                user_question=test_question,
                user_context=test_context,
                emotional_state='uncertainty',
                tone_adjustment=test_tone,
                question_metadata=test_metadata
            ):
                if event['type'] == 'start':
                    print(f"[Stream started at {event['timestamp']}]")
                    
                elif event['type'] == 'chunk':
                    print(event['content'], end='', flush=True)
                    full_response += event['content']
                    
                elif event['type'] == 'complete':
                    metadata = event['metadata']
                    print("\n" + "-" * 80)
                    print("[Stream completed]")
                    
                elif event['type'] == 'error':
                    print(f"\n❌ Error: {event['error']}")
                    return
            
            # Print metadata
            if metadata:
                print("\n" + "=" * 80)
                print("RESPONSE METADATA")
                print("=" * 80)
                print(f"Response Time: {metadata['response_time']}s")
                print(f"Prompt Tokens: {metadata['prompt_tokens']}")
                print(f"Completion Tokens: {metadata['completion_tokens']}")
                print(f"Total Tokens: {metadata['total_tokens']}")
                print(f"Cost: ${metadata['cost']:.6f}")
                print(f"Model: {metadata['model']}")
                print("=" * 80)
                
                # Check performance targets
                print("\n" + "=" * 80)
                print("PERFORMANCE TARGETS")
                print("=" * 80)
                
                response_time = metadata['response_time']
                target_met = 8 <= response_time <= 12
                
                print(f"Target: 8-12 seconds")
                print(f"Actual: {response_time}s")
                print(f"Status: {'✅ PASS' if target_met else '⚠️  Outside target range'}")
                print("=" * 80)
                
                print("\n✅ Test completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error during test: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Run test
    print("=" * 80)
    print("CHIEF OF STAFF AGENT - INTEGRATION TEST")
    print("=" * 80)
    
    asyncio.run(test_agent())