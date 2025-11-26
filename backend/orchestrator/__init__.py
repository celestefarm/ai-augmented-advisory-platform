# orchestrator/__init__.py

"""
Multi-Agent Orchestration with LangGraph

Fast, parallel execution of specialized AI agents with intelligent synthesis.

Main Components:
- State: Shared state flowing through pipeline
- Nodes: Individual pipeline stages
- Graph: LangGraph orchestration engine

Usage:
    from agents.orchestrator import run_multi_agent_pipeline
    
    result = await run_multi_agent_pipeline(
        question="Should we expand to enterprise?",
        user_context="Series A SaaS CEO",
        workspace_id="ws_123",
        user_id="user_456"
    )
    
    print(result['final_response'])
"""

from .state import MultiAgentState, initialize_state
from .graph import (
    create_multi_agent_graph,
    run_multi_agent_pipeline,
    stream_multi_agent_pipeline
)

__all__ = [
    'MultiAgentState',
    'initialize_state',
    'create_multi_agent_graph',
    'run_multi_agent_pipeline',
    'stream_multi_agent_pipeline'
]