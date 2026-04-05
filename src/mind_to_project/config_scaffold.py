from pathlib import Path

DEFAULT_CONFIG = """providers:
  cleanup:
    base_url: https://api.anthropic.com
    api_key_env: ANTHROPIC_API_KEY

  extract:
    base_url: https://api.anthropic.com
    api_key_env: ANTHROPIC_API_KEY

pipeline:
  cleanup:
    provider: cleanup
    model: claude-3-5-haiku-20241022

  extract:
    provider: extract
    model: claude-3-5-sonnet-20241022
"""

DEFAULT_PROMPT_CLEANUP = """# Cleanup Prompt

Clean up and format the following content:

{{content}}
"""

DEFAULT_PROMPT_EXTRACT = """# Extract Prompt

Extract and structure information from the following content:

{{content}}
"""


def setup_config(config_dir: Path) -> None:
    """
    Scaffold config directory with default files if they don't exist.

    Creates:
    - config.yaml with default providers and pipeline configuration
    - prompts/cleanup.md with default cleanup template
    - prompts/extract.md with default extract template

    Never overwrites existing files.
    """
    config_dir.mkdir(parents=True, exist_ok=True)

    _write_if_missing(config_dir / "config.yaml", DEFAULT_CONFIG)

    prompts_dir = config_dir / "prompts"
    prompts_dir.mkdir(exist_ok=True)
    _write_if_missing(prompts_dir / "cleanup.md", DEFAULT_PROMPT_CLEANUP)
    _write_if_missing(prompts_dir / "extract.md", DEFAULT_PROMPT_EXTRACT)


def _write_if_missing(file_path: Path, content: str) -> None:
    """Write content to file only if it doesn't already exist."""
    if not file_path.exists():
        file_path.write_text(content)
