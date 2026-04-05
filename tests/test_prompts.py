from pathlib import Path

import pytest

from mind_to_project.prompts import load_prompt
from mind_to_project.errors import ProjectInitError


class TestLoadPrompt:
    def test_substitutes_content_into_template(self, config_dir: Path):
        template_path = config_dir / "prompts" / "cleanup.md"
        brain_dump = "some raw notes about the project"

        result = load_prompt(template_path, brain_dump)

        assert "some raw notes about the project" in result
        assert "{{content}}" not in result

    def test_preserves_template_text_around_content(self, config_dir: Path):
        template_path = config_dir / "prompts" / "cleanup.md"

        result = load_prompt(template_path, "my notes")

        assert result.startswith("Clean up the following")
        assert "my notes" in result

    def test_fails_when_template_file_is_missing(self, tmp_path: Path):
        missing_template = tmp_path / "prompts" / "nonexistent.md"

        with pytest.raises(ProjectInitError, match="setup"):
            load_prompt(missing_template, "content")

    def test_works_with_multiline_content(self, config_dir: Path):
        template_path = config_dir / "prompts" / "extract.md"
        multiline_content = "line one\nline two\nline three"

        result = load_prompt(template_path, multiline_content)

        assert "line one\nline two\nline three" in result
