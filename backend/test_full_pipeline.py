import asyncio
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from orchestrator import run_multi_agent_pipeline

async def test():
    result = await run_multi_agent_pipeline(
        question="Investors want Series C for $100M+ by 2027 (50%+ YoY). Need to hire 60+, go horizontal, shift model. Alternative: pass, optimize for profitability, $30-40M, acquired for $200-300M in 3-5 years. Built $1B company or $300M company?",
        user_context="Series A SaaS CEO, 100 SMB customers, $30M ARR",
        workspace_id="test_ws",
        user_id="test_user"
    )
    
    print(f"\n{'='*80}")
    print("PIPELINE RESULTS")
    print('='*80)
    print(f"✅ Success: {result['success']}")
    print(f"⏱️  Total Time: {result['total_time']:.2f}s")
    print(f"💰 Total Cost: ${result['total_cost']:.6f}")
    print(f"🎯 Confidence: {result['confidence_level']}")
    print(f"\nAgents Used: {', '.join(result['metadata']['agents_succeeded'])}")
    print(f"\n📝 Response Preview:")
    print(result['final_response'][:300] + "...")

asyncio.run(test())
