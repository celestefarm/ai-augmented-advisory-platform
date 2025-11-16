import re
from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class ConfidenceMarker:
    """
    Calculates confidence level for AI responses
    """
    
    # Strong evidence indicators
    EVIDENCE_PATTERNS = [
        r'\b(data shows|research finds|studies indicate)\b',
        r'\b(evidence suggests|analysis reveals)\b',
        r'\b(according to|based on|drawing from)\b',
        r'\b(proven|demonstrated|established)\b',
        r'\b(consistently|repeatedly|reliably)\b',
        r'\b(x% of|majority of|most)\b',
    ]
    
    # Hedging language (reduces confidence)
    HEDGING_PATTERNS = [
        r'\b(might|may|could|possibly|perhaps)\b',
        r'\b(seems|appears|suggests|indicates)\b',
        r'\b(likely|probably|potentially)\b',
        r'\b(tend to|generally|typically)\b',
        r'\b(uncertain|unclear|ambiguous)\b',
        r'\b(depending on|it depends)\b',
    ]
    
    # Uncertainty admissions (good but reduces confidence)
    UNCERTAINTY_PATTERNS = [
        r'\b(don\'t know|can\'t say|hard to know)\b',
        r'\b(without (more|additional) (data|information))\b',
        r'\b(would need to (know|understand|see))\b',
        r'\b(missing (information|data|context))\b',
        r'\b(information gaps?|unknowns?)\b',
    ]
    
    # Alternative possibilities mentioned (reduces confidence)
    ALTERNATIVES_PATTERNS = [
        r'\b(alternatively|on the other hand|however)\b',
        r'\b(could also|might also|may also)\b',
        r'\b(another (option|possibility|approach))\b',
        r'\b(multiple (paths|options|possibilities))\b',
    ]
    
    # Confidence level thresholds
    CONFIDENCE_LEVELS = {
        'high': (85, 100),
        'medium': (65, 84),
        'low': (50, 64),
        'speculative': (30, 49),
    }
    
    def calculate_confidence(
        self,
        response: str,
        question_complexity: str,
        model_used: str,
        response_time: float = None,
        question_type: str = None
    ) -> Tuple[str, int, str]:
        """
        Calculate confidence level for response
        
        Args:
            response: AI response text
            question_complexity: 'simple' | 'medium' | 'complex'
            model_used: Model name (e.g., 'claude-sonnet-4-20250514')
            response_time: Optional response time in seconds
            question_type: Optional question type ('decision', 'exploration', etc.)
            
        Returns:
            Tuple of (level, percentage, explanation):
            - level: 'high' | 'medium' | 'low' | 'speculative'
            - percentage: Confidence percentage (0-100)
            - explanation: Human-readable explanation
        """
        logger.info(f"Calculating confidence for response (complexity={question_complexity})")
        
        # Start with base confidence based on question complexity
        base_confidence = self._get_base_confidence(question_complexity)
        
        # Adjust for evidence quality
        evidence_adjustment = self._calculate_evidence_adjustment(response)
        
        # Adjust for hedging
        hedging_adjustment = self._calculate_hedging_adjustment(response)
        
        # Adjust for uncertainty admissions
        uncertainty_adjustment = self._calculate_uncertainty_adjustment(response)
        
        # Adjust for alternatives mentioned
        alternatives_adjustment = self._calculate_alternatives_adjustment(response)
        
        # Adjust for model capabilities
        model_adjustment = self._get_model_adjustment(model_used, question_complexity)
        
        # Adjust for question type
        type_adjustment = self._get_type_adjustment(question_type)
        
        # Calculate final confidence
        confidence_percentage = base_confidence
        confidence_percentage += evidence_adjustment
        confidence_percentage += hedging_adjustment
        confidence_percentage += uncertainty_adjustment
        confidence_percentage += alternatives_adjustment
        confidence_percentage += model_adjustment
        confidence_percentage += type_adjustment
        
        # Clamp to 30-100 range
        confidence_percentage = max(30, min(100, confidence_percentage))
        
        # Determine level
        level = self._get_confidence_level(confidence_percentage)
        
        # Generate explanation
        explanation = self._generate_explanation(
            confidence_percentage,
            level,
            evidence_adjustment,
            hedging_adjustment,
            uncertainty_adjustment,
            question_complexity,
            model_used
        )
        
        logger.info(
            f"Confidence calculated: {level.upper()} ({confidence_percentage}%)"
        )
        
        return level, confidence_percentage, explanation
    
    def _get_base_confidence(self, complexity: str) -> int:
        """
        Get base confidence based on question complexity
        
        Args:
            complexity: 'simple' | 'medium' | 'complex'
            
        Returns:
            Base confidence percentage
        """
        base_map = {
            'simple': 75,    # Simple questions easier to answer confidently
            'medium': 65,    # Medium questions have more uncertainty
            'complex': 55,   # Complex questions harder to be confident about
        }
        
        return base_map.get(complexity, 65)
    
    def _calculate_evidence_adjustment(self, response: str) -> int:
        """
        Calculate confidence adjustment based on evidence quality
        
        Args:
            response: AI response
            
        Returns:
            Confidence adjustment (-10 to +20)
        """
        response_lower = response.lower()
        
        # Count evidence indicators
        evidence_count = sum(
            len(re.findall(pattern, response_lower))
            for pattern in self.EVIDENCE_PATTERNS
        )
        
        # More evidence = higher confidence
        # 0 evidence: -5
        # 1-2 evidence: +0
        # 3-4 evidence: +10
        # 5+ evidence: +15
        
        if evidence_count == 0:
            return -5
        elif evidence_count <= 2:
            return 0
        elif evidence_count <= 4:
            return 10
        else:
            return 15
    
    def _calculate_hedging_adjustment(self, response: str) -> int:
        """
        Calculate confidence adjustment based on hedging language
        
        Args:
            response: AI response
            
        Returns:
            Confidence adjustment (-20 to 0)
        """
        response_lower = response.lower()
        
        # Count hedge words
        hedge_count = sum(
            len(re.findall(pattern, response_lower))
            for pattern in self.HEDGING_PATTERNS
        )
        
        # Get response word count for normalization
        word_count = len(response.split())
        hedge_ratio = hedge_count / max(word_count, 1) * 100
        
        # High hedge ratio = lower confidence
        # <2% hedging: 0
        # 2-5% hedging: -5
        # 5-10% hedging: -10
        # >10% hedging: -15
        
        if hedge_ratio < 2:
            return 0
        elif hedge_ratio < 5:
            return -5
        elif hedge_ratio < 10:
            return -10
        else:
            return -15
    
    def _calculate_uncertainty_adjustment(self, response: str) -> int:
        """
        Calculate adjustment based on uncertainty admissions
        
        Args:
            response: AI response
            
        Returns:
            Confidence adjustment (-15 to +5)
        """
        response_lower = response.lower()
        
        # Count uncertainty admissions
        uncertainty_count = sum(
            len(re.findall(pattern, response_lower))
            for pattern in self.UNCERTAINTY_PATTERNS
        )
        
        # Admitting uncertainty is honest but reduces confidence
        # However, complete absence might indicate overconfidence
        # 0 admissions: -5 (possible overconfidence)
        # 1 admission: +5 (honest transparency)
        # 2+ admissions: -10 (significant uncertainty)
        
        if uncertainty_count == 0:
            return -5
        elif uncertainty_count == 1:
            return +5  # Reward honest transparency
        else:
            return -10
    
    def _calculate_alternatives_adjustment(self, response: str) -> int:
        """
        Calculate adjustment based on alternatives mentioned
        
        Args:
            response: AI response
            
        Returns:
            Confidence adjustment (-10 to 0)
        """
        response_lower = response.lower()
        
        # Count alternative possibilities
        alternatives_count = sum(
            len(re.findall(pattern, response_lower))
            for pattern in self.ALTERNATIVES_PATTERNS
        )
        
        # More alternatives = less certainty about one path
        # 0-1 alternatives: 0
        # 2-3 alternatives: -5
        # 4+ alternatives: -10
        
        if alternatives_count <= 1:
            return 0
        elif alternatives_count <= 3:
            return -5
        else:
            return -10
    
    def _get_model_adjustment(self, model: str, complexity: str) -> int:
        """
        Adjust confidence based on model capabilities
        
        Args:
            model: Model name
            complexity: Question complexity
            
        Returns:
            Confidence adjustment (-5 to +10)
        """
        # Model capability map
        model_strength = {
            'claude-opus-4': 10,      # Highest capability
            'claude-sonnet-4': 5,     # Strong capability
            'claude-3-5-sonnet': 5,   # Strong capability
            'gemini-2.0-pro': 3,      # Good capability
            'gemini-2.0-flash': -5,   # Fast but lower capability
        }
        
        # Get base model strength
        strength = 0
        for model_key, value in model_strength.items():
            if model_key in model:
                strength = value
                break
        
        # Adjust for complexity
        if complexity == 'complex':
            # Complex questions benefit more from capable models
            strength = int(strength * 1.5)
        
        return max(-5, min(10, strength))
    
    def _get_type_adjustment(self, question_type: str) -> int:
        """
        Adjust confidence based on question type
        
        Args:
            question_type: Type of question
            
        Returns:
            Confidence adjustment (-5 to +5)
        """
        # Some question types are inherently more uncertain
        type_map = {
            'exploration': -5,    # Exploratory questions are uncertain
            'validation': +5,     # Validation can be more definitive
            'decision': 0,        # Neutral
            'crisis': +5,         # Crisis needs decisiveness
        }
        
        return type_map.get(question_type, 0)
    
    def _get_confidence_level(self, percentage: int) -> str:
        """
        Get confidence level from percentage
        
        Args:
            percentage: Confidence percentage
            
        Returns:
            Confidence level string
        """
        for level, (low, high) in self.CONFIDENCE_LEVELS.items():
            if low <= percentage <= high:
                return level
        
        return 'medium'  # Default
    
    def _generate_explanation(
        self,
        confidence: int,
        level: str,
        evidence_adj: int,
        hedging_adj: int,
        uncertainty_adj: int,
        complexity: str,
        model: str
    ) -> str:
        """
        Generate human-readable confidence explanation
        
        Args:
            confidence: Final confidence percentage
            level: Confidence level
            evidence_adj: Evidence adjustment
            hedging_adj: Hedging adjustment
            uncertainty_adj: Uncertainty adjustment
            complexity: Question complexity
            model: Model used
            
        Returns:
            Explanation string
        """
        explanations = []
        
        # Level-based opening
        level_openings = {
            'high': "High confidence in this analysis.",
            'medium': "Moderate confidence - good evidence with some uncertainty.",
            'low': "Lower confidence - limited evidence or multiple unknowns.",
            'speculative': "Speculative analysis - significant uncertainty."
        }
        
        explanations.append(level_openings.get(level, ""))
        
        # Evidence quality
        if evidence_adj > 5:
            explanations.append("Strong evidence cited.")
        elif evidence_adj < 0:
            explanations.append("Limited evidence available.")
        
        # Hedging
        if hedging_adj < -10:
            explanations.append("Significant hedging due to uncertainty.")
        
        # Uncertainty
        if uncertainty_adj == 5:
            explanations.append("Honest about information gaps.")
        elif uncertainty_adj < 0:
            explanations.append("Multiple unknowns acknowledged.")
        
        # Complexity
        if complexity == 'complex':
            explanations.append("Complex question with multiple factors.")
        
        return " ".join(explanations)


# Example usage and testing
if __name__ == '__main__':
    """Test confidence marker with sample responses"""
    
    # Initialize marker
    marker = ConfidenceMarker()
    
    # Test cases
    test_cases = [
        {
            'name': 'High Confidence Response',
            'response': """
                Based on analysis of 50+ similar companies, the data clearly shows 
                that enterprise pivots succeed when: 1) You have 18+ months runway 
                (you have 18), 2) You have proven product-market fit in SMB (you do), 
                and 3) You can staff a dedicated enterprise team (you can). The evidence 
                consistently demonstrates these factors drive success.
            """,
            'complexity': 'medium',
            'model': 'claude-sonnet-4-20250514',
            'expected_level': 'high'
        },
        {
            'name': 'Medium Confidence Response',
            'response': """
                You're probably right to consider this, though it depends on several 
                factors. The market data suggests this could work, but there are some 
                unknowns about your specific situation. Generally, companies in your 
                position tend to succeed with this approach, though results may vary.
            """,
            'complexity': 'medium',
            'model': 'claude-sonnet-4-20250514',
            'expected_level': 'medium'
        },
        {
            'name': 'Low Confidence Response',
            'response': """
                This is uncertain territory. It might work, or it could also fail. 
                There are multiple possibilities here. Alternatively, you could try 
                a different approach. Without more information about your specific 
                context, it's hard to say. Several unknowns remain.
            """,
            'complexity': 'complex',
            'model': 'claude-sonnet-4-20250514',
            'expected_level': 'low'
        },
        {
            'name': 'Speculative Response',
            'response': """
                Perhaps this could work, though it may not. It seems possible, but 
                possibly unlikely. Depending on various factors, this might succeed 
                or might fail. It's unclear which approach would be better. The answer 
                is ambiguous and highly dependent on unknowns.
            """,
            'complexity': 'complex',
            'model': 'gemini-2.0-flash-exp',
            'expected_level': 'speculative'
        },
    ]
    
    print("=" * 80)
    print("CONFIDENCE MARKER TEST")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST CASE {i}: {test['name']}")
        print("=" * 80)
        
        # Calculate confidence
        level, percentage, explanation = marker.calculate_confidence(
            response=test['response'],
            question_complexity=test['complexity'],
            model_used=test['model']
        )
        
        # Print results
        print(f"\nComplexity: {test['complexity']}")
        print(f"Model: {test['model']}")
        print(f"\nExpected Level: {test['expected_level']}")
        print(f"Actual Level: {level}")
        print(f"Confidence: {percentage}%")
        print(f"\nExplanation: {explanation}")
        
        # Verify expectation
        if level == test['expected_level']:
            print("\n✅ Confidence level matches expectation")
        else:
            print(f"\n⚠️ Expected {test['expected_level']}, got {level}")
    
    print("\n" + "=" * 80)
    print("CONFIDENCE MARKER TEST COMPLETE")
    print("=" * 80)