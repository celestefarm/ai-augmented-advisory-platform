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
- Primary: Gemini 2.0 Pro (for web search capability)
- Fallback: Claude Sonnet (for analysis without search)
- Two-phase for complex queries: Gemini (research) → Claude (synthesis)

Output: Market intelligence with confidence marking, sources, and blindspot detection
"""

import time
import asyncio
from typing import Dict, Optional, Tuple
import logging

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
        use_web_search: bool = True
    ):
        """
        Initialize Market Compass Agent
        
        Args:
            anthropic_api_key: Anthropic API key (fallback)
            google_api_key: Google AI API key (for Gemini + search)
            use_web_search: Whether to use real-time web search
        """
        self.use_web_search = use_web_search and GEMINI_AVAILABLE and google_api_key
        
        # Initialize Claude (fallback)
        self.claude_client = AsyncAnthropic(api_key=anthropic_api_key)
        
        # Initialize Gemini if available
        if self.use_web_search:
            genai.configure(api_key=google_api_key)
            self.gemini_model = genai.GenerativeModel(
                model_name='gemini-2.0-flash-exp',  # Fast model with search
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1500,
                    temperature=0.6,
                )
            )
            logger.info("Market Compass initialized with Gemini web search")
        else:
            logger.info("Market Compass initialized with Claude (no web search)")
    
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
            
            # Route to appropriate analysis method
            if question_type in ['market_data', 'competitive_intelligence'] and self.use_web_search:
                # Use Gemini with web search for factual retrieval
                result = await self._analyze_with_web_search(
                    question,
                    user_context,
                    question_metadata,
                    question_type
                )
            elif question_type == 'signal_interpretation':
                # Two-phase: Gemini research + Claude interpretation
                result = await self._analyze_signal_two_phase(
                    question,
                    user_context,
                    question_metadata
                )
            else:
                # Use Claude for strategic analysis
                result = await self._analyze_with_claude(
                    question,
                    user_context,
                    question_metadata
                )
            
            # Add timing metadata
            result['response_time'] = round(time.time() - start_time, 2)
            result['agent_name'] = 'market_compass'
            result['question_type'] = question_type
            result['success'] = True
            
            logger.info(
                f"Market Compass analysis complete - "
                f"type={question_type}, time={result['response_time']}s"
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
    
    async def _analyze_with_web_search(
        self,
        question: str,
        user_context: str,
        question_metadata: Dict,
        question_type: str
    ) -> Dict:
        """
        Analyze using Gemini with web search (for factual market data)
        """
        # Build prompt with context
        prompt = self._build_research_prompt(
            question,
            user_context,
            question_metadata,
            question_type
        )
        
        # Call Gemini with Google Search grounding
        response = await asyncio.to_thread(
            self.gemini_model.generate_content,
            prompt,
            tools=[genai.protos.Tool(google_search_retrieval={})]
        )
        
        # Parse response
        response_text = response.text
        
        # Extract structured data (basic parsing)
        result = self._parse_agent_response(response_text)
        result['model_used'] = 'gemini-2.0-flash-exp'
        result['web_search_used'] = True
        
        return result
    
    async def _analyze_with_claude(
        self,
        question: str,
        user_context: str,
        question_metadata: Dict
    ) -> Dict:
        """
        Analyze using Claude (for strategic analysis without web search)
        """
        # Build prompt
        prompt = self._build_strategic_prompt(
            question,
            user_context,
            question_metadata
        )
        
        # Call Claude
        response = await self.claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            temperature=0.7,
            system=self.SYSTEM_PROMPT,
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        response_text = response.content[0].text
        
        # Parse response
        result = self._parse_agent_response(response_text)
        result['model_used'] = 'claude-sonnet-4'
        result['web_search_used'] = False
        
        return result
    
    async def _analyze_signal_two_phase(
        self,
        question: str,
        user_context: str,
        question_metadata: Dict
    ) -> Dict:
        """
        Two-phase analysis: Gemini research + Claude interpretation
        """
        # Phase 1: Gemini gathers data
        if self.use_web_search:
            research_prompt = f"""Research this market signal: {question}

                    Find recent data, news, and trends related to this signal.
                    Focus on: facts, data points, recent developments, expert opinions.

                    Return factual research only (no interpretation yet)."""

            research_response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                research_prompt,
                tools=[genai.protos.Tool(google_search_retrieval={})]
            )
            
            research_data = research_response.text
        else:
            research_data = "No web search available - using Claude's knowledge only"
        
        # Phase 2: Claude interprets with user context
        interpretation_prompt = f"""
            {self.SYSTEM_PROMPT}

            USER CONTEXT:
            {user_context}

            RESEARCH DATA:
            {research_data}

            USER QUESTION:
            {question}

            Interpret this signal specifically for this user's situation.
            Apply the Market Compass framework to provide personalized intelligence.
            """
        
        response = await self.claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            temperature=0.7,
            messages=[{'role': 'user', 'content': interpretation_prompt}]
        )
        
        response_text = response.content[0].text
        
        # Parse response
        result = self._parse_agent_response(response_text)
        result['model_used'] = 'gemini-research + claude-interpretation'
        result['web_search_used'] = self.use_web_search
        result['two_phase'] = True
        
        return result
    
    def _build_research_prompt(
        self,
        question: str,
        user_context: str,
        question_metadata: Dict,
        question_type: str
    ) -> str:
        """Build prompt for research-focused questions"""
        
        return f"""
            {self.SYSTEM_PROMPT}

            USER CONTEXT:
            {user_context}

            QUESTION TYPE: {question_type}
            COMPLEXITY: {question_metadata.get('complexity', 'medium')}
            URGENCY: {question_metadata.get('urgency', 'routine')}

            USER QUESTION:
            {question}

            Use real-time web search to gather current market data.
            Then provide Market Compass analysis following the framework.
            Include sources from your research.
            """
    
    def _build_strategic_prompt(
        self,
        question: str,
        user_context: str,
        question_metadata: Dict
    ) -> str:
        """Build prompt for strategic analysis"""
        
        return f"""
            USER CONTEXT:
            {user_context}

            COMPLEXITY: {question_metadata.get('complexity', 'medium')}
            URGENCY: {question_metadata.get('urgency', 'routine')}

            USER QUESTION:
            {question}

            Provide Market Compass analysis following the framework.
            Use your knowledge of market patterns and strategic principles.
            """
                
    def _parse_agent_response(self, response_text: str) -> Dict:
        """
        Parse agent response using LLM (Ollama) for robust extraction
        
        Handles natural language variations better than regex
        """
        from .utils.llm_parser import LLMResponseParser
        
        try:
            return LLMResponseParser.parse_market_compass_response(response_text)
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
        print(f"Web Search: {result.get('web_search_used', False)}")
        print(f"\nAnalysis:\n{result['analysis']}")
        print(f"\nConfidence: {result['confidence']}")
        
        if result.get('blindspot'):
            print(f"\nBlindspot: {result['blindspot']}")
        
        print("\n" + "=" * 80)
    
    asyncio.run(test_agent())