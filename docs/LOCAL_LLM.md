# Local LLM Setup Guide

This guide shows how to use the Portfolio Health Agent with local, offline language models instead of relying on OpenAI's API.

## Overview

The agent supports three LLM backends:
- **OpenAI** (cloud-based, requires API key)
- **Ollama** (local, fully offline)
- **HuggingFace** (cloud-based inference)

## Quick Start with Ollama

### 1. Install Ollama

Download and install from [ollama.ai](https://ollama.ai):

```bash
# macOS/Linux
curl https://ollama.ai/install.sh | sh

# Or download from https://ollama.ai/download
```

### 2. Pull a Model

```bash
# Llama 2 (7B, ~4GB) - Recommended for CPU
ollama pull llama2

# Or other models
ollama pull mistral    # Mistral 7B
ollama pull neural-chat  # Intel Neural Chat
ollama pull dolphin-mixtral  # Dolphin Mixtral
```

### 3. Start Ollama Server

```bash
ollama serve
# Server runs on http://localhost:11434
```

### 4. Run the Agent

```python
from src.llm.provider import create_llm_provider

# Create agent with local LLM
llm_provider = create_llm_provider(
    provider_type="ollama",
    model_name="llama2",
    temperature=0.7,
    streaming=True  # Stream responses for real-time feedback
)

llm = llm_provider.get_llm()

# Use in portfolio agent
from src.agent.portfolio_agent import PortfolioHealthAgent
agent = PortfolioHealthAgent(llm=llm)
```

## Performance Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| Llama 2 7B | 4GB | Fast | Good | CPU, Local |
| Mistral 7B | 4GB | Fast | Better | CPU, Local |
| Llama 2 13B | 8GB | Medium | Better | GPU with 8GB+ |
| Neural Chat 7B | 4GB | Fast | Good | Domain-specific |

## System Requirements

### Minimum (CPU only)
- 8GB RAM
- 10GB disk space
- Any modern CPU

### Recommended (for faster inference)
- GPU with CUDA support (NVIDIA)
- 16GB+ RAM
- SSD storage

## Configuration Options

### Via Environment Variables

```bash
export LLM_PROVIDER=ollama
export LLM_MODEL=llama2
export LLM_BASE_URL=http://localhost:11434
export LLM_TEMPERATURE=0.7
```

### Via Python Configuration

```python
from src.config import LLMConfig

config = LLMConfig(
    provider="ollama",
    model_name="llama2",
    base_url="http://localhost:11434",
    temperature=0.7,
    streaming=True,
)
```

## Troubleshooting

### Ollama Connection Failed

```bash
# Make sure Ollama is running
ollama serve

# Check if server is responding
curl http://localhost:11434/api/tags

# Verify port availability
lsof -i :11434
```

### Model Too Slow

Try a faster model:
```bash
ollama pull mistral  # Generally faster than Llama 2
```

### Out of Memory

Reduce model size or enable GPU:
```bash
# Use smaller model
ollama pull neural-chat

# Enable NVIDIA GPU (if available)
export CUDA_VISIBLE_DEVICES=0
ollama serve
```

### Poor Response Quality

Adjust temperature:
```python
# Lower temperature = more consistent (0.1-0.5)
llm = create_llm_provider("ollama", temperature=0.3)

# Higher temperature = more creative (0.7-1.0)
llm = create_llm_provider("ollama", temperature=0.9)
```

## Comparing Providers

### Cost Comparison

```
Provider      | Setup Cost | Per Request | Offline
--------------------------------------------------
Ollama        | Free       | $0          | Yes
OpenAI GPT3.5 | Free       | $0.002      | No
HuggingFace   | Free       | $0.004      | No
```

### Latency (First Response)

```
Provider      | 1st Response | Subsequent
----------------------------------------
Ollama (CPU)  | 500-2000ms   | 100-500ms
Ollama (GPU)  | 100-300ms    | 50-100ms
OpenAI        | 500-1000ms   | 500-1000ms
HuggingFace   | 1000-3000ms  | 1000-3000ms
```

## Advanced: GPU Acceleration

### NVIDIA GPU Setup

```bash
# Install NVIDIA Docker runtime
docker install nvidia-docker

# Run Ollama with GPU
docker run --gpus all -d -v ollama:/root/.ollama \
  -p 11434:11434 --name ollama ollama/ollama

# Pull and run model
docker exec ollama ollama pull llama2
```

### macOS Metal Acceleration

Ollama automatically uses Metal GPU on Apple Silicon. No additional setup needed.

## Best Practices

1. **Start with Ollama + Llama2** - Best balance of speed and quality
2. **Use streaming** for real-time feedback in agent responses
3. **Keep model running** - Don't stop Ollama server between requests
4. **Monitor performance** - Watch response latency and quality
5. **Choose appropriate temperature** - Lower for consistency, higher for creativity

## Example: Production Setup

```python
import os
from src.llm.provider import create_llm_provider

def get_llm():
    """Get LLM based on environment configuration"""
    provider = os.getenv("LLM_PROVIDER", "ollama")
    
    if provider == "ollama":
        return create_llm_provider(
            provider_type="ollama",
            model_name=os.getenv("LLM_MODEL", "llama2"),
            base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            streaming=os.getenv("LLM_STREAMING", "true").lower() == "true",
        )
    elif provider == "openai":
        return create_llm_provider(
            provider_type="openai",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
        )
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

# Usage
llm = get_llm()
```

## Resources

- [Ollama Official](https://ollama.ai)
- [Ollama Models](https://ollama.ai/library)
- [LangChain + Ollama](https://python.langchain.com/docs/integrations/llms/ollama)
- [Open Source LLM Benchmarks](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)
