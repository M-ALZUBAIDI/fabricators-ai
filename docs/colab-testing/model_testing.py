"""Model testing and comparison framework for development."""
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

# Metrics storage directory
METRICS_DIR = Path("metrics")
METRICS_DIR.mkdir(exist_ok=True)


@dataclass
class ModelTestResult:
    """Single test result for a model."""

    timestamp: str
    model_name: str
    prompt_template: str
    user_question: str
    model_response: str
    response_quality: int  # 1-5 rating
    response_time: float  # seconds
    tokens_used: int
    notes: str

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class ModelTestingFramework:
    """Framework to test and compare different models."""

    def __init__(self):
        self.results: List[ModelTestResult] = []
        self.current_model = None

    async def test_model(
        self,
        model_name: str,
        llm_provider,
        prompt_template: str,
        user_question: str,
        response_quality: int = 5,
    ) -> ModelTestResult:
        """
        Test a model and log results.

        Args:
            model_name: Name of model (e.g., "llama-2-7b", "mistral-7b")
            llm_provider: The LLM provider instance
            prompt_template: The prompt being tested
            user_question: The test question
            response_quality: Your rating of response (1-5 scale)

        Returns:
            ModelTestResult with all metrics
        """
        import time

        logger.info(f"Testing model: {model_name}")

        # Record start time
        start_time = time.time()

        # Generate response
        try:
            response = await llm_provider.generate(prompt_template)
            response_time = time.time() - start_time

            # Create result
            result = ModelTestResult(
                timestamp=datetime.now().isoformat(),
                model_name=model_name,
                prompt_template=prompt_template[:100],  # First 100 chars
                user_question=user_question,
                model_response=response,
                response_quality=response_quality,
                response_time=response_time,
                tokens_used=len(response.split()),  # Approximate
                notes=""
            )

            self.results.append(result)
            logger.info(f"Model {model_name} test completed in {response_time:.2f}s")

            return result

        except Exception as e:
            logger.error(f"Error testing model {model_name}: {e}")
            raise

    def rate_result(self, result_index: int, quality_rating: int, notes: str = ""):
        """
        Rate a test result after reviewing it.

        Args:
            result_index: Index in results list
            quality_rating: 1-5 scale rating
            notes: Your feedback/notes
        """
        if 0 <= result_index < len(self.results):
            self.results[result_index].response_quality = quality_rating
            self.results[result_index].notes = notes
            logger.info(f"Result {result_index} rated: {quality_rating}/5")

    def save_results(self, filename: str = None):
        """Save test results to JSON file."""
        if filename is None:
            filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = METRICS_DIR / filename

        # Convert to dictionaries
        data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "results": [r.to_dict() for r in self.results]
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Results saved to {filepath}")
        return filepath

    def compare_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Compare all tested models.

        Returns:
            Dictionary with statistics for each model
        """
        comparison = {}

        # Group by model
        models = {}
        for result in self.results:
            if result.model_name not in models:
                models[result.model_name] = []
            models[result.model_name].append(result)

        # Calculate stats
        for model_name, results_list in models.items():
            qualities = [r.response_quality for r in results_list]
            times = [r.response_time for r in results_list]

            comparison[model_name] = {
                "total_tests": len(results_list),
                "avg_quality": sum(qualities) / len(qualities),
                "max_quality": max(qualities),
                "min_quality": min(qualities),
                "avg_response_time": sum(times) / len(times),
                "fastest": min(times),
                "slowest": max(times),
            }

        return comparison

    def get_best_model(self) -> str:
        """Get model with best average quality rating."""
        comparison = self.compare_models()
        if not comparison:
            return None

        best_model = max(
            comparison.items(),
            key=lambda x: x[1]["avg_quality"]
        )[0]

        logger.info(f"Best model: {best_model}")
        return best_model

    def print_comparison(self):
        """Print formatted comparison of all models."""
        comparison = self.compare_models()

        print("\n" + "="*80)
        print("MODEL COMPARISON RESULTS")
        print("="*80)

        for model_name, stats in comparison.items():
            print(f"\n📊 {model_name}")
            print(f"   Tests: {stats['total_tests']}")
            print(f"   Quality Score: {stats['avg_quality']:.2f}/5 (range: {stats['min_quality']}-{stats['max_quality']})")
            print(f"   Response Time: {stats['avg_response_time']:.2f}s (range: {stats['fastest']:.2f}s - {stats['slowest']:.2f}s)")

        best = self.get_best_model()
        print(f"\n🏆 WINNER: {best}")
        print("="*80 + "\n")

    def export_to_csv(self, filename: str = None):
        """Export results to CSV for analysis."""
        if filename is None:
            filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        filepath = METRICS_DIR / filename

        import csv

        with open(filepath, "w", newline="") as f:
            if self.results:
                writer = csv.DictWriter(f, fieldnames=self.results[0].to_dict().keys())
                writer.writeheader()
                for result in self.results:
                    writer.writerow(result.to_dict())

        logger.info(f"Results exported to {filepath}")
        return filepath
