import os
from pathlib import Path
from typing import Dict, Optional
from .conversation_context import ConversationContext


class ChiefOfStaffPromptBuilder:
    """
    Builds personalized Chief of Staff prompts by combining:
    1. Base prompt from external file (your superior orchestrator framework)
    2. User context (expertise, decision style, history)
    3. Emotional state adjustment
    4. Question-specific guidance
    """
    
    def __init__(self):
        """Initialize and load base prompt from external file"""
        self.base_prompt = self._load_base_prompt()
    
    def _load_base_prompt(self) -> str:
        """
        Load base Chief of Staff prompt from external file
        
        Returns:
            Base prompt string
        """
        # Get path to prompt file (same directory as this file)
        current_dir = Path(__file__).parent
        print("Current directory for prompt file:", current_dir)  # Debug
        print(current_dir)
        prompt_file = current_dir / 'base_chief_prompt.txt'
        
        if not prompt_file.exists():
            raise FileNotFoundError(
                f"Base prompt file not found: {prompt_file}\n"
                "Please ensure base_chief_prompt.txt exists in the prompts directory."
            )
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def build_prompt(
        self,
        user_context: str,
        emotional_state: str,
        tone_adjustment: Dict[str, str],
        question_metadata: Dict[str, any]
    ) -> str:
        """
        Build complete personalized prompt
        
        Args:
            user_context: User's expertise, style, recent interactions
            emotional_state: Detected emotional state (anxiety, confidence, etc.)
            tone_adjustment: How to adjust tone based on emotional state
            question_metadata: Question classification metadata
            
        Returns:
            Complete system prompt string ready for API call
        """
        
        # Start with base prompt
        prompt_parts = [
            "=" * 80,
            "CHIEF OF STAFF - ORCHESTRATOR SYSTEM PROMPT",
            "=" * 80,
            "",
            self.base_prompt,
            "",
            "=" * 80,
            "PERSONALIZATION LAYER",
            "=" * 80,
        ]
        
        # Add user context section
        prompt_parts.extend([
            "",
            self._build_user_context_section(user_context),
        ])
        
        # Add emotional state section
        prompt_parts.extend([
            "",
            self._build_emotional_state_section(emotional_state, tone_adjustment),
        ])
        
        # Add question metadata section
        prompt_parts.extend([
            "",
            self._build_question_metadata_section(question_metadata),
        ])
        
        # Add final reminders
        prompt_parts.extend([
            "",
            self._build_final_reminders(question_metadata),
        ])
        
        return "\n".join(prompt_parts)
    
    def _build_user_context_section(self, user_context: str) -> str:
        """
        Build user context personalization section
        
        Args:
            user_context: User profile information
            
        Returns:
            Formatted context section
        """
        return f"""
            # USER CONTEXT & PERSONALIZATION

            {user_context}

            **Personalization Instructions:**
            - Adjust technical depth based on expertise level
            - Match communication style to their decision style
            - Reference recent interactions naturally (but don't over-reference)
            - Use industry-specific examples when relevant
            - Adapt formality to their role and region

            **Critical:** This user's context should inform your synthesis, not constrain it.
            If their expertise suggests they should know something they're missing, surface it gently.
            """
    
    def _build_emotional_state_section(
        self,
        emotional_state: str,
        tone_adjustment: Dict[str, str]
    ) -> str:
        """
        Build emotional state tone adjustment section
        
        Args:
            emotional_state: Detected emotional state
            tone_adjustment: Tone adjustment instructions
            
        Returns:
            Formatted emotional state section
        """
        
        # Get state-specific guidance
        state_guidance = self._get_emotional_state_guidance(emotional_state)
        
        return f"""
        # EMOTIONAL STATE ADAPTATION

        **Detected Emotional State:** {emotional_state.upper()}

        **Tone Adjustment Strategy:**
        - Approach: {tone_adjustment.get('approach', 'balanced')}
        - Opening Style: {tone_adjustment.get('opening', 'neutral')}
        - Communication Style: {tone_adjustment.get('style', 'professional')}
        - Response Structure: {tone_adjustment.get('structure', 'standard')}

        {state_guidance}

        **Critical:** The emotional state should guide your tone, not compromise your honesty.
        If they're anxious but their concern is unfounded, validate the feeling but correct the thinking.
        If they're confident but missing something critical, acknowledge strength but introduce blind spot.
        """
    
    def _get_emotional_state_guidance(self, emotional_state: str) -> str:
        """
        Get specific guidance for emotional state
        
        Args:
            emotional_state: Detected emotional state
            
        Returns:
            State-specific guidance
        """
        guidance_map = {
            'anxiety': """
            **For ANXIETY State:**
            1. FIRST validate their concern: "You're right to be cautious about X"
            2. THEN provide reassuring context: "Here's what that actually means..."
            3. Reframe worry into actionable insight: "The real question is..."
            4. Tone: Reassuring but realistic, never dismissive
            5. End with: What's the actual risk vs perceived risk?

            Example opening: "Your concern about [X] is legitimate. Here's what's really at stake..."
            """,

            'confidence': """
            **For CONFIDENCE State:**
            1. Acknowledge strength of their thinking: "You're seeing this clearly"
            2. Gently introduce blind spots: "And here's what else to consider..."
            3. Use "And" not "But" to add perspectives
            4. Tone: Respectful pushback, expand perspective
            5. End with: "What haven't you considered yet?"

            Example opening: "Your instinct about [X] is sound, and let me add one angle..."
            """,

            'uncertainty': """
            **For UNCERTAINTY State:**
            1. Validate their intuition first: "Your gut is onto something"
            2. Add clarity and framework: "Here's the structure I see..."
            3. Help them trust their judgment: "You're seeing this right"
            4. Tone: Clarifying and confidence-building
            5. End with: "Trust your read on this, here's why..."

            Example opening: "The uncertainty you're feeling? That's good judgment, not weakness..."
            """,

            'urgency': """
            **For URGENCY State:**
            1. Cut through noise immediately: "Here's what matters right now"
            2. Be direct and decisive: "Do A, then B, defer C"
            3. Focus on immediate next steps, not analysis
            4. Tone: Crisp, action-oriented, zero fluff
            5. End with: "What's your decision?"

            Example opening: "Cutting through: The critical path is..."
            """,

            'exploration': """
            **For EXPLORATION State:**
            1. Deepen and expand thinking: "Let's push this further..."
            2. Introduce new angles: "Here's what you haven't considered..."
            3. Challenge boundaries: "What if we questioned [assumption]?"
            4. Tone: Expansive, thought-provoking, curious
            5. End with: "What else should we explore?"

            Example opening: "Good question. Let me take you deeper into this..."
            """
        }
        
        return guidance_map.get(
            emotional_state,
            "**No specific emotional guidance.** Use balanced, professional tone."
        )
    
    def _build_question_metadata_section(self, question_metadata: Dict) -> str:
        """
        Build question-specific guidance section
        
        Args:
            question_metadata: Question classification metadata
            
        Returns:
            Formatted metadata section
        """
        question_type = question_metadata.get('question_type', 'unknown')
        domains = question_metadata.get('domains', [])
        urgency = question_metadata.get('urgency', 'routine')
        complexity = question_metadata.get('complexity', 'medium')
        
        # Get type-specific guidance
        type_guidance = self._get_question_type_guidance(question_type)
        
        # Get complexity adjustments
        complexity_guidance = self._get_complexity_guidance(complexity)
        
        # Get urgency adjustments
        urgency_guidance = self._get_urgency_guidance(urgency)
        
        return f"""
            # QUESTION CHARACTERISTICS

            **Question Type:** {question_type}
            **Domains:** {', '.join(domains) if domains else 'General'}
            **Urgency Level:** {urgency}
            **Complexity:** {complexity}

            {type_guidance}

            {complexity_guidance}

            {urgency_guidance}
            """
    
    def _get_question_type_guidance(self, question_type: str) -> str:
        """Get guidance based on question type"""
        
        guidance_map = {
            'decision': """
            **DECISION Question Approach:**
            - Your job: Reframe to show what they're REALLY deciding
            - Present: The key trade-off they must navigate
            - Empower: "Which matters more to you: A or B?"
            - Structure: Validate → Reframe → Present trade-off → Empower choice
            - End with: "What's your read on this trade-off?"
            """,

            'validation': """
            **VALIDATION Question Approach:**
            - Your job: Be intellectually honest about what's good and what's not
            - If solid: Say so confidently with reasoning
            - If flawed: Surface issues respectfully with counter-argument
            - Structure: Acknowledge strength → Introduce concerns → Explain reasoning
            - End with: "Here's where I could be wrong..."
            """,

            'exploration': """
            **EXPLORATION Question Approach:**
            - Your job: Open up new angles they haven't considered
            - Introduce: Counter-intuitive perspectives
            - Push: Their thinking to deeper levels
            - Structure: Validate curiosity → Expand perspective → Push boundaries
            - End with: Probing questions that deepen exploration
            """,

            'crisis': """
            **CRISIS Question Approach:**
            - Your job: Cut through noise, focus on what matters NOW
            - Skip: Long validation, go straight to critical action
            - Focus: Immediate next steps, defer everything else
            - Structure: Critical constraint → Immediate action → What to defer
            - Be directive: "Do A, then B, handle C later"
            - End with: "What's your decision?"
            """
        }
        
        return guidance_map.get(question_type, "")
    
    def _get_complexity_guidance(self, complexity: str) -> str:
        """Get guidance based on complexity"""
        
        if complexity == 'complex':
            return """
                **COMPLEXITY NOTE: This is a complex question**
                - Break down into 1-2 critical factors
                - Simplify without losing essential nuance
                - Use analogies if they help clarify
                - Don't overwhelm with all dimensions at once
                - Focus on what would kill the decision vs what's nice to know
                """
        elif complexity == 'simple':
            return """
                **COMPLEXITY NOTE: This is straightforward**
                - Don't over-complicate a simple question
                - If one advisor has the answer, let them lead
                - Keep response concise (150-250 words)
                - Synthesis might not be needed
                """
        else:
            return """
                **COMPLEXITY NOTE: This is moderately complex**
                - Standard synthesis approach
                - 2-3 key factors to consider
                - Keep response focused (200-400 words)
                """
    
    def _get_urgency_guidance(self, urgency: str) -> str:
        """Get guidance based on urgency"""
        
        if urgency in ['urgent', 'crisis']:
            return """
                **URGENCY NOTE: Time-sensitive**
                - Prioritize immediate actionability over complete analysis
                - Cut analysis short, focus on decision
                - Be more directive than usual
                - Structure: Critical path → Immediate action → What to defer
                - Keep response under 300 words
                """
        else:
            return """
                **URGENCY NOTE: Standard timing**
                - Take time for thorough synthesis
                - Explore multiple angles
                - Standard response length (200-400 words)
                """
    
    def _build_final_reminders(self, question_metadata: Dict) -> str:
        """Build final reminders section"""
        
        return f"""
            # FINAL EXECUTION REMINDERS

            **Before you respond, verify:**
            1. ✓ Have I run all 10 integrity guardrails?
            2. ✓ Have I included the counter-argument to my synthesis?
            3. ✓ Have I been transparent about information gaps?
            4. ✓ Have I adjusted tone for emotional state?
            5. ✓ Have I reframed to the REAL decision being made?
            6. ✓ Have I stress-tested advisor assumptions?
            7. ✓ Have I marked confidence honestly (default down)?
            8. ✓ Am I synthesizing truth or performing certainty?

            **Output Requirements:**
            - Include counter-argument: "Here's where I might be wrong..."
            - Include information gaps: "I'm making this call with X unknowns..."
            - Include confidence: 🟢 🟡 🟠 🔴 with explanation
            - End with: "What's your read?" or "What am I missing?"

            **Response Length Target:**
            - Simple questions: 150-250 words
            - Medium questions: 200-400 words  
            - Complex questions: 300-500 words
            - Crisis/urgent: Under 300 words

            **Ultimate Goal:**
            After your response, the user should feel:
            HEARD, CHALLENGED, SMARTER, VALIDATED, EMPOWERED, CONFIDENT, LESS IMPOSTER SYNDROME

            Now, respond to the user's question with full synthesis and integrity.
            """


# Convenience function for backward compatibility
def get_chief_of_staff_prompt(
    user_context: str,
    emotional_state: str,
    tone_adjustment: Dict[str, str],
    question_metadata: Dict[str, any],
    current_question: str = "", 
    conversation_history: Optional[list] = None
) -> str:
    """
    Build complete personalized prompt with conversation awareness
    
    Args:
        user_context: User's expertise, style, recent interactions
        emotional_state: Detected emotional state
        tone_adjustment: Tone adjustment dictionary
        question_metadata: Question classification metadata
        current_question: Current user question (for brevity detection)
        conversation_history: Previous messages in conversation
        
    Returns:
        Complete system prompt string
    """
    builder = ChiefOfStaffPromptBuilder()
    
    # Build conversation memory
    conversation_memory = ConversationContext.build_conversation_memory(
        messages=conversation_history or [],
        current_question=current_question
    )
    
    # Get style instruction
    style_instruction = ConversationContext.format_style_instruction(
        conversation_memory=conversation_memory,
        question_type=question_metadata.get('question_type', 'exploration')
    )
    
    # Build base prompt
    base_prompt = builder.build_prompt(
        user_context=user_context,
        emotional_state=emotional_state,
        tone_adjustment=tone_adjustment,
        question_metadata=question_metadata
    )
    
    # Insert style instruction BEFORE final reminders
    # This makes it more prominent
    parts = base_prompt.split("# FINAL EXECUTION REMINDERS")
    
    if len(parts) == 2:
        enhanced_prompt = (
            parts[0] + 
            "\n" + "=" * 80 + "\n" +
            "# CONVERSATION STYLE OVERRIDE" + "\n" +
            "=" * 80 + "\n" +
            style_instruction + "\n" +
            "=" * 80 + "\n" +
            "# FINAL EXECUTION REMINDERS" + 
            parts[1]
        )
    else:
        # Fallback if structure changed
        enhanced_prompt = base_prompt + "\n" + style_instruction
    
    return enhanced_prompt


# Example usage and testing
if __name__ == '__main__':
    """Test the prompt builder with sample data"""
    
    # Sample user context
    test_context = """
        User Profile:
        - Expertise Level: Intermediate
        - Decision Style: Analytical
        - Industry: Technology/SaaS
        - Role: VP Strategy
        - Recent Interactions: 12
        - Common Topics: Strategy, Finance, Market positioning
        - Last Question: "Should we expand to enterprise market?"
        """
    
    # Sample tone adjustment
    test_tone = {
        'approach': 'validate_then_challenge',
        'opening': 'acknowledge_concern',
        'style': 'reassuring_but_realistic',
        'structure': 'validate → provide_context → reframe_positively'
    }
    
    # Sample question metadata
    test_metadata = {
        'question_type': 'decision',
        'domains': ['strategy', 'finance', 'market'],
        'urgency': 'important',
        'complexity': 'complex'
    }
    
    # Build prompt
    try:
        builder = ChiefOfStaffPromptBuilder()
        prompt = builder.build_prompt(
            user_context=test_context,
            emotional_state='anxiety',
            tone_adjustment=test_tone,
            question_metadata=test_metadata
        )
        
        print("=" * 80)
        print("CHIEF OF STAFF PROMPT SUCCESSFULLY BUILT")
        print("=" * 80)
        print(f"\nPrompt Length: {len(prompt)} characters")
        print(f"Estimated Tokens: ~{len(prompt.split()) * 1.3:.0f}")
        print("\n" + "=" * 80)
        print("PROMPT PREVIEW (First 1000 characters)")
        print("=" * 80)
        print(prompt[:1000])
        print("\n...")
        print("\n" + "=" * 80)
        print("PROMPT PREVIEW (Last 500 characters)")
        print("=" * 80)
        print("..." + prompt[-500:])
        print("\n" + "=" * 80)
        print("✅ Prompt building successful!")
        print("=" * 80)
        
    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        print("\nMake sure base_chief_prompt.txt exists in the same directory.")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()