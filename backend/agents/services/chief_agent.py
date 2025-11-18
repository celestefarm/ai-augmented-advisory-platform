# agents/services/chief_agent.py - UPDATED WITH OLLAMA

"""
Chief of Staff Agent - Core AI Implementation

Integrates with multiple LLM providers:
- Anthropic Claude (primary)
- Google Gemini (cost optimization) 
- Ollama (local, free fallback)

Key Responsibilities:
1. Build personalized prompts using ChiefOfStaffPromptBuilder
2. Route to appropriate LLM provider
3. Call API with streaming
4. Track performance metrics (tokens, timing, cost)
5. Handle errors with graceful fallbacks
6. Yield response chunks for SSE streaming
"""

import time
import asyncio
from typing import AsyncGenerator, Dict, Optional, Tuple
from anthropic import AsyncAnthropic
from anthropic.types import Message, MessageStreamEvent
import logging

from ..prompts.chief_of_staff import get_chief_of_staff_prompt

logger = logging.getLogger(__name__)

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI SDK not installed. Gemini models unavailable.")

# Try to import Ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.info("Ollama not installed. Local LLM unavailable (optional).")


class ChiefOfStaffAgent:
    """
    Chief of Staff AI Agent
    
    Supports multiple LLM providers:
    - Claude (Sonnet, Opus, Haiku)
    - Gemini (2.0 Flash, 2.0 Pro) - optional
    - Ollama (qwen2.5, llama3.2) - optional, local
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        google_api_key: Optional[str] = None
    ):
        """
        Initialize Chief of Staff Agent
        
        Args:
            api_key: Anthropic API key
            model: Model name (claude-*, gemini-*, or ollama model)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            google_api_key: Optional Google AI API key for Gemini models
        """
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Determine provider based on model name
        if 'gemini' in model.lower():
            self.provider = 'gemini'
            
            if not GEMINI_AVAILABLE:
                raise ImportError(
                    "Gemini model requested but google-generativeai not installed. "
                    "Install with: pip install google-generativeai"
                )
            
            if not google_api_key:
                raise ValueError("google_api_key required for Gemini models")
            
            # Configure Gemini
            genai.configure(api_key=google_api_key)
            self.gemini_model = genai.GenerativeModel(
                model_name=model,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )
            )
            
            logger.info(f"ChiefOfStaffAgent initialized with Gemini: {model}")
        
        elif 'qwen' in model.lower() or 'llama' in model.lower() or 'mistral' in model.lower():
            # Ollama models (local)
            self.provider = 'ollama'
            
            if not OLLAMA_AVAILABLE:
                raise ImportError(
                    "Ollama model requested but ollama not installed. "
                    "Install with: pip install ollama\n"
                    "And install Ollama: https://ollama.com"
                )
            
            logger.info(f"ChiefOfStaffAgent initialized with Ollama: {model}")
        
        else:
            # Default to Claude
            self.provider = 'claude'
            self.client = AsyncAnthropic(api_key=api_key)
            
            logger.info(
                f"ChiefOfStaffAgent initialized with Claude: {model}, "
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
        Generate streaming response from LLM
        
        Routes to appropriate provider based on model
        
        Args:
            user_question: User's question
            user_context: User profile and recent interactions
            emotional_state: Detected emotional state
            tone_adjustment: Tone adjustment instructions
            question_metadata: Question classification metadata
            conversation_history: Optional previous messages for context
            
        Yields:
            Dict with response chunks and metadata
        """
        if self.provider == 'ollama':
            async for event in self._generate_ollama_response(
                user_question,
                user_context,
                emotional_state,
                tone_adjustment,
                question_metadata,
                conversation_history
            ):
                yield event
        
        elif self.provider == 'gemini':
            async for event in self._generate_gemini_response(
                user_question,
                user_context,
                emotional_state,
                tone_adjustment,
                question_metadata,
                conversation_history
            ):
                yield event
        
        else:
            async for event in self._generate_claude_response(
                user_question,
                user_context,
                emotional_state,
                tone_adjustment,
                question_metadata,
                conversation_history
            ):
                yield event
    
    async def _generate_ollama_response(
        self,
        user_question: str,
        user_context: str,
        emotional_state: str,
        tone_adjustment: Dict[str, str],
        question_metadata: Dict[str, any],
        conversation_history: Optional[list] = None
    ) -> AsyncGenerator[Dict[str, any], None]:
        """
        Generate Ollama response (local LLM)
        """
        start_time = time.time()
        total_content = ""
        
        try:
            # 1. Build personalized system prompt
            logger.info("Building personalized Chief of Staff prompt for Ollama")
            
            system_prompt = get_chief_of_staff_prompt(
                user_context=user_context,
                emotional_state=emotional_state,
                tone_adjustment=tone_adjustment,
                question_metadata=question_metadata,
                current_question=user_question,
                conversation_history=conversation_history
            )
            
            # 2. Build messages for Ollama
            messages = []
            
            # Add system prompt as first message
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
            
            # Add conversation history
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
            
            logger.info(f"Calling Ollama API - model={self.model}")
            
            # Yield start event
            yield {
                'type': 'start',
                'timestamp': time.time(),
                'model': self.model
            }
            
            # 3. Call Ollama with streaming
            response_stream = await asyncio.to_thread(
                ollama.chat,
                model=self.model,
                messages=messages,
                stream=True,
                options={
                    'temperature': self.temperature,
                    'num_predict': self.max_tokens
                }
            )
            
            # 4. Stream response chunks
            chunk_count = 0
            for chunk in response_stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    if content:
                        chunk_count += 1
                        total_content += content
                        
                        # Yield chunk
                        yield {
                            'type': 'chunk',
                            'content': content,
                            'timestamp': time.time()
                        }
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # 5. Estimate tokens (Ollama doesn't provide exact counts)
            prompt_tokens = int(len(system_prompt.split()) * 1.3)
            completion_tokens = int(len(total_content.split()) * 1.3)
            total_tokens = prompt_tokens + completion_tokens
            
            # 6. Yield completion event
            metadata = {
                'response_time': round(response_time, 2),
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens,
                'cost': 0.0,  # Ollama is free!
                'model': self.model,
                'full_response': total_content,
                'success': True
            }
            
            logger.info(
                f"Ollama response generated - "
                f"time={response_time:.2f}s, "
                f"tokens={total_tokens}, "
                f"cost=$0.00 (local)"
            )
            
            yield {
                'type': 'complete',
                'metadata': metadata,
                'timestamp': time.time()
            }
            
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(
                f"Error generating Ollama response: {str(e)}",
                exc_info=True
            )
            
            yield {
                'type': 'error',
                'error': str(e),
                'error_type': type(e).__name__,
                'timestamp': time.time(),
                'response_time': round(error_time, 2)
            }
    
    async def _generate_claude_response(
        self,
        user_question: str,
        user_context: str,
        emotional_state: str,
        tone_adjustment: Dict[str, str],
        question_metadata: Dict[str, any],
        conversation_history: Optional[list] = None
    ) -> AsyncGenerator[Dict[str, any], None]:
        """
        Generate Claude response (existing implementation)
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
                question_metadata=question_metadata,
                current_question=user_question,
                conversation_history=conversation_history
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
                f"Error generating Claude response: {str(e)}",
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
    
    async def _generate_gemini_response(
        self,
        user_question: str,
        user_context: str,
        emotional_state: str,
        tone_adjustment: Dict[str, str],
        question_metadata: Dict[str, any],
        conversation_history: Optional[list] = None
    ) -> AsyncGenerator[Dict[str, any], None]:
        """
        Generate Gemini response
        """
        start_time = time.time()
        total_content = ""
        
        try:
            # 1. Build system prompt
            logger.info("Building personalized Chief of Staff prompt for Gemini")
            system_prompt = get_chief_of_staff_prompt(
                user_context=user_context,
                emotional_state=emotional_state,
                tone_adjustment=tone_adjustment,
                question_metadata=question_metadata,
                current_question=user_question,
                conversation_history=conversation_history
            )
            
            # Combine system prompt with question
            full_prompt = f"{system_prompt}\n\nUser Question: {user_question}\n\nResponse:"
            
            logger.info(f"Calling Gemini API - model={self.model}")
            
            # Yield start event
            yield {
                'type': 'start',
                'timestamp': time.time(),
                'model': self.model
            }
            
            # 2. Generate streaming response
            response_text = ""
            chunk_count = 0
            
            # Use grounding if Pro model
            use_grounding = 'pro' in self.model.lower()
            
            if use_grounding:
                # Enable Google Search grounding for Pro
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content,
                    full_prompt,
                    stream=True,
                    tools=[genai.protos.Tool(google_search_retrieval={})]
                )
            else:
                # Standard generation
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content,
                    full_prompt,
                    stream=True
                )
            
            # 3. Stream chunks
            for chunk in response:
                if chunk.text:
                    chunk_count += 1
                    response_text += chunk.text
                    
                    yield {
                        'type': 'chunk',
                        'content': chunk.text,
                        'timestamp': time.time()
                    }
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # 4. Estimate tokens (Gemini doesn't provide exact counts)
            prompt_tokens = int(len(full_prompt.split()) * 1.3)
            completion_tokens = int(len(response_text.split()) * 1.3)
            total_tokens = prompt_tokens + completion_tokens
            
            # Calculate cost
            cost = self._calculate_gemini_cost(prompt_tokens, completion_tokens)
            
            # 5. Yield completion event
            metadata = {
                'response_time': round(response_time, 2),
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens,
                'cost': round(cost, 6),
                'model': self.model,
                'full_response': response_text,
                'success': True
            }
            
            logger.info(
                f"Gemini response generated - "
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
            error_time = time.time() - start_time
            logger.error(
                f"Error generating Gemini response: {str(e)}",
                exc_info=True
            )
            
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
        
        Supports Claude and Ollama (not Gemini)
        """
        if self.provider == 'gemini':
            raise NotImplementedError("Simple generation not supported for Gemini")
        
        if self.provider == 'ollama':
            # Ollama non-streaming
            start_time = time.time()
            
            system_prompt = get_chief_of_staff_prompt(
                user_context=user_context,
                emotional_state=emotional_state,
                tone_adjustment=tone_adjustment,
                question_metadata=question_metadata,
                current_question=user_question,
                conversation_history=conversation_history
            )
            
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_question}
            ]
            
            response = await asyncio.to_thread(
                ollama.chat,
                model=self.model,
                messages=messages,
                stream=False
            )
            
            response_text = response['message']['content']
            end_time = time.time()
            
            metadata = {
                'response_time': round(end_time - start_time, 2),
                'prompt_tokens': int(len(system_prompt.split()) * 1.3),
                'completion_tokens': int(len(response_text.split()) * 1.3),
                'total_tokens': 0,  # Calculated below
                'cost': 0.0,
                'model': self.model,
                'success': True
            }
            metadata['total_tokens'] = metadata['prompt_tokens'] + metadata['completion_tokens']
            
            return response_text, metadata
        
        # Claude non-streaming (original code)
        start_time = time.time()
        
        try:
            # 1. Build personalized system prompt
            system_prompt = get_chief_of_staff_prompt(
                user_context=user_context,
                emotional_state=emotional_state,
                tone_adjustment=tone_adjustment,
                question_metadata=question_metadata,
                current_question=user_question,
                conversation_history=conversation_history
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
            conversation_history: Previous messages
            
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
        Calculate Claude API cost
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
    
    def _calculate_gemini_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Calculate Gemini API cost
        
        Pricing per 1M tokens:
        - Flash: $0.075 input / $0.30 output
        - Pro: $1.25 input / $5.00 output
        """
        pricing = {
            'gemini-2.0-flash-exp': {
                'input': 0.075,
                'output': 0.30
            },
            'gemini-2.0-pro': {
                'input': 1.25,
                'output': 5.00
            }
        }
        
        model_pricing = pricing.get(
            self.model,
            pricing['gemini-2.0-flash-exp']  # Default to Flash
        )
        
        input_cost = (prompt_tokens / 1_000_000) * model_pricing['input']
        output_cost = (completion_tokens / 1_000_000) * model_pricing['output']
        
        return input_cost + output_cost
    
    async def test_connection(self) -> bool:
        """
        Test LLM API connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info(f"Testing {self.provider} API connection...")
            
            if self.provider == 'ollama':
                # Test Ollama
                response = await asyncio.to_thread(
                    ollama.chat,
                    model=self.model,
                    messages=[
                        {'role': 'user', 'content': 'Hello! Reply with OK.'}
                    ],
                    stream=False
                )
                logger.info(f"✅ Ollama API connection successful")
                return True
            
            elif self.provider == 'gemini':
                # Test Gemini
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content,
                    'Hello! Just testing. Reply with OK.'
                )
                logger.info(f"✅ Gemini API connection successful")
                return True
            
            else:
                # Test Claude
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
                
                logger.info("✅ Claude API connection successful")
                return True
            
        except Exception as e:
            logger.error(f"❌ {self.provider} API connection failed: {str(e)}")
            return False


# Example usage and testing
if __name__ == '__main__':
    """Test the Chief of Staff Agent"""
    from decouple import config
    
    async def test_agent():
        """Test agent with all providers"""
        
        # Get API keys
        anthropic_key = config('ANTHROPIC_API_KEY', default=None)
        google_key = config('GOOGLE_AI_API_KEY', default=None)
        
        if not anthropic_key:
            print("❌ ERROR: ANTHROPIC_API_KEY not found")
            return
        
        # Test Claude
        print("\n" + "=" * 80)
        print("TESTING CLAUDE")
        print("=" * 80)
        
        claude_agent = ChiefOfStaffAgent(
            api_key=anthropic_key,
            model="claude-sonnet-4-20250514"
        )
        
        if await claude_agent.test_connection():
            print("✅ Claude working!")
        
        # Test Ollama if available
        if OLLAMA_AVAILABLE:
            print("\n" + "=" * 80)
            print("TESTING OLLAMA")
            print("=" * 80)
            
            try:
                ollama_agent = ChiefOfStaffAgent(
                    api_key=anthropic_key,  # Not used for Ollama
                    model="llama3.2:3b"
                )
                
                if await ollama_agent.test_connection():
                    print("✅ Ollama working!")
            except Exception as e:
                print(f"⚠️ Ollama not available: {str(e)}")
        else:
            print("\n⚠️ Ollama not installed (optional)")
        
        # Test Gemini if available
        if google_key and GEMINI_AVAILABLE:
            print("\n" + "=" * 80)
            print("TESTING GEMINI")
            print("=" * 80)
            
            gemini_agent = ChiefOfStaffAgent(
                api_key=anthropic_key,
                google_api_key=google_key,
                model="gemini-2.0-flash-exp"
            )
            
            if await gemini_agent.test_connection():
                print("✅ Gemini working!")
        else:
            print("\n⚠️ Gemini not configured (optional)")
    
    asyncio.run(test_agent())