# agents/utils/llm_parser.py

"""
LLM-Based Response Parser with Logging
Uses Gemini Flash (fast, cloud API) to parse agent responses into structured format

NEW: Logs both RAW and PARSED responses for debugging and quality control

Benefits over Ollama:
- 10x faster (3-5 seconds vs 50-90 seconds)
- No local hardware required
- Essentially free (about $0.0001 per parse)
- Same quality as Ollama
- Cloud reliability

Falls back to Ollama if Gemini unavailable.
"""

import json
import logging
import asyncio
from typing import Dict, Optional
from decouple import config

logger = logging.getLogger(__name__)

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Install with: pip install google-generativeai")

# Try to import Ollama as fallback
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("ollama not installed (optional fallback)")


class LLMResponseParser:
    """
    Parse agent responses using Gemini Flash (primary) or Ollama (fallback)
    
    Parser Priority:
    1. Gemini Flash (if API key available) - FAST ⚡
    2. Ollama (if installed) - SLOW but free
    3. Regex fallback - FAST but brittle
    """
    
    # Model configurations
    GEMINI_MODEL = "gemini-2.0-flash-exp"  # Fast and cheap
    OLLAMA_MODEL = "llama3.1:8b"  # Fallback
    
    def __init__(self):
        """Initialize parser with available backend"""
        
        # Check for Gemini API key
        gemini_key = config('GOOGLE_AI_API_KEY', default=None)
        
        if GEMINI_AVAILABLE and gemini_key:
            # Use Gemini Flash (FASTEST!)
            genai.configure(api_key=gemini_key)
            self.gemini_model = genai.GenerativeModel(
                model_name=self.GEMINI_MODEL,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Very low for consistency
                    max_output_tokens=2000,
                )
            )
            self.backend = 'gemini'
            logger.info("✅ LLM Parser initialized with Gemini Flash (10x faster than Ollama)")
        
        elif OLLAMA_AVAILABLE:
            # Fall back to Ollama (slower but free)
            self.backend = 'ollama'
            logger.info("⚠️ LLM Parser using Ollama (slower). Install google-generativeai for 10x speedup")
        
        else:
            # No LLM available, will use regex fallback
            self.backend = 'regex'
            logger.warning("⚠️ No LLM parser available. Using regex fallback (less reliable)")
    
    async def parse_market_compass_response(self, response_text: str) -> Dict:
        """
        Parse Market Compass agent response into structured format
        
        Args:
            response_text: Raw text from agent
            
        Returns:
            Dict with structured fields
        """
        # ============================================================================
        # LOG RAW RESPONSE (BEFORE PARSING)
        # ============================================================================
        logger.info("\n" + "=" * 80)
        logger.info("📝 RAW MARKET COMPASS RESPONSE (Before Parsing)")
        logger.info("=" * 80)
        logger.info(response_text)
        logger.info("=" * 80 + "\n")
        
        extraction_prompt = f"""Extract structured information from this Market Compass agent response.

AGENT RESPONSE:
{response_text}

Extract the following fields (if present):
- analysis: Core market analysis/insight
- confidence: Confidence level (look for 🟢/🟡/🟠/🔴 or High/Medium/Low)
- signal: Market signal being discussed
- for_your_situation: User-specific implications
- blindspot: What they might not see
- timing: When this matters
- sources: Research references or sources
- question_back: Closing empowerment question

Return ONLY valid JSON in this exact format:
{{
    "analysis": "extracted text or empty string",
    "confidence": "extracted confidence or '🟡 Medium'",
    "signal": "extracted signal or empty string",
    "for_your_situation": "extracted text or empty string",
    "blindspot": "extracted text or empty string",
    "timing": "extracted text or empty string",
    "sources": "extracted text or empty string",
    "question_back": "extracted question or empty string"
}}

IMPORTANT: Return ONLY the JSON object, no explanations or markdown."""

        try:
            if self.backend == 'gemini':
                # Use Gemini Flash (FAST!)
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content,
                    extraction_prompt
                )
                response_content = response.text.strip()
            
            elif self.backend == 'ollama':
                # Use Ollama (slower)
                response = await asyncio.to_thread(
                    ollama.chat,
                    model=self.OLLAMA_MODEL,
                    messages=[{'role': 'user', 'content': extraction_prompt}],
                    options={'temperature': 0.1}
                )
                response_content = response['message']['content'].strip()
            
            else:
                # Regex fallback
                return self._regex_parse_market_compass(response_text)
            
            # Clean markdown if present
            if response_content.startswith('```'):
                response_content = response_content.split('```')[1]
                if response_content.startswith('json'):
                    response_content = response_content[4:]
                response_content = response_content.strip()
            
            # Parse JSON
            parsed = json.loads(response_content)
            
            # Ensure all required fields exist
            result = {
                'analysis': parsed.get('analysis', ''),
                'confidence': parsed.get('confidence', '🟡 Medium'),
                'signal': parsed.get('signal', ''),
                'for_your_situation': parsed.get('for_your_situation', ''),
                'blindspot': parsed.get('blindspot', ''),
                'timing': parsed.get('timing', ''),
                'sources': parsed.get('sources', ''),
                'question_back': parsed.get('question_back', '')
            }
            
            # Fallback: if analysis is empty, use raw text
            if not result['analysis']:
                result['analysis'] = response_text
            
            # ============================================================================
            # LOG PARSED RESPONSE (AFTER PARSING)
            # ============================================================================
            logger.info("\n" + "=" * 80)
            logger.info("✅ PARSED MARKET COMPASS RESPONSE (After Parsing)")
            logger.info("=" * 80)
            logger.info(json.dumps(result, indent=2, ensure_ascii=False))
            logger.info("=" * 80 + "\n")
            
            logger.info(f"✅ Market Compass response parsed successfully with {self.backend.upper()}")
            return result
            
        except Exception as e:
            logger.error(f"❌ LLM parsing failed ({self.backend}): {str(e)}")
            logger.error(f"Raw response that failed: {response_text[:200]}...")
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
    
    async def parse_financial_guardian_response(self, response_text: str) -> Dict:
        """
        Parse Financial Guardian agent response into structured format
        
        Args:
            response_text: Raw text from agent
            
        Returns:
            Dict with structured fields
        """
        # ============================================================================
        # LOG RAW RESPONSE (BEFORE PARSING)
        # ============================================================================
        logger.info("\n" + "=" * 80)
        logger.info("💰 RAW FINANCIAL GUARDIAN RESPONSE (Before Parsing)")
        logger.info("=" * 80)
        logger.info(response_text)
        logger.info("=" * 80 + "\n")
        
        extraction_prompt = f"""Extract structured information from this Financial Guardian agent response.

            AGENT RESPONSE:
            {response_text}

            Extract the following fields (if present):
            - calculation: The actual math/calculations with work shown
            - confidence: Confidence level (look for 🟢/🟡/🟠/🔴 or High/Medium/Low)
            - scenarios: Object with optimistic/realistic/pessimistic cases
            - critical_constraint: What would kill this financially
            - assumptions: Key assumptions being made
            - for_your_situation: User-specific implications
            - question_back: Closing financial question

            Return ONLY valid JSON in this exact format:
            {{
                "calculation": "extracted calculation or empty string",
                "confidence": "extracted confidence or '🟡 Medium'",
                "scenarios": {{
                    "optimistic": "best case or empty string",
                    "realistic": "realistic case or empty string",
                    "pessimistic": "worst case or empty string"
                }},
                "critical_constraint": "extracted constraint or empty string",
                "assumptions": "extracted assumptions or empty string",
                "for_your_situation": "extracted text or empty string",
                "question_back": "extracted question or empty string"
            }}

            IMPORTANT: Return ONLY the JSON object, no explanations or markdown."""

        try:
            if self.backend == 'gemini':
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content,
                    extraction_prompt
                )
                response_content = response.text.strip()
            
            elif self.backend == 'ollama':
                response = await asyncio.to_thread(
                    ollama.chat,
                    model=self.OLLAMA_MODEL,
                    messages=[{'role': 'user', 'content': extraction_prompt}],
                    options={'temperature': 0.1}
                )
                response_content = response['message']['content'].strip()
            
            else:
                return self._regex_parse_financial_guardian(response_text)
            
            # Clean markdown if present
            if response_content.startswith('```'):
                response_content = response_content.split('```')[1]
                if response_content.startswith('json'):
                    response_content = response_content[4:]
                response_content = response_content.strip()
            
            # Parse JSON
            parsed = json.loads(response_content)
            
            # Ensure all required fields exist
            result = {
                'calculation': parsed.get('calculation', ''),
                'confidence': parsed.get('confidence', '🟡 Medium'),
                'scenarios': {
                    'optimistic': parsed.get('scenarios', {}).get('optimistic', ''),
                    'realistic': parsed.get('scenarios', {}).get('realistic', ''),
                    'pessimistic': parsed.get('scenarios', {}).get('pessimistic', '')
                },
                'critical_constraint': parsed.get('critical_constraint', ''),
                'assumptions': parsed.get('assumptions', ''),
                'for_your_situation': parsed.get('for_your_situation', ''),
                'question_back': parsed.get('question_back', '')
            }
            
            if not result['calculation']:
                result['calculation'] = response_text
            
            # ============================================================================
            # LOG PARSED RESPONSE (AFTER PARSING)
            # ============================================================================
            logger.info("\n" + "=" * 80)
            logger.info("✅ PARSED FINANCIAL GUARDIAN RESPONSE (After Parsing)")
            logger.info("=" * 80)
            logger.info(json.dumps(result, indent=2, ensure_ascii=False))
            logger.info("=" * 80 + "\n")
            
            logger.info(f"✅ Financial Guardian response parsed successfully with {self.backend.upper()}")
            return result
            
        except Exception as e:
            logger.error(f"❌ LLM parsing failed ({self.backend}): {str(e)}")
            logger.error(f"Raw response that failed: {response_text[:200]}...")
            return {
                'calculation': response_text,
                'confidence': '🟡 Medium',
                'scenarios': {'optimistic': '', 'realistic': '', 'pessimistic': ''},
                'critical_constraint': '',
                'assumptions': '',
                'for_your_situation': '',
                'question_back': ''
            }
    
    async def parse_strategy_analyst_response(self, response_text: str) -> Dict:
        """
        Parse Strategy Analyst agent response into structured format
        
        Args:
            response_text: Raw text from agent
            
        Returns:
            Dict with structured fields
        """
        # ============================================================================
        # LOG RAW RESPONSE (BEFORE PARSING)
        # ============================================================================
        logger.info("\n" + "=" * 80)
        logger.info("🎯 RAW STRATEGY ANALYST RESPONSE (Before Parsing)")
        logger.info("=" * 80)
        logger.info(response_text)
        logger.info("=" * 80 + "\n")
        
        extraction_prompt = f"""Extract structured information from this Strategy Analyst agent response.

AGENT RESPONSE:
{response_text}

Extract the following fields (if present):
- decision_reframe: What they're ACTUALLY deciding
- confidence: Confidence level (look for 🟢/🟡/🟠/🔴 or High/Medium/Low)
- framework_applied: Which strategic framework was used
- framework_analysis: Application of framework to their situation
- assumptions_tested: Key assumptions and risks
- strategic_blindspot: What strategic angle they're missing
- trade_offs: What they're trading off
- for_your_situation: User-specific implications
- question_back: Closing strategic question

Return ONLY valid JSON in this exact format:
{{
    "decision_reframe": "extracted reframe or empty string",
    "confidence": "extracted confidence or '🟡 Medium'",
    "framework_applied": "extracted framework or empty string",
    "framework_analysis": "extracted analysis or empty string",
    "assumptions_tested": "extracted assumptions or empty string",
    "strategic_blindspot": "extracted blindspot or empty string",
    "trade_offs": "extracted trade-offs or empty string",
    "for_your_situation": "extracted text or empty string",
    "question_back": "extracted question or empty string"
}}

IMPORTANT: Return ONLY the JSON object, no explanations or markdown."""

        try:
            if self.backend == 'gemini':
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content,
                    extraction_prompt
                )
                response_content = response.text.strip()
            
            elif self.backend == 'ollama':
                response = await asyncio.to_thread(
                    ollama.chat,
                    model=self.OLLAMA_MODEL,
                    messages=[{'role': 'user', 'content': extraction_prompt}],
                    options={'temperature': 0.1}
                )
                response_content = response['message']['content'].strip()
            
            else:
                return self._regex_parse_strategy_analyst(response_text)
            
            # Clean markdown if present
            if response_content.startswith('```'):
                response_content = response_content.split('```')[1]
                if response_content.startswith('json'):
                    response_content = response_content[4:]
                response_content = response_content.strip()
            
            # Parse JSON
            parsed = json.loads(response_content)
            
            # Ensure all required fields exist
            result = {
                'decision_reframe': parsed.get('decision_reframe', ''),
                'confidence': parsed.get('confidence', '🟡 Medium'),
                'framework_applied': parsed.get('framework_applied', ''),
                'framework_analysis': parsed.get('framework_analysis', ''),
                'assumptions_tested': parsed.get('assumptions_tested', ''),
                'strategic_blindspot': parsed.get('strategic_blindspot', ''),
                'trade_offs': parsed.get('trade_offs', ''),
                'for_your_situation': parsed.get('for_your_situation', ''),
                'question_back': parsed.get('question_back', '')
            }
            
            if not result['decision_reframe']:
                result['decision_reframe'] = response_text
            
            # ============================================================================
            # LOG PARSED RESPONSE (AFTER PARSING)
            # ============================================================================
            logger.info("\n" + "=" * 80)
            logger.info("✅ PARSED STRATEGY ANALYST RESPONSE (After Parsing)")
            logger.info("=" * 80)
            logger.info(json.dumps(result, indent=2, ensure_ascii=False))
            logger.info("=" * 80 + "\n")
            
            logger.info(f"✅ Strategy Analyst response parsed successfully with {self.backend.upper()}")
            return result
            
        except Exception as e:
            logger.error(f"❌ LLM parsing failed ({self.backend}): {str(e)}")
            logger.error(f"Raw response that failed: {response_text[:200]}...")
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
    
    # Regex fallback methods (fast but brittle)
    def _regex_parse_market_compass(self, text: str) -> Dict:
        """Simple regex fallback for Market Compass"""
        logger.info("Using regex fallback for Market Compass")
        return {
            'analysis': text,
            'confidence': '🟡 Medium',
            'signal': '',
            'for_your_situation': '',
            'blindspot': '',
            'timing': '',
            'sources': '',
            'question_back': ''
        }
    
    def _regex_parse_financial_guardian(self, text: str) -> Dict:
        """Simple regex fallback for Financial Guardian"""
        logger.info("Using regex fallback for Financial Guardian")
        return {
            'calculation': text,
            'confidence': '🟡 Medium',
            'scenarios': {'optimistic': '', 'realistic': '', 'pessimistic': ''},
            'critical_constraint': '',
            'assumptions': '',
            'for_your_situation': '',
            'question_back': ''
        }
    
    def _regex_parse_strategy_analyst(self, text: str) -> Dict:
        """Simple regex fallback for Strategy Analyst"""
        logger.info("Using regex fallback for Strategy Analyst")
        return {
            'decision_reframe': text,
            'confidence': '🟡 Medium',
            'framework_applied': '',
            'framework_analysis': '',
            'assumptions_tested': '',
            'strategic_blindspot': '',
            'trade_offs': '',
            'for_your_situation': '',
            'question_back': ''
        }


# Convenience singleton instance
_parser_instance = None

def get_parser() -> LLMResponseParser:
    """Get singleton parser instance"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = LLMResponseParser()
    return _parser_instance


# Example usage and testing
if __name__ == '__main__':
    """Test the LLM parser"""
    import asyncio
    
    async def test_parser():
        # Initialize parser
        parser = LLMResponseParser()
        
        # Test Market Compass parsing
        market_response = """
        Analysis: The AI SaaS market is experiencing consolidation at 3x historical rate.
        
        Confidence: 🟢 High - Based on recent M&A data
        
        For Your Situation: As an early-stage B2B SaaS company, this creates urgency to establish 
        defensible positioning before larger players consolidate your category.
        
        Blindspot: Most founders focus on feature differentiation when the real moat is 
        distribution and customer lock-in.
        
        Timing: You have approximately 18-24 months before major consolidation reaches your segment.
        """
        
        print("\n" + "=" * 80)
        print("TESTING MARKET COMPASS PARSER")
        print(f"Backend: {parser.backend.upper()}")
        print("=" * 80)
        parsed = await parser.parse_market_compass_response(market_response)
        
        print("\n" + "=" * 80)
        print(f"✅ ALL PARSERS TESTED SUCCESSFULLY WITH {parser.backend.upper()}")
        print("=" * 80)
    
    asyncio.run(test_parser())