# agents/strategy_analyst.py

"""
STRATEGY ANALYST AGENT
Mission: Strategic framework application and decision reframing

Core Capabilities:
1. Apply strategic frameworks (Porter's Five Forces, Blue Ocean, etc.)
2. Test underlying assumptions
3. Reframe decisions to reveal true choices
4. Identify strategic blindspots
5. Reveal trade-offs (saying YES to X means NO to Y)

Model Strategy:
- Primary: Claude Sonnet (excellent strategic reasoning)
- Temperature: 0.7 (standard)
- Pure reasoning, no external tools needed

Output: Strategic analysis with framework application, assumption testing, and confidence marking
"""

import time
import asyncio
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

from anthropic import AsyncAnthropic


class StrategyAnalystAgent:
    """
    Strategy Analyst - Strategic Framework & Decision Reframing Agent
    
    Responsibilities:
    - Apply strategic frameworks to real situations
    - Reframe decisions to reveal core trade-offs
    - Test assumptions and identify risks
    - Find relevant precedents and patterns
    - Identify strategic blindspots
    """
    
    @staticmethod
    def _load_system_prompt() -> str:
        """Load Strategy Analyst Harvard-level prompt from external file"""
        from pathlib import Path
        
        # Look for prompt file
        prompt_file = Path(__file__).parent / 'prompts' / 'strategy_analyst_prompt.txt'
        
        if not prompt_file.exists():
            # Fallback to basic prompt if file doesn't exist
            logger.warning(f"Strategy Analyst prompt file not found: {prompt_file}")
            return """You are STRATEGY ANALYST, a strategic framework expert.
Provide strategic analysis, framework application, and decision reframing.
Focus on actionable strategic intelligence specific to the user's situation."""
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Agent system prompt loaded from external file
    SYSTEM_PROMPT = _load_system_prompt()
    
    def __init__(self, anthropic_api_key: str):
        """
        Initialize Strategy Analyst Agent
        
        Args:
            anthropic_api_key: Anthropic API key
        """
        self.claude_client = AsyncAnthropic(api_key=anthropic_api_key)
        logger.info("Strategy Analyst initialized with Claude Sonnet")
    
    async def analyze(
        self,
        question: str,
        user_context: str,
        question_metadata: Dict
    ) -> Dict:
        """
        Analyze strategic question and provide framework-based insights
        
        Args:
            question: User's strategic question
            user_context: User profile and context
            question_metadata: Question classification metadata
            
        Returns:
            Dict with decision reframe, framework analysis, trade-offs, etc.
        """
        start_time = time.time()
        
        try:
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
            result['agent_name'] = 'strategy_analyst'
            result['question_type'] = question_type
            result['framework_suggested'] = suggested_framework
            result['response_time'] = round(time.time() - start_time, 2)
            result['success'] = True
            
            logger.info(
                f"Strategy Analyst analysis complete - "
                f"type={question_type}, framework={suggested_framework}, "
                f"time={result['response_time']}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Strategy Analyst analysis failed: {str(e)}", exc_info=True)
            
            # Return fallback response
            return {
                'agent_name': 'strategy_analyst',
                'success': False,
                'error': str(e),
                'response_time': round(time.time() - start_time, 2),
                'decision_reframe': 'Unable to complete strategic analysis due to technical error.',
                'confidence': '🔴 Low - Analysis failed',
                'fallback': True
            }
    
    def _classify_strategic_question(self, question: str) -> tuple[str, str]:
        """
        Classify type of strategic question and suggest framework
        
        Returns:
            Tuple of (question_type, suggested_framework)
        """
        question_lower = question.lower()
        
        # Competitive dynamics
        if any(word in question_lower for word in [
            'competitive', 'competition', 'rivals', 'barriers to entry',
            'industry structure', 'threat of'
        ]):
            return ('competitive_dynamics', 'porters_five_forces')
        
        # Differentiation
        if any(word in question_lower for word in [
            'differentiate', 'unique', 'stand out', 'value innovation',
            'blue ocean', 'uncontested'
        ]):
            return ('differentiation', 'blue_ocean')
        
        # Market entry
        if any(word in question_lower for word in [
            'enter market', 'new market', 'expand to', 'where to play',
            'target market'
        ]):
            return ('market_entry', 'playing_to_win')
        
        # Positioning
        if any(word in question_lower for word in [
            'position', 'messaging', 'brand', 'perception',
            'how we\'re seen'
        ]):
            return ('positioning', 'positioning')
        
        # Trade-offs
        if any(word in question_lower for word in [
            'or', 'versus', 'vs', 'choose between', 'trade-off',
            'should we', 'which option'
        ]):
            return ('trade_offs', 'strategic_tradeoffs')
        
        # Default to general strategic analysis
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
    
    def _parse_agent_response(self, response_text: str) -> Dict:
        """
        Parse agent response using LLM (Ollama) for robust extraction
        
        Handles natural language variations better than regex
        """
        from .utils.llm_parser import LLMResponseParser
        
        try:
            return LLMResponseParser.parse_strategy_analyst_response(response_text)
        except Exception as e:
            logger.error(f"LLM parsing failed: {str(e)}")
            # Ultimate fallback
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
    """Test Strategy Analyst agent"""
    from decouple import config
    
    async def test_agent():
        anthropic_key = config('ANTHROPIC_API_KEY')
        
        agent = StrategyAnalystAgent(anthropic_api_key=anthropic_key)
        
        # Test question
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
        print("TESTING STRATEGY ANALYST AGENT")
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
        print(f"Framework Suggested: {result.get('framework_suggested', 'N/A')}")
        print(f"\nDecision Reframe:\n{result['decision_reframe']}")
        print(f"\nConfidence: {result['confidence']}")
        
        if result.get('framework_applied'):
            print(f"\nFramework Applied: {result['framework_applied']}")
        
        if result.get('trade_offs'):
            print(f"\nTrade-offs: {result['trade_offs']}")
        
        if result.get('strategic_blindspot'):
            print(f"\nStrategic Blindspot: {result['strategic_blindspot']}")
        
        print("\n" + "=" * 80)
    
    asyncio.run(test_agent())