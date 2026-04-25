"""LLM Provider for Unsloth models - Production only."""
import logging

logger = logging.getLogger(__name__)


class UnslothProvider:
    """Unsloth-based LLM provider for production."""

    def __init__(
        self,
        model_name: str = "meta-llama/Llama-2-7b-hf",
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.model = None
        self.tokenizer = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize Unsloth model."""
        try:
            from unsloth import FastLanguageModel

            logger.info(f"Loading Unsloth model: {self.model_name}")

            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name=self.model_name,
                max_seq_length=self.max_tokens,
                dtype=None,
                load_in_4bit=True,
            )

            FastLanguageModel.for_inference(self.model)
            self._initialized = True
            logger.info("✓ Unsloth model initialized successfully")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Unsloth model: {e}")
            raise

    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate text using Unsloth model."""
        if not self._initialized:
            raise RuntimeError("Provider not initialized. Call initialize() first.")

        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=self.temperature,
                top_p=0.95,
                do_sample=True,
            )
            response = self.tokenizer.decode(
                outputs[0], skip_special_tokens=True, max_new_tokens=max_tokens
            )
            return response[len(prompt):].strip()
        except Exception as e:
            logger.error(f"✗ Error generating text: {e}")
            raise

    async def shutdown(self) -> None:
        """Shutdown and cleanup."""
        self.model = None
        self.tokenizer = None
        self._initialized = False
        logger.info("✓ Unsloth provider shutdown")


class LLMProviderFactory:
    """Factory for creating LLM providers."""

    @staticmethod
    def create(
        provider_type: str = "unsloth",
        model_name: str = "meta-llama/Llama-2-7b-hf",
        **kwargs,
    ) -> UnslothProvider:
        """Create Unsloth provider instance."""
        if provider_type.lower() != "unsloth":
            logger.warning(f"Unknown provider type: {provider_type}. Using unsloth.")

        return UnslothProvider(model_name=model_name, **kwargs)
