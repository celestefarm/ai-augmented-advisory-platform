# agents/market_compass.py

"""
MARKET COMPASS AGENT
Mission: Reveal market signals, competitive threats, and opportunity assessment

Core Capabilities:
1. Real-time market data retrieval (web search via Gemini)
2. Competitive intelligence tracking
3. Market signal interpretation
4. Trend analysis and blindspot detection

Model Strategy:
- Multi-model support: Claude, Gemini, Ollama
- Automatic client detection based on model name
- Gemini preferred for web search capability

Caching Strategy:
- System prompts: 1 hour (Redis)
- Model outputs: 30 minutes (Redis)
- Agent responses: 15 minutes (Redis)

Output: Market intelligence with confidence marking, sources, and blindspot detection
"""

import time
import asyncio
from typing import Dict, Optional, Tuple
import logging
import aiohttp
import hashlib

logger = logging.getLogger(__name__)

from agents.utils.cache import get_cache_manager

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI SDK not installed. Gemini unavailable.")

# Import Claude as fallback
from anthropic import AsyncAnthropic


class MarketCompassAgent:
    """
    Market Compass - Market Intelligence & Competitive Analysis Agent
    
    Responsibilities:
    - Spot early market signals
    - Track competitive moves
    - Identify market blindspots
    - Assess market opportunities with timing
    - Translate signals to user-specific implications
    
    Multi-Model Support:
    - Claude (claude-*): Anthropic API
    - Gemini (gemini-*): Google AI API with web search
    - Ollama (llama*, mistral*, etc.): Local Ollama server
    
    Caching Strategy:
    - Redis cache for all model outputs
    - Condensed prompts for Ollama (faster first requests)
    - Full prompts for Claude/Gemini (better quality)
    """
    
    # Condensed prompt for Ollama (faster)
    CONDENSED_SYSTEM_PROMPT = """You are a Market Compass - market intelligence expert.

        Provide market analysis with:
        1. **Analysis**: Market signals, competitive threats, opportunities
        2. **Signal**: Key market signal or trend identified
        3. **For Your Situation**: Specific implications for this user
        4. **Blindspot**: What they might be missing
        5. **Timing**: When to act (now/soon/monitor)
        6. **Confidence**: Mark as 🟢 High, 🟡 Medium, or 🔴 Low

        Focus on actionable market intelligence."""
    
    @staticmethod
    def _load_system_prompt() -> str:
        """Load Market Compass Harvard-level prompt from external file"""
        from pathlib import Path
        
        # Look for prompt file
        prompt_file = Path(__file__).parent / 'prompts' / 'market_compass_prompt.txt'
        
        if not prompt_file.exists():
            # Fallback to basic prompt if file doesn't exist
            logger.warning(f"Market Compass prompt file not found: {prompt_file}")
            return """You are MARKET COMPASS, a market intelligence agent.
Provide market analysis, competitive intelligence, and trend insights.
Focus on actionable intelligence specific to the user's situation."""
                        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Agent system prompt loaded from external file
    SYSTEM_PROMPT = _load_system_prompt()
    
    def __init__(
        self,
        anthropic_api_key: str,
        google_api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        use_web_search: bool = True
    ):
        """
        Initialize Market Compass Agent with multi-model support and caching
        
        Args:
            anthropic_api_key: Anthropic API key
            google_api_key: Google AI API key (for Gemini)
            model: Model to use (auto-detects client type)
            use_web_search: Whether to use real-time web search
        """
        self.cache = get_cache_manager()  # ✅ UNIFIED CACHE
        self.model = model
        self.use_web_search = use_web_search

        # Hash system prompts for caching
        self.full_prompt_hash = hashlib.md5(self.SYSTEM_PROMPT.encode()).hexdigest()
        self.condensed_prompt_hash = hashlib.md5(self.CONDENSED_SYSTEM_PROMPT.encode()).hexdigest()
        
        # ✅ AUTO-DETECT CLIENT TYPE
        if model.startswith('llama') or model.startswith('ollama') or model.startswith('mistral'):
            # Ollama model
            self.client_type = 'ollama'
            self.ollama_url = 'http://localhost:11434'
            logger.info(f"Market Compass initialized with Ollama: {model}")
            
        elif model.startswith('gemini') and GEMINI_AVAILABLE and google_api_key:
            # Gemini model with web search
            self.client_type = 'gemini'
            genai.configure(api_key=google_api_key)
            self.gemini_model = genai.GenerativeModel(
                model_name=model,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1500,
                    temperature=0.3,
                )
            )
            logger.info(f"Market Compass initialized with Gemini: {model}")
            
        else:
            # Claude model (default)
            self.client_type = 'claude'
            self.claude_client = AsyncAnthropic(api_key=anthropic_api_key)
            logger.info(f"Market Compass initialized with Claude: {model}")
    
    async def analyze(
        self,
        question: str,
        user_context: str,
        question_metadata: Dict
    ) -> Dict:
        """
        Analyze market question and provide intelligence with caching
        
        Args:
            question: User's market question
            user_context: User profile and context
            question_metadata: Question classification metadata
            
        Returns:
            Dict with analysis, confidence, sources, etc.
        """
        start_time = time.time()
        
        try:
            # Check cache for complete agent response
            question_hash = hashlib.md5(
                f"{question}:{user_context}".encode()
            ).hexdigest()
            
            cached_response = self.cache.get_agent_response(
                question_hash,
                'market_compass'
            )
            
            if cached_response:
                logger.info("✅ Using cached Market Compass response")
                cached_response['response_time'] = round(time.time() - start_time, 2)
                cached_response['from_cache'] = True
                return cached_response
            
            # Determine question type
            question_type = self._classify_market_question(question)
            
            # Build prompt
            prompt = self._build_analysis_prompt(
                question,
                user_context,
                question_metadata,
                question_type
            )
            
            # ✅ ROUTE TO APPROPRIATE CLIENT
            if self.client_type == 'ollama':
                response_text = await self._call_ollama(prompt)
                web_search_used = False
            elif self.client_type == 'gemini':
                # Use Gemini with web search if enabled
                if self.use_web_search and question_type in ['market_data', 'competitive_intelligence']:
                    response_text = await self._call_gemini_with_search(prompt)
                    web_search_used = True
                else:
                    response_text = await self._call_gemini(prompt)
                    web_search_used = False
            else:  # claude
                response_text = await self._call_claude(prompt)
                web_search_used = False
            
            # Parse response
            result = await self._parse_agent_response(response_text)
            result['model_used'] = self.model
            result['client_type'] = self.client_type
            result['web_search_used'] = web_search_used
            result['agent_name'] = 'market_compass'
            result['question_type'] = question_type
            result['response_time'] = round(time.time() - start_time, 2)
            result['success'] = True
            result['from_cache'] = False
            
            # Cache the agent response
            self.cache.set_agent_response(
                question_hash,
                'market_compass',
                result
            )
            
            logger.info(
                f"Market Compass analysis complete - "
                f"type={question_type}, client={self.client_type}, "
                f"search={web_search_used}, time={result['response_time']}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Market Compass analysis failed: {str(e)}", exc_info=True)
            
            # Return fallback response
            return {
                'agent_name': 'market_compass',
                'success': False,
                'error': str(e),
                'response_time': round(time.time() - start_time, 2),
                'analysis': 'Unable to complete market analysis due to technical error.',
                'confidence': '🔴 Low - Analysis failed',
                'fallback': True,
                'from_cache': False
            }
    
    async def _call_claude(self, prompt: str) -> str:
        """Call Claude API with Redis + Anthropic dual caching"""
        
        # Generate cache key
        input_hash = hashlib.md5(prompt.encode()).hexdigest()
        
        # Try Redis cache first (30 min TTL)
        cached_output = self.cache.get_model_output(
            f"claude_{self.model}",
            input_hash
        )
        if cached_output:
            logger.info("✅ Using Redis cached Claude response")
            return cached_output
        
        # Call Claude API with Anthropic's prompt caching
        logger.info("🌐 Calling Claude API with prompt caching")
        response = await self.claude_client.messages.create(
            model=self.model,
            max_tokens=1500,
            temperature=0.7,
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
        
        # Cache in Redis (30 min)
        self.cache.set_model_output(
            f"claude_{self.model}",
            input_hash,
            output
        )
        logger.info("Cached Claude response in Redis")
        
        return output
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API with Redis caching (without web search)"""
        
        # Generate cache key
        full_prompt = f"{self.SYSTEM_PROMPT}\n\n{prompt}"
        input_hash = hashlib.md5(full_prompt.encode()).hexdigest()
        
        # Try Redis cache first
        cached_output = self.cache.get_model_output(
            f"gemini_{self.model}",
            input_hash
        )
        if cached_output:
            logger.info("✅ Using Redis cached Gemini response")
            return cached_output
        
        # Call Gemini API
        logger.info("🌐 Calling Gemini API")
        response = await asyncio.to_thread(
            self.gemini_model.generate_content,
            full_prompt
        )
        
        output = response.text
        
        # Cache in Redis
        self.cache.set_model_output(
            f"gemini_{self.model}",
            input_hash,
            output
        )
        logger.info("💾 Cached Gemini response in Redis")
        
        return output
    
    async def _call_gemini_with_search(self, prompt: str) -> str:
        """Call Gemini API with Google Search grounding and Redis caching"""
        
        # Generate cache key (include 'search' in key to differentiate)
        full_prompt = f"{self.SYSTEM_PROMPT}\n\n{prompt}"
        input_hash = hashlib.md5(f"search:{full_prompt}".encode()).hexdigest()
        
        # Try Redis cache first
        cached_output = self.cache.get_model_output(
            f"gemini_{self.model}_search",
            input_hash
        )
        if cached_output:
            logger.info("✅ Using Redis cached Gemini+Search response")
            return cached_output
        
        # Call Gemini API with search
        logger.info("🌐 Calling Gemini API with Google Search")
        response = await asyncio.to_thread(
            self.gemini_model.generate_content,
            full_prompt,
            tools=[genai.protos.Tool(google_search_retrieval={})]
        )
        
        output = response.text
        
        # Cache in Redis
        self.cache.set_model_output(
            f"gemini_{self.model}_search",
            input_hash,
            output
        )
        logger.info("💾 Cached Gemini+Search response in Redis")
        
        return output
    
    async def _call_ollama(self, prompt: str) -> str:
        """Call Ollama with condensed prompt and Redis caching"""
        
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
            return cached_output
        
        # Call Ollama API
        logger.info("🌐 Calling Ollama API with condensed prompt")
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
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
                    
                    # Cache in Redis
                    self.cache.set_model_output(
                        f"ollama_{self.model}",
                        input_hash,
                        output
                    )
                    logger.info("Cached Ollama response in Redis")
                    
                    return output
                else:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error {response.status}: {error_text}")
    
    def _classify_market_question(self, question: str) -> str:
        """
        Classify type of market question
        
        Returns:
            'market_data' | 'competitive_intelligence' | 'signal_interpretation' | 'market_strategy'
        """
        question_lower = question.lower()
        
        # Market data keywords
        if any(word in question_lower for word in [
            'market size', 'tam', 'market value', 'industry size',
            'benchmark', 'average', 'typical', 'industry standard'
        ]):
            return 'market_data'
        
        # Competitive intelligence keywords
        if any(word in question_lower for word in [
            'competitor', 'competition', 'rival', 'competing',
            'what are they doing', 'their strategy', 'competitive'
        ]):
            return 'competitive_intelligence'
        
        # Signal interpretation keywords
        if any(word in question_lower for word in [
            'trend', 'signal', 'emerging', 'shift', 'changing',
            'is this real', 'should i worry', 'threat', 'opportunity'
        ]):
            return 'signal_interpretation'
        
        # Default to market strategy
        return 'market_strategy'
    
    def _build_analysis_prompt(
        self,
        question: str,
        user_context: str,
        question_metadata: Dict,
        question_type: str
    ) -> str:
        """Build prompt for market analysis"""
        
        return f"""
USER CONTEXT:
{user_context}

QUESTION TYPE: {question_type}
COMPLEXITY: {question_metadata.get('complexity', 'medium')}
URGENCY: {question_metadata.get('urgency', 'routine')}

USER QUESTION:
{question}

Provide Market Compass analysis following the framework.
Identify market signals, competitive threats, and opportunities.
Include confidence marking and sources where applicable.
"""
                
    async def _parse_agent_response(self, response_text: str) -> Dict:
        """
        Parse agent response using LLM parser for robust extraction
        
        Handles natural language variations better than regex
        """
        from .utils.llm_parser import get_parser

        try:
            parser = get_parser()
            return await parser.parse_market_compass_response(response_text)
        except Exception as e:
            logger.error(f"LLM parsing failed: {str(e)}")
            # Ultimate fallback
            return {
                'analysis': response_text,
                'confidence': '🟡 Medium',
                'signal': '',
                'for_your_situation': '',
                'blindspot': '',
                'timing': '',
                'sources': '',
                'question_back': ''
            }


# Example usage
if __name__ == '__main__':
    """Test Market Compass agent with caching"""
    from decouple import config
    
    async def test_agent():
        anthropic_key = config('ANTHROPIC_API_KEY')
        google_key = config('GOOGLE_AI_API_KEY', default=None)
        
        agent = MarketCompassAgent(
            anthropic_api_key=anthropic_key,
            google_api_key=google_key,
            model='claude-sonnet-4-20250514',  # Try: 'gemini-2.0-flash-exp' or 'llama3.1:8b'
            use_web_search=True
        )
        
        # Test question
        test_question = "What's the current state of the AI SaaS market?"
        test_context = """
User: VP Strategy at early-stage SaaS company
Industry: B2B Software
Expertise: Intermediate
Recent questions: Market positioning, competitive analysis
"""
        test_metadata = {
            'question_type': 'exploration',
            'domains': ['market', 'strategy'],
            'complexity': 'medium',
            'urgency': 'routine'
        }
        
        print("\n" + "=" * 80)
        print("TESTING MARKET COMPASS AGENT WITH CACHE")
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
        print(f"✅ Model Used: {result1.get('model_used', 'N/A')}")
        print(f"✅ Web Search: {result1.get('web_search_used', False)}")
        
        # Second call - should hit cache
        print("\n[TEST 2] Second call (Cache)...")
        result2 = await agent.analyze(
            question=test_question,
            user_context=test_context,
            question_metadata=test_metadata
        )
        print(f"✅ Response Time: {result2['response_time']}s")
        print(f"✅ From Cache: {result2.get('from_cache', False)}")
        
        # Cache stats
        cache = get_cache_manager()
        stats = cache.get_stats()
        print(f"\n📊 Cache Stats: {stats}")
        
        print("\n" + "=" * 80)
    
    asyncio.run(test_agent())