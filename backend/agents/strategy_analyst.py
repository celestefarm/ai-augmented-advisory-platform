# agents/strategy_analyst.py - FIXED WITH TOKEN TRACKING

"""
STRATEGY ANALYST AGENT
Mission: Strategic framework application and decision reframing

Multi-Model Support: Claude, Gemini, Ollama
Caching: Unified Redis cache layer
Token Tracking: Complete token counting for all providers
"""

import time
import asyncio
from typing import Dict, Optional
import logging
import aiohttp
import hashlib

logger = logging.getLogger(__name__)

from anthropic import AsyncAnthropic
from agents.utils.cache import get_cache_manager

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI SDK not installed. Gemini unavailable.")


class StrategyAnalystAgent:
    """
    Strategy Analyst - Strategic Framework & Decision Reframing Agent
    
    Multi-Model Support:
    - Claude (claude-*): Anthropic API
    - Gemini (gemini-*): Google AI API
    - Ollama (llama*, mistral*, etc.): Local Ollama server
    
    Caching Strategy:
    - System prompts: 1 hour (Redis)
    - Model outputs: 30 minutes (Redis)
    - User context: 5 minutes (Redis)
    
    Token Tracking:
    - Claude: Exact counts from API
    - Gemini: Estimated (word count * 1.3)
    - Ollama: Estimated (word count * 1.3)
    """
    
    # Condensed prompt for Ollama (faster)
    CONDENSED_SYSTEM_PROMPT = """You are a Strategy Analyst expert.

Provide strategic analysis with:
1. **Decision Reframe**: What they're REALLY choosing
2. **Framework Applied**: Use Porter's Five Forces, Blue Ocean, Playing to Win, etc.
3. **Assumptions Tested**: Challenge key assumptions
4. **Trade-offs**: What YES means saying NO to
5. **Confidence**: Mark as 🟢 High, 🟡 Medium, or 🔴 Low

Be concise, actionable, specific to user's situation."""
    
    @staticmethod
    def _load_system_prompt() -> str:
        """Load Strategy Analyst Harvard-level prompt from external file"""
        from pathlib import Path
        
        prompt_file = Path(__file__).parent / 'prompts' / 'strategy_analyst_prompt.txt'
        
        if not prompt_file.exists():
            logger.warning(f"Strategy Analyst prompt file not found: {prompt_file}")
            return """You are STRATEGY ANALYST, a strategic framework expert.
Provide strategic analysis, framework application, and decision reframing.
Focus on actionable strategic intelligence specific to the user's situation."""
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    SYSTEM_PROMPT = _load_system_prompt()
    
    def __init__(
        self,
        anthropic_api_key: str,
        model: str = "claude-sonnet-4-20250514",
        google_api_key: Optional[str] = None
    ):
        """Initialize Strategy Analyst Agent with multi-model support and caching"""
        self.model = model
        self.cache = get_cache_manager()
        
        # Token tracking variables
        self.last_prompt_tokens = 0
        self.last_completion_tokens = 0
        self.last_total_tokens = 0
        
        # Hash system prompts for cache keys
        self.full_prompt_hash = hashlib.md5(self.SYSTEM_PROMPT.encode()).hexdigest()
        self.condensed_prompt_hash = hashlib.md5(self.CONDENSED_SYSTEM_PROMPT.encode()).hexdigest()
        
        # AUTO-DETECT CLIENT TYPE
        if model.startswith('llama') or model.startswith('ollama') or model.startswith('mistral'):
            self.client_type = 'ollama'
            self.ollama_url = 'http://localhost:11434'
            logger.info(f"Strategy Analyst initialized with Ollama: {model}")
            
        elif model.startswith('gemini') and GEMINI_AVAILABLE and google_api_key:
            self.client_type = 'gemini'
            genai.configure(api_key=google_api_key)
            self.gemini_client = genai.GenerativeModel(
                model_name=model,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1500,
                    temperature=0.3,
                )
            )
            logger.info(f"Strategy Analyst initialized with Gemini: {model}")
            
        else:
            self.client_type = 'claude'
            self.claude_client = AsyncAnthropic(api_key=anthropic_api_key)
            logger.info(f"Strategy Analyst initialized with Claude: {model}")
    
    async def analyze(
        self,
        question: str,
        user_context: str,
        question_metadata: Dict
    ) -> Dict:
        """Analyze strategic question using appropriate model client"""
        start_time = time.time()
        
        try:
            # Check cache for complete agent response
            question_hash = hashlib.md5(
                f"{question}:{user_context}".encode()
            ).hexdigest()
            
            cached_response = self.cache.get_agent_response(
                question_hash,
                'strategy_analyst'
            )
            
            if cached_response:
                logger.info("✅ Using cached agent response")
                cached_response['response_time'] = round(time.time() - start_time, 2)
                cached_response['from_cache'] = True
                return cached_response
            
            # Determine question type and framework
            question_type, suggested_framework = self._classify_strategic_question(question)
            
            # Build prompt
            prompt = self._build_analysis_prompt(
                question,
                user_context,
                question_metadata,
                question_type,
                suggested_framework
            )
            
            # ROUTE TO APPROPRIATE CLIENT
            if self.client_type == 'ollama':
                response_text = await self._call_ollama(prompt)
            elif self.client_type == 'gemini':
                response_text = await self._call_gemini(prompt)
            else:  # claude
                response_text = await self._call_claude(prompt)
            
            # Get token counts from last API call
            token_counts = self._get_last_token_counts()
            
            # Parse response
            result = await self._parse_agent_response(response_text)
            result['model_used'] = self.model
            result['client_type'] = self.client_type
            result['agent_name'] = 'strategy_analyst'
            result['question_type'] = question_type
            result['framework_suggested'] = suggested_framework
            result['response_time'] = round(time.time() - start_time, 2)
            result['success'] = True
            result['from_cache'] = False
            
            # Include token metadata in result
            result.update({
                'prompt_tokens': token_counts['prompt_tokens'],
                'completion_tokens': token_counts['completion_tokens'],
                'total_tokens': token_counts['total_tokens'],
                'cost': self._calculate_cost(
                    token_counts['prompt_tokens'],
                    token_counts['completion_tokens']
                )
            })
            
            # Cache the agent response
            self.cache.set_agent_response(
                question_hash,
                'strategy_analyst',
                result
            )
            
            logger.info(
                f"Strategy Analyst analysis complete - "
                f"type={question_type}, framework={suggested_framework}, "
                f"client={self.client_type}, time={result['response_time']}s, "
                f"tokens={token_counts['total_tokens']}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Strategy Analyst analysis failed: {str(e)}", exc_info=True)
            
            return {
                'agent_name': 'strategy_analyst',
                'success': False,
                'error': str(e),
                'response_time': round(time.time() - start_time, 2),
                'decision_reframe': 'Unable to complete strategic analysis due to technical error.',
                'confidence': '🔴 Low - Analysis failed',
                'fallback': True,
                'from_cache': False,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0,
                'cost': 0.0
            }
    
    async def _call_claude(self, prompt: str) -> str:
        """Call Claude API with Redis + Anthropic dual caching and token tracking"""
        
        # Generate cache key
        input_hash = hashlib.md5(prompt.encode()).hexdigest()
        
        # Try Redis cache first (30 min TTL)
        cached_output = self.cache.get_model_output(
            f"claude_{self.model}",
            input_hash
        )
        if cached_output:
            logger.info("✅ Using Redis cached Claude response")
            # Estimate tokens for cached response
            self._estimate_tokens_from_text(self.SYSTEM_PROMPT + prompt, cached_output)
            return cached_output
        
        # Call Claude API with Anthropic's prompt caching
        logger.info("🌐 Calling Claude API with prompt caching")
        response = await self.claude_client.messages.create(
            model=self.model,
            max_tokens=1500,
            temperature=0.3,
            system=[
                {
                    "type": "text",
                    "text": self.SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"}  # Anthropic cache (5 min)
                }
            ],
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        output = response.content[0].text
        
        # Track actual token counts from Claude
        self.last_prompt_tokens = response.usage.input_tokens
        self.last_completion_tokens = response.usage.output_tokens
        self.last_total_tokens = self.last_prompt_tokens + self.last_completion_tokens
        
        # Cache in Redis (30 min)
        self.cache.set_model_output(
            f"claude_{self.model}",
            input_hash,
            output
        )
        logger.info(f"Cached Claude response in Redis (tokens={self.last_total_tokens})")
        
        return output
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API with Redis caching and token estimation"""
        
        # Generate cache key
        input_hash = hashlib.md5(prompt.encode()).hexdigest()
        
        # Try Redis cache first
        cached_output = self.cache.get_model_output(
            f"gemini_{self.model}",
            input_hash
        )
        if cached_output:
            logger.info("✅ Using Redis cached Gemini response")
            # Estimate tokens for cached response
            self._estimate_tokens_from_text(self.SYSTEM_PROMPT + prompt, cached_output)
            return cached_output
        
        # Call Gemini API
        logger.info("🌐 Calling Gemini API")
        full_prompt = f"{self.SYSTEM_PROMPT}\n\n{prompt}"
        response = await asyncio.to_thread(
            self.gemini_client.generate_content,
            full_prompt
        )
        
        output = response.text
        
        # Estimate tokens (Gemini doesn't provide exact counts)
        self._estimate_tokens_from_text(full_prompt, output)
        
        # Cache in Redis
        self.cache.set_model_output(
            f"gemini_{self.model}",
            input_hash,
            output
        )
        logger.info(f"Cached Gemini response in Redis (est. tokens={self.last_total_tokens})")
        
        return output
    
    async def _call_ollama(self, prompt: str) -> str:
        """Call Ollama with condensed prompt, Redis caching, and token estimation"""
        
        # Use condensed prompt for speed
        full_prompt = f"{self.CONDENSED_SYSTEM_PROMPT}\n\n{prompt}"
        
        # Generate cache key
        input_hash = hashlib.md5(full_prompt.encode()).hexdigest()
        
        # Try Redis cache first
        cached_output = self.cache.get_model_output(
            f"ollama_{self.model}",
            input_hash
        )
        if cached_output:
            logger.info("✅ Using Redis cached Ollama response")
            # Estimate tokens for cached response
            self._estimate_tokens_from_text(full_prompt, cached_output)
            return cached_output
        
        # Call Ollama API
        logger.info("🌐 Calling Ollama API")
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 1500
                }
            }
            
            async with session.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    output = result.get('response', '')
                    
                    # Estimate tokens (Ollama doesn't provide exact counts)
                    self._estimate_tokens_from_text(full_prompt, output)
                    
                    # Cache in Redis
                    self.cache.set_model_output(
                        f"ollama_{self.model}",
                        input_hash,
                        output
                    )
                    logger.info(f"💾 Cached Ollama response in Redis (est. tokens={self.last_total_tokens})")
                    
                    return output
                else:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error {response.status}: {error_text}")
    
    # Token estimation for non-Claude models
    def _estimate_tokens_from_text(self, prompt: str, completion: str):
        """Estimate token counts from text (for Gemini/Ollama)"""
        # Rough estimation: 1 token ≈ 0.75 words
        # More accurate: 1 token ≈ 4 characters
        self.last_prompt_tokens = int(len(prompt.split()) * 1.3)
        self.last_completion_tokens = int(len(completion.split()) * 1.3)
        self.last_total_tokens = self.last_prompt_tokens + self.last_completion_tokens
    
    # Get token counts helper
    def _get_last_token_counts(self) -> Dict:
        """Get token counts from last API call"""
        return {
            'prompt_tokens': self.last_prompt_tokens,
            'completion_tokens': self.last_completion_tokens,
            'total_tokens': self.last_total_tokens
        }
    
    # ✅ NEW: Cost calculation
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost based on model and token counts"""
        
        # Claude pricing (per 1M tokens)
        if self.client_type == 'claude':
            if 'opus' in self.model:
                input_cost = (prompt_tokens / 1_000_000) * 15.00
                output_cost = (completion_tokens / 1_000_000) * 75.00
            elif 'sonnet' in self.model:
                input_cost = (prompt_tokens / 1_000_000) * 3.00
                output_cost = (completion_tokens / 1_000_000) * 15.00
            elif 'haiku' in self.model:
                input_cost = (prompt_tokens / 1_000_000) * 0.80
                output_cost = (completion_tokens / 1_000_000) * 4.00
            else:
                input_cost = (prompt_tokens / 1_000_000) * 3.00
                output_cost = (completion_tokens / 1_000_000) * 15.00
            
            return input_cost + output_cost
        
        # Gemini pricing
        elif self.client_type == 'gemini':
            if 'pro' in self.model:
                input_cost = (prompt_tokens / 1_000_000) * 1.25
                output_cost = (completion_tokens / 1_000_000) * 5.00
            else:  # flash
                input_cost = (prompt_tokens / 1_000_000) * 0.075
                output_cost = (completion_tokens / 1_000_000) * 0.30
            
            return input_cost + output_cost
        
        # Ollama is free
        else:
            return 0.0
    
    def _classify_strategic_question(self, question: str) -> tuple[str, str]:
        """Classify type of strategic question and suggest framework"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in [
            'competitive', 'competition', 'rivals', 'barriers to entry',
            'industry structure', 'threat of'
        ]):
            return ('competitive_dynamics', 'porters_five_forces')
        
        if any(word in question_lower for word in [
            'differentiate', 'unique', 'stand out', 'value innovation',
            'blue ocean', 'uncontested'
        ]):
            return ('differentiation', 'blue_ocean')
        
        if any(word in question_lower for word in [
            'enter market', 'new market', 'expand to', 'where to play',
            'target market'
        ]):
            return ('market_entry', 'playing_to_win')
        
        if any(word in question_lower for word in [
            'position', 'messaging', 'brand', 'perception',
            'how we\'re seen'
        ]):
            return ('positioning', 'positioning')
        
        if any(word in question_lower for word in [
            'or', 'versus', 'vs', 'choose between', 'trade-off',
            'should we', 'which option'
        ]):
            return ('trade_offs', 'strategic_tradeoffs')
        
        return ('strategic_decision', 'playing_to_win')
    
    def _build_analysis_prompt(
        self,
        question: str,
        user_context: str,
        question_metadata: Dict,
        question_type: str,
        suggested_framework: str
    ) -> str:
        """Build prompt for strategic analysis"""
        
        return f"""
USER CONTEXT:
{user_context}

QUESTION TYPE: {question_type}
SUGGESTED FRAMEWORK: {suggested_framework}
COMPLEXITY: {question_metadata.get('complexity', 'medium')}
URGENCY: {question_metadata.get('urgency', 'routine')}

USER QUESTION:
{question}

Provide Strategy Analyst analysis following the framework.
Reframe the decision to reveal what they're REALLY choosing.
Apply the most relevant strategic framework.
Test key assumptions and identify trade-offs.
"""
    
    async def _parse_agent_response(self, response_text: str) -> Dict:
        """Parse agent response using LLM parser"""
        from .utils.llm_parser import get_parser
        
        try:
            parser = get_parser()
            return await parser.parse_strategy_analyst_response(response_text)
        except Exception as e:
            logger.error(f"LLM parsing failed: {str(e)}")
            return {
                'decision_reframe': response_text,
                'confidence': '🟡 Medium',
                'framework_applied': '',
                'framework_analysis': '',
                'assumptions_tested': '',
                'strategic_blindspot': '',
                'trade_offs': '',
                'for_your_situation': '',
                'question_back': ''
            }


# Example usage
if __name__ == '__main__':
    """Test Strategy Analyst agent with caching and token tracking"""
    from decouple import config
    
    async def test_agent():
        anthropic_key = config('ANTHROPIC_API_KEY')
        google_key = config('GOOGLE_AI_API_KEY', default=None)
        
        agent = StrategyAnalystAgent(
            anthropic_api_key=anthropic_key,
            google_api_key=google_key,
            model='claude-sonnet-4-20250514'
        )
        
        test_question = "Should we target enterprise customers or stay focused on SMB?"
        test_context = """
User: CEO at Series A SaaS startup
Company: B2B Project Management Tool
Current State: 100 SMB customers, $500K ARR, team of 12
Recent questions: Market positioning, growth strategy, competitive advantage
"""
        test_metadata = {
            'question_type': 'decision',
            'domains': ['strategy', 'market'],
            'complexity': 'complex',
            'urgency': 'important'
        }
        
        print("\n" + "=" * 80)
        print("TESTING STRATEGY ANALYST AGENT WITH TOKEN TRACKING")
        print("=" * 80)
        
        # First call - should hit API
        print("\n[TEST 1] First call (API)...")
        result1 = await agent.analyze(
            question=test_question,
            user_context=test_context,
            question_metadata=test_metadata
        )
        print(f"✅ Response Time: {result1['response_time']}s")
        print(f"✅ From Cache: {result1.get('from_cache', False)}")
        print(f"✅ Prompt Tokens: {result1.get('prompt_tokens', 0)}")
        print(f"✅ Completion Tokens: {result1.get('completion_tokens', 0)}")
        print(f"✅ Total Tokens: {result1.get('total_tokens', 0)}")
        print(f"✅ Cost: ${result1.get('cost', 0):.6f}")
        
        # Second call - should hit cache
        print("\n[TEST 2] Second call (Cache)...")
        result2 = await agent.analyze(
            question=test_question,
            user_context=test_context,
            question_metadata=test_metadata
        )
        print(f"✅ Response Time: {result2['response_time']}s")
        print(f"✅ From Cache: {result2.get('from_cache', False)}")
        print(f"✅ Total Tokens: {result2.get('total_tokens', 0)}")
        
        # Cache stats
        cache = get_cache_manager()
        stats = cache.get_stats()
        print(f"\n📊 Cache Stats: {stats}")
        
        print("\n" + "=" * 80)
    
    asyncio.run(test_agent())