from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    key: str
    slug: str
    tag: str
    label: str


MODEL_SPECS: dict[str, ModelSpec] = {
    "gpt55": ModelSpec(
        key="gpt55",
        slug="openai/gpt-5.5",
        tag="GPT55",
        label="GPT-5.5",
    ),
    "gemini31pro": ModelSpec(
        key="gemini31pro",
        slug="google/gemini-3.1-pro-preview",
        tag="GEMINI31PRO",
        label="Gemini 3.1 Pro",
    ),
    "mistrallarge3": ModelSpec(
        key="mistrallarge3",
        slug="mistralai/mistral-large-2512",
        tag="MISTRALLARGE3",
        label="Mistral Large 3",
    ),
    "deepseekv4pro": ModelSpec(
        key="deepseekv4pro",
        slug="deepseek/deepseek-v4-pro",
        tag="DEEPSEEKV4PRO",
        label="DeepSeek V4 Pro",
    ),
    "qwen35max": ModelSpec(
        key="qwen35max",
        slug="qwen/qwen3-max",
        tag="QWEN35MAX",
        label="Qwen 3.5 Max",
    ),
}
