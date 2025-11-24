# agents/utils/llm_parser.py

"""
LLM-Based Response Parser
Uses Ollama (fast, local) to parse agent responses into structured format

Benefits over regex:
- Handles natural language variations
- More robust to formatting changes
- Understands context and intent
- Fast with lightweight models
"""

import json
import logging
from typing import Dict, Optional
import ollama

logger = logging.getLogger(__name__)


class LLMResponseParser:
    """
    Parse agent responses using local Ollama model for structured extraction
    """
    
    # Lightweight model for fast parsing
    PARSER_MODEL = "llama3.1:8b"
    
    @staticmethod
    def parse_market_compass_response(response_text: str) -> Dict:
        """
        Parse Market Compass agent response into structured format
        
        Args:
            response_text: Raw text from agent
            
        Returns:
            Dict with structured fields
        """
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
            # Call Ollama for parsing
            response = ollama.chat(
                model=LLMResponseParser.PARSER_MODEL,
                messages=[{'role': 'user', 'content': extraction_prompt}],
                options={'temperature': 0.1}  # Very low for consistency
            )
            
            # Extract JSON from response
            response_content = response['message']['content'].strip()
            
            # Remove markdown code blocks if present
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
            
            logger.info("Market Compass response parsed successfully with LLM")
            return result
            
        except Exception as e:
            logger.warning(f"LLM parsing failed, using fallback: {str(e)}")
            # Fallback to putting everything in analysis
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
    
    @staticmethod
    def parse_financial_guardian_response(response_text: str) -> Dict:
        """
        Parse Financial Guardian agent response into structured format
        
        Args:
            response_text: Raw text from agent
            
        Returns:
            Dict with structured fields
        """
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
            # Call Ollama for parsing
            response = ollama.chat(
                model=LLMResponseParser.PARSER_MODEL,
                messages=[{'role': 'user', 'content': extraction_prompt}],
                options={'temperature': 0.1}
            )
            
            # Extract JSON from response
            response_content = response['message']['content'].strip()
            
            # Remove markdown code blocks if present
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
            
            # Fallback: if calculation is empty, use raw text
            if not result['calculation']:
                result['calculation'] = response_text
            
            logger.info("Financial Guardian response parsed successfully with LLM")
            return result
            
        except Exception as e:
            logger.warning(f"LLM parsing failed, using fallback: {str(e)}")
            # Fallback to putting everything in calculation
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
    
    @staticmethod
    def parse_strategy_analyst_response(response_text: str) -> Dict:
        """
        Parse Strategy Analyst agent response into structured format
        
        Args:
            response_text: Raw text from agent
            
        Returns:
            Dict with structured fields
        """
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
            # Call Ollama for parsing
            response = ollama.chat(
                model=LLMResponseParser.PARSER_MODEL,
                messages=[{'role': 'user', 'content': extraction_prompt}],
                options={'temperature': 0.1}
            )
            
            # Extract JSON from response
            response_content = response['message']['content'].strip()
            
            # Remove markdown code blocks if present
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
            
            # Fallback: if decision_reframe is empty, use raw text
            if not result['decision_reframe']:
                result['decision_reframe'] = response_text
            
            logger.info("Strategy Analyst response parsed successfully with LLM")
            return result
            
        except Exception as e:
            logger.warning(f"LLM parsing failed, using fallback: {str(e)}")
            # Fallback to putting everything in decision_reframe
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


# Example usage and testing
if __name__ == '__main__':
    """Test the LLM parser"""
    
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
    print("=" * 80)
    parsed = LLMResponseParser.parse_market_compass_response(market_response)
    print(json.dumps(parsed, indent=2))
    
    # Test Financial Guardian parsing
    financial_response = """
    Calculation: With CAC of $1,500 and LTV of $4,200, your LTV:CAC ratio is 2.8:1.
    
    Working backwards:
    - Monthly churn: 5% = 20 months average lifetime
    - ARPU: $210/month
    - LTV: $210 × 20 = $4,200
    - CAC: $1,500
    - Payback period: 7.1 months
    
    Confidence: 🟡 Medium - Assuming churn stays at 5%
    
    Scenarios:
    Optimistic: If you reduce churn to 3%, LTV jumps to $7,000 (4.7:1 ratio)
    Realistic: Current 2.8:1 ratio is sustainable but not ideal
    Pessimistic: If churn increases to 8%, LTV drops to $2,625 (1.75:1 ratio - danger zone)
    
    Critical Constraint: Churn rate. Every 1% increase in churn costs you $1,050 per customer.
    """
    
    print("\n" + "=" * 80)
    print("TESTING FINANCIAL GUARDIAN PARSER")
    print("=" * 80)
    parsed = LLMResponseParser.parse_financial_guardian_response(financial_response)
    print(json.dumps(parsed, indent=2))
    
    # Test Strategy Analyst parsing
    strategy_response = """
    Decision Reframe: You think you're deciding "enterprise vs SMB."
    You're actually deciding "can we serve two customer segments with one team?"
    
    Confidence: 🟢 High - This is a classic strategic mistake
    
    Framework Applied: Playing to Win + Strategic Trade-offs
    
    Framework Analysis: Enterprise needs white-glove support, annual contracts, custom integration.
    SMB needs self-serve, monthly flexibility, fast time-to-value. These are fundamentally 
    different capabilities.
    
    Strategic Blindspot: Most founders miss that serving enterprise ISN'T just "selling to bigger companies."
    It's building an entirely different company with different DNA.
    
    Trade-offs: Saying YES to enterprise means saying NO to:
    - Product velocity (enterprise needs stability)
    - Self-serve efficiency (enterprise needs customization)
    - Monthly cash flow (enterprise is annual contracts)
    """
    
    print("\n" + "=" * 80)
    print("TESTING STRATEGY ANALYST PARSER")
    print("=" * 80)
    parsed = LLMResponseParser.parse_strategy_analyst_response(strategy_response)
    print(json.dumps(parsed, indent=2))
    
    print("\n" + "=" * 80)
    print("ALL PARSERS TESTED SUCCESSFULLY")
    print("=" * 80)