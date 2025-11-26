# orchestrator/state.py

"""
Multi-Agent State Definition for LangGraph

This defines the shared state that flows through the entire pipeline.
Each node reads from and writes to this state.
"""

from typing import TypedDict, Dict, List, Optional, Any


class MultiAgentState(TypedDict, total=False):
    """
    Shared state for multi-agent orchestration
    
    Flow through pipeline:
    Input → Analyze → Route → Execute → Synthesize → Quality → Output
    """
    
    # ============================================================================
    # INPUT (from user/API)
    # ============================================================================
    question: str                           # User's question
    user_context: str                       # User profile and history
    workspace_id: str                       # Workspace identifier
    user_id: str                            # User identifier
    conversation_history: Optional[List[Dict]]  # Previous messages
    
    # ============================================================================
    # STAGE 1: ANALYZE (Question Classification)
    # ============================================================================
    classification: Dict[str, Any]          # Question classification
    question_type: str                      # decision/validation/exploration/crisis
    domains: List[str]                      # market/finance/strategy/people/execution
    complexity: str                         # simple/medium/complex
    urgency: str                            # routine/important/urgent/crisis
    emotional_state: str                    # anxiety/confidence/uncertainty/urgency
    tone_adjustment: Dict[str, str]         # Tone adjustment instructions
    
    # ============================================================================
    # STAGE 2: ROUTE (Agent Selection)
    # ============================================================================
    routing_decision: Dict[str, Any]        # Routing decision from agent_router
    agents_to_activate: List[str]           # Which agents to use
    execution_strategy: str                 # parallel/sequential
    routing_reasoning: str                  # Why these agents selected
    
    # ============================================================================
    # STAGE 3: EXECUTE (Agent Responses)
    # ============================================================================
    agent_responses: Dict[str, Dict]        # Responses from each agent
    agent_timings: Dict[str, float]         # Response time per agent
    agent_errors: Dict[str, str]            # Any errors encountered
    agents_succeeded: List[str]             # Which agents succeeded
    agents_failed: List[str]                # Which agents failed
    
    # ============================================================================
    # STAGE 4: SYNTHESIZE (Chief of Staff Synthesis)
    # ============================================================================
    synthesis: str                          # Combined narrative from Chief of Staff
    synthesis_metadata: Dict[str, Any]      # Synthesis timing and tokens
    key_insights: List[str]                 # Main takeaways
    conflicting_views: Optional[str]        # If agents disagreed
    
    # ============================================================================
    # STAGE 5: QUALITY GATES (Validation)
    # ============================================================================
    quality_score: float                    # 0-1 quality score
    confidence_level: str                   # 🟢/🟡/🟠/🔴
    completeness: bool                      # All agents responded?
    quality_issues: List[str]               # Any quality concerns
    retry_needed: bool                      # Should we retry?
    
    # ============================================================================
    # OUTPUT (to user/API)
    # ============================================================================
    final_response: str                     # What user sees
    metadata: Dict[str, Any]                # Complete metadata
    total_time: float                       # End-to-end timing
    total_cost: float                       # Total API cost
    success: bool                           # Overall success flag
    
    # ============================================================================
    # INTERNAL (for orchestration)
    # ============================================================================
    _start_time: float                      # Pipeline start timestamp
    _current_stage: str                     # Current pipeline stage
    _retry_count: int                       # How many retries attempted


# Type aliases for convenience
AgentResponse = Dict[str, Any]
AgentResponses = Dict[str, AgentResponse]


# Helper functions for state manipulation
def initialize_state( question: str, user_context: str, workspace_id: str, user_id: str, conversation_history: Optional[List[Dict]] = None) -> MultiAgentState:
    """
    Initialize state with user input
    
    Args:
        question: User's question
        user_context: User profile
        workspace_id: Workspace ID
        user_id: User ID
        conversation_history: Optional previous messages
        
    Returns:
        Initialized state dict
    """
    import time
    
    return {
        # Input
        'question': question,
        'user_context': user_context,
        'workspace_id': workspace_id,
        'user_id': user_id,
        'conversation_history': conversation_history or [],
        
        # Initialize empty structures
        'agent_responses': {},
        'agent_timings': {},
        'agent_errors': {},
        'agents_succeeded': [],
        'agents_failed': [],
        
        # Internal
        '_start_time': time.time(),
        '_current_stage': 'input',
        '_retry_count': 0,
        
        # Defaults
        'retry_needed': False,
        'success': False
    }


def get_state_summary(state: MultiAgentState) -> str:
    """
    Get human-readable state summary for debugging
    
    Args:
        state: Current state
        
    Returns:
        Summary string
    """
    import json
    
    summary_parts = [
        f"Question: {state.get('question', 'N/A')[:100]}...",
        f"Stage: {state.get('_current_stage', 'unknown')}",
        f"Agents Activated: {', '.join(state.get('agents_to_activate', []))}",
        f"Agents Succeeded: {', '.join(state.get('agents_succeeded', []))}",
        f"Agents Failed: {', '.join(state.get('agents_failed', []))}",
        f"Quality Score: {state.get('quality_score', 0):.2f}",
        f"Confidence: {state.get('confidence_level', 'unknown')}",
        f"Success: {state.get('success', False)}"
    ]
    
    return "\n".join(summary_parts)


# Example usage
if __name__ == '__main__':
    """Test state initialization"""
    
    # Initialize test state
    test_state = initialize_state(
        question="Should we expand to enterprise market?",
        user_context="Series A SaaS, 100 SMB customers, $2M ARR",
        workspace_id="ws_123",
        user_id="user_456"
    )
    
    print("=" * 80)
    print("MULTI-AGENT STATE INITIALIZED")
    print("=" * 80)
    print("\nState Summary:")
    print(get_state_summary(test_state))
    print("\n" + "=" * 80)
    print("✅ State definition ready")
    print("=" * 80)