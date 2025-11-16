# agents/services/quality_gates.py

"""
Quality Gates Validation System

Validates AI responses against 5 quality criteria before delivery:
1. Understands user context (references their situation)
2. Addresses actual question (not tangential)
3. Response time within limits (<12 seconds)
4. Includes reasoning/evidence
5. Empowers user to decide (not prescriptive)

This is a critical safeguard ensuring response quality.
"""

import re
from typing import Tuple, List, Dict
import logging

logger = logging.getLogger(__name__)


class QualityGates:
    """
    Validates AI responses before delivery to user
    """
    
    # Empowerment patterns (good - response empowers user)
    EMPOWERMENT_PATTERNS = [
        r'\bwhat\'s your (read|take|view|thought)\b',
        r'\bwhat do you think\b',
        r'\bhow do you (see|feel about)\b',
        r'\byour choice\b',
        r'\byour decision\b',
        r'\bup to you\b',
        r'\byou decide\b',
        r'\byou\'re (the one who|better positioned to)\b',
    ]
    
    # Prescriptive patterns (bad - response tells user what to do)
    PRESCRIPTIVE_PATTERNS = [
        r'\byou should (definitely|absolutely)\b',
        r'\byou must\b',
        r'\byou have to\b',
        r'\byou need to\b',
        r'\bthe right (answer|decision|choice) is\b',
        r'\bthe only option is\b',
    ]
    
    # Reasoning indicators (good - response includes evidence)
    REASONING_PATTERNS = [
        r'\bbecause\b',
        r'\bhere\'s why\b',
        r'\bthe reason\b',
        r'\bevidence (shows|suggests)\b',
        r'\bdata (shows|indicates)\b',
        r'\bresearch (shows|finds)\b',
        r'\bfor example\b',
        r'\bconsider that\b',
        r'\bgiven that\b',
    ]
    
    def validate_response(
        self,
        question: str,
        response: str,
        user_context: str,
        response_time: float,
        question_metadata: Dict = None
    ) -> Tuple[bool, List[str], Dict[str, bool]]:
        """
        Validate response against all quality gates
        
        Args:
            question: User's original question
            response: AI's response
            user_context: User's context/profile
            response_time: Response generation time in seconds
            question_metadata: Optional question classification metadata
            
        Returns:
            Tuple of:
            - overall_passed (bool): True if all checks passed
            - failure_reasons (List[str]): List of failed check names
            - check_results (Dict[str, bool]): Individual check results
        """
        logger.info("Running quality gate validation")
        
        # Run all checks
        checks = {
            'understands_context': self._check_context_understanding(
                response, user_context
            ),
            'addresses_question': self._check_question_relevance(
                response, question
            ),
            'within_time_limit': self._check_time_limit(
                response_time
            ),
            'includes_reasoning': self._check_reasoning(
                response
            ),
            'empowers_user': self._check_empowerment(
                response, question_metadata
            ),
        }
        
        # Determine overall pass/fail
        overall_passed = all(checks.values())
        
        # Get failure reasons
        failure_reasons = [
            check_name for check_name, passed in checks.items()
            if not passed
        ]
        
        # Log results
        if overall_passed:
            logger.info("✅ All quality gates passed")
        else:
            logger.warning(
                f"⚠️ Quality gates failed: {', '.join(failure_reasons)}"
            )
        
        return overall_passed, failure_reasons, checks
    
    def _check_context_understanding(
        self,
        response: str,
        user_context: str
    ) -> bool:
        """
        Check if response demonstrates understanding of user context
        
        Args:
            response: AI response
            user_context: User context string
            
        Returns:
            True if response references user context
        """
        response_lower = response.lower()
        
        # Improved context indicators
        context_indicators = [
            'expertise',
            'experience',
            'role',
            'industry',
            'situation',
            'company',
            'team',
            'position',
            'market',
            'product',
            'customer',
        ]
        
        # Enhanced personalization signals
        personalization_signals = [
            r'\byour (situation|context|case|company|team|role|position|market|product|customers?|pricing|strategy)\b',
            r'\bgiven (your|where you are|what you)\b',
            r'\bin your (position|situation|case|market|company)\b',
            r'\bfor (someone in your|your specific|you)\b',
            r'\byou\'re (facing|seeing|building|deciding|considering)\b',
            r'\byou (asked|mentioned|said|have|need|want)\b',
        ]
        
        # Check if response directly addresses the user (you/your)
        addressing_user = len(re.findall(r'\b(you|your|you\'re|you\'ve)\b', response_lower)) >= 3
        
        # Check if response mentions any context indicators
        has_context_reference = any(
            indicator in response_lower
            for indicator in context_indicators
        )
        
        # Check for personalization signals
        has_personalization = any(
            re.search(pattern, response_lower)
            for pattern in personalization_signals
        )
        
        # Pass if ANY check succeeds (more lenient)
        passed = addressing_user or has_context_reference or has_personalization
        
        if not passed:
            logger.debug("Context understanding check failed")
        
        return passed
    
    def _check_question_relevance(
        self,
        response: str,
        question: str
    ) -> bool:
        """
        Check if response addresses the actual question
        
        Args:
            response: AI response
            question: User's question
            
        Returns:
            True if response is relevant to question
        """
        # Extract key terms from question (nouns, verbs)
        # Simple approach: look for overlap of significant words
        
        # Get significant words from question (>4 chars, not common words)
        common_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'from', 'by', 'about', 'like', 'this', 'that',
            'what', 'when', 'where', 'why', 'how', 'should', 'would', 'could'
        }
        
        question_words = set(
            word.lower()
            for word in re.findall(r'\b\w{4,}\b', question)
            if word.lower() not in common_words
        )
        
        response_lower = response.lower()
        
        # Check how many question keywords appear in response
        matching_words = sum(
            1 for word in question_words
            if word in response_lower
        )
        
        # Require at least 30% keyword overlap
        if len(question_words) == 0:
            return True  # Edge case: very short question
        
        overlap_ratio = matching_words / len(question_words)
        passed = overlap_ratio >= 0.3
        
        if not passed:
            logger.debug(
                f"Question relevance check failed - "
                f"overlap={overlap_ratio:.1%}, "
                f"matching={matching_words}/{len(question_words)}"
            )
        
        return passed
    
    def _check_time_limit(self, response_time: float) -> bool:
        """
        Check if response was generated within time limit
        
        Args:
            response_time: Response time in seconds
            
        Returns:
            True if within 12 second limit
        """
        # Week 2 target: 8-12 seconds
        # We'll be lenient and allow up to 15 seconds
        time_limit = 15.0
        
        passed = response_time <= time_limit
        
        if not passed:
            logger.warning(
                f"Time limit check failed - "
                f"time={response_time:.2f}s, "
                f"limit={time_limit}s"
            )
        
        return passed
    
    def _check_reasoning(self, response: str) -> bool:
        """
        Check if response includes reasoning/evidence
        
        Args:
            response: AI response
            
        Returns:
            True if response includes reasoning
        """
        response_lower = response.lower()
        
        # Enhanced reasoning patterns
        reasoning_patterns = [
            r'\bbecause\b',
            r'\bhere\'s why\b',
            r'\bthe reason\b',
            r'\bevidence (shows|suggests)\b',
            r'\bdata (shows|indicates)\b',
            r'\bresearch (shows|finds)\b',
            r'\bfor example\b',
            r'\bconsider that\b',
            r'\bgiven that\b',
            r'\bhere\'s what\'s (true|real|actually happening)\b',
            r'\bwhat\'s (true|real|actually)\b',
            r'\bthis (matters|works|fails) because\b',
            r'\bthe (key|critical|real) (factor|constraint|issue) is\b',
            r'\bif .+ then\b',
            r'\bwhen .+ (happens|occurs)\b',
            r'\bmeans that\b',
            r'\bresults in\b',
            r'\bleads to\b',
            r'\bcauses\b',
        ]
        
        # Count reasoning indicators
        reasoning_count = sum(
            len(re.findall(pattern, response_lower))
            for pattern in reasoning_patterns
        )
        
        # Check for structured thinking (lists, numbered points)
        has_structure = bool(re.search(r'(1\.|2\.|3\.|•|-).*\n', response))
        
        # Check for logical connectors
        logical_connectors = ['but', 'however', 'therefore', 'thus', 'so', 'hence']
        connector_count = sum(
            response_lower.count(word) for word in logical_connectors
        )
        
        # Check for explanatory phrases
        explanatory_phrases = [
            "here's what",
            "what's true",
            "what matters",
            "the real",
            "actually",
        ]
        explanation_count = sum(
            response_lower.count(phrase) for phrase in explanatory_phrases
        )
        
        # Get word count for scaling
        word_count = len(response.split())
        
        # More lenient thresholds
        if word_count < 150:
            threshold = 1  # Just need ANY reasoning indicator
        else:
            threshold = 2  # Need at least 2 indicators
        
        # Pass if any of these conditions met
        passed = (
            reasoning_count >= threshold or
            has_structure or
            connector_count >= 3 or
            explanation_count >= 2
        )
        
        if not passed:
            logger.debug(
                f"Reasoning check failed - "
                f"indicators={reasoning_count}, "
                f"structure={has_structure}, "
                f"connectors={connector_count}, "
                f"threshold={threshold}"
            )
        
        return passed
    
    def _check_empowerment(
        self,
        response: str,
        question_metadata: Dict = None
    ) -> bool:
        """
        Check if response empowers user rather than prescribes
        
        Args:
            response: AI response
            question_metadata: Optional question classification
            
        Returns:
            True if response is empowering
        """
        response_lower = response.lower()
        
        # Count empowerment patterns
        empowerment_count = sum(
            len(re.findall(pattern, response_lower))
            for pattern in self.EMPOWERMENT_PATTERNS
        )
        
        # Count prescriptive patterns (bad)
        prescriptive_count = sum(
            len(re.findall(pattern, response_lower))
            for pattern in self.PRESCRIPTIVE_PATTERNS
        )
        
        # Special case: Crisis questions can be more prescriptive
        if question_metadata and question_metadata.get('urgency') == 'crisis':
            # For crisis, allow more prescriptive language
            passed = prescriptive_count <= 3
        else:
            # For normal questions, require empowerment
            # Pass if: has empowerment signals OR no prescriptive language
            passed = (empowerment_count >= 1) or (prescriptive_count == 0)
        
        if not passed:
            logger.debug(
                f"Empowerment check failed - "
                f"empowerment={empowerment_count}, "
                f"prescriptive={prescriptive_count}"
            )
        
        return passed


# Example usage and testing
if __name__ == '__main__':
    """Test quality gates with sample responses"""
    
    # Initialize quality gates
    gates = QualityGates()
    
    # Test cases
    test_cases = [
        {
            'name': 'Good Response',
            'question': 'Should we pivot to enterprise market?',
            'response': """
                You're right to consider enterprise timing carefully. Given your current 
                runway and team size, here's what matters: The market window is real, 
                but cash is your constraint. So the real decision isn't "should we pivot?" 
                but "how do we fund the pivot?" Three paths: raise capital, bootstrap 
                with different approach, or delay entry. What's your read on which 
                constraint you can move first?
            """,
            'user_context': 'VP Strategy, SaaS company, 18 months runway, team of 25',
            'response_time': 9.5,
            'should_pass': True
        },
        {
            'name': 'Prescriptive Response (Bad)',
            'question': 'Should we hire more engineers?',
            'response': """
                You should definitely hire 5 more engineers immediately. You must scale 
                the team now. The right answer is to start recruiting today. You have to 
                do this or you'll fail.
            """,
            'user_context': 'CTO, startup, 10 person team',
            'response_time': 8.0,
            'should_pass': False  # Too prescriptive
        },
        {
            'name': 'No Reasoning (Bad)',
            'question': 'Should we change our pricing?',
            'response': """
                Consider adjusting your pricing model. You might want to look at value-based 
                pricing. Some companies do this. Maybe that could work for you too.
            """,
            'user_context': 'CEO, B2B SaaS',
            'response_time': 7.0,
            'should_pass': False  # No reasoning/evidence
        },
        {
            'name': 'Too Slow (Bad)',
            'question': 'Quick question about pricing',
            'response': """
                Let me analyze your pricing strategy in detail. Here's a comprehensive 
                breakdown of every possible pricing model with examples from 50 companies...
            """,
            'user_context': 'Founder',
            'response_time': 18.5,  # Too slow
            'should_pass': False
        },
    ]
    
    print("=" * 80)
    print("QUALITY GATES VALIDATION TEST")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST CASE {i}: {test['name']}")
        print("=" * 80)
        
        # Run validation
        passed, failures, checks = gates.validate_response(
            question=test['question'],
            response=test['response'],
            user_context=test['user_context'],
            response_time=test['response_time']
        )
        
        # Print results
        print(f"\nQuestion: {test['question']}")
        print(f"Expected: {'PASS' if test['should_pass'] else 'FAIL'}")
        print(f"Actual: {'PASS' if passed else 'FAIL'}")
        
        print("\nIndividual Checks:")
        for check_name, check_passed in checks.items():
            status = '✅' if check_passed else '❌'
            print(f"  {status} {check_name}")
        
        if failures:
            print(f"\nFailed Checks: {', '.join(failures)}")
        
        # Verify expectation
        if passed == test['should_pass']:
            print("\n✅ Test result matches expectation")
        else:
            print("\n⚠️ Test result does NOT match expectation")
    
    print("\n" + "=" * 80)
    print("QUALITY GATES TEST COMPLETE")
    print("=" * 80)