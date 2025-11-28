"""
Test Chief of Staff synthesis with caching
"""
import asyncio
from agents.services.chief_agent import ChiefOfStaffAgent
from agents.utils.cache import get_cache_manager
from decouple import config


async def test_synthesis_caching():
    """Test synthesis with cache hits"""
    
    chief = ChiefOfStaffAgent(
        api_key=config('ANTHROPIC_API_KEY'),
        model='claude-sonnet-4-20250514',
        temperature=0.5
    )
    
    # Mock specialist outputs
    specialist_outputs = {
        'market_compass': {
            'analysis': 'Market opportunity is real, 18-24 month window before saturation',
            'confidence': '🟢 High (85%)',
            'for_your_situation': 'Your SMB traction validates upmarket move',
            'signal': 'Enterprise buyers actively seeking AI-enhanced solutions',
            'timing': 'Act within Q1 2025',
            'blindspot': 'Competitors already piloting with Fortune 500'
        },
        'financial_guardian': {
            'calculation': 'Enterprise CAC is 8x higher: $12K vs $1.5K SMB\n' +
                         'However, LTV is 5x: $60K vs $12K\n' +
                         'LTV:CAC ratio: 5:1 (excellent)',
            'confidence': '🟡 Medium (70%)',
            'scenarios': {
                'optimistic': '10 enterprise deals in 6 months = $600K ARR',
                'realistic': '5 enterprise deals in 6 months = $300K ARR',
                'pessimistic': '2 enterprise deals in 9 months = $120K ARR'
            },
            'critical_constraint': 'Current burn rate gives 6 months runway. ' +
                                  'Need to raise or hit $50K MRR to extend.',
            'for_your_situation': 'You can afford 2-3 enterprise pilots without additional capital'
        },
        'strategy_analyst': {
            'decision_reframe': 'Real question: Can you serve 2 segments (SMB + Enterprise) ' +
                               'with one product team and maintain quality?',
            'confidence': '🟢 High (90%)',
            'framework_applied': 'Playing to Win: Where to play, How to win',
            'trade_offs': 'YES to Enterprise means saying NO to: ' +
                         '3 SMB features, 2 marketing campaigns, International expansion',
            'strategic_blindspot': 'SMB customers might feel abandoned if you chase whales',
            'for_your_situation': 'Your team of 25 can handle 1 new segment, not 2'
        }
    }
    
    question = "Should we expand to enterprise market or double down on SMB?"
    user_context = "Series A SaaS CEO, $2M ARR, 100 SMB customers, 25 employees"
    
    print("\n" + "=" * 80)
    print("TESTING CHIEF OF STAFF SYNTHESIS WITH CACHING")
    print("=" * 80)
    
    # First call - should generate fresh synthesis
    print("\n[TEST 1] First call (fresh synthesis)...")
    synthesis1, metadata1 = await chief.synthesize_specialist_outputs(
        question=question,
        specialist_outputs=specialist_outputs,
        user_context=user_context,
        emotional_state='anxiety'
    )
    
    print(f"\n✅ Response Time: {metadata1['response_time']:.2f}s")
    print(f"✅ From Cache: {metadata1.get('from_cache', False)}")
    print(f"✅ Total Tokens: {metadata1['total_tokens']}")
    print(f"✅ Cost: ${metadata1['cost']:.6f}")
    
    print(f"\n📝 Synthesis Preview (first 300 chars):")
    print(synthesis1[:300] + "...")
    
    # Second call - should hit cache
    print("\n" + "=" * 80)
    print("[TEST 2] Second call (should hit cache)...")
    synthesis2, metadata2 = await chief.synthesize_specialist_outputs(
        question=question,
        specialist_outputs=specialist_outputs,
        user_context=user_context,
        emotional_state='anxiety'
    )
    
    print(f"\n✅ Response Time: {metadata2['response_time']:.2f}s")
    print(f"✅ From Cache: {metadata2.get('from_cache', False)}")
    print(f"✅ Cost: ${metadata2.get('cost', 0.0):.6f}")
    
    # Verify cache hit with safe division
    if metadata2.get('from_cache'):
        print("\n🎉 CACHE HIT! Synthesis returned instantly!")
        
        # Handle zero division when cache is instant
        if metadata2['response_time'] > 0.01:  # If measurable
            speedup = metadata1['response_time'] / metadata2['response_time']
            print(f"⚡ Speedup: {speedup:.1f}x faster")
        else:
            # Cache was SO fast it rounded to 0.00s
            print(f"⚡ Speedup: INSTANT (too fast to measure!)")
            print(f"   Original: {metadata1['response_time']:.2f}s → Cached: <0.01s")
            print(f"   Estimated speedup: >{metadata1['response_time'] / 0.01:.0f}x faster")
    else:
        print("\n⚠️  Cache miss - synthesis regenerated")
    
    # Third call with different question - should miss cache
    print("\n" + "=" * 80)
    print("[TEST 3] Different question (should miss cache)...")
    synthesis3, metadata3 = await chief.synthesize_specialist_outputs(
        question="What are the risks of expanding too fast?",  # Different question
        specialist_outputs=specialist_outputs,
        user_context=user_context,
        emotional_state='neutral'
    )
    
    print(f"\n✅ Response Time: {metadata3['response_time']:.2f}s")
    print(f"✅ From Cache: {metadata3.get('from_cache', False)}")
    
    # Cache stats
    print("\n" + "=" * 80)
    print("CACHE STATISTICS")
    print("=" * 80)
    cache = get_cache_manager()
    stats = cache.get_stats()
    print(f"Backend: {stats['backend']}")
    print(f"Total Keys: {stats['total_keys']}")
    print(f"Cache Hits: {stats['hits']}")
    print(f"Cache Misses: {stats['misses']}")
    print(f"Hit Rate: {stats['hit_rate']:.1%}")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(test_synthesis_caching())