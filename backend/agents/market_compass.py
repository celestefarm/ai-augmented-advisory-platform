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

Output: Market intelligence with confidence marking, sources, and blindspot detection
"""

import time
import asyncio
from typing import Dict, Optional, Tuple
import logging
import aiohttp

logger = logging.getLogger(__name__)

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
    """
    
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
        Initialize Market Compass Agent with multi-model support
        
        Args:
            anthropic_api_key: Anthropic API key
            google_api_key: Google AI API key (for Gemini)
            model: Model to use (auto-detects client type)
            use_web_search: Whether to use real-time web search
        """
        self.model = model
        self.use_web_search = use_web_search
        
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
        Analyze market question and provide intelligence
        
        Args:
            question: User's market question
            user_context: User profile and context
            question_metadata: Question classification metadata
            
        Returns:
            Dict with analysis, confidence, sources, etc.
        """
        start_time = time.time()
        
        try:
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
                'fallback': True
            }
    
    async def _call_claude(self, prompt: str) -> str:
        """Call Claude API"""
        response = await self.claude_client.messages.create(
            model=self.model,
            max_tokens=1500,
            temperature=0.7,
            system=self.SYSTEM_PROMPT,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response.content[0].text
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API (without web search)"""
        full_prompt = f"{self.SYSTEM_PROMPT}\n\n{prompt}"
        response = await asyncio.to_thread(
            self.gemini_model.generate_content,
            full_prompt
        )
        return response.text
    
    async def _call_gemini_with_search(self, prompt: str) -> str:
        """Call Gemini API with Google Search grounding"""
        full_prompt = f"{self.SYSTEM_PROMPT}\n\n{prompt}"
        response = await asyncio.to_thread(
            self.gemini_model.generate_content,
            full_prompt,
            tools=[genai.protos.Tool(google_search_retrieval={})]
        )
        return response.text
    
    async def _call_ollama(self, prompt: str) -> str:
        """Call Ollama local server"""
        full_prompt = f"{self.SYSTEM_PROMPT}\n\n{prompt}"
        
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
                    return result.get('response', '')
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
        Parse agent response using LLM (Ollama) for robust extraction
        
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
    """Test Market Compass agent"""
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
        print("TESTING MARKET COMPASS AGENT")
        print("=" * 80)
        print(f"\nQuestion: {test_question}")
        print(f"Context: {test_context.strip()}")
        
        result = await agent.analyze(
            question=test_question,
            user_context=test_context,
            question_metadata=test_metadata
        )
        
        print("\n" + "=" * 80)
        print("AGENT RESPONSE")
        print("=" * 80)
        print(f"\nSuccess: {result['success']}")
        print(f"Response Time: {result['response_time']}s")
        print(f"Model Used: {result.get('model_used', 'N/A')}")
        print(f"Client Type: {result.get('client_type', 'N/A')}")
        print(f"Web Search: {result.get('web_search_used', False)}")
        print(f"\nAnalysis:\n{result['analysis']}")
        print(f"\nConfidence: {result['confidence']}")
        
        if result.get('blindspot'):
            print(f"\nBlindspot: {result['blindspot']}")
        
        print("\n" + "=" * 80)
    
    asyncio.run(test_agent())