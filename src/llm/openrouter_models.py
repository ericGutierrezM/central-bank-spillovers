from dataclasses import dataclass


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MISTRAL_BASE_URL = "https://api.mistral.ai/v1"


@dataclass(frozen=True)
class ModelSpec:
    key: str
    slug: str
    tag: str
    label: str
    rpm: int = 60  # requests per minute; used by AsyncRateLimiter
    base_url: str = OPENROUTER_BASE_URL
    api_key_env: str = "OPENROUTER_API_KEY"


MODEL_SPECS: dict[str, ModelSpec] = {
    "gpt55": ModelSpec(
        key="gpt55",
        slug="openai/gpt-5.5",
        tag="GPT55",
        label="GPT-5.5",
        rpm=20,
    ),
    "gemini31pro": ModelSpec(
        key="gemini31pro",
        slug="google/gemini-3.1-pro-preview",
        tag="GEMINI31PRO",
        label="Gemini 3.1 Pro",
        rpm=20,
    ),
    "mistrallarge3": ModelSpec(
        key="mistrallarge3",
        slug="mistral-large-2512",
        tag="MISTRALLARGE3",
        label="Mistral Large 3",
        rpm=60,
        base_url=MISTRAL_BASE_URL,
        api_key_env="MISTRAL_API_KEY",
    ),
    "mistrallarge_or": ModelSpec(
        key="mistrallarge_or",
        slug="mistralai/mistral-large",
        tag="MISTRALLARGE_OR",
        label="Mistral Large (OpenRouter)",
        rpm=300,
    ),
    "deepseekv3": ModelSpec(
        key="deepseekv3",
        slug="deepseek/deepseek-chat",
        tag="DEEPSEEKV3",
        label="DeepSeek V3",
        rpm=60,
    ),
    "qwen35max": ModelSpec(
        key="qwen35max",
        slug="qwen/qwen3-max",
        tag="QWEN35MAX",
        label="Qwen 3.5 Max",
        rpm=20,  # OpenRouter hard cap due to high demand
    ),
    "qwen25_72b": ModelSpec(
        key="qwen25_72b",
        slug="qwen/qwen-2.5-72b-instruct",
        tag="QWEN25_72B",
        label="Qwen 2.5 72B Instruct",
        rpm=60,
    ),

    "gpt-4o": ModelSpec(
        key="gpt-4o",
        slug="openai/gpt-4o-mini",
        tag="GPT4O",
        label="GPT-4o Mini",
        rpm=60,
    ),
    "gpt41nano": ModelSpec(
        key="gpt41nano",
        slug="openai/gpt-4.1-nano",
        tag="GPT41NANO",
        label="GPT-4.1 Nano",
        rpm=60,
    ),
    "gemma4": ModelSpec(
        key="gemma4",
        slug="google/gemma-3-27b-it",  # verify slug on openrouter.ai/models
        tag="GEMMA4",
        label="Gemma 4 31B",
        rpm=60,
    ),
    "deepseekv3flash": ModelSpec(
        key="deepseekv3flash",
        slug="deepseek/deepseek-chat-v3-5",  # verify slug on openrouter.ai/models
        tag="DEEPSEEKV3FLASH",
        label="DeepSeek V3 Flash",
        rpm=60,
    ),
    "gemini25flash": ModelSpec(
        key="gemini25flash",
        slug="google/gemini-2.5-flash",
        tag="GEMINI25FLASH",
        label="Gemini 2.5 Flash",
        rpm=60,
    ),
    "gemini25flashlite": ModelSpec(
        key="gemini25flashlite",
        slug="google/gemini-2.5-flash-lite-preview",  # verify slug on openrouter.ai/models
        tag="GEMINI25FLASHLITE",
        label="Gemini 2.5 Flash Lite",
        rpm=60,
    ),

    "claude3haiku": ModelSpec(
        key="claude3haiku",
        slug="anthropic/claude-3-haiku",
        tag="CLAUDE3HAIKU",
        label="Claude 3 Haiku",
        rpm=60,
    ),
    "llama33": ModelSpec(
        key="llama33",
        slug="llama-3.3-70b-versatile",
        tag="LLAMA33",
        label="Llama 3.3 70B Instruct",
        rpm=200,
        base_url=GROQ_BASE_URL,
        api_key_env="GROQ_API_KEY",
    ),
}
