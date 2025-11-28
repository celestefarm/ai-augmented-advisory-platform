# agents/financial_guardian.py

"""
FINANCIAL GUARDIAN AGENT
Mission: Quantitative reality checking and financial analysis

Core Capabilities:
1. Financial calculations with work shown
2. Scenario modeling (best/realistic/worst cases)
3. Unit economics breakdown (CAC, LTV, payback)
4. Cash flow and runway analysis
5. ROI and payback period calculations

Model Strategy:
- Multi-model support: Claude, Gemini, Ollama
- Automatic client detection based on model name
- Lower temperature (0.3) for mathematical accuracy

Output: Financial analysis with calculations, scenarios, constraints, and confidence marking
"""

import time
import asyncio
from typing import Dict, Optional
import logging
import aiohttp

logger = logging.getLogger(__name__)

from anthropic import AsyncAnthropic

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI SDK not installed. Gemini unavailable.")


class FinancialGuardianAgent:
    """
    Financial Guardian - Quantitative Analysis & Reality Checking Agent
    
    Responsibilities:
    - Run financial calculations with work shown
    - Stress-test assumptions
    - Reveal cash constraints
    - Provide scenario ranges
    - Calculate ROI and payback periods
    
    Multi-Model Support:
    - Claude (claude-*): Anthropic API
    - Gemini (gemini-*): Google AI API
    - Ollama (llama*, mistral*, etc.): Local Ollama server
    """
    
    @staticmethod
    def _load_system_prompt() -> str:
        """Load Financial Guardian Harvard-level prompt from external file"""
        from pathlib import Path
        
        # Look for prompt file
        prompt_file = Path(__file__).parent / 'prompts' / 'financial_guardian_prompt.txt'
        
        if not prompt_file.exists():
            # Fallback to basic prompt if file doesn't exist
            logger.warning(f"Financial Guardian prompt file not found: {prompt_file}")
            return """You are FINANCIAL GUARDIAN, the quantitative reality checker.
                Provide financial analysis, unit economics assessment, and cash flow insights.
                Focus on actionable financial intelligence specific to the user's situation."""
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Agent system prompt loaded from external file
    SYSTEM_PROMPT = _load_system_prompt()
    
    def __init__(
        self,
        anthropic_api_key: str,
        model: str = "claude-sonnet-4-20250514",
        google_api_key: Optional[str] = None
    ):
        """
        Initialize Financial Guardian Agent with multi-model support
        
        Args:
            anthropic_api_key: Anthropic API key
            model: Model to use (auto-detects client type)
            google_api_key: Google API key (for Gemini models)
        """
        self.model = model
        
        # ✅ AUTO-DETECT CLIENT TYPE
        if model.startswith('llama') or model.startswith('ollama') or model.startswith('mistral'):
            # Ollama model
            self.client_type = 'ollama'
            self.ollama_url = 'http://localhost:11434'
            logger.info(f"Financial Guardian initialized with Ollama: {model}")
            
        elif model.startswith('gemini') and GEMINI_AVAILABLE and google_api_key:
            # Gemini model
            self.client_type = 'gemini'
            genai.configure(api_key=google_api_key)
            self.gemini_client = genai.GenerativeModel(
                model_name=model,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1500,
                    temperature=0.3,  # Lower for math accuracy
                )
            )
            logger.info(f"Financial Guardian initialized with Gemini: {model}")
            
        else:
            # Claude model (default)
            self.client_type = 'claude'
            self.claude_client = AsyncAnthropic(api_key=anthropic_api_key)
            logger.info(f"Financial Guardian initialized with Claude: {model}")
    
    async def analyze(
        self,
        question: str,
        user_context: str,
        question_metadata: Dict
    ) -> Dict:
        """
        Analyze financial question and provide quantitative reality check
        
        Args:
            question: User's financial question
            user_context: User profile and context
            question_metadata: Question classification metadata
            
        Returns:
            Dict with calculation, scenarios, constraints, etc.
        """
        start_time = time.time()
        
        try:
            # Determine question type
            question_type = self._classify_financial_question(question)
            
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
            elif self.client_type == 'gemini':
                response_text = await self._call_gemini(prompt)
            else:  # claude
                response_text = await self._call_claude(prompt)
            
            # Parse response
            result = await self._parse_agent_response(response_text)
            result['model_used'] = self.model
            result['client_type'] = self.client_type
            result['agent_name'] = 'financial_guardian'
            result['question_type'] = question_type
            result['response_time'] = round(time.time() - start_time, 2)
            result['success'] = True
            
            logger.info(
                f"Financial Guardian analysis complete - "
                f"type={question_type}, client={self.client_type}, "
                f"time={result['response_time']}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Financial Guardian analysis failed: {str(e)}", exc_info=True)
            
            # Return fallback response
            return {
                'agent_name': 'financial_guardian',
                'success': False,
                'error': str(e),
                'response_time': round(time.time() - start_time, 2),
                'calculation': 'Unable to complete financial analysis due to technical error.',
                'confidence': '🔴 Low - Analysis failed',
                'fallback': True
            }
    
    async def _call_claude(self, prompt: str) -> str:
        """Call Claude API"""
        response = await self.claude_client.messages.create(
            model=self.model,
            max_tokens=1500,
            temperature=0.3,  # Lower for math accuracy
            system=self.SYSTEM_PROMPT,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response.content[0].text
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API"""
        full_prompt = f"{self.SYSTEM_PROMPT}\n\n{prompt}"
        response = await asyncio.to_thread(
            self.gemini_client.generate_content,
            full_prompt
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
                    "temperature": 0.3,  # Lower for math accuracy
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
    
    def _classify_financial_question(self, question: str) -> str:
        """
        Classify type of financial question
        
        Returns:
            'calculation' | 'scenario' | 'unit_economics' | 'runway' | 'roi'
        """
        question_lower = question.lower()
        
        # Calculation keywords
        if any(word in question_lower for word in [
            'calculate', 'compute', 'what is', 'how much',
            'cost', 'price', 'revenue', 'profit'
        ]):
            return 'calculation'
        
        # Scenario keywords
        if any(word in question_lower for word in [
            'what if', 'scenario', 'best case', 'worst case',
            'if we', 'suppose', 'assuming'
        ]):
            return 'scenario'
        
        # Unit economics keywords
        if any(word in question_lower for word in [
            'cac', 'ltv', 'customer acquisition', 'lifetime value',
            'payback', 'unit economics', 'margin', 'per customer'
        ]):
            return 'unit_economics'
        
        # Runway keywords
        if any(word in question_lower for word in [
            'runway', 'burn rate', 'how long', 'when will we run out',
            'cash flow', 'burn'
        ]):
            return 'runway'
        
        # ROI keywords
        if any(word in question_lower for word in [
            'roi', 'return on investment', 'worth it', 'payback period',
            'break even'
        ]):
            return 'roi'
        
        # Default to calculation
        return 'calculation'
    
    def _build_analysis_prompt(
        self,
        question: str,
        user_context: str,
        question_metadata: Dict,
        question_type: str
    ) -> str:
        """Build prompt for financial analysis"""
        
        return f"""
            USER CONTEXT:
            {user_context}

            QUESTION TYPE: {question_type}
            COMPLEXITY: {question_metadata.get('complexity', 'medium')}
            URGENCY: {question_metadata.get('urgency', 'routine')}

            USER QUESTION:
            {question}

            Provide Financial Guardian analysis following the framework.
            Show your work for all calculations.
            Provide scenario ranges (best/realistic/worst).
            Identify critical constraints.
            """
                
    async def _parse_agent_response(self, response_text: str) -> Dict:
        """
        Parse agent response using LLM (Ollama) for robust extraction
        
        Handles natural language variations better than regex
        """
        from .utils.llm_parser import get_parser
        
        try:
            parser = get_parser()
            return await parser.parse_financial_guardian_response(response_text)
        except Exception as e:
            logger.error(f"LLM parsing failed: {str(e)}")
            # Ultimate fallback
            return {
                'calculation': response_text,
                'confidence': '🟡 Medium',
                'scenarios': {
                    'optimistic': '',
                    'realistic': '',
                    'pessimistic': ''
                },
                'critical_constraint': '',
                'assumptions': '',
                'for_your_situation': '',
                'question_back': ''
            }


# Example usage
if __name__ == '__main__':
    """Test Financial Guardian agent"""
    from decouple import config
    
    async def test_agent():
        anthropic_key = config('ANTHROPIC_API_KEY')
        google_key = config('GOOGLE_AI_API_KEY', default=None)
        
        agent = FinancialGuardianAgent(
            anthropic_api_key=anthropic_key,
            google_api_key=google_key,
            model='claude-sonnet-4-20250514'  # Try: 'gemini-2.0-flash-exp' or 'llama3.1:8b'
        )
        
        # Test question
        test_question = "Is our CAC of $1,500 sustainable with an LTV of $4,200?"
        test_context = """
            User: CFO at Series A SaaS startup
            Company: B2B Marketing Platform
            Current Metrics: $2M ARR, 50 customers, $150K MRR burn rate
            Recent questions: Unit economics, fundraising runway
            """
        test_metadata = {
            'question_type': 'validation',
            'domains': ['finance'],
            'complexity': 'medium',
            'urgency': 'important'
        }
        
        print("\n" + "=" * 80)
        print("TESTING FINANCIAL GUARDIAN AGENT")
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
        print(f"\nCalculation:\n{result['calculation']}")
        print(f"\nConfidence: {result['confidence']}")
        
        if result.get('scenarios'):
            print(f"\nScenarios:")
            for scenario_type, scenario_text in result['scenarios'].items():
                if scenario_text:
                    print(f"  {scenario_type.title()}: {scenario_text}")
        
        if result.get('critical_constraint'):
            print(f"\nCritical Constraint: {result['critical_constraint']}")
        
        print("\n" + "=" * 80)
    
    asyncio.run(test_agent())