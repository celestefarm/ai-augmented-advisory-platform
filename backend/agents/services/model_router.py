# agents/services/model_router.py

"""
Model Selection Router

Intelligently selects optimal LLM based on:
- Question complexity
- Required capabilities (reasoning vs research vs calculation)
- Urgency level
- Cost optimization

Model Strategy:
- Claude Sonnet 4: Primary model (balanced quality/speed/cost)
- Claude Opus 4: Complex reasoning, high-stakes decisions
- Gemini 2.0 Flash: Fast, simple queries, benchmarks
- Gemini 2.0 Pro: Research-heavy queries (with search)

Pricing (per 1M tokens):
- Claude Sonnet 4: $3 input / $15 output
- Claude Opus 4: $15 input / $75 output
- Gemini Flash: $0.075 input / $0.30 output
- Gemini Pro: $1.25 input / $5 output
"""

from typing import Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class ModelName(str, Enum):
    """Available models"""
    CLAUDE_SONNET = "claude-sonnet-4-20250514"
    CLAUDE_OPUS = "claude-opus-4-20250514"
    GEMINI_FLASH = "gemini-2.0-flash-exp"
    GEMINI_PRO = "gemini-2.0-pro"


@dataclass
class ModelCharacteristics:
    """Model characteristics for selection"""
    name: str
    reasoning_quality: int  # 1-10
    research_capability: int  # 1-10
    speed: int  # 1-10 (higher = faster)
    cost_per_1k_tokens: float  # Approximate average
    best_for: list


class ModelSelectionResult:
    """Result of model selection"""
    def __init__(
        self,
        model_name: str,
        selection_criteria: Dict,
        estimated_cost: float,
        estimated_latency: float,
        reasoning: str
    ):
        self.model_name = model_name
        self.selection_criteria = selection_criteria
        self.estimated_cost = estimated_cost
        self.estimated_latency = estimated_latency
        self.reasoning = reasoning


class ModelRouter:
    """
    Intelligent model selection based on task requirements
    """
    
    # Model characteristics database
    MODELS = {
        ModelName.CLAUDE_SONNET: ModelCharacteristics(
            name=ModelName.CLAUDE_SONNET,
            reasoning_quality=9,
            research_capability=6,
            speed=7,
            cost_per_1k_tokens=0.009,  # Average of input/output
            best_for=[
                'strategic_decisions',
                'people_problems',
                'nuanced_thinking',
                'synthesis',
                'default_choice'
            ]
        ),
        ModelName.CLAUDE_OPUS: ModelCharacteristics(
            name=ModelName.CLAUDE_OPUS,
            reasoning_quality=10,
            research_capability=7,
            speed=5,
            cost_per_1k_tokens=0.045,  # Average of input/output
            best_for=[
                'high_stakes_decisions',
                'complex_reasoning',
                'ethical_dilemmas',
                'novel_problems',
                'synthesis_of_contradictions'
            ]
        ),
        ModelName.GEMINI_FLASH: ModelCharacteristics(
            name=ModelName.GEMINI_FLASH,
            reasoning_quality=6,
            research_capability=5,
            speed=10,
            cost_per_1k_tokens=0.0002,  # Average of input/output
            best_for=[
                'simple_queries',
                'quick_facts',
                'benchmarks',
                'standard_timelines',
                'cost_optimization'
            ]
        ),
        ModelName.GEMINI_PRO: ModelCharacteristics(
            name=ModelName.GEMINI_PRO,
            reasoning_quality=8,
            research_capability=10,
            speed=6,
            cost_per_1k_tokens=0.003,  # Average of input/output
            best_for=[
                'market_research',
                'competitor_analysis',
                'web_search_queries',
                'data_gathering',
                'trend_analysis'
            ]
        ),
    }
    
    def select_model(
        self,
        question_type: str,
        domains: list,
        urgency: str,
        complexity: str,
        emotional_state: str = None
    ) -> ModelSelectionResult:
        """
        Select optimal model based on question characteristics
        
        Args:
            question_type: decision | validation | exploration | crisis
            domains: List of domains (market, strategy, finance, people, execution)
            urgency: routine | important | urgent | crisis
            complexity: simple | medium | complex
            emotional_state: Optional emotional state
            
        Returns:
            ModelSelectionResult with selected model and reasoning
        """
        criteria = {
            'question_type': question_type,
            'domains': domains,
            'urgency': urgency,
            'complexity': complexity,
            'emotional_state': emotional_state
        }
        
        # Decision tree for model selection
        selected_model = self._apply_selection_logic(
            question_type,
            domains,
            urgency,
            complexity,
            emotional_state
        )
        
        # Estimate cost and latency
        estimated_cost, estimated_latency = self._estimate_performance(
            selected_model,
            complexity
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            selected_model,
            question_type,
            domains,
            urgency,
            complexity
        )
        
        return ModelSelectionResult(
            model_name=selected_model,
            selection_criteria=criteria,
            estimated_cost=estimated_cost,
            estimated_latency=estimated_latency,
            reasoning=reasoning
        )
    
    def _apply_selection_logic(
        self,
        question_type: str,
        domains: list,
        urgency: str,
        complexity: str,
        emotional_state: str
    ) -> str:
        """
        Apply model selection decision tree
        
        Returns:
            Selected model name
        """
        # RULE 1: Market research queries → Gemini Pro (best for research)
        if 'market' in domains and question_type == 'exploration':
            return ModelName.GEMINI_PRO
        
        # RULE 2: Simple routine queries → Gemini Flash (fast and cheap)
        if complexity == 'simple' and urgency == 'routine':
            return ModelName.GEMINI_FLASH
        
        # RULE 3: Crisis + high urgency → Claude Sonnet (fast reasoning)
        if urgency in ['crisis', 'urgent']:
            # Unless it's also highly complex
            if complexity == 'complex':
                return ModelName.CLAUDE_OPUS  # Need best reasoning despite urgency
            return ModelName.CLAUDE_SONNET
        
        # RULE 4: Complex decisions + multiple domains → Claude Opus
        if complexity == 'complex' and len(domains) >= 3:
            return ModelName.CLAUDE_OPUS
        
        # RULE 5: People/organizational questions + complexity → Claude Sonnet/Opus
        if 'people' in domains:
            if complexity == 'complex' or emotional_state == 'anxiety':
                return ModelName.CLAUDE_OPUS  # Need best psychological nuance
            return ModelName.CLAUDE_SONNET
        
        # RULE 6: Financial calculations → Claude Sonnet (good at math)
        if 'finance' in domains and question_type == 'decision':
            return ModelName.CLAUDE_SONNET
        
        # RULE 7: Strategic decisions + medium-high complexity → Claude Sonnet
        if 'strategy' in domains and complexity in ['medium', 'complex']:
            if complexity == 'complex':
                return ModelName.CLAUDE_OPUS
            return ModelName.CLAUDE_SONNET
        
        # RULE 8: Execution planning → Claude Sonnet (logical sequencing)
        if 'execution' in domains:
            return ModelName.CLAUDE_SONNET
        
        # DEFAULT: Claude Sonnet (best all-rounder)
        return ModelName.CLAUDE_SONNET
    
    def _estimate_performance(
        self,
        model_name: str,
        complexity: str
    ) -> Tuple[float, float]:
        """
        Estimate cost and latency for selected model
        
        Args:
            model_name: Selected model
            complexity: Question complexity
            
        Returns:
            (estimated_cost_usd, estimated_latency_seconds)
        """
        model_chars = self.MODELS[model_name]
        
        # Estimate token count based on complexity
        token_estimates = {
            'simple': 500,    # ~500 tokens total
            'medium': 1500,   # ~1500 tokens total
            'complex': 3000,  # ~3000 tokens total
        }
        
        estimated_tokens = token_estimates.get(complexity, 1500)
        estimated_cost = (estimated_tokens / 1000) * model_chars.cost_per_1k_tokens
        
        # Estimate latency (inverse of speed, adjusted by complexity)
        base_latency = 12 - model_chars.speed  # 10 speed = ~2s, 5 speed = ~7s
        complexity_multiplier = {
            'simple': 0.7,
            'medium': 1.0,
            'complex': 1.5,
        }
        estimated_latency = base_latency * complexity_multiplier.get(complexity, 1.0)
        
        return round(estimated_cost, 6), round(estimated_latency, 1)
    
    def _generate_reasoning(
        self,
        model_name: str,
        question_type: str,
        domains: list,
        urgency: str,
        complexity: str
    ) -> str:
        """
        Generate human-readable reasoning for model selection
        
        Returns:
            Reasoning string
        """
        model_chars = self.MODELS[model_name]
        
        reasons = []
        
        # Add primary reason
        if model_name == ModelName.CLAUDE_OPUS:
            reasons.append("Selected Claude Opus for highest reasoning quality")
        elif model_name == ModelName.GEMINI_PRO:
            reasons.append("Selected Gemini Pro for superior research capability")
        elif model_name == ModelName.GEMINI_FLASH:
            reasons.append("Selected Gemini Flash for speed and cost efficiency")
        else:
            reasons.append("Selected Claude Sonnet as optimal all-rounder")
        
        # Add context
        if complexity == 'complex':
            reasons.append(f"Complex question requires advanced reasoning")
        
        if len(domains) >= 3:
            reasons.append(f"Multi-domain question ({len(domains)} domains) needs synthesis")
        
        if urgency in ['crisis', 'urgent']:
            reasons.append(f"{urgency.capitalize()} urgency prioritizes response time")
        
        if 'people' in domains:
            reasons.append("People/organizational question needs psychological nuance")
        
        # Add model strengths
        reasons.append(f"Best for: {', '.join(model_chars.best_for[:2])}")
        
        return " | ".join(reasons)
    
    def get_model_config(self, model_name: str) -> Dict:
        """
        Get configuration for API call
        
        Args:
            model_name: Model to configure
            
        Returns:
            Dict with API configuration
        """
        # Model-specific configurations
        configs = {
            ModelName.CLAUDE_SONNET: {
                'model': ModelName.CLAUDE_SONNET,
                'max_tokens': 2000,
                'temperature': 0.7,
                'top_p': 0.9,
            },
            ModelName.CLAUDE_OPUS: {
                'model': ModelName.CLAUDE_OPUS,
                'max_tokens': 3000,
                'temperature': 0.8,
                'top_p': 0.95,
            },
            ModelName.GEMINI_FLASH: {
                'model': ModelName.GEMINI_FLASH,
                'max_tokens': 1000,
                'temperature': 0.5,
            },
            ModelName.GEMINI_PRO: {
                'model': ModelName.GEMINI_PRO,
                'max_tokens': 2500,
                'temperature': 0.6,
            },
        }
        
        return configs.get(model_name, configs[ModelName.CLAUDE_SONNET])


# Example usage
if __name__ == '__main__':
    router = ModelRouter()
    
    test_cases = [
        {
            'question_type': 'decision',
            'domains': ['strategy', 'finance', 'market'],
            'urgency': 'important',
            'complexity': 'complex',
            'emotional_state': 'anxiety'
        },
        {
            'question_type': 'exploration',
            'domains': ['market'],
            'urgency': 'routine',
            'complexity': 'medium',
            'emotional_state': 'exploration'
        },
        {
            'question_type': 'crisis',
            'domains': ['execution'],
            'urgency': 'crisis',
            'complexity': 'complex',
            'emotional_state': 'urgency'
        },
    ]
    
    for case in test_cases:
        result = router.select_model(**case)
        print(f"\nCase: {case['question_type']} - {case['complexity']}")
        print(f"Selected: {result.model_name}")
        print(f"Cost: ${result.estimated_cost:.4f}")
        print(f"Latency: {result.estimated_latency}s")
        print(f"Reasoning: {result.reasoning}")