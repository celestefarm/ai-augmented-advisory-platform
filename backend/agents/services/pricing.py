# agents/services/pricing.py

"""
API Pricing Calculator

Based on Anthropic Claude pricing as of December 2024:
https://www.anthropic.com/pricing

Models:
- Claude Opus 4.1: $15/MTok input, $75/MTok output
- Claude Sonnet 4.5: $3/MTok input (<200K), $6/MTok input (>200K), $15/MTok output (<200K), $22.50/MTok output (>200K)
- Claude Haiku 4.5: $1/MTok input, $5/MTok output

Prompt Caching (when enabled):
- Write to cache: More expensive (storage cost)
- Read from cache: Cheaper (90% discount)
"""

from typing import Dict, Tuple
from decimal import Decimal


class PricingCalculator:
    """
    Calculates API costs based on token usage and model
    """
    
    # Pricing per 1M tokens (MTok)
    PRICING = {
        'claude-opus-4-20250514': {
            'input': Decimal('15.00'),
            'output': Decimal('75.00'),
            'cache_write': Decimal('18.75'),  # $18.75/MTok
            'cache_read': Decimal('1.50'),    # $1.50/MTok (90% discount)
        },
        'claude-sonnet-4-20250514': {
            'input_low': Decimal('3.00'),      # < 200K tokens
            'input_high': Decimal('6.00'),     # > 200K tokens
            'output_low': Decimal('15.00'),    # < 200K tokens
            'output_high': Decimal('22.50'),   # > 200K tokens
            'cache_write_low': Decimal('3.75'),   # < 200K
            'cache_write_high': Decimal('7.50'),  # > 200K
            'cache_read_low': Decimal('0.30'),    # < 200K (90% discount)
            'cache_read_high': Decimal('0.60'),   # > 200K (90% discount)
        },
        'claude-haiku-4-20250514': {
            'input': Decimal('1.00'),
            'output': Decimal('5.00'),
            'cache_write': Decimal('1.25'),
            'cache_read': Decimal('0.10'),  # 90% discount
        },
        # Legacy models (for backward compatibility)
        'claude-3-5-sonnet-20241022': {
            'input': Decimal('3.00'),
            'output': Decimal('15.00'),
            'cache_write': Decimal('3.75'),
            'cache_read': Decimal('0.30'),
        },
    }
    
    # Threshold for Sonnet high/low pricing
    SONNET_THRESHOLD = 200_000  # 200K tokens
    
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
        if model not in self.PRICING:
            # Default to Sonnet for unknown models
            model = 'claude-sonnet-4-20250514'
        
        pricing = self.PRICING[model]
        
        # Calculate costs based on model type
        if 'sonnet-4' in model:
            costs = self._calculate_sonnet_cost(
                pricing,
                prompt_tokens,
                completion_tokens,
                cache_creation_tokens,
                cache_read_tokens
            )
        else:
            costs = self._calculate_simple_cost(
                pricing,
                prompt_tokens,
                completion_tokens,
                cache_creation_tokens,
                cache_read_tokens
            )
        
        # Add total tokens
        costs['total_tokens'] = (
            prompt_tokens + 
            completion_tokens + 
            cache_creation_tokens + 
            cache_read_tokens
        )
        
        return costs
    
    def _calculate_sonnet_cost(
        self,
        pricing: Dict,
        prompt_tokens: int,
        completion_tokens: int,
        cache_creation_tokens: int,
        cache_read_tokens: int
    ) -> Dict[str, Decimal]:
        """Calculate cost for Sonnet 4 (has threshold-based pricing)"""
        
        # Determine if we're in high or low tier
        total_prompt = prompt_tokens + cache_creation_tokens
        use_high_pricing = total_prompt > self.SONNET_THRESHOLD
        
        # Input cost
        if use_high_pricing:
            input_cost = (Decimal(prompt_tokens) / Decimal('1000000')) * pricing['input_high']
        else:
            input_cost = (Decimal(prompt_tokens) / Decimal('1000000')) * pricing['input_low']
        
        # Output cost
        if completion_tokens > self.SONNET_THRESHOLD:
            output_cost = (Decimal(completion_tokens) / Decimal('1000000')) * pricing['output_high']
        else:
            output_cost = (Decimal(completion_tokens) / Decimal('1000000')) * pricing['output_low']
        
        # Cache write cost
        if use_high_pricing:
            cache_write_cost = (Decimal(cache_creation_tokens) / Decimal('1000000')) * pricing['cache_write_high']
        else:
            cache_write_cost = (Decimal(cache_creation_tokens) / Decimal('1000000')) * pricing['cache_write_low']
        
        # Cache read cost (always discounted)
        if use_high_pricing:
            cache_read_cost = (Decimal(cache_read_tokens) / Decimal('1000000')) * pricing['cache_read_high']
        else:
            cache_read_cost = (Decimal(cache_read_tokens) / Decimal('1000000')) * pricing['cache_read_low']
        
        total_cost = input_cost + output_cost + cache_write_cost + cache_read_cost
        
        return {
            'input_cost': input_cost,
            'output_cost': output_cost,
            'cache_write_cost': cache_write_cost,
            'cache_read_cost': cache_read_cost,
            'total_cost': total_cost,
        }
    
    def _calculate_simple_cost(
        self,
        pricing: Dict,
        prompt_tokens: int,
        completion_tokens: int,
        cache_creation_tokens: int,
        cache_read_tokens: int
    ) -> Dict[str, Decimal]:
        """Calculate cost for Opus/Haiku (simple flat pricing)"""
        
        input_cost = (Decimal(prompt_tokens) / Decimal('1000000')) * pricing['input']
        output_cost = (Decimal(completion_tokens) / Decimal('1000000')) * pricing['output']
        cache_write_cost = (Decimal(cache_creation_tokens) / Decimal('1000000')) * pricing['cache_write']
        cache_read_cost = (Decimal(cache_read_tokens) / Decimal('1000000')) * pricing['cache_read']
        
        total_cost = input_cost + output_cost + cache_write_cost + cache_read_cost
        
        return {
            'input_cost': input_cost,
            'output_cost': output_cost,
            'cache_write_cost': cache_write_cost,
            'cache_read_cost': cache_read_cost,
            'total_cost': total_cost,
        }
    
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
        if model not in self.PRICING:
            model = 'claude-sonnet-4-20250514'
        
        pricing = self.PRICING[model]
        
        if 'sonnet-4' in model:
            return {
                'model': model,
                'input_low': f"${pricing['input_low']}/MTok (<200K)",
                'input_high': f"${pricing['input_high']}/MTok (>200K)",
                'output_low': f"${pricing['output_low']}/MTok (<200K)",
                'output_high': f"${pricing['output_high']}/MTok (>200K)",
                'cache_available': True,
            }
        else:
            return {
                'model': model,
                'input': f"${pricing['input']}/MTok",
                'output': f"${pricing['output']}/MTok",
                'cache_available': True,
            }


# Example usage
if __name__ == '__main__':
    calc = PricingCalculator()
    
    print("=" * 80)
    print("CLAUDE API PRICING CALCULATOR")
    print("=" * 80)
    
    # Test cases
    test_cases = [
        {
            'name': 'Small Sonnet request (no cache)',
            'model': 'claude-sonnet-4-20250514',
            'prompt_tokens': 1000,
            'completion_tokens': 500,
            'cache_creation_tokens': 0,
            'cache_read_tokens': 0,
        },
        {
            'name': 'Large Sonnet request (>200K)',
            'model': 'claude-sonnet-4-20250514',
            'prompt_tokens': 250_000,
            'completion_tokens': 2000,
            'cache_creation_tokens': 0,
            'cache_read_tokens': 0,
        },
        {
            'name': 'Sonnet with cache hit',
            'model': 'claude-sonnet-4-20250514',
            'prompt_tokens': 1000,
            'completion_tokens': 500,
            'cache_creation_tokens': 0,
            'cache_read_tokens': 150_000,
        },
        {
            'name': 'Opus 4 request',
            'model': 'claude-opus-4-20250514',
            'prompt_tokens': 5000,
            'completion_tokens': 2000,
            'cache_creation_tokens': 0,
            'cache_read_tokens': 0,
        },
        {
            'name': 'Haiku 4 request',
            'model': 'claude-haiku-4-20250514',
            'prompt_tokens': 2000,
            'completion_tokens': 1000,
            'cache_creation_tokens': 0,
            'cache_read_tokens': 0,
        },
    ]
    
    for test in test_cases:
        print(f"\n{test['name']}")
        print("-" * 80)
        
        costs = calc.calculate_cost(
            model=test['model'],
            prompt_tokens=test['prompt_tokens'],
            completion_tokens=test['completion_tokens'],
            cache_creation_tokens=test['cache_creation_tokens'],
            cache_read_tokens=test['cache_read_tokens']
        )
        
        print(f"Model: {test['model']}")
        print(f"Prompt tokens: {test['prompt_tokens']:,}")
        print(f"Completion tokens: {test['completion_tokens']:,}")
        print(f"Cache read tokens: {test['cache_read_tokens']:,}")
        print(f"Total tokens: {costs['total_tokens']:,}")
        print(f"\nCost breakdown:")
        print(f"  Input: ${costs['input_cost']:.6f}")
        print(f"  Output: ${costs['output_cost']:.6f}")
        if costs['cache_read_cost'] > 0:
            print(f"  Cache read: ${costs['cache_read_cost']:.6f}")
        print(f"  TOTAL: ${costs['total_cost']:.6f}")
    
    print("\n" + "=" * 80)
    print("✅ Pricing calculator ready!")
    print("=" * 80)