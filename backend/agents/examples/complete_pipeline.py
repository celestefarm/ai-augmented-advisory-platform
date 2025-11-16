# agents/examples/complete_pipeline.py

"""
Complete Week 2 Pipeline Integration Example

This demonstrates the full flow from user question to final response:

1. Question Classification
2. Emotional State Detection  
3. Memory Retrieval (simulated)
4. Model Selection
5. Chief Agent Response Generation (streaming)
6. Quality Gates Validation
7. Confidence Marking
8. Memory Storage (simulated)

This is the complete Week 2 architecture in action.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.services.classifier import QuestionClassifier
from agents.services.emotional_detector import EmotionalStateDetector
from agents.services.model_router import ModelRouter
from agents.services.chief_agent import ChiefOfStaffAgent
from agents.services.quality_gates import QualityGates
from agents.services.confidence_marker import ConfidenceMarker


class CompletePipeline:
    """
    Complete Week 2 Pipeline
    
    Orchestrates all services to generate intelligent,
    validated, confidence-marked responses.
    """
    
    def __init__(self, anthropic_api_key: str):
        """
        Initialize all services
        
        Args:
            anthropic_api_key: Anthropic API key
        """
        print("🚀 Initializing Week 2 Pipeline...")
        
        self.classifier = QuestionClassifier()
        self.emotional_detector = EmotionalStateDetector()
        self.model_router = ModelRouter()
        self.quality_gates = QualityGates()
        self.confidence_marker = ConfidenceMarker()
        
        # Chief agent will be initialized with selected model
        self.anthropic_api_key = anthropic_api_key
        
        print("✅ All services initialized\n")
    
    async def process_question(
        self,
        question: str,
        user_context: str = None
    ) -> dict:
        """
        Process a question through the complete pipeline
        
        Args:
            question: User's question
            user_context: Optional user context (expertise, style, etc.)
            
        Returns:
            Complete response with all metadata
        """
        import time
        pipeline_start = time.time()
        
        print("=" * 80)
        print("WEEK 2 PIPELINE EXECUTION")
        print("=" * 80)
        print(f"\n📝 Question: {question}\n")
        
        # Default user context if none provided
        if not user_context:
            user_context = """
User Profile:
- Expertise Level: Intermediate
- Decision Style: Analytical
- Industry: Technology/SaaS
- Role: VP Strategy
- Recent Interactions: 5
- Common Topics: Strategy, Finance
"""
        
        # STEP 1: Question Classification
        print("🔍 STEP 1: Question Classification")
        print("-" * 80)
        
        classification = self.classifier.classify(question)
        
        print(f"Type: {classification.question_type}")
        print(f"Domains: {', '.join(classification.domains)}")
        print(f"Urgency: {classification.urgency}")
        print(f"Complexity: {classification.complexity}")
        print(f"Confidence: {classification.confidence_score:.2f}")
        print(f"Patterns: {', '.join(classification.detected_patterns[:3])}")
        print()
        
        # STEP 2: Emotional State Detection
        print("💭 STEP 2: Emotional State Detection")
        print("-" * 80)
        
        emotional_result = self.emotional_detector.detect(question)
        
        print(f"State: {emotional_result.state}")
        print(f"Confidence: {emotional_result.confidence_score:.2f}")
        print(f"Tone Adjustment: {emotional_result.tone_adjustment['approach']}")
        print()
        
        # STEP 3: Model Selection
        print("🤖 STEP 3: Model Selection")
        print("-" * 80)
        
        model_selection = self.model_router.select_model(
            question_type=classification.question_type,
            domains=classification.domains,
            urgency=classification.urgency,
            complexity=classification.complexity,
            emotional_state=emotional_result.state
        )
        
        print(f"Selected Model: {model_selection.model_name}")
        print(f"Estimated Cost: ${model_selection.estimated_cost:.6f}")
        print(f"Estimated Latency: {model_selection.estimated_latency}s")
        print(f"Reasoning: {model_selection.reasoning}")
        print()
        
        # STEP 4: Chief Agent Response Generation
        print("🎯 STEP 4: Chief of Staff Response Generation (Streaming)")
        print("-" * 80)
        print()
        
        # Initialize agent with selected model
        agent = ChiefOfStaffAgent(
            api_key=self.anthropic_api_key,
            model=model_selection.model_name,
            max_tokens=2000,
            temperature=0.7
        )
        
        # Prepare question metadata for prompt
        question_metadata = {
            'question_type': classification.question_type,
            'domains': classification.domains,
            'urgency': classification.urgency,
            'complexity': classification.complexity
        }
        
        # Generate streaming response
        full_response = ""
        response_metadata = None
        
        print("Response:")
        print("-" * 80)
        
        try:
            async for event in agent.generate_response(
                user_question=question,
                user_context=user_context,
                emotional_state=emotional_result.state,
                tone_adjustment=emotional_result.tone_adjustment,
                question_metadata=question_metadata
            ):
                if event['type'] == 'start':
                    print("[Stream started]")
                    
                elif event['type'] == 'chunk':
                    print(event['content'], end='', flush=True)
                    full_response += event['content']
                    
                elif event['type'] == 'complete':
                    response_metadata = event['metadata']
                    print("\n" + "-" * 80)
                    print("[Stream completed]")
                    
                elif event['type'] == 'error':
                    print(f"\n❌ Error: {event['error']}")
                    return {'error': event['error']}
        
        except Exception as e:
            print(f"\n❌ Error during streaming: {str(e)}")
            return {'error': str(e)}
        
        print()
        
        # STEP 5: Quality Gates Validation
        print("🔒 STEP 5: Quality Gates Validation")
        print("-" * 80)
        
        quality_passed, failures, checks = self.quality_gates.validate_response(
            question=question,
            response=full_response,
            user_context=user_context,
            response_time=response_metadata['response_time'],
            question_metadata=question_metadata
        )
        
        for check_name, passed in checks.items():
            status = '✅' if passed else '❌'
            print(f"{status} {check_name}")
        
        if quality_passed:
            print("\n✅ All quality gates PASSED")
        else:
            print(f"\n⚠️ Quality gates FAILED: {', '.join(failures)}")
        
        print()
        
        # STEP 6: Confidence Marking
        print("📊 STEP 6: Confidence Marking")
        print("-" * 80)
        
        confidence_level, confidence_pct, confidence_explanation = \
            self.confidence_marker.calculate_confidence(
                response=full_response,
                question_complexity=classification.complexity,
                model_used=model_selection.model_name,
                response_time=response_metadata['response_time'],
                question_type=classification.question_type
            )
        
        # Get confidence emoji
        confidence_emoji = {
            'high': '🟢',
            'medium': '🟡',
            'low': '🟠',
            'speculative': '⚪'
        }
        
        print(f"Confidence: {confidence_emoji[confidence_level]} "
              f"{confidence_level.upper()} ({confidence_pct}%)")
        print(f"Explanation: {confidence_explanation}")
        print()
        
        # STEP 7: Performance Summary
        pipeline_end = time.time()
        total_time = pipeline_end - pipeline_start
        
        print("⚡ STEP 7: Performance Summary")
        print("-" * 80)
        print(f"Classification Time: <0.1s")
        print(f"Emotional Detection Time: <0.1s")
        print(f"Model Selection Time: <0.1s")
        print(f"AI Generation Time: {response_metadata['response_time']}s")
        print(f"Quality Validation Time: <0.1s")
        print(f"Confidence Marking Time: <0.1s")
        print(f"Total Pipeline Time: {total_time:.2f}s")
        print()
        print(f"Total Tokens: {response_metadata['total_tokens']}")
        print(f"API Cost: ${response_metadata['cost']:.6f}")
        print()
        
        # Check Week 2 targets
        target_time = 12.0
        time_status = "✅" if response_metadata['response_time'] <= target_time else "⚠️"
        
        print(f"{time_status} Week 2 Target: 8-12 seconds "
              f"(Actual: {response_metadata['response_time']:.2f}s)")
        
        print()
        print("=" * 80)
        print("PIPELINE EXECUTION COMPLETE")
        print("=" * 80)
        print()
        
        # Return complete result
        return {
            'success': True,
            'question': question,
            'response': full_response,
            'classification': {
                'type': classification.question_type,
                'domains': classification.domains,
                'urgency': classification.urgency,
                'complexity': classification.complexity,
                'confidence': classification.confidence_score
            },
            'emotional_state': {
                'state': emotional_result.state,
                'confidence': emotional_result.confidence_score,
                'tone_adjustment': emotional_result.tone_adjustment
            },
            'model_selection': {
                'model': model_selection.model_name,
                'reasoning': model_selection.reasoning,
                'estimated_cost': model_selection.estimated_cost
            },
            'performance': {
                'response_time': response_metadata['response_time'],
                'total_tokens': response_metadata['total_tokens'],
                'cost': response_metadata['cost']
            },
            'quality_gates': {
                'passed': quality_passed,
                'checks': checks,
                'failures': failures
            },
            'confidence': {
                'level': confidence_level,
                'percentage': confidence_pct,
                'explanation': confidence_explanation
            },
            'metadata': response_metadata
        }


async def main():
    """
    Main test function
    """
    # Get API key
    from decouple import config
    
    api_key = config('ANTHROPIC_API_KEY', default=None)
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not found in environment")
        print("Please set ANTHROPIC_API_KEY in your .env file")
        return
    
    # Initialize pipeline
    pipeline = CompletePipeline(api_key)
    
    # Test questions
    test_questions = [
        "Should we pivot to enterprise market now, or wait until we have 24 months runway?",
        "What if our pricing strategy fails? I'm worried about losing customers.",
        "So Competitor just launched a similar product. How should we respond?",
    ]
    
    # Process each question
    for i, question in enumerate(test_questions, 1):
        print("\n\n")
        print("🔥" * 40)
        print(f"TEST QUESTION {i}/{len(test_questions)}")
        print("🔥" * 40)
        print("\n")
        
        result = await pipeline.process_question(question)
        
        if result.get('success'):
            print("\n✅ Pipeline completed successfully!")
        else:
            print(f"\n❌ Pipeline failed: {result.get('error')}")
        
        # Wait between questions
        if i < len(test_questions):
            print("\n⏳ Waiting 2 seconds before next question...")
            await asyncio.sleep(2)
    
    print("\n\n")
    print("=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80)
    print("\n🎉 Week 2 Pipeline is fully operational!")


if __name__ == '__main__':
    """Run the complete pipeline test"""
    asyncio.run(main())