"""
Development testing script - Test different models and prompts.

This is where you experiment in development before moving to production.
"""
import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import development tools
from development.model_testing import ModelTestingFramework
from development.prompt_manager import PromptManager, create_prompt_versions_for_testing
from models.llm_provider import LLMProviderFactory, MockProvider, UnslothProvider
from instructions import get_fabrication_assistant_prompt
from services import ChatService, DesignAnalyzerService, ReportService
from services.three_d_generator import ThreeDGeneratorService


async def test_scenario_1_different_models():
    """
    SCENARIO 1: Test same prompt with different models

    Shows how to:
    - Load different models via Unsloth
    - Test same question with each model
    - Compare quality and speed
    - Choose the best one
    """
    print("\n" + "="*80)
    print("SCENARIO 1: Testing Different Models")
    print("="*80)

    framework = ModelTestingFramework()

    # Test question
    test_question = "How do I design a cube for 3D printing in plastic?"

    # Models to test (you can add more)
    models_to_test = [
        "meta-llama/Llama-2-7b-hf",      # Llama 2 7B
        "meta-llama/Llama-2-13b-hf",     # Llama 2 13B (better quality, slower)
        # "mistralai/Mistral-7B-v0.1",   # Mistral 7B (uncomment to test)
    ]

    # Test each model
    for model_name in models_to_test:
        try:
            logger.info(f"\n>>> Testing {model_name}")

            # Create provider
            provider = LLMProviderFactory.create(
                provider_type="unsloth",
                model_name=model_name,
                max_tokens=512,
                temperature=0.7,
            )

            # Initialize
            await provider.initialize()

            # Get prompt
            prompt = get_fabrication_assistant_prompt(test_question)

            # Test the model
            result = await framework.test_model(
                model_name=model_name,
                llm_provider=provider,
                prompt_template=prompt,
                user_question=test_question,
                response_quality=5,  # You rate it after
            )

            print(f"\n✓ Response from {model_name}:")
            print(f"  Time: {result.response_time:.2f}s")
            print(f"  Response: {result.model_response[:200]}...")

            # Shutdown
            await provider.shutdown()

            # After reviewing response, rate it
            print("\nRate this response (1-5): ", end="")
            user_rating = int(input() or "5")
            framework.rate_result(
                len(framework.results) - 1,
                user_rating,
                f"Manual review of {model_name}"
            )

        except Exception as e:
            logger.error(f"Error testing {model_name}: {e}")

    # Compare results
    logger.info("\n>>> Comparing Results...")
    framework.print_comparison()

    # Save results
    filepath = framework.save_results("model_comparison.json")
    logger.info(f"Saved to: {filepath}")

    # Get best model
    best_model = framework.get_best_model()
    logger.info(f"\n🏆 RECOMMENDED MODEL: {best_model}")

    return best_model


async def test_scenario_2_different_prompts():
    """
    SCENARIO 2: Test same model with different prompts

    Shows how to:
    - Create multiple prompt versions
    - Test same model with different prompts
    - Measure which prompt gets better responses
    - Lock best prompt for production
    """
    print("\n" + "="*80)
    print("SCENARIO 2: Testing Different Prompts")
    print("="*80)

    framework = ModelTestingFramework()
    prompt_manager = create_prompt_versions_for_testing()

    # Model to test (use the one you chose from scenario 1)
    model_name = "meta-llama/Llama-2-7b-hf"
    test_question = "How do I design a cube for 3D printing in plastic?"

    logger.info(f"Testing model: {model_name}")

    # Initialize model once
    provider = LLMProviderFactory.create(
        provider_type="unsloth",
        model_name=model_name,
    )
    await provider.initialize()

    # Get all prompt versions
    versions = prompt_manager.get_prompt_versions("fabrication_assistant")

    # Test each prompt version
    for prompt_version in versions:
        try:
            logger.info(f"\n>>> Testing prompt v{prompt_version.version}")
            logger.info(f"    Description: {prompt_version.description}")

            # Create full prompt with question
            full_prompt = (
                prompt_version.content + "\n\n" +
                f"User Question: {test_question}\n\n" +
                "Please provide a detailed response:"
            )

            # Test
            result = await framework.test_model(
                model_name=f"{model_name}-v{prompt_version.version}",
                llm_provider=provider,
                prompt_template=full_prompt,
                user_question=test_question,
                response_quality=5,
            )

            print(f"\n✓ Response from prompt v{prompt_version.version}:")
            print(f"  Time: {result.response_time:.2f}s")
            print(f"  Response: {result.model_response[:200]}...")

            # Rate prompt
            print("\nRate this prompt version (1-5): ", end="")
            user_rating = int(input() or "5")
            framework.rate_result(
                len(framework.results) - 1,
                user_rating,
                f"Prompt v{prompt_version.version}"
            )

        except Exception as e:
            logger.error(f"Error testing prompt v{prompt_version.version}: {e}")

    # Shutdown
    await provider.shutdown()

    # Compare results
    logger.info("\n>>> Comparing Prompt Versions...")
    framework.print_comparison()

    # Set best version as active
    best_model = framework.get_best_model()
    if best_model:
        best_version = best_model.split("-v")[-1]
        logger.info(f"\nSetting prompt v{best_version} as ACTIVE")
        prompt_manager.set_active_prompt("fabrication_assistant", best_version)

    # Show prompt status
    prompt_manager.print_status()

    # Save everything
    framework.save_results("prompt_comparison.json")
    prompt_manager.save_prompts()

    return prompt_manager


async def test_scenario_3_complete_workflow():
    """
    SCENARIO 3: Complete workflow - Test everything end-to-end

    This is the workflow when you're ready to test your complete system.
    """
    print("\n" + "="*80)
    print("SCENARIO 3: Complete End-to-End Testing")
    print("="*80)

    # Setup
    logger.info("Initializing services...")

    provider = LLMProviderFactory.create(
        provider_type="unsloth",
        model_name="meta-llama/Llama-2-7b-hf",
    )
    await provider.initialize()

    # Create services
    chat_service = ChatService(provider)
    design_analyzer = DesignAnalyzerService(provider)
    three_d_generator = ThreeDGeneratorService()
    report_service = ReportService(provider, chat_service, design_analyzer)

    # Test conversation
    logger.info("\n>>> Starting test conversation")

    session_id = await chat_service.start_conversation()
    logger.info(f"Session ID: {session_id}")

    # User questions
    questions = [
        "I want to design a cube for 3D printing",
        "What material do you recommend?",
        "How long will printing take?",
    ]

    # Ask questions
    for question in questions:
        logger.info(f"\nUser: {question}")
        response = await chat_service.send_message(session_id, question)
        logger.info(f"Assistant: {response.answer}\n")

    # Generate report
    logger.info("\n>>> Generating report...")
    report = await report_service.generate_report(session_id)
    logger.info(f"Report ID: {report.report_id}")
    logger.info(f"Summary: {report.conversation_summary}")

    # Shutdown
    await provider.shutdown()

    return report


async def main():
    """Main testing orchestrator."""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "FABRICATORS AI - DEVELOPMENT TESTING" + " "*23 + "║")
    print("╚" + "="*78 + "╝")

    print("\nWhat would you like to do?")
    print("1. Test different models (SCENARIO 1)")
    print("2. Test different prompts (SCENARIO 2)")
    print("3. Test complete system (SCENARIO 3)")
    print("4. Test with Mock LLM (fast testing)")

    choice = input("\nEnter choice (1-4): ").strip()

    try:
        if choice == "1":
            await test_scenario_1_different_models()

        elif choice == "2":
            await test_scenario_2_different_prompts()

        elif choice == "3":
            await test_scenario_3_complete_workflow()

        elif choice == "4":
            logger.info("Using MockProvider for fast testing...")
            provider = MockProvider()
            await provider.initialize()

            chat_service = ChatService(provider)
            session_id = await chat_service.start_conversation()

            response = await chat_service.send_message(
                session_id,
                "How do I make a cube?"
            )
            logger.info(f"Mock Response: {response.answer}")

        else:
            print("Invalid choice")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == "__main__":
    # This is how you run development tests
    # python development/dev_testing.py
    asyncio.run(main())
