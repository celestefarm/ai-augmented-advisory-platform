# agents/services/agent_router.py

"""
Agent Router - Decides which specialized agents to activate

Based on question classification from Week 2, determines:
1. Which agents should respond (1-5 agents)
2. Execution strategy (parallel vs sequential)
3. Priority/importance of each agent's input

Agent Domains:
- Market Compass: Market intelligence, competitor analysis, trends
- Financial Guardian: Financials, calculations, scenario modeling
- Strategy Analyst: Strategic frameworks, assumption testing
- People Advisor: Organizational dynamics, team issues, culture
- Execution Architect: Timeline estimation, execution planning

Week 3 Focus: Market Compass, Financial Guardian, Strategy Analyst
"""

from typing import List, Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentActivation:
    """Represents an agent that should be activated"""
    agent_name: str
    priority: str  # 'primary' | 'secondary' | 'optional'
    reasoning: str
    
    def __repr__(self):
        return f"{self.agent_name} ({self.priority})"


class AgentRoutingDecision:
    """Result of agent routing decision"""
    def __init__(
        self,
        activated_agents: List[AgentActivation],
        execution_strategy: str,
        reasoning: str
    ):
        self.activated_agents = activated_agents
        self.execution_strategy = execution_strategy  # 'parallel' | 'sequential'
        self.reasoning = reasoning
        
        # Extract agent names for easy access
        self.agent_names = [agent.agent_name for agent in activated_agents]
        self.primary_agents = [
            agent.agent_name for agent in activated_agents 
            if agent.priority == 'primary'
        ]
    
    def __repr__(self):
        return (
            f"AgentRoutingDecision(agents={self.agent_names}, "
            f"strategy={self.execution_strategy})"
        )


class AgentRouter:
    """
    Intelligent agent routing based on question characteristics
    
    Routes to 1-5 specialized agents based on:
    - Question type (decision, validation, exploration, crisis)
    - Domains involved (market, finance, strategy, people, execution)
    - Complexity level
    - Urgency
    """
    
    # Agent domain expertise mapping
    AGENT_DOMAINS = {
        'market_compass': ['market', 'competition', 'trends', 'customers'],
        'financial_guardian': ['finance', 'numbers', 'calculations', 'roi', 'pricing'],
        'strategy_analyst': ['strategy', 'frameworks', 'positioning', 'decisions'],
        'people_advisor': ['people', 'team', 'culture', 'hiring', 'organization'],
        'execution_architect': ['execution', 'timeline', 'resources', 'implementation']
    }
    
    def route_question(
        self,
        question_type: str,
        domains: List[str],
        complexity: str,
        urgency: str
    ) -> AgentRoutingDecision:
        """
        Determine which agents should respond to the question
        
        Args:
            question_type: decision | validation | exploration | crisis
            domains: List of relevant domains
            complexity: simple | medium | complex
            urgency: routine | important | urgent | crisis
            
        Returns:
            AgentRoutingDecision with activated agents and strategy
        """
        activated_agents = []
        
        # WEEK 3: Only use Market Compass, Financial Guardian, Strategy Analyst
        available_agents = ['market_compass', 'financial_guardian', 'strategy_analyst']
        
        # Step 1: Domain-based activation
        for domain in domains:
            for agent_name in available_agents:
                agent_domains = self.AGENT_DOMAINS[agent_name]
                
                # Check if this agent covers this domain
                if any(keyword in domain.lower() for keyword in agent_domains):
                    # Check if agent not already activated
                    if not any(a.agent_name == agent_name for a in activated_agents):
                        priority = self._determine_priority(
                            agent_name, 
                            domain, 
                            question_type, 
                            complexity
                        )
                        
                        reasoning = self._generate_activation_reasoning(
                            agent_name,
                            domain,
                            question_type
                        )
                        
                        activated_agents.append(
                            AgentActivation(
                                agent_name=agent_name,
                                priority=priority,
                                reasoning=reasoning
                            )
                        )
        
        # Step 2: Question type adjustments
        activated_agents = self._apply_question_type_rules(
            activated_agents,
            question_type,
            domains,
            available_agents
        )
        
        # Step 3: Complexity adjustments
        if complexity == 'simple' and len(activated_agents) > 1:
            # For simple questions, only use primary agent
            activated_agents = [
                agent for agent in activated_agents 
                if agent.priority == 'primary'
            ][:1]
        
        # Step 4: Ensure at least one agent is activated
        if not activated_agents:
            # Default to Strategy Analyst for general questions
            activated_agents.append(
                AgentActivation(
                    agent_name='strategy_analyst',
                    priority='primary',
                    reasoning='Default agent for general strategic questions'
                )
            )
        
        # Step 5: Determine execution strategy
        execution_strategy = self._determine_execution_strategy(
            activated_agents,
            urgency,
            complexity
        )
        
        # Step 6: Generate overall reasoning
        reasoning = self._generate_routing_reasoning(
            activated_agents,
            question_type,
            domains,
            complexity,
            urgency
        )
        
        logger.info(
            f"Agent routing decision: {[a.agent_name for a in activated_agents]} "
            f"(strategy: {execution_strategy})"
        )
        
        return AgentRoutingDecision(
            activated_agents=activated_agents,
            execution_strategy=execution_strategy,
            reasoning=reasoning
        )
    
    def _determine_priority(
        self,
        agent_name: str,
        domain: str,
        question_type: str,
        complexity: str
    ) -> str:
        """
        Determine if agent should be primary or secondary
        
        Returns:
            'primary' | 'secondary' | 'optional'
        """
        # Market questions → Market Compass is primary
        if 'market' in domain.lower() and agent_name == 'market_compass':
            return 'primary'
        
        # Financial questions → Financial Guardian is primary
        if any(word in domain.lower() for word in ['finance', 'pricing', 'roi']) and \
           agent_name == 'financial_guardian':
            return 'primary'
        
        # Strategy questions → Strategy Analyst is primary
        if 'strategy' in domain.lower() and agent_name == 'strategy_analyst':
            return 'primary'
        
        # For complex questions, more agents are primary
        if complexity == 'complex':
            return 'primary'
        
        # Otherwise secondary
        return 'secondary'
    
    def _apply_question_type_rules(
        self,
        activated_agents: List[AgentActivation],
        question_type: str,
        domains: List[str],
        available_agents: List[str]
    ) -> List[AgentActivation]:
        """
        Apply question-type specific routing rules
        """
        agent_names = [a.agent_name for a in activated_agents]
        
        # DECISION questions often need financial + strategic perspective
        if question_type == 'decision':
            if 'financial_guardian' not in agent_names and \
               'financial_guardian' in available_agents:
                activated_agents.append(
                    AgentActivation(
                        agent_name='financial_guardian',
                        priority='secondary',
                        reasoning='Decisions require financial impact assessment'
                    )
                )
            
            if 'strategy_analyst' not in agent_names and \
               'strategy_analyst' in available_agents:
                activated_agents.append(
                    AgentActivation(
                        agent_name='strategy_analyst',
                        priority='primary',
                        reasoning='Strategic analysis crucial for decisions'
                    )
                )
        
        # EXPLORATION questions → use multiple perspectives
        elif question_type == 'exploration':
            # Activate all 3 Week 3 agents for exploration
            for agent_name in available_agents:
                if agent_name not in agent_names:
                    activated_agents.append(
                        AgentActivation(
                            agent_name=agent_name,
                            priority='secondary',
                            reasoning='Exploration benefits from multiple perspectives'
                        )
                    )
        
        # VALIDATION questions → focused on primary domain
        elif question_type == 'validation':
            # Keep only primary agents for validation
            activated_agents = [
                agent for agent in activated_agents 
                if agent.priority == 'primary'
            ]
        
        # CRISIS questions → need execution perspective (not in Week 3)
        elif question_type == 'crisis':
            # For now, use strategy analyst for crisis
            if 'strategy_analyst' not in agent_names:
                activated_agents.append(
                    AgentActivation(
                        agent_name='strategy_analyst',
                        priority='primary',
                        reasoning='Crisis requires strategic triage'
                    )
                )
        
        return activated_agents
    
    def _determine_execution_strategy(
        self,
        activated_agents: List[AgentActivation],
        urgency: str,
        complexity: str
    ) -> str:
        """
        Determine if agents should execute in parallel or sequential
        
        Returns:
            'parallel' | 'sequential'
        """
        # Week 3: Always use parallel execution
        # This is the core feature we're building
        return 'parallel'
    
    def _generate_activation_reasoning(
        self,
        agent_name: str,
        domain: str,
        question_type: str
    ) -> str:
        """Generate reasoning for why this agent was activated"""
        
        agent_expertise = {
            'market_compass': 'market intelligence and competitive analysis',
            'financial_guardian': 'financial modeling and quantitative analysis',
            'strategy_analyst': 'strategic frameworks and decision analysis'
        }
        
        expertise = agent_expertise.get(agent_name, 'general expertise')
        
        return f"Activated for {domain} domain - provides {expertise}"
    
    def _generate_routing_reasoning(
        self,
        activated_agents: List[AgentActivation],
        question_type: str,
        domains: List[str],
        complexity: str,
        urgency: str
    ) -> str:
        """Generate overall routing reasoning"""
        
        agent_count = len(activated_agents)
        agent_names = [a.agent_name.replace('_', ' ').title() for a in activated_agents]
        
        reasons = []
        
        # Agent count reasoning
        if agent_count == 1:
            reasons.append(f"Single agent ({agent_names[0]}) sufficient for focused query")
        elif agent_count == 2:
            reasons.append(f"Two agents ({', '.join(agent_names)}) for dual perspective")
        else:
            reasons.append(f"Multiple agents ({', '.join(agent_names)}) for comprehensive analysis")
        
        # Domain reasoning
        if len(domains) >= 3:
            reasons.append(f"Multi-domain question ({len(domains)} domains)")
        
        # Complexity reasoning
        if complexity == 'complex':
            reasons.append("Complex question benefits from multiple expert perspectives")
        
        # Question type reasoning
        if question_type == 'decision':
            reasons.append("Decision requires balanced analysis across dimensions")
        elif question_type == 'exploration':
            reasons.append("Exploration enhanced by diverse viewpoints")
        
        return " | ".join(reasons)


# Example usage and testing
if __name__ == '__main__':
    """Test agent routing with different scenarios"""
    
    router = AgentRouter()
    
    test_cases = [
        {
            'name': 'Market Strategy Decision',
            'question_type': 'decision',
            'domains': ['market', 'strategy'],
            'complexity': 'complex',
            'urgency': 'important'
        },
        {
            'name': 'Financial Validation',
            'question_type': 'validation',
            'domains': ['finance'],
            'complexity': 'medium',
            'urgency': 'routine'
        },
        {
            'name': 'Exploration - Multiple Domains',
            'question_type': 'exploration',
            'domains': ['market', 'finance', 'strategy'],
            'complexity': 'complex',
            'urgency': 'routine'
        },
        {
            'name': 'Simple Pricing Question',
            'question_type': 'decision',
            'domains': ['finance'],
            'complexity': 'simple',
            'urgency': 'routine'
        }
    ]
    
    print("\n" + "=" * 80)
    print("AGENT ROUTING TEST CASES")
    print("=" * 80)
    
    for case in test_cases:
        print(f"\n{'=' * 80}")
        print(f"Case: {case['name']}")
        print(f"{'=' * 80}")
        print(f"Type: {case['question_type']} | Domains: {case['domains']}")
        print(f"Complexity: {case['complexity']} | Urgency: {case['urgency']}")
        
        decision = router.route_question(
            question_type=case['question_type'],
            domains=case['domains'],
            complexity=case['complexity'],
            urgency=case['urgency']
        )
        
        print(f"\nActivated Agents: {len(decision.activated_agents)}")
        for agent in decision.activated_agents:
            print(f"  • {agent.agent_name} [{agent.priority}]")
            print(f"    → {agent.reasoning}")
        
        print(f"\nExecution: {decision.execution_strategy}")
        print(f"Reasoning: {decision.reasoning}")
    
    print("\n" + "=" * 80)
    print("✅ Agent routing tests complete!")
    print("=" * 80)