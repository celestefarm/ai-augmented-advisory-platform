# orchestrator/graph.py

"""
LangGraph Multi-Agent Orchestrator - Optimized for Speed

This is the main orchestration engine that coordinates all agents.

Key Optimizations:
1. Parallel agent execution (2.6x faster)
2. No unnecessary retry logic (accept what we got)
3. Minimal state overhead
4. Fast rule-based routing (no LLM calls in orchestration)

Target Performance:
- Simple questions (1 agent): 3-5 seconds
- Medium questions (2 agents): 4-6 seconds  
- Complex questions (3 agents): 5-7 seconds
"""

import logging
from typing import Literal
from langgraph.graph import StateGraph, END
from .state import MultiAgentState
from .nodes import (
    analyze_question_node,
    route_to_agents_node,
    execute_agents_parallel_node,
    synthesize_responses_node,
    quality_check_node,
    finalize_response_node
)

logger = logging.getLogger(__name__)


def create_multi_agent_graph():
    """
    Create the LangGraph orchestration pipeline
    
    Pipeline Flow:
    Input → Analyze → Route → Execute (Parallel!) → Synthesize → Quality → Finalize → Output
    
    Returns:
        Compiled LangGraph
    """
    
    # Initialize StateGraph
    workflow = StateGraph(MultiAgentState)
    
    # ========================================================================
    # Add Nodes (Each node is a stage in the pipeline)
    # ========================================================================
    
    logger.info("Building LangGraph workflow...")
    
    workflow.add_node("analyze", analyze_question_node)
    workflow.add_node("route", route_to_agents_node)
    workflow.add_node("execute", execute_agents_parallel_node)
    workflow.add_node("synthesize", synthesize_responses_node)
    workflow.add_node("quality", quality_check_node)
    workflow.add_node("finalize", finalize_response_node)
    
    # ========================================================================
    # Define Flow (How state moves between nodes)
    # ========================================================================
    
    # Set entry point
    workflow.set_entry_point("analyze")
    
    # Linear flow for speed (no complex branching)
    workflow.add_edge("analyze", "route")
    workflow.add_edge("route", "execute")
    workflow.add_edge("execute", "synthesize")
    workflow.add_edge("synthesize", "quality")
    workflow.add_edge("quality", "finalize")
    
    # Exit after finalization
    workflow.add_edge("finalize", END)
    
    # Note: Tell celeste We removed retry logic for speed
    # In production, add conditional retry:
    # workflow.add_conditional_edges(
    #     "quality",
    #     should_retry,
    #     {
    #         "retry": "execute",
    #         "continue": "finalize"
    #     }
    # )
    
    # ========================================================================
    # Compile Graph
    # ========================================================================
    
    logger.info("✅ LangGraph workflow compiled")
    
    return workflow.compile()


def should_retry(state: MultiAgentState) -> Literal["retry", "continue"]:
    """
    Conditional logic for retry (currently disabled for speed)
    
    Args:
        state: Current state
        
    Returns:
        "retry" or "continue"
    """
    # Check if retry needed and haven't exceeded retry limit
    if state.get('retry_needed', False) and state.get('_retry_count', 0) < 1:
        logger.info("Quality too low, retrying execution...")
        state['_retry_count'] = state.get('_retry_count', 0) + 1
        return "retry"
    
    return "continue"


# ============================================================================
# Convenience Functions
# ============================================================================

async def run_multi_agent_pipeline(question: str, user_context: str, workspace_id: str, user_id: str, conversation_history: list = None) -> MultiAgentState:
    """
    Run the complete multi-agent pipeline
    
    This is the main entry point for executing the orchestration.
    
    Args:
        question: User's question
        user_context: User profile
        workspace_id: Workspace ID
        user_id: User ID
        conversation_history: Optional previous messages
        
    Returns:
        Final state with response and metadata
    """
    from .state import initialize_state
    
    # Initialize state
    initial_state = initialize_state(
        question=question,
        user_context=user_context,
        workspace_id=workspace_id,
        user_id=user_id,
        conversation_history=conversation_history
    )
    
    # Create graph
    graph = create_multi_agent_graph()
    
    # Execute pipeline
    logger.info("🚀 Starting multi-agent pipeline...")
    final_state = await graph.ainvoke(initial_state)
    
    logger.info(
        f"✅ Pipeline complete - "
        f"Time: {final_state.get('total_time', 0):.2f}s, "
        f"Cost: ${final_state.get('total_cost', 0):.6f}, "
        f"Success: {final_state.get('success', False)}"
    )
    
    return final_state


async def stream_multi_agent_pipeline(
    question: str,
    user_context: str,
    workspace_id: str,
    user_id: str,
    conversation_history: list = None
):
    """
    Stream the multi-agent pipeline execution with progress updates
    
    This allows the frontend to show progress as the pipeline executes.
    
    Args:
        question: User's question
        user_context: User profile
        workspace_id: Workspace ID
        user_id: User ID
        conversation_history: Optional previous messages
        
    Yields:
        State updates as pipeline progresses
    """
    from .state import initialize_state
    
    # Initialize state
    initial_state = initialize_state(
        question=question,
        user_context=user_context,
        workspace_id=workspace_id,
        user_id=user_id,
        conversation_history=conversation_history
    )
    
    # Create graph
    graph = create_multi_agent_graph()
    
    # Stream execution
    logger.info("🚀 Starting streaming multi-agent pipeline...")
    
    async for chunk in graph.astream(initial_state):
        # Each chunk is the state after a node completes
        # The key is the node name, value is the updated state
        
        for node_name, state_update in chunk.items():
            yield {
                'node': node_name,
                'stage': state_update.get('_current_stage', 'unknown'),
                'state': state_update
            }
    
    logger.info("✅ Streaming pipeline complete")


# ============================================================================
# Testing and Examples
# ============================================================================

async def test_pipeline():
    """Test the complete pipeline"""
    
    print("=" * 80)
    print("TESTING MULTI-AGENT PIPELINE")
    print("=" * 80)
    
    # Test question
    test_question = "Should we expand to enterprise market?"
    test_context = """
    User Profile:
    - Role: CEO
    - Company: Series A SaaS
    - Current State: 100 SMB customers, $2M ARR, team of 12
    - Expertise: Intermediate
    - Decision Style: Analytical
    """
    
    print(f"\nQuestion: {test_question}")
    print(f"Context: {test_context.strip()}")
    
    try:
        # Run pipeline
        print("\n🚀 Running pipeline...")
        final_state = await run_multi_agent_pipeline(
            question=test_question,
            user_context=test_context,
            workspace_id="test_ws",
            user_id="test_user"
        )
        
        # Display results
        print("\n" + "=" * 80)
        print("PIPELINE RESULTS")
        print("=" * 80)
        
        print(f"\nSuccess: {final_state['success']}")
        print(f"Total Time: {final_state['total_time']:.2f}s")
        print(f"Total Cost: ${final_state['total_cost']:.6f}")
        print(f"Confidence: {final_state['confidence_level']}")
        print(f"Quality Score: {final_state['quality_score']:.2f}")
        
        print(f"\nAgents Activated: {', '.join(final_state['agents_to_activate'])}")
        print(f"Agents Succeeded: {', '.join(final_state['agents_succeeded'])}")
        
        if final_state['agents_failed']:
            print(f"Agents Failed: {', '.join(final_state['agents_failed'])}")
        
        print("\n" + "-" * 80)
        print("FINAL RESPONSE:")
        print("-" * 80)
        print(final_state['final_response'][:500] + "...")
        
        print("\n" + "-" * 80)
        print("AGENT TIMINGS:")
        print("-" * 80)
        for agent, timing in final_state['agent_timings'].items():
            print(f"  {agent}: {timing:.2f}s")
        
        print("\n" + "=" * 80)
        print("✅ Pipeline test complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Pipeline test failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_streaming():
    """Test streaming pipeline"""
    
    print("=" * 80)
    print("TESTING STREAMING PIPELINE")
    print("=" * 80)
    
    test_question = "What's the ROI on our marketing spend?"
    test_context = "CFO at B2B SaaS, analyzing marketing efficiency"
    
    print(f"\nQuestion: {test_question}")
    print("\n🚀 Streaming progress...\n")
    
    try:
        async for update in stream_multi_agent_pipeline(
            question=test_question,
            user_context=test_context,
            workspace_id="test_ws",
            user_id="test_user"
        ):
            node = update['node']
            stage = update['stage']
            print(f"  ✓ {node.upper()} → {stage}")
        
        print("\n✅ Streaming test complete!")
        
    except Exception as e:
        print(f"\n❌ Streaming test failed: {str(e)}")


if __name__ == '__main__':
    """Run tests"""
    import asyncio
    
    # Test basic pipeline
    asyncio.run(test_pipeline())
    
    # Test streaming (uncomment to test)
    # asyncio.run(test_streaming())