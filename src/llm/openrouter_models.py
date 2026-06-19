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
    sleep_between_calls: float = 1.0  # seconds; increase for rate-limited premium models
    base_url: str = OPENROUTER_BASE_URL
    api_key_env: str = "OPENROUTER_API_KEY"


MODEL_SPECS: dict[str, ModelSpec] = {
    "gpt55": ModelSpec(
        key="gpt55",
        slug="openai/gpt-5.5",
        tag="GPT55",
        label="GPT-5.5",
        sleep_between_calls=3.0,
    ),
    "gemini31pro": ModelSpec(
        key="gemini31pro",
        slug="google/gemini-3.1-pro-preview",
        tag="GEMINI31PRO",
        label="Gemini 3.1 Pro",
        sleep_between_calls=3.0,
    ),
    "mistrallarge3": ModelSpec(
        key="mistrallarge3",
        slug="mistral-large-2512",
        tag="MISTRALLARGE3",
        label="Mistral Large 3",
        sleep_between_calls=0.5,
        base_url=MISTRAL_BASE_URL,
        api_key_env="MISTRAL_API_KEY",
    ),
    "deepseekv3": ModelSpec(
        key="deepseekv3",
        slug="deepseek/deepseek-chat",
        tag="DEEPSEEKV3",
        label="DeepSeek V3",
        sleep_between_calls=0.5,
    ),
    "qwen35max": ModelSpec(
        key="qwen35max",
        slug="qwen/qwen3-max",
        tag="QWEN35MAX",
        label="Qwen 3.5 Max",
        sleep_between_calls=1.0,
    ),
    "llama33": ModelSpec(
        key="llama33",
        slug="llama-3.3-70b-versatile",
        tag="LLAMA33",
        label="Llama 3.3 70B Instruct",
        sleep_between_calls=0.5,
        base_url=GROQ_BASE_URL,
        api_key_env="GROQ_API_KEY",
    ),
}
