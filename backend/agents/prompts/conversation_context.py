# agents/services/conversation_context.py

"""
Conversation Context Manager

Tracks user preferences within a conversation:
- Brevity requests ("be brief", "make it shorter")
- Tone preferences ("more casual", "more formal")
- Previous questions for context

This gives Claude memory of what the user wants in THIS conversation.
"""

from typing import Dict, List, Optional
import re


class ConversationContext:
    """
    Manages conversation-level context and preferences
    """
    
    # Brevity signals
    BREVITY_PATTERNS = [
        r'\b(brief|short|concise|quick|tl;?dr)\b',
        r'\b(less words?|fewer words?)\b',
        r'\b(cut (it|this) short)\b',
        r'\b(straight to the point)\b',
        r'\b(bottom line|key point)\b',
        r'\bmake (it|this|the answer) (more )?(brief|short|concise)\b',
    ]
    
    # Expansion signals
    EXPANSION_PATTERNS = [
        r'\b(more detail|elaborate|expand)\b',
        r'\b(tell me more|explain more)\b',
        r'\b(go deeper|dig deeper)\b',
    ]
    
    @staticmethod
    def detect_brevity_request(question: str) -> bool:
        """
        Detect if user is asking for brevity
        
        Args:
            question: User's question text
            
        Returns:
            True if user wants brief response
        """
        question_lower = question.lower()
        
        return any(
            re.search(pattern, question_lower)
            for pattern in ConversationContext.BREVITY_PATTERNS
        )
    
    @staticmethod
    def detect_expansion_request(question: str) -> bool:
        """
        Detect if user wants more detail
        
        Args:
            question: User's question text
            
        Returns:
            True if user wants expanded response
        """
        question_lower = question.lower()
        
        return any(
            re.search(pattern, question_lower)
            for pattern in ConversationContext.EXPANSION_PATTERNS
        )
    
    @staticmethod
    def build_conversation_memory(
        messages: List[Dict],
        current_question: str
    ) -> Dict[str, any]:
        """
        Build conversation memory from message history
        
        Args:
            messages: List of previous messages
            current_question: Current user question
            
        Returns:
            Dict with conversation preferences
        """
        # Check current question for preferences
        wants_brevity = ConversationContext.detect_brevity_request(current_question)
        wants_expansion = ConversationContext.detect_expansion_request(current_question)
        
        # Check previous messages for patterns
        brevity_requests = 0
        expansion_requests = 0
        
        for msg in messages[-5:]:  # Last 5 messages
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                if ConversationContext.detect_brevity_request(content):
                    brevity_requests += 1
                if ConversationContext.detect_expansion_request(content):
                    expansion_requests += 1
        
        # Determine overall preference
        if wants_brevity or brevity_requests > expansion_requests:
            response_style = 'brief'
            max_words = 150  # ~2-3 paragraphs
        elif wants_expansion or expansion_requests > brevity_requests:
            response_style = 'detailed'
            max_words = 500
        else:
            response_style = 'balanced'
            max_words = 300
        
        return {
            'response_style': response_style,
            'max_words': max_words,
            'wants_brevity': wants_brevity,
            'wants_expansion': wants_expansion,
            'brevity_signal_count': brevity_requests,
            'expansion_signal_count': expansion_requests
        }
    
    @staticmethod
    def format_style_instruction(
        conversation_memory: Dict,
        question_type: str
    ) -> str:
        """
        Generate style instruction for system prompt
        
        Args:
            conversation_memory: Conversation preferences
            question_type: Type of question
            
        Returns:
            Style instruction string
        """
        style = conversation_memory['response_style']
        max_words = conversation_memory['max_words']
        wants_brevity = conversation_memory['wants_brevity']
        
        if wants_brevity:
            return f"""
🚨 CRITICAL BREVITY REQUEST DETECTED 🚨

The user EXPLICITLY asked for a brief response in their current message.

MANDATORY REQUIREMENTS:
1. Maximum {max_words} words (strictly enforce)
2. Cut all fluff, introduction, and meta-commentary
3. Start with the core insight immediately
4. Use 2-3 sentences maximum
5. No bullet points unless absolutely necessary
6. One key point, then stop

Structure:
- [Core insight in 1-2 sentences]
- [One supporting point if essential]
- [One question to engage, optional]

DO NOT:
❌ Explain your reasoning process
❌ Provide multiple perspectives
❌ Give extensive background
❌ Use lengthy introductions
❌ Exceed {max_words} words under any circumstances

The user values your insight but wants it FAST and CONCISE.
"""
        
        elif style == 'brief':
            return f"""
Response Style: BRIEF (max {max_words} words)

The user has shown a preference for concise responses in this conversation.

Guidelines:
- Focus on core insight
- 3-5 sentences
- Skip extensive explanations
- Be direct and actionable
"""
        
        elif style == 'detailed':
            return f"""
Response Style: DETAILED (up to {max_words} words)

The user wants comprehensive analysis.

Guidelines:
- Explore multiple angles
- Provide supporting evidence
- Use examples
- Be thorough
"""
        
        else:
            return f"""
Response Style: BALANCED (max {max_words} words)

Standard response depth.
"""


# Example usage
if __name__ == '__main__':
    """Test conversation context detection"""
    
    test_cases = [
        "Make the answer more brief",
        "Can you be more concise?",
        "Give me the short version",
        "I want details on this",
        "What should I do?",
    ]
    
    for question in test_cases:
        wants_brevity = ConversationContext.detect_brevity_request(question)
        wants_expansion = ConversationContext.detect_expansion_request(question)
        
        print(f"\nQuestion: {question}")
        print(f"  Brevity: {wants_brevity}")
        print(f"  Expansion: {wants_expansion}")