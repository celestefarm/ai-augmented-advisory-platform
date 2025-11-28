# agents/services/pricing.py

"""
API Pricing Calculator

Based on Anthropic Claude pricing as of January 2025:
https://www.anthropic.com/pricing

Claude 4.5 Models (Current):
- Claude Opus 4.5: TBD (not yet released)
- Claude Sonnet 4.5: $3/MTok input, $15/MTok output
- Claude Haiku 4.5: $1/MTok input, $5/MTok output

Prompt Caching (when enabled):
- Cache writes: 25% markup
- Cache reads: 90% discount
"""

from typing import Dict, Tuple
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PricingCalculator:
    """
    Calculates API costs based on token usage and model
    
    Supports:
    - Claude 4.5 models (Sonnet, Haiku)
    - Gemini 2.0 models (Flash, Pro)
    - Ollama (free local models)
    """
    
    # Pricing per 1M tokens (MTok)  Updated January 2025
    PRICING = {
        # Claude 4.5 (Current)
        'claude-sonnet-4-5-20250929': {
            'input': Decimal('3.00'),
            'output': Decimal('15.00'),
            'cache_write': Decimal('3.75'),    # 25% markup
            'cache_read': Decimal('0.30'),     # 90% discount
        },
        'claude-haiku-4-5-20251001': {
            'input': Decimal('1.00'),
            'output': Decimal('5.00'),
            'cache_write': Decimal('1.25'),    # 25% markup
            'cache_read': Decimal('0.10'),     # 90% discount
        },
        
        # Claude 4 (Legacy - for backward compatibility)
        'claude-sonnet-4-20250514': {
            'input': Decimal('3.00'),
            'output': Decimal('15.00'),
            'cache_write': Decimal('3.75'),
            'cache_read': Decimal('0.30'),
        },
        'claude-opus-4-20250514': {
            'input': Decimal('15.00'),
            'output': Decimal('75.00'),
            'cache_write': Decimal('18.75'),
            'cache_read': Decimal('1.50'),
        },
        'claude-haiku-4-20250514': {
            'input': Decimal('1.00'),
            'output': Decimal('5.00'),
            'cache_write': Decimal('1.25'),
            'cache_read': Decimal('0.10'),
        },
        
        # Gemini 2.0
        'gemini-2.0-flash-exp': {
            'input': Decimal('0.075'),
            'output': Decimal('0.30'),
            'cache_write': Decimal('0.075'),
            'cache_read': Decimal('0.075'),
        },
        'gemini-2.0-pro': {
            'input': Decimal('1.25'),
            'output': Decimal('5.00'),
            'cache_write': Decimal('1.25'),  
            'cache_read': Decimal('1.25'),
        },
        
        # Ollama (Local - Free)
        'llama3.1:8b': {
            'input': Decimal('0.00'),
            'output': Decimal('0.00'),
            'cache_write': Decimal('0.00'),
            'cache_read': Decimal('0.00'),
        },
    }
    
    def calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cache_creation_tokens: int = 0,
        cache_read_tokens: int = 0
    ) -> Dict[str, Decimal]:
        """
        Calculate API cost breakdown
        
        Args:
            model: Model name
            prompt_tokens: Input tokens (not from cache)
            completion_tokens: Output tokens
            cache_creation_tokens: Tokens written to cache
            cache_read_tokens: Tokens read from cache
            
        Returns:
            Dict with cost breakdown:
            {
                'input_cost': Decimal,
                'output_cost': Decimal,
                'cache_write_cost': Decimal,
                'cache_read_cost': Decimal,
                'total_cost': Decimal,
                'total_tokens': int
            }
        """
        # Handle model aliases and variants
        normalized_model = self._normalize_model_name(model)
        
        if normalized_model not in self.PRICING:
            # Default to Sonnet for unknown models
            logger.warning(f"Unknown model {model}, defaulting to claude-sonnet-4-5-20250929 pricing")
            normalized_model = 'claude-sonnet-4-5-20250929'
        
        pricing = self.PRICING[normalized_model]
        
        # Calculate costs
        input_cost = (Decimal(prompt_tokens) / Decimal('1000000')) * pricing['input']
        output_cost = (Decimal(completion_tokens) / Decimal('1000000')) * pricing['output']
        cache_write_cost = (Decimal(cache_creation_tokens) / Decimal('1000000')) * pricing['cache_write']
        cache_read_cost = (Decimal(cache_read_tokens) / Decimal('1000000')) * pricing['cache_read']
        
        total_cost = input_cost + output_cost + cache_write_cost + cache_read_cost
        total_tokens = prompt_tokens + completion_tokens + cache_creation_tokens + cache_read_tokens
        
        return {
            'input_cost': input_cost,
            'output_cost': output_cost,
            'cache_write_cost': cache_write_cost,
            'cache_read_cost': cache_read_cost,
            'total_cost': total_cost,
            'total_tokens': total_tokens,
        }
    
    def _normalize_model_name(self, model: str) -> str:
        """Normalize model name to match pricing keys"""
        model_lower = model.lower()
        
        # Handle Ollama models
        if any(x in model_lower for x in ['llama', 'mistral', 'qwen']):
            return 'llama3.1:8b' 
        
        # Handle Gemini models
        if 'gemini-2.0-flash' in model_lower:
            return 'gemini-2.0-flash-exp'
        if 'gemini-2.0-pro' in model_lower:
            return 'gemini-2.0-pro'
        
        # Return as-is for Claude models
        return model
    
    def estimate_cost(
        self,
        model: str,
        estimated_prompt_tokens: int,
        estimated_completion_tokens: int,
        use_cache: bool = False
    ) -> Tuple[Decimal, str]:
        """
        Estimate cost before making API call
        
        Args:
            model: Model name
            estimated_prompt_tokens: Estimated input tokens
            estimated_completion_tokens: Estimated output tokens
            use_cache: Whether prompt caching will be used
            
        Returns:
            (estimated_cost, explanation)
        """
        if use_cache:
            # Assume 50% cache hit rate for estimation
            cache_read = int(estimated_prompt_tokens * 0.5)
            regular_prompt = estimated_prompt_tokens - cache_read
            
            costs = self.calculate_cost(
                model=model,
                prompt_tokens=regular_prompt,
                completion_tokens=estimated_completion_tokens,
                cache_creation_tokens=0,
                cache_read_tokens=cache_read
            )
            
            explanation = (
                f"Estimated: {costs['total_tokens']:,} tokens "
                f"(~{cache_read:,} from cache) = ${costs['total_cost']:.6f}"
            )
        else:
            costs = self.calculate_cost(
                model=model,
                prompt_tokens=estimated_prompt_tokens,
                completion_tokens=estimated_completion_tokens
            )
            
            explanation = (
                f"Estimated: {costs['total_tokens']:,} tokens = "
                f"${costs['total_cost']:.6f}"
            )
        
        return costs['total_cost'], explanation
    
    def get_pricing_info(self, model: str) -> Dict:
        """Get pricing information for a model"""
        normalized_model = self._normalize_model_name(model)
        
        if normalized_model not in self.PRICING:
            normalized_model = 'claude-sonnet-4-5-20250929'
        
        pricing = self.PRICING[normalized_model]
        
        # Check if free (Ollama)
        if pricing['input'] == Decimal('0.00'):
            return {
                'model': model,
                'pricing': 'FREE (Local Ollama)',
                'cache_available': False,
            }
        
        return {
            'model': model,
            'input': f"${pricing['input']}/MTok",
            'output': f"${pricing['output']}/MTok",
            'cache_write': f"${pricing['cache_write']}/MTok",
            'cache_read': f"${pricing['cache_read']}/MTok",
            'cache_available': True,
        }


# Example usage
if __name__ == '__main__':
    calc = PricingCalculator()
    
    print("=" * 80)
    print("MULTI-MODEL API PRICING CALCULATOR")
    print("=" * 80)
    
    # Test cases
    test_cases = [
        {
            'name': 'Claude Sonnet 4.5 (current)',
            'model': 'claude-sonnet-4-5-20250929',
            'prompt_tokens': 1000,
            'completion_tokens': 500,
        },
        {
            'name': 'Claude Haiku 4.5 (fast/cheap)',
            'model': 'claude-haiku-4-5-20251001',
            'prompt_tokens': 1000,
            'completion_tokens': 500,
        },
        {
            'name': 'Gemini 2.0 Flash (very cheap)',
            'model': 'gemini-2.0-flash-exp',
            'prompt_tokens': 1000,
            'completion_tokens': 500,
        },
        {
            'name': 'Gemini 2.0 Pro',
            'model': 'gemini-2.0-pro',
            'prompt_tokens': 1000,
            'completion_tokens': 500,
        },
        {
            'name': 'Ollama Llama3.1 (FREE)',
            'model': 'llama3.1:8b',
            'prompt_tokens': 1000,
            'completion_tokens': 500,
        },
        {
            'name': 'Claude Sonnet with cache hit (90% discount)',
            'model': 'claude-sonnet-4-5-20250929',
            'prompt_tokens': 1000,
            'completion_tokens': 500,
            'cache_read_tokens': 5000,
        },
    ]
    
    for test in test_cases:
        print(f"\n{test['name']}")
        print("-" * 80)
        
        costs = calc.calculate_cost(
            model=test['model'],
            prompt_tokens=test['prompt_tokens'],
            completion_tokens=test['completion_tokens'],
            cache_read_tokens=test.get('cache_read_tokens', 0)
        )
        
        print(f"Model: {test['model']}")
        print(f"Prompt tokens: {test['prompt_tokens']:,}")
        print(f"Completion tokens: {test['completion_tokens']:,}")
        if test.get('cache_read_tokens', 0) > 0:
            print(f"Cache read tokens: {test['cache_read_tokens']:,}")
        print(f"Total tokens: {costs['total_tokens']:,}")
        print(f"\nCost breakdown:")
        print(f"  Input: ${costs['input_cost']:.6f}")
        print(f"  Output: ${costs['output_cost']:.6f}")
        if costs['cache_read_cost'] > 0:
            print(f"  Cache read: ${costs['cache_read_cost']:.6f} (90% discount!)")
        print(f"  TOTAL: ${costs['total_cost']:.6f}")
    
    print("\n" + "=" * 80)
    print("✅ Pricing calculator ready!")
    print("=" * 80)