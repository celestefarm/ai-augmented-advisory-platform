# agents/orchestrator/nodes.py

"""
LangGraph Node Implementations - Optimized for Speed

Each node is a function that takes state and returns updated state.
Focus: Fast, parallel execution, minimal overhead.
"""

import time
import asyncio
import logging
from typing import Dict, Any
from .state import MultiAgentState

logger = logging.getLogger(__name__)


# ============================================================================
# STAGE 1: ANALYZE - Question Classification
# ============================================================================

async def analyze_question_node(state: MultiAgentState) -> MultiAgentState:
    """
    Stage 1: Classify question and detect emotional state
    
    Fast: Uses existing classifier (no LLM call needed)
    Time: ~50ms
    """
    stage_start = time.time()
    logger.info("Stage 1: Analyzing question...")
    
    try:
        # Import classifier (assumes it exists from Week 2)
        from agents.services.classifier import QuestionClassifier
        from agents.services.emotional_detector import EmotionalStateDetector
        
        # Initialize services
        classifier = QuestionClassifier()
        emotional_detector = EmotionalStateDetector()
        
        # Classify question
        classification = classifier.classify(state['question'])
        
        # Detect emotional state - CORRECTED: Use 'text' parameter
        emotional_result = emotional_detector.detect(text=state['question'])
        
        # Update state - CORRECTED: Store both object and dict for flexibility
        state['classification'] = {
            'question_type': classification.question_type,
            'domains': classification.domains,
            'urgency': classification.urgency,
            'complexity': classification.complexity,
            'confidence_score': classification.confidence_score,
            'detected_patterns': classification.detected_patterns
        }
        state['question_type'] = classification.question_type
        state['domains'] = classification.domains
        state['complexity'] = classification.complexity
        state['urgency'] = classification.urgency
        state['emotional_state'] = emotional_result.state
        state['tone_adjustment'] = emotional_result.tone_adjustment
        
        state['_current_stage'] = 'analyzed'
        
        elapsed = time.time() - stage_start
        logger.info(f"✅ Analysis complete - {elapsed:.3f}s")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {str(e)}")
        # Fallback defaults - Create a simple dict since we can't create QuestionMetadata
        from dataclasses import dataclass
        from typing import List
        
        @dataclass
        class FallbackClassification:
            question_type: str = 'exploration'
            domains: List[str] = None
            complexity: str = 'medium'
            urgency: str = 'routine'
            
            def __post_init__(self):
                if self.domains is None:
                    self.domains = ['strategy']
        
        state['classification'] = FallbackClassification()
        state['question_type'] = 'exploration'
        state['domains'] = ['strategy']
        state['complexity'] = 'medium'
        state['urgency'] = 'routine'
        state['emotional_state'] = 'neutral'
        state['tone_adjustment'] = {}
        state['_current_stage'] = 'analyzed_with_errors'
        return state


# ============================================================================
# STAGE 2: ROUTE - Agent Selection
# ============================================================================

async def route_to_agents_node(state: MultiAgentState) -> MultiAgentState:
    """
    Stage 2: Decide which agents to activate
    
    Fast: Rule-based routing (no LLM call)
    Time: ~10ms
    """
    stage_start = time.time()
    logger.info("Stage 2: Routing to agents...")
    
    try:
        # Import agent router (from your Week 3 work)
        from agents.services.agent_router import AgentRouter
        
        router = AgentRouter()
        
        # Get routing decision - CORRECTED: Use individual parameters
        routing_decision = router.route_question(
            question_type=state['question_type'],
            domains=state['domains'],
            complexity=state['complexity'],
            urgency=state['urgency']
        )
        
        # Update state - routing_decision is an object, not dict
        state['routing_decision'] = {
            'agents': routing_decision.agent_names,
            'execution_strategy': routing_decision.execution_strategy,
            'reasoning': routing_decision.reasoning
        }
        state['agents_to_activate'] = routing_decision.agent_names
        state['execution_strategy'] = routing_decision.execution_strategy
        state['routing_reasoning'] = routing_decision.reasoning
        
        state['_current_stage'] = 'routed'
        
        elapsed = time.time() - stage_start
        logger.info(
            f"✅ Routing complete - {elapsed:.3f}s - "
            f"Activating: {', '.join(state['agents_to_activate'])}"
        )
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Routing failed: {str(e)}")
        # Fallback: activate all agents
        state['agents_to_activate'] = ['market_compass', 'financial_guardian', 'strategy_analyst']
        state['execution_strategy'] = 'parallel'
        state['routing_reasoning'] = 'Fallback: All agents'
        state['_current_stage'] = 'routed_with_errors'
        return state


# ============================================================================
# STAGE 3: EXECUTE - Run Agents in Parallel (FAST!)
# ============================================================================

async def execute_agents_parallel_node(state: MultiAgentState) -> MultiAgentState:
    """
    Stage 3: Execute selected agents IN PARALLEL
    
    CRITICAL FOR SPEED: All agents run simultaneously
    Time: ~5s (longest agent) instead of ~13s (sequential)
    
    This is the core speed optimization!
    """
    stage_start = time.time()
    logger.info("Stage 3: Executing agents in parallel...")
    
    try:
        # Import agents
        from agents.market_compass import MarketCompassAgent
        from agents.financial_guardian import FinancialGuardianAgent
        from agents.strategy_analyst import StrategyAnalystAgent
        from decouple import config
        
        # Initialize agents
        agents_map = {}
        
        if 'market_compass' in state['agents_to_activate']:
            agents_map['market_compass'] = MarketCompassAgent(
                anthropic_api_key=config('ANTHROPIC_API_KEY', default=None),
                google_api_key=config('GOOGLE_API_KEY', default=None),
                use_web_search=True
            )
        
        if 'financial_guardian' in state['agents_to_activate']:
            agents_map['financial_guardian'] = FinancialGuardianAgent(
                anthropic_api_key=config('ANTHROPIC_API_KEY', default=None)
            )
        
        if 'strategy_analyst' in state['agents_to_activate']:
            agents_map['strategy_analyst'] = StrategyAnalystAgent(
                anthropic_api_key=config('ANTHROPIC_API_KEY', default=None)
            )
        
        # Build metadata for agents
        question_metadata = {
            'question_type': state['question_type'],
            'domains': state['domains'],
            'complexity': state['complexity'],
            'urgency': state['urgency']
        }
        
        # Build parallel tasks
        tasks = []
        agent_names = []
        
        for agent_name, agent_instance in agents_map.items():
            task = agent_instance.analyze(
                question=state['question'],
                user_context=state['user_context'],
                question_metadata=question_metadata
            )
            tasks.append(task)
            agent_names.append(agent_name)
        
        logger.info(f"🚀 Launching {len(tasks)} agents in parallel...")
        
        # Execute ALL agents in parallel - THIS IS THE SPEED BOOST!
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        agent_responses = {}
        agent_timings = {}
        agent_errors = {}
        agents_succeeded = []
        agents_failed = []
        
        for agent_name, result in zip(agent_names, results):
            if isinstance(result, Exception):
                # Agent failed
                error_msg = str(result)
                agent_errors[agent_name] = error_msg
                agents_failed.append(agent_name)
                logger.error(f"❌ {agent_name} failed: {error_msg}")
            
            elif result.get('success', False):
                # Agent succeeded
                agent_responses[agent_name] = result
                agent_timings[agent_name] = result.get('response_time', 0)
                agents_succeeded.append(agent_name)
                logger.info(
                    f"✅ {agent_name} completed - "
                    f"{result.get('response_time', 0):.2f}s"
                )
            
            else:
                # Agent returned but with error
                agent_errors[agent_name] = result.get('error', 'Unknown error')
                agents_failed.append(agent_name)
                logger.error(f"❌ {agent_name} error: {result.get('error')}")
        
        # Update state
        state['agent_responses'] = agent_responses
        state['agent_timings'] = agent_timings
        state['agent_errors'] = agent_errors
        state['agents_succeeded'] = agents_succeeded
        state['agents_failed'] = agents_failed
        
        state['_current_stage'] = 'executed'
        
        elapsed = time.time() - stage_start
        logger.info(
            f"✅ Parallel execution complete - {elapsed:.2f}s - "
            f"Success: {len(agents_succeeded)}/{len(agent_names)}"
        )
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Execution failed: {str(e)}", exc_info=True)
        state['agent_errors']['execution'] = str(e)
        state['_current_stage'] = 'execution_failed'
        return state


# ============================================================================
# STAGE 4: SYNTHESIZE - Chief of Staff Combines Outputs
# ============================================================================

async def synthesize_responses_node(state: MultiAgentState) -> MultiAgentState:
    """
    Stage 4: Chief of Staff synthesizes agent outputs
    
    Time: ~3-5s (one LLM call)
    """
    stage_start = time.time()
    logger.info("Stage 4: Synthesizing responses...")
    
    try:
        # Import Chief of Staff
        from agents.services.chief_agent import ChiefOfStaffAgent
        from decouple import config
        
        # Initialize Chief of Staff
        chief_agent = ChiefOfStaffAgent(
            api_key=config('ANTHROPIC_API_KEY', default=None),
            model="claude-sonnet-4-20250514"
        )
        
        # Check if we have any successful responses
        if not state['agent_responses']:
            logger.warning("No agent responses to synthesize - using fallback")
            state['synthesis'] = "Unable to generate complete analysis due to technical issues."
            state['synthesis_metadata'] = {'response_time': 0, 'success': False}
            state['_current_stage'] = 'synthesis_failed'
            return state
        
        # Synthesize using Chief of Staff
        synthesis, metadata = await chief_agent.synthesize_specialist_outputs(
            question=state['question'],
            specialist_outputs=state['agent_responses'],
            user_context=state['user_context'],
            emotional_state=state['emotional_state']
        )
        
        # Update state
        state['synthesis'] = synthesis
        state['synthesis_metadata'] = metadata
        state['_current_stage'] = 'synthesized'
        
        elapsed = time.time() - stage_start
        logger.info(f"✅ Synthesis complete - {elapsed:.2f}s")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Synthesis failed: {str(e)}", exc_info=True)
        # Fallback: concatenate agent responses
        fallback_synthesis = _create_fallback_synthesis(state['agent_responses'])
        state['synthesis'] = fallback_synthesis
        state['synthesis_metadata'] = {'response_time': 0, 'success': False, 'fallback': True}
        state['_current_stage'] = 'synthesis_fallback'
        return state


def _create_fallback_synthesis(agent_responses: Dict[str, Dict]) -> str:
    """Create simple fallback synthesis if Chief of Staff fails"""
    parts = ["Based on the analysis:\n"]
    
    if 'market_compass' in agent_responses:
        parts.append(f"\n**Market Perspective:**\n{agent_responses['market_compass'].get('analysis', 'N/A')}")
    
    if 'financial_guardian' in agent_responses:
        parts.append(f"\n**Financial Perspective:**\n{agent_responses['financial_guardian'].get('calculation', 'N/A')}")
    
    if 'strategy_analyst' in agent_responses:
        parts.append(f"\n**Strategic Perspective:**\n{agent_responses['strategy_analyst'].get('decision_reframe', 'N/A')}")
    
    return "\n".join(parts)


# ============================================================================
# STAGE 5: QUALITY GATES - Validate Output
# ============================================================================

async def quality_check_node(state: MultiAgentState) -> MultiAgentState:
    """
    Stage 5: Quality gates and confidence marking
    
    Fast: Rule-based checks (no LLM call)
    Time: ~10ms
    """
    stage_start = time.time()
    logger.info("Stage 5: Quality checking...")
    
    try:
        quality_score = 0.0
        quality_issues = []
        
        # Check 1: Synthesis length (30%)
        if state.get('synthesis') and len(state['synthesis']) > 100:
            quality_score += 0.3
        else:
            quality_issues.append("Synthesis too short")
        
        # Check 2: Agent completeness (30%)
        expected = len(state.get('agents_to_activate', []))
        actual = len(state.get('agents_succeeded', []))
        
        if actual == expected and expected > 0:
            quality_score += 0.3
        elif actual > 0:
            quality_score += 0.15  # Partial credit
            quality_issues.append(f"Only {actual}/{expected} agents succeeded")
        else:
            quality_issues.append("No agents succeeded")
        
        # Check 3: Confidence levels (40%)
        high_confidence_count = 0
        total_agents = len(state.get('agent_responses', {}))
        
        for response in state.get('agent_responses', {}).values():
            confidence = response.get('confidence', '')
            if '🟢' in confidence or 'High' in confidence:
                high_confidence_count += 1
        
        if total_agents > 0:
            confidence_ratio = high_confidence_count / total_agents
            quality_score += 0.4 * confidence_ratio
        
        # Determine overall confidence level
        if quality_score >= 0.8:
            confidence_level = '🟢 High'
        elif quality_score >= 0.6:
            confidence_level = '🟡 Medium'
        elif quality_score >= 0.4:
            confidence_level = '🟠 Low'
        else:
            confidence_level = '🔴 Very Low'
        
        # Check completeness
        completeness = (actual == expected) if expected > 0 else False
        
        # Decide if retry needed (disabled for speed - accept what we got)
        retry_needed = False  # quality_score < 0.4 and state.get('_retry_count', 0) < 1
        
        # Update state
        state['quality_score'] = quality_score
        state['confidence_level'] = confidence_level
        state['completeness'] = completeness
        state['quality_issues'] = quality_issues
        state['retry_needed'] = retry_needed
        state['_current_stage'] = 'quality_checked'
        
        elapsed = time.time() - stage_start
        logger.info(
            f"✅ Quality check complete - {elapsed:.3f}s - "
            f"Score: {quality_score:.2f}, Confidence: {confidence_level}"
        )
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Quality check failed: {str(e)}")
        state['quality_score'] = 0.5
        state['confidence_level'] = '🟡 Medium'
        state['completeness'] = False
        state['quality_issues'] = ['Quality check error']
        state['retry_needed'] = False
        state['_current_stage'] = 'quality_check_failed'
        return state


# ============================================================================
# STAGE 6: FINALIZE - Build Final Response
# ============================================================================

async def finalize_response_node(state: MultiAgentState) -> MultiAgentState:
    """
    Stage 6: Build final response and metadata
    
    Fast: Simple data aggregation
    Time: ~5ms
    """
    stage_start = time.time()
    logger.info("Stage 6: Finalizing response...")
    
    try:
        # Calculate total time
        total_time = time.time() - state.get('_start_time', time.time())
        
        # Calculate total cost
        total_cost = 0.0
        for response in state.get('agent_responses', {}).values():
            total_cost += response.get('cost', 0)
        
        # Add synthesis cost
        synthesis_meta = state.get('synthesis_metadata', {})
        total_cost += synthesis_meta.get('cost', 0)
        
        # Build metadata
        metadata = {
            'agents_activated': state.get('agents_to_activate', []),
            'agents_succeeded': state.get('agents_succeeded', []),
            'agents_failed': state.get('agents_failed', []),
            'agent_timings': state.get('agent_timings', {}),
            'agent_errors': state.get('agent_errors', {}),
            'quality_score': state.get('quality_score', 0),
            'confidence_level': state.get('confidence_level', '🟡 Medium'),
            'completeness': state.get('completeness', False),
            'quality_issues': state.get('quality_issues', []),
            'total_time': round(total_time, 2),
            'total_cost': round(total_cost, 6),
            'execution_strategy': state.get('execution_strategy', 'parallel'),
            'question_type': state.get('question_type', 'unknown'),
            'complexity': state.get('complexity', 'unknown')
        }
        
        # Final response is the synthesis
        final_response = state.get('synthesis', 'Unable to generate response.')
        
        # Update state
        state['final_response'] = final_response
        state['metadata'] = metadata
        state['total_time'] = total_time
        state['total_cost'] = total_cost
        state['success'] = len(state.get('agents_succeeded', [])) > 0
        state['_current_stage'] = 'finalized'
        
        elapsed = time.time() - stage_start
        logger.info(
            f"✅ Finalization complete - {elapsed:.3f}s - "
            f"Total: {total_time:.2f}s, Cost: ${total_cost:.6f}"
        )
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Finalization failed: {str(e)}")
        state['success'] = False
        state['_current_stage'] = 'finalization_failed'
        return state


# Example usage and testing
if __name__ == '__main__':
    """Test nodes individually"""
    import asyncio
    from .state import initialize_state
    
    async def test_nodes():
        print("=" * 80)
        print("TESTING LANGGRAPH NODES")
        print("=" * 80)
        
        # Initialize state
        state = initialize_state(
            question="Should we expand to enterprise market?",
            user_context="Series A SaaS, 100 SMB customers",
            workspace_id="ws_test",
            user_id="user_test"
        )
        
        print("\n✅ State initialized")
        
        # Test each node
        print("\n" + "-" * 80)
        print("Testing Stage 1: Analyze")
        state = await analyze_question_node(state)
        print(f"Result: {state['_current_stage']}")
        
        print("\n" + "-" * 80)
        print("Testing Stage 2: Route")
        state = await route_to_agents_node(state)
        print(f"Agents to activate: {state['agents_to_activate']}")
        
        print("\n" + "-" * 80)
        print("Note: Stages 3-6 require Django settings and API keys")
        print("Run full integration test to test those stages")
        
        print("\n" + "=" * 80)
        print("✅ Node tests complete")
        print("=" * 80)
    
    asyncio.run(test_nodes())