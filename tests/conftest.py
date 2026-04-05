from pathlib import Path

import pytest
import yaml


SAMPLE_CONFIG = {
    "providers": {
        "fast": {
            "base_url": "https://api.groq.com/openai/v1",
            "api_key_env": "GROQ_API_KEY",
        },
        "capable": {
            "base_url": "https://api.anthropic.com/v1",
            "api_key_env": "ANTHROPIC_API_KEY",
        },
    },
    "pipeline": {
        "cleanup": {
            "provider": "fast",
            "model": "llama-3.1-70b-versatile",
        },
        "extract": {
            "provider": "capable",
            "model": "claude-sonnet-4-20250514",
        },
    },
}

RAW_BRAIN_DUMP = """\
ok so the idea is basically a todo app but with AI
users can type natural language and it figures out the task
maybe use react? or vue idk
needs auth, probably oauth
deploy on aws or maybe vercel
"""

CLEANED_BRAIN_DUMP = """\
A todo application with AI-powered natural language task input.
Users type in natural language and the system extracts structured tasks.
Frontend: React or Vue (TBD). Authentication: OAuth.
Deployment: AWS or Vercel.
"""

EXTRACTED_PROJECT_OVERVIEW = """\
# Todo AI

## Summary
An AI-powered todo application that converts natural language into structured tasks.

## Tech Stack
- Frontend: React
- Auth: OAuth 2.0
- Deployment: Vercel
"""

CLEANUP_PROMPT_TEMPLATE = """\
Clean up the following raw project notes into coherent prose.

{{content}}
"""

EXTRACT_PROMPT_TEMPLATE = """\
Extract a structured project overview from the following cleaned notes.

{{content}}
"""


@pytest.fixture
def raw_file(tmp_path: Path) -> Path:
    path = tmp_path / "Project_Overview.raw.md"
    path.write_text(RAW_BRAIN_DUMP)
    return path


@pytest.fixture
def cleaned_file(tmp_path: Path) -> Path:
    path = tmp_path / "Project_Overview.raw.cleaned.md"
    path.write_text(CLEANED_BRAIN_DUMP)
    return path


@pytest.fixture
def output_file(tmp_path: Path) -> Path:
    path = tmp_path / "Project_Overview.md"
    path.write_text(EXTRACTED_PROJECT_OVERVIEW)
    return path


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    config_path = tmp_path / "config"
    config_path.mkdir()

    config_file = config_path / "config.yaml"
    config_file.write_text(yaml.dump(SAMPLE_CONFIG))

    prompts_dir = config_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "cleanup.md").write_text(CLEANUP_PROMPT_TEMPLATE)
    (prompts_dir / "extract.md").write_text(EXTRACT_PROMPT_TEMPLATE)

    return config_path
