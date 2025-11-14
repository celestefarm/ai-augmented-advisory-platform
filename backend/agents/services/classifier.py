# agents/services/classifier.py

"""
Question Classification Service

Classifies user questions across multiple dimensions:
- Type: decision | validation | exploration | crisis
- Domain: market | strategy | finance | people | execution (can be multiple)
- Urgency: routine | important | urgent | crisis
- Complexity: simple | medium | complex

Uses combination of:
1. Keyword pattern matching (fast)
2. NLP sentiment/urgency analysis
3. Question structure analysis
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class QuestionMetadata:
    """Container for question classification results"""
    question_type: str
    domains: List[str]
    urgency: str
    complexity: str
    confidence_score: float
    detected_patterns: List[str]


class QuestionClassifier:
    """
    Classifies questions using multi-dimensional analysis
    """
    
    # Question type patterns
    TYPE_PATTERNS = {
        'decision': [
            r'\bshould (i|we)\b',
            r'\bwhich (option|choice|path)\b',
            r'\b(choose|decide|pick)\b',
            r'\bbetter to\b',
            r'\bworth (it|doing)\b',
            r'\bmake (a|the) decision\b',
        ],
        'validation': [
            r'\bis (this|it) (correct|right|good)\b',
            r'\bam i (right|wrong|correct)\b',
            r'\bdoes (this|it) make sense\b',
            r'\bwhat do you think (about|of)\b',
            r'\b(validate|verify|confirm)\b',
            r'\bgood (idea|approach|strategy)\b',
        ],
        'exploration': [
            r'\bwhat (if|are|about)\b',
            r'\bhow (can|do|does|would)\b',
            r'\btell me (about|more)\b',
            r'\bexplain\b',
            r'\bhelp me understand\b',
            r'\bcurious about\b',
            r'\bwhat are the options\b',
        ],
        'crisis': [
            r'\bemergency\b',
            r'\b(urgent|asap|immediately)\b',
            r'\bcrisis\b',
            r'\bfailing (fast|quickly)\b',
            r'\bmust (decide|act) (now|today)\b',
            r'\bdeadline (is|in)\b',
        ],
    }
    
    # Domain patterns
    DOMAIN_PATTERNS = {
        'market': [
            r'\b(market|competitor|customer|demand)\b',
            r'\b(competitive|competition)\b',
            r'\b(market share|positioning)\b',
            r'\b(customer needs|buyer)\b',
            r'\b(industry trends|market timing)\b',
        ],
        'strategy': [
            r'\b(strategy|strategic|pivot)\b',
            r'\b(long.?term|vision|mission)\b',
            r'\b(differentiation|advantage)\b',
            r'\b(product.?market fit)\b',
            r'\b(positioning|moat)\b',
            r'\b(business model|value prop)\b',
        ],
        'finance': [
            r'\b(revenue|profit|margin|cash)\b',
            r'\b(runway|burn rate|budget)\b',
            r'\b(pricing|cost|roi)\b',
            r'\b(funding|investment|raise)\b',
            r'\b(financial|finances)\b',
            r'\b(valuation|cap table)\b',
        ],
        'people': [
            r'\b(team|hire|hiring|staff)\b',
            r'\b(employee|culture|org)\b',
            r'\b(fire|firing|let go)\b',
            r'\b(performance|manager)\b',
            r'\b(office politics|resistance)\b',
            r'\b(talent|skills|capability)\b',
        ],
        'execution': [
            r'\b(execute|launch|ship|deliver)\b',
            r'\b(timeline|deadline|schedule)\b',
            r'\b(implementation|rollout)\b',
            r'\b(project|task|milestone)\b',
            r'\b(resources|bandwidth)\b',
            r'\b(feasible|realistic|doable)\b',
        ],
    }
    
    # Urgency signal words
    URGENCY_SIGNALS = {
        'crisis': ['emergency', 'crisis', 'critical', 'breaking', 'failing'],
        'urgent': ['urgent', 'asap', 'immediately', 'now', 'today', 'must', 'need to act'],
        'important': ['important', 'significant', 'key', 'critical decision', 'major'],
        'routine': ['considering', 'thinking about', 'wondering', 'curious'],
    }
    
    # Complexity indicators
    COMPLEXITY_INDICATORS = {
        'complex': [
            r'\bmultiple (options|factors|stakeholders)\b',
            r'\b(tradeoff|trade.?off)\b',
            r'\bcomplex\b',
            r'\b(interconnected|dependencies)\b',
            r'\b(long.?term implications)\b',
        ],
        'medium': [
            r'\b(several|few|some) (factors|considerations)\b',
            r'\b(pros and cons|advantages and disadvantages)\b',
            r'\b(balanced|weigh)\b',
        ],
    }
    
    def classify(self, question: str) -> QuestionMetadata:
        """
        Main classification method
        
        Args:
            question: User question text
            
        Returns:
            QuestionMetadata with all classifications
        """
        question_lower = question.lower()
        detected_patterns = []
        
        # Classify type
        question_type, type_confidence, type_patterns = self._classify_type(question_lower)
        detected_patterns.extend(type_patterns)
        
        # Classify domains (can be multiple)
        domains, domain_patterns = self._classify_domains(question_lower)
        detected_patterns.extend(domain_patterns)
        
        # Classify urgency
        urgency, urgency_patterns = self._classify_urgency(question_lower)
        detected_patterns.extend(urgency_patterns)
        
        # Classify complexity
        complexity, complexity_patterns = self._classify_complexity(question, question_lower)
        detected_patterns.extend(complexity_patterns)
        
        # Calculate overall confidence
        confidence_score = self._calculate_confidence(
            type_confidence,
            len(domains),
            len(detected_patterns)
        )
        
        return QuestionMetadata(
            question_type=question_type,
            domains=domains,
            urgency=urgency,
            complexity=complexity,
            confidence_score=confidence_score,
            detected_patterns=list(set(detected_patterns))  # Remove duplicates
        )
    
    def _classify_type(self, question: str) -> Tuple[str, float, List[str]]:
        """
        Classify question type
        
        Returns:
            (type, confidence, detected_patterns)
        """
        type_scores = {}
        detected_patterns = []
        
        for qtype, patterns in self.TYPE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, question):
                    score += 1
                    detected_patterns.append(f"type:{qtype}")
            type_scores[qtype] = score
        
        # Get highest scoring type
        if not type_scores or max(type_scores.values()) == 0:
            # Default to exploration if no clear match
            return 'exploration', 0.5, []
        
        best_type = max(type_scores, key=type_scores.get)
        confidence = min(type_scores[best_type] / 3.0, 1.0)  # Normalize to 0-1
        
        return best_type, confidence, detected_patterns
    
    def _classify_domains(self, question: str) -> Tuple[List[str], List[str]]:
        """
        Classify domains (can be multiple)
        
        Returns:
            (domains_list, detected_patterns)
        """
        domain_scores = {}
        detected_patterns = []
        
        for domain, patterns in self.DOMAIN_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, question):
                    score += 1
                    detected_patterns.append(f"domain:{domain}")
            if score > 0:
                domain_scores[domain] = score
        
        # Return domains with score > 0, sorted by score
        if not domain_scores:
            return ['strategy'], []  # Default to strategy
        
        sorted_domains = sorted(domain_scores.keys(), key=lambda x: domain_scores[x], reverse=True)
        
        return sorted_domains, detected_patterns
    
    def _classify_urgency(self, question: str) -> Tuple[str, List[str]]:
        """
        Classify urgency level
        
        Returns:
            (urgency_level, detected_patterns)
        """
        detected_patterns = []
        
        # Check for urgency signals in order of priority
        for level in ['crisis', 'urgent', 'important', 'routine']:
            for signal in self.URGENCY_SIGNALS[level]:
                if signal in question:
                    detected_patterns.append(f"urgency:{level}:{signal}")
                    return level, detected_patterns
        
        # Default to routine
        return 'routine', []
    
    def _classify_complexity(self, original_question: str, question_lower: str) -> Tuple[str, List[str]]:
        """
        Classify complexity based on:
        - Question length
        - Multiple parts/questions
        - Complexity indicators
        
        Returns:
            (complexity_level, detected_patterns)
        """
        detected_patterns = []
        
        # Check for explicit complexity indicators
        for level, patterns in self.COMPLEXITY_INDICATORS.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    detected_patterns.append(f"complexity:{level}")
                    return level, detected_patterns
        
        # Analyze question structure
        
        # Count sentences/questions
        question_marks = original_question.count('?')
        sentences = len(re.split(r'[.!?]+', original_question))
        
        # Check word count
        word_count = len(original_question.split())
        
        # Complexity rules
        if question_marks > 2 or sentences > 3 or word_count > 100:
            detected_patterns.append("complexity:multi-part")
            return 'complex', detected_patterns
        elif word_count > 50 or sentences > 2:
            detected_patterns.append("complexity:moderate-length")
            return 'medium', detected_patterns
        else:
            detected_patterns.append("complexity:simple")
            return 'simple', detected_patterns
    
    def _calculate_confidence(
        self,
        type_confidence: float,
        domain_count: int,
        pattern_count: int
    ) -> float:
        """
        Calculate overall classification confidence
        
        Args:
            type_confidence: Confidence in type classification (0-1)
            domain_count: Number of domains detected
            pattern_count: Total patterns detected
            
        Returns:
            Overall confidence score (0-1)
        """
        # Start with type confidence
        confidence = type_confidence * 0.5
        
        # Add domain confidence (having domains increases confidence)
        domain_confidence = min(domain_count / 3.0, 1.0) * 0.3
        confidence += domain_confidence
        
        # Add pattern confidence (more patterns = more confidence)
        pattern_confidence = min(pattern_count / 10.0, 1.0) * 0.2
        confidence += pattern_confidence
        
        return min(confidence, 1.0)


# Example usage
if __name__ == '__main__':
    classifier = QuestionClassifier()
    
    test_questions = [
        # Simple test
        "Should we pivot to enterprise market?",
        
        # Complex crisis scenario
        """URGENT: Our Series B lead investor just pulled out 48 hours before closing, 
        we have 6 weeks of runway left, our VP of Engineering threatened to quit if 
        we don't raise his equity from 2% to 5%, our biggest customer (40% of revenue) 
        is demanding we build a feature that would take 4 months but they need it in 6 weeks 
        or they'll churn, and our competitor just announced they raised $50M. 
        What should I prioritize first?""",
        
        # Co-founder dilemma
        """Should I fire my co-founder who's also my best friend? He's underperforming 
        (missing deadlines, not coding much), owns 40% equity which blocks future fundraising, 
        the team privately complained about his leadership, but he's been loyal for 3 years, 
        his wife just had a baby, and I'm worried about the optics of founder drama 
        scaring off investors.""",
    ]
    
    for q in test_questions:
        result = classifier.classify(q)
        print(f"\nQuestion: {q}")
        print(f"Type: {result.question_type}")
        print(f"Domains: {result.domains}")
        print(f"Urgency: {result.urgency}")
        print(f"Complexity: {result.complexity}")
        print(f"Confidence: {result.confidence_score:.2f}")
        print(f"Patterns: {result.detected_patterns[:3]}")