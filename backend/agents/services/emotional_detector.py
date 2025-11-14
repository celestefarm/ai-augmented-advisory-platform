# agents/services/emotional_detector.py

"""
Emotional State Detection Service

Detects user's emotional state from language patterns:
- Anxiety: "What if...", "risk", "but..."
- Confidence: "I know...", "I think..."
- Uncertainty: "Maybe...", "Could..."
- Urgency: "Now", "ASAP", "Must..."
- Exploration: "Curious about...", "Options..."

Adjusts response tone accordingly:
- Anxiety → Validate first, then reframe
- Confidence → Challenge gently
- Uncertainty → Validate instinct, add clarity
- Urgency → Be direct, cut through noise
- Exploration → Deepen thinking
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class EmotionalStateResult:
    """Container for emotional state detection results"""
    state: str
    confidence_score: float
    detected_patterns: List[str]
    tone_adjustment: Dict[str, str]


class EmotionalStateDetector:
    """
    Detects emotional state from language patterns
    """
    
    # Emotional state patterns with their linguistic signals
    STATE_PATTERNS = {
        'anxiety': {
            'patterns': [
                r'\bwhat if\b',
                r'\b(worry|worried|concern|concerned)\b',
                r'\b(risk|risky|dangerous)\b',
                r'\bbut what (if|about)\b',
                r'\bafraid\b',
                r'\b(scared|fear|nervous)\b',
                r'\b(hesitant|uncertain)\b',
                r'\bmight (fail|go wrong)\b',
                r'\b(worst case|downside)\b',
                r'\bcan\'t afford\b',
            ],
            'tone_adjustment': {
                'approach': 'validate_then_reframe',
                'opening': 'acknowledge_concern',
                'style': 'reassuring_but_realistic',
                'structure': 'validate → provide_context → reframe_positively',
            }
        },
        'confidence': {
            'patterns': [
                r'\bi (know|believe|think) (that|this)\b',
                r'\b(certain|sure|convinced)\b',
                r'\bconfident\b',
                r'\b(clearly|obviously|definitely)\b',
                r'\bno doubt\b',
                r'\bwe should (definitely|absolutely)\b',
                r'\bmy (gut|instinct) says\b',
            ],
            'tone_adjustment': {
                'approach': 'challenge_gently',
                'opening': 'acknowledge_strength',
                'style': 'respectful_pushback',
                'structure': 'validate_thinking → surface_blind_spots → expand_perspective',
            }
        },
        'uncertainty': {
            'patterns': [
                r'\b(maybe|perhaps|possibly)\b',
                r'\b(not sure|unsure)\b',
                r'\bcould (it be|this be)\b',
                r'\bmight\b',
                r'\bdon\'t know (if|whether)\b',
                r'\b(confused|unclear)\b',
                r'\b(torn between|can\'t decide)\b',
                r'\bwhat do you think\b',
            ],
            'tone_adjustment': {
                'approach': 'validate_and_clarify',
                'opening': 'trust_instinct',
                'style': 'clarifying_and_empowering',
                'structure': 'validate_intuition → add_clarity → provide_framework',
            }
        },
        'urgency': {
            'patterns': [
                r'\b(urgent|asap|immediately|now)\b',
                r'\b(must|need to|have to) (decide|act|move)\b',
                r'\btoday\b',
                r'\b(deadline|time.?sensitive)\b',
                r'\bquickly\b',
                r'\bpress(ing|ure)\b',
                r'\bcan\'t wait\b',
                r'\bwindow (is|closing)\b',
            ],
            'tone_adjustment': {
                'approach': 'direct_and_actionable',
                'opening': 'cut_through_noise',
                'style': 'crisp_and_decisive',
                'structure': 'key_constraint → immediate_action → what_to_delay',
            }
        },
        'exploration': {
            'patterns': [
                r'\bcurious (about|to know)\b',
                r'\bwhat are the options\b',
                r'\bexploring\b',
                r'\bthinking about\b',
                r'\bconsidering\b',
                r'\bwondering\b',
                r'\bwhat if we\b',
                r'\bhow (could|would|might) we\b',
                r'\b(brainstorm|ideate)\b',
            ],
            'tone_adjustment': {
                'approach': 'deepen_thinking',
                'opening': 'expand_curiosity',
                'style': 'exploratory_and_expansive',
                'structure': 'surface_options → explore_implications → push_thinking',
            }
        },
    }
    
    # Intensity modifiers (make emotional state stronger)
    INTENSITY_MODIFIERS = [
        r'\breally\b',
        r'\bvery\b',
        r'\bextremely\b',
        r'\bseriously\b',
        r'\bdeeply\b',
        r'\bquite\b',
        r'!+',  # Multiple exclamation marks
        r'\b(all caps|CAPS)\b',
    ]
    
    # Hedge words (make emotional state weaker)
    HEDGE_WORDS = [
        r'\bkind of\b',
        r'\bsort of\b',
        r'\ba bit\b',
        r'\ba little\b',
        r'\bsomewhat\b',
    ]
    
    def detect(self, text: str) -> EmotionalStateResult:
        """
        Main detection method
        
        Args:
            text: User input text
            
        Returns:
            EmotionalStateResult with detected state and adjustments
        """
        text_lower = text.lower()
        
        # Score each emotional state
        state_scores = {}
        detected_patterns = {}
        
        for state, config in self.STATE_PATTERNS.items():
            score, patterns = self._score_state(text_lower, config['patterns'])
            state_scores[state] = score
            if patterns:
                detected_patterns[state] = patterns
        
        # Get dominant emotional state
        if not state_scores or max(state_scores.values()) == 0:
            # Default to exploration if no clear signals
            return EmotionalStateResult(
                state='exploration',
                confidence_score=0.3,
                detected_patterns=[],
                tone_adjustment=self.STATE_PATTERNS['exploration']['tone_adjustment']
            )
        
        dominant_state = max(state_scores, key=state_scores.get)
        base_score = state_scores[dominant_state]
        
        # Adjust confidence based on intensity and hedging
        intensity_factor = self._calculate_intensity(text_lower)
        hedge_factor = self._calculate_hedging(text_lower)
        
        # Calculate final confidence
        confidence = self._calculate_confidence(
            base_score,
            intensity_factor,
            hedge_factor
        )
        
        return EmotionalStateResult(
            state=dominant_state,
            confidence_score=confidence,
            detected_patterns=detected_patterns.get(dominant_state, []),
            tone_adjustment=self.STATE_PATTERNS[dominant_state]['tone_adjustment']
        )
    
    def _score_state(self, text: str, patterns: List[str]) -> Tuple[float, List[str]]:
        """
        Score a specific emotional state
        
        Args:
            text: Input text (lowercased)
            patterns: Regex patterns for this state
            
        Returns:
            (score, detected_pattern_strings)
        """
        score = 0
        detected = []
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                score += len(matches)
                detected.extend(matches)
        
        return score, detected
    
    def _calculate_intensity(self, text: str) -> float:
        """
        Calculate intensity factor from modifiers
        
        Returns:
            Multiplier (1.0 = normal, >1.0 = more intense)
        """
        intensity = 1.0
        
        for modifier in self.INTENSITY_MODIFIERS:
            matches = len(re.findall(modifier, text))
            intensity += matches * 0.2  # Each modifier adds 20%
        
        return min(intensity, 2.0)  # Cap at 2x
    
    def _calculate_hedging(self, text: str) -> float:
        """
        Calculate hedge factor
        
        Returns:
            Multiplier (1.0 = normal, <1.0 = more hedged/uncertain)
        """
        hedge = 1.0
        
        for hedge_word in self.HEDGE_WORDS:
            matches = len(re.findall(hedge_word, text))
            hedge -= matches * 0.15  # Each hedge reduces by 15%
        
        return max(hedge, 0.5)  # Floor at 0.5x
    
    def _calculate_confidence(
        self,
        base_score: float,
        intensity: float,
        hedge: float
    ) -> float:
        """
        Calculate overall confidence in detection
        
        Args:
            base_score: Raw pattern match count
            intensity: Intensity multiplier
            hedge: Hedge multiplier
            
        Returns:
            Confidence score (0-1)
        """
        # Normalize base score
        normalized_score = min(base_score / 5.0, 1.0)
        
        # Apply intensity and hedging
        adjusted_score = normalized_score * intensity * hedge
        
        return min(adjusted_score, 1.0)
    
    def get_response_guidance(self, state: str) -> Dict[str, str]:
        """
        Get response guidance for a given emotional state
        
        Args:
            state: Emotional state
            
        Returns:
            Dict with guidance on how to respond
        """
        return self.STATE_PATTERNS.get(state, {}).get('tone_adjustment', {})
    
    def format_tone_instructions(self, tone_adjustment: Dict[str, str]) -> str:
        """
        Format tone adjustment into instructions for AI prompt
        
        Args:
            tone_adjustment: Tone adjustment dict
            
        Returns:
            Formatted string for prompt injection
        """
        instructions = []
        
        approach = tone_adjustment.get('approach', '')
        opening = tone_adjustment.get('opening', '')
        style = tone_adjustment.get('style', '')
        structure = tone_adjustment.get('structure', '')
        
        instructions.append(f"Approach: {approach}")
        instructions.append(f"Opening: {opening}")
        instructions.append(f"Style: {style}")
        instructions.append(f"Structure: {structure}")
        
        return "\n".join(instructions)


# Example usage
if __name__ == '__main__':
    detector = EmotionalStateDetector()
    
    test_cases = [
        "What if this decision fails? I'm worried about the downside risk.",
        "I know we should pivot to enterprise. It's clearly the right move.",
        "Maybe we should consider raising prices? I'm not sure though.",
        "URGENT: Competitor launched today, we must respond now!",
        "I'm curious about exploring different market segments. What are our options?",
    ]
    
    for text in test_cases:
        result = detector.detect(text)
        print(f"\nText: {text}")
        print(f"State: {result.state}")
        print(f"Confidence: {result.confidence_score:.2f}")
        print(f"Patterns: {result.detected_patterns[:3]}")
        print(f"Tone: {result.tone_adjustment['approach']}")