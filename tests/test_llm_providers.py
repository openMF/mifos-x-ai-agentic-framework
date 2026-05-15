"""
Tests for LLM Providers
Tests local LLM (Ollama) and OpenAI providers with performance benchmarks
"""

import pytest
import time
import logging
from unittest.mock import Mock, patch, MagicMock
from src.llm.provider import (
    create_llm_provider,
    OpenAIProvider,
    OllamaProvider,
    HuggingFaceProvider,
)

logger = logging.getLogger(__name__)


class TestOpenAIProvider:
    """Test OpenAI LLM Provider"""

    def test_openai_provider_creation(self):
        """Test creating OpenAI provider"""
        provider = OpenAIProvider(
            model_name="gpt-3.5-turbo",
            api_key="sk-test-key",
            temperature=0.7,
        )
        assert provider.model_name == "gpt-3.5-turbo"
        assert provider.temperature == 0.7
        assert provider.api_key == "sk-test-key"

    @patch("src.llm.provider.ChatOpenAI")
    def test_openai_get_llm(self, mock_chat_openai):
        """Test getting OpenAI LLM instance"""
        provider = OpenAIProvider(api_key="sk-test-key")
        llm = provider.get_llm()
        mock_chat_openai.assert_called_once()

    def test_openai_temperature_ranges(self):
        """Test temperature parameter validation"""
        for temp in [0.0, 0.5, 1.0, 2.0]:
            provider = OpenAIProvider(temperature=temp)
            assert provider.temperature == temp


class TestOllamaProvider:
    """Test Ollama Local LLM Provider"""

    def test_ollama_provider_creation(self):
        """Test creating Ollama provider"""
        provider = OllamaProvider(
            model_name="llama2",
            base_url="http://localhost:11434",
            temperature=0.5,
        )
        assert provider.model_name == "llama2"
        assert provider.base_url == "http://localhost:11434"
        assert provider.temperature == 0.5

    @patch("requests.get")
    def test_ollama_connection_validation_success(self, mock_get):
        """Test successful Ollama connection validation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        provider = OllamaProvider(base_url="http://localhost:11434")
        assert provider._validate_ollama_connection() == True

    @patch("requests.get")
    def test_ollama_connection_validation_failure(self, mock_get):
        """Test failed Ollama connection validation"""
        mock_get.side_effect = Exception("Connection refused")
        provider = OllamaProvider(base_url="http://localhost:11434")
        assert provider._validate_ollama_connection() == False

    @patch("src.llm.provider.Ollama")
    def test_ollama_get_llm(self, mock_ollama):
        """Test getting Ollama LLM instance"""
        provider = OllamaProvider(model_name="llama2")
        llm = provider.get_llm()
        mock_ollama.assert_called_once()

    def test_ollama_streaming_callback(self):
        """Test Ollama with streaming enabled"""
        provider = OllamaProvider(streaming=True)
        assert provider.streaming == True


class TestHuggingFaceProvider:
    """Test HuggingFace LLM Provider"""

    def test_huggingface_provider_creation(self):
        """Test creating HuggingFace provider"""
        provider = HuggingFaceProvider(
            model_name="meta-llama/Llama-2-7b-chat",
            api_key="hf_test_key",
            temperature=0.6,
        )
        assert provider.model_name == "meta-llama/Llama-2-7b-chat"
        assert provider.api_key == "hf_test_key"
        assert provider.temperature == 0.6

    @patch("src.llm.provider.HuggingFaceHub")
    def test_huggingface_get_llm(self, mock_hf_hub):
        """Test getting HuggingFace LLM instance"""
        provider = HuggingFaceProvider(api_key="hf_test_key")
        llm = provider.get_llm()
        mock_hf_hub.assert_called_once()


class TestLLMProviderFactory:
    """Test LLM Provider Factory"""

    def test_factory_openai_creation(self):
        """Test factory creates OpenAI provider"""
        provider = create_llm_provider("openai", api_key="sk-test")
        assert isinstance(provider, OpenAIProvider)

    def test_factory_ollama_creation(self):
        """Test factory creates Ollama provider"""
        provider = create_llm_provider("ollama", model_name="llama2")
        assert isinstance(provider, OllamaProvider)

    def test_factory_huggingface_creation(self):
        """Test factory creates HuggingFace provider"""
        provider = create_llm_provider("huggingface", api_key="hf_test")
        assert isinstance(provider, HuggingFaceProvider)

    def test_factory_invalid_provider(self):
        """Test factory raises error for invalid provider"""
        with pytest.raises(ValueError, match="Unknown provider type"):
            create_llm_provider("invalid_provider")

    def test_factory_case_insensitive(self):
        """Test factory is case-insensitive"""
        provider1 = create_llm_provider("OPENAI", api_key="sk-test")
        provider2 = create_llm_provider("OpenAI", api_key="sk-test")
        assert isinstance(provider1, OpenAIProvider)
        assert isinstance(provider2, OpenAIProvider)

    def test_factory_custom_model_names(self):
        """Test factory with custom model names"""
        provider1 = create_llm_provider(
            "openai", model_name="gpt-4", api_key="sk-test"
        )
        provider2 = create_llm_provider("ollama", model_name="mistral")
        assert provider1.model_name == "gpt-4"
        assert provider2.model_name == "mistral"

    def test_factory_temperature_settings(self):
        """Test factory passes temperature correctly"""
        for temp in [0.1, 0.5, 0.9, 1.5]:
            provider = create_llm_provider("ollama", temperature=temp)
            assert provider.temperature == temp

    def test_factory_streaming_flag(self):
        """Test factory passes streaming flag"""
        provider1 = create_llm_provider("openai", streaming=False)
        provider2 = create_llm_provider("ollama", streaming=True)
        assert provider1.streaming == False
        assert provider2.streaming == True


class TestLLMProviderPerformance:
    """Performance benchmarks for LLM providers"""

    def test_provider_creation_performance(self):
        """Benchmark provider creation time"""
        start = time.time()
        for _ in range(100):
            create_llm_provider("openai", api_key="sk-test")
        creation_time = time.time() - start

        # Provider creation should be fast (< 1 second for 100 iterations)
        assert creation_time < 1.0, f"Provider creation too slow: {creation_time:.3f}s"
        logger.info(f"✓ Provider creation: {creation_time:.3f}s for 100 iterations")

    def test_factory_function_overhead(self):
        """Benchmark factory function overhead"""
        # Direct instantiation
        start = time.time()
        for _ in range(1000):
            OpenAIProvider(api_key="sk-test")
        direct_time = time.time() - start

        # Via factory
        start = time.time()
        for _ in range(1000):
            create_llm_provider("openai", api_key="sk-test")
        factory_time = time.time() - start

        # Factory overhead should be minimal
        overhead_percent = ((factory_time - direct_time) / direct_time) * 100
        assert overhead_percent < 50, f"Factory overhead too high: {overhead_percent:.1f}%"
        logger.info(
            f"✓ Factory overhead: {overhead_percent:.1f}% "
            f"({direct_time:.3f}s vs {factory_time:.3f}s)"
        )

    def test_provider_memory_efficiency(self):
        """Test memory usage with multiple provider instances"""
        import sys

        providers = [
            create_llm_provider("openai", api_key="sk-test") for _ in range(100)
        ]

        total_size = sum(sys.getsizeof(p) for p in providers)
        avg_size = total_size / len(providers)

        # Average provider size should be reasonable
        assert avg_size < 10000, f"Provider size too large: {avg_size:.0f} bytes"
        logger.info(f"✓ Average provider size: {avg_size:.0f} bytes")


class TestLLMProviderIntegration:
    """Integration tests for LLM providers"""

    def test_provider_switching(self):
        """Test switching between different providers"""
        # Simulate agent setup with different providers
        providers = {
            "openai": create_llm_provider("openai", api_key="sk-test"),
            "ollama": create_llm_provider("ollama"),
            "huggingface": create_llm_provider("huggingface", api_key="hf-test"),
        }

        assert len(providers) == 3
        for name, provider in providers.items():
            assert provider is not None
            logger.info(f"✓ Provider {name}: {provider.__class__.__name__}")

    def test_provider_configuration_isolation(self):
        """Test that providers don't interfere with each other"""
        provider1 = create_llm_provider("openai", temperature=0.5)
        provider2 = create_llm_provider("ollama", temperature=0.9)

        assert provider1.temperature == 0.5
        assert provider2.temperature == 0.9
        # Ensure modifying one doesn't affect the other
        provider1.temperature = 0.1
        assert provider2.temperature == 0.9
