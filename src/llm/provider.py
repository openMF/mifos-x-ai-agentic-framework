"""
LLM Provider Factory
Supports multiple LLM backends: OpenAI, Ollama (local), HuggingFace
"""

from typing import Optional
from langchain.llms.base import LLM
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import logging

logger = logging.getLogger(__name__)


class LLMProvider:
    """Base class for LLM providers"""

    def __init__(self, model_name: str, temperature: float = 0.7, streaming: bool = False):
        self.model_name = model_name
        self.temperature = temperature
        self.streaming = streaming

    def get_llm(self) -> LLM:
        """Get the LLM instance"""
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """OpenAI LLM Provider"""

    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        streaming: bool = False,
    ):
        super().__init__(model_name, temperature, streaming)
        self.api_key = api_key

    def get_llm(self) -> ChatOpenAI:
        """Get ChatOpenAI instance"""
        callbacks = []
        if self.streaming:
            callbacks.append(StreamingStdOutCallbackHandler())

        return ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key,
            callbacks=CallbackManager(callbacks) if callbacks else None,
            request_timeout=60,
        )


class OllamaProvider(LLMProvider):
    """Ollama Local LLM Provider"""

    def __init__(
        self,
        model_name: str = "llama2",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        streaming: bool = False,
    ):
        super().__init__(model_name, temperature, streaming)
        self.base_url = base_url
        self._validate_ollama_connection()

    def _validate_ollama_connection(self) -> bool:
        """Check if Ollama server is running"""
        try:
            import requests

            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"✓ Connected to Ollama at {self.base_url}")
                return True
        except Exception as e:
            logger.warning(
                f"⚠ Could not connect to Ollama at {self.base_url}. "
                f"Make sure Ollama is running: 'ollama serve'\n{str(e)}"
            )
        return False

    def get_llm(self) -> LLM:
        """Get Ollama LLM instance using LangChain"""
        try:
            from langchain.llms import Ollama

            callbacks = []
            if self.streaming:
                callbacks.append(StreamingStdOutCallbackHandler())

            return Ollama(
                model=self.model_name,
                base_url=self.base_url,
                temperature=self.temperature,
                callbacks=CallbackManager(callbacks) if callbacks else None,
            )
        except ImportError:
            raise ImportError(
                "Ollama support requires 'langchain' and 'ollama' packages. "
                "Install with: pip install langchain ollama"
            )


class HuggingFaceProvider(LLMProvider):
    """HuggingFace LLM Provider (via HuggingFace Inference API)"""

    def __init__(
        self,
        model_name: str = "meta-llama/Llama-2-7b-chat",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        streaming: bool = False,
    ):
        super().__init__(model_name, temperature, streaming)
        self.api_key = api_key

    def get_llm(self) -> LLM:
        """Get HuggingFace LLM instance"""
        try:
            from langchain.llms import HuggingFaceHub

            callbacks = []
            if self.streaming:
                callbacks.append(StreamingStdOutCallbackHandler())

            return HuggingFaceHub(
                repo_id=self.model_name,
                huggingfacehub_api_token=self.api_key,
                model_kwargs={"temperature": self.temperature},
                callbacks=CallbackManager(callbacks) if callbacks else None,
            )
        except ImportError:
            raise ImportError(
                "HuggingFace support requires 'huggingface-hub' package. "
                "Install with: pip install huggingface-hub"
            )


def create_llm_provider(
    provider_type: str = "openai",
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.7,
    streaming: bool = False,
    **kwargs,
) -> LLMProvider:
    """
    Factory function to create LLM providers

    Args:
        provider_type: Type of provider ('openai', 'ollama', 'huggingface')
        model_name: Name of the model
        api_key: API key for providers that need it
        temperature: Temperature for model sampling
        streaming: Enable streaming responses
        **kwargs: Additional provider-specific arguments

    Returns:
        LLMProvider instance

    Examples:
        # OpenAI
        llm = create_llm_provider('openai', model_name='gpt-3.5-turbo', api_key='sk-...')

        # Local Ollama
        llm = create_llm_provider('ollama', model_name='llama2')

        # HuggingFace
        llm = create_llm_provider('huggingface', model_name='meta-llama/Llama-2-7b-chat', api_key='hf_...')
    """
    provider_type = provider_type.lower()

    if provider_type == "openai":
        return OpenAIProvider(
            model_name=model_name or "gpt-3.5-turbo",
            api_key=api_key,
            temperature=temperature,
            streaming=streaming,
        )

    elif provider_type == "ollama":
        return OllamaProvider(
            model_name=model_name or "llama2",
            base_url=kwargs.get("base_url", "http://localhost:11434"),
            temperature=temperature,
            streaming=streaming,
        )

    elif provider_type == "huggingface":
        return HuggingFaceProvider(
            model_name=model_name or "meta-llama/Llama-2-7b-chat",
            api_key=api_key,
            temperature=temperature,
            streaming=streaming,
        )

    else:
        raise ValueError(
            f"Unknown provider type: {provider_type}. "
            f"Supported: 'openai', 'ollama', 'huggingface'"
        )
