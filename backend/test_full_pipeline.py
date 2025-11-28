import asyncio
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from orchestrator import run_multi_agent_pipeline

async def test():
    result = await run_multi_agent_pipeline(
        question="37% of execs without AI strategy report 'very successful' vs 80% with strategy. We lack formal AI strategy. Do I pump brakes or keep shipping?",
        user_context="Series A SaaS CEO, 100 SMB customers, $40M ARR",
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
