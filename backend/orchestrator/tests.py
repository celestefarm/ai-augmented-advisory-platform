# test_orchestrator.py
"""
Quick test script for orchestrator nodes
Run with: python test_orchestrator.py
"""

import asyncio
import sys
import os

# Add backend to path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator.state import initialize_state
from orchestrator.nodes import analyze_question_node, route_to_agents_node


async def test_nodes():
    print("=" * 80)
    print("TESTING ORCHESTRATOR NODES")
    print("=" * 80)
    
    # Initialize state
    state = initialize_state(
        question="Should we expand to enterprise market?",
        user_context="Series A SaaS, 100 SMB customers, $2M ARR",
        workspace_id="ws_test",
        user_id="user_test"
    )
    
    print("\n✅ State initialized")
    print(f"Question: {state['question']}")
    
    # Test Stage 1: Analyze
    print("\n" + "-" * 80)
    print("Testing Stage 1: ANALYZE")
    print("-" * 80)
    
    state = await analyze_question_node(state)
    
    if state['_current_stage'] == 'analyzed':
        print("✅ Analysis successful!")
        print(f"   Question Type: {state['question_type']}")
        print(f"   Domains: {state['domains']}")
        print(f"   Complexity: {state['complexity']}")
        print(f"   Urgency: {state['urgency']}")
        print(f"   Emotional State: {state['emotional_state']}")
    else:
        print(f"⚠️  Analysis completed with issues: {state['_current_stage']}")
    
    # Test Stage 2: Route
    print("\n" + "-" * 80)
    print("Testing Stage 2: ROUTE")
    print("-" * 80)
    
    state = await route_to_agents_node(state)
    
    if state['_current_stage'] == 'routed':
        print("✅ Routing successful!")
        print(f"   Agents to activate: {state['agents_to_activate']}")
        print(f"   Execution strategy: {state['execution_strategy']}")
        print(f"   Reasoning: {state['routing_reasoning']}")
    else:
        print(f"⚠️  Routing completed with issues: {state['_current_stage']}")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if state['_current_stage'] == 'routed':
        print("✅ ALL TESTS PASSED!")
        print(f"✅ Stage 1 (Analyze): OK")
        print(f"✅ Stage 2 (Route): OK")
        print(f"\n📊 Next Steps:")
        print(f"   - Stages 3-6 require Django settings and API keys")
        print(f"   - Use full integration test for complete pipeline")
    else:
        print("⚠️  Some tests had issues")
    
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(test_nodes())