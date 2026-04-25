"""
Colab Testing Launcher

Run this in Google Colab to start testing.
Or run locally for development: python development/colab_launcher.py

This is the entry point for all testing workflows.
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
from development.prompt_manager import PromptManager
from models.llm_provider import LLMProviderFactory
from instructions import get_fabrication_assistant_prompt
from services import ChatService, DesignAnalyzerService, ReportService


async def scenario_1_test_models():
    """
    SCENARIO 1: Compare different LLM models

    This scenario helps you find the best model by:
    - Testing multiple models with the same question
    - Measuring response quality and speed
    - Comparing results
    - Identifying the winner
    """
    print("\n" + "="*80)
    print("SCENARIO 1: Finding the Best Model")
    print("="*80)

    framework = ModelTestingFramework()
    test_question = "How do I design a cube for 3D printing in plastic?"

    models_to_test = [
        "meta-llama/Llama-2-7b-hf",
        "meta-llama/Llama-2-13b-hf",
        # Add more: "mistralai/Mistral-7B-v0.1"
    ]

    for model_name in models_to_test:
        try:
            logger.info(f"Testing: {model_name}")

            provider = LLMProviderFactory.create(
                provider_type="unsloth",
                model_name=model_name,
                max_tokens=512,
                temperature=0.7,
            )
            await provider.initialize()

            prompt = f"You are a fabrication assistant.\n\nQuestion: {test_question}\n\nProvide a detailed response:"
            result = await framework.test_model(
                model_name=model_name,
                llm_provider=provider,
                prompt_template=prompt,
                user_question=test_question,
                response_quality=5,
            )

            print(f"\n✓ Response from {model_name}:")
            print(f"  Time: {result.response_time:.2f}s")
            print(f"  Response: {result.model_response[:200]}...")

            await provider.shutdown()

        except Exception as e:
            logger.error(f"Error testing {model_name}: {e}")

    # Show comparison
    framework.print_comparison()
    best_model = framework.get_best_model()

    # Save results
    filepath = framework.save_results("model_comparison.json")
    logger.info(f"Results saved to: {filepath}")
    logger.info(f"\n🏆 BEST MODEL: {best_model}")
    logger.info("\nNext: Update config/production.py with this model name")

    return best_model


async def scenario_2_test_prompts():
    """
    SCENARIO 2: Compare different prompts

    Find the best prompt by:
    - Creating multiple prompt versions
    - Testing with same model
    - Measuring response quality
    - Locking the best version
    """
    print("\n" + "="*80)
    print("SCENARIO 2: Finding the Best Prompt")
    print("="*80)

    framework = ModelTestingFramework()
    model_name = "meta-llama/Llama-2-7b-hf"
    test_question = "How do I design a cube for 3D printing in plastic?"

    # Define prompt versions to test
    prompts = {
        "v1_basic": """You are a helpful fabrication assistant.
Help users design parts for 3D printing.
Be concise and practical.""",

        "v2_detailed": """You are an expert in 3D printing and fabrication.
You help users:
1. Design parts optimized for 3D printing
2. Choose the right materials
3. Estimate print time and cost

Always be specific and practical in your advice.""",

        "v3_expert": """You are a fabrication expert with 10 years of experience.
When users ask about 3D printing, you:
- Ask clarifying questions about their use case
- Recommend optimal materials and settings
- Warn about common mistakes
- Provide cost and time estimates"""
    }

    logger.info(f"Testing model: {model_name}")

    provider = LLMProviderFactory.create(
        provider_type="unsloth",
        model_name=model_name,
    )
    await provider.initialize()

    # Test each prompt
    for prompt_name, prompt_content in prompts.items():
        try:
            logger.info(f"Testing: {prompt_name}")

            full_prompt = f"{prompt_content}\n\nUser: {test_question}\nAssistant:"
            result = await framework.test_model(
                model_name=f"{model_name}-{prompt_name}",
                llm_provider=provider,
                prompt_template=full_prompt,
                user_question=test_question,
                response_quality=5,
            )

            print(f"\n✓ {prompt_name}")
            print(f"  Response: {result.model_response[:200]}...")

        except Exception as e:
            logger.error(f"Error testing {prompt_name}: {e}")

    await provider.shutdown()

    # Show comparison
    framework.print_comparison()
    best = framework.get_best_model()

    # Save results
    framework.save_results("prompt_comparison.json")
    logger.info(f"\n🏆 BEST PROMPT: {best}")
    logger.info("\nNext: Update instructions/fabrication_assistant.md with this prompt")

    return best


async def scenario_3_complete_workflow():
    """
    SCENARIO 3: End-to-end system test

    Test the complete workflow:
    - Initialize all services
    - Run multi-turn conversation
    - Generate report
    - Verify everything works
    """
    print("\n" + "="*80)
    print("SCENARIO 3: Complete System Test")
    print("="*80)

    logger.info("Initializing services...")

    provider = LLMProviderFactory.create(
        provider_type="unsloth",
        model_name="meta-llama/Llama-2-7b-hf",
    )
    await provider.initialize()

    chat_service = ChatService(provider)
    design_analyzer = DesignAnalyzerService(provider)
    report_service = ReportService(provider, chat_service, design_analyzer)

    # Start conversation
    logger.info("\n>>> Starting test conversation")
    session_id = await chat_service.start_conversation()
    logger.info(f"Session ID: {session_id}")

    # Send test messages
    messages = [
        "I want to design a cube for 3D printing",
        "What material do you recommend?",
        "How long will it take to print?",
    ]

    for msg in messages:
        logger.info(f"\nUser: {msg}")
        response = await chat_service.send_message(session_id, msg)
        logger.info(f"Assistant: {response.answer}\n")

    # Generate report
    logger.info(">>> Generating report...")
    report = await report_service.generate_report(session_id)
    logger.info(f"Report ID: {report.report_id}")
    logger.info(f"Summary: {report.conversation_summary}")

    await provider.shutdown()
    logger.info("\n✓ Complete system test successful")

    return report


async def main():
    """Main testing menu."""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "FABRICATORS AI - DEVELOPMENT TESTING" + " "*23 + "║")
    print("║" + " "*78 + "║")
    print("║ Local dev or Google Colab testing. Find your best model and prompt." + " "*10 + "║")
    print("╚" + "="*78 + "╝")

    print("\n📊 What would you like to do?\n")
    print("1. Test different models (find the best one)")
    print("2. Test different prompts (find the best one)")
    print("3. Run complete system test (verify everything works)")
    print("4. Exit")

    choice = input("\nEnter choice (1-4): ").strip()

    try:
        if choice == "1":
            await scenario_1_test_models()
        elif choice == "2":
            await scenario_2_test_prompts()
        elif choice == "3":
            await scenario_3_complete_workflow()
        elif choice == "4":
            print("Goodbye!")
        else:
            print("Invalid choice")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
