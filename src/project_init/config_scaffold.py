from pathlib import Path

from project_init import errors


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

    _create_default_config(config_dir)
    _create_default_prompts(config_dir)


def _create_default_config(config_dir: Path) -> None:
    config_file = config_dir / "config.yaml"

    if config_file.exists():
        return

    default_config = """providers:
  cleanup:
    base_url: https://api.anthropic.com
    model: claude-3-5-haiku-20241022
    api_key_env_var: ANTHROPIC_API_KEY

  extract:
    base_url: https://api.anthropic.com
    model: claude-3-5-sonnet-20241022
    api_key_env_var: ANTHROPIC_API_KEY

pipeline:
  cleanup:
    provider: cleanup

  extract:
    provider: extract
"""
    config_file.write_text(default_config)


def _create_default_prompts(config_dir: Path) -> None:
    prompts_dir = config_dir / "prompts"
    prompts_dir.mkdir(exist_ok=True)

    cleanup_file = prompts_dir / "cleanup.md"
    if not cleanup_file.exists():
        cleanup_file.write_text("""# Cleanup Prompt

Clean up and format the following content:

{{content}}
""")

    extract_file = prompts_dir / "extract.md"
    if not extract_file.exists():
        extract_file.write_text("""# Extract Prompt

Extract and structure information from the following content:

{{content}}
""")
