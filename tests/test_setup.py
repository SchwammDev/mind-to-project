from pathlib import Path

import pytest
import yaml

from project_init.config_scaffold import setup_config


class TestSetupConfig:
    def test_creates_config_directory(self, tmp_path: Path):
        config_dir = tmp_path / ".config" / "project-init"

        setup_config(config_dir)

        assert config_dir.exists()

    def test_creates_default_config_yaml(self, tmp_path: Path):
        config_dir = tmp_path / ".config" / "project-init"

        setup_config(config_dir)

        config_file = config_dir / "config.yaml"
        assert config_file.exists()

        config = yaml.safe_load(config_file.read_text())
        assert "providers" in config
        assert "pipeline" in config

    def test_creates_default_prompt_templates(self, tmp_path: Path):
        config_dir = tmp_path / ".config" / "project-init"

        setup_config(config_dir)

        prompts_dir = config_dir / "prompts"
        assert (prompts_dir / "cleanup.md").exists()
        assert (prompts_dir / "extract.md").exists()

    def test_prompt_templates_contain_content_placeholder(self, tmp_path: Path):
        config_dir = tmp_path / ".config" / "project-init"

        setup_config(config_dir)

        cleanup_template = (config_dir / "prompts" / "cleanup.md").read_text()
        extract_template = (config_dir / "prompts" / "extract.md").read_text()
        assert "{{content}}" in cleanup_template
        assert "{{content}}" in extract_template

    def test_does_not_overwrite_existing_config(self, tmp_path: Path):
        config_dir = tmp_path / ".config" / "project-init"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text("my custom config")

        setup_config(config_dir)

        assert config_file.read_text() == "my custom config"

    def test_does_not_overwrite_existing_prompt_templates(self, tmp_path: Path):
        config_dir = tmp_path / ".config" / "project-init"
        prompts_dir = config_dir / "prompts"
        prompts_dir.mkdir(parents=True)
        (prompts_dir / "cleanup.md").write_text("my custom cleanup prompt")

        setup_config(config_dir)

        assert (prompts_dir / "cleanup.md").read_text() == "my custom cleanup prompt"

    def test_creates_missing_files_alongside_existing_ones(self, tmp_path: Path):
        config_dir = tmp_path / ".config" / "project-init"
        config_dir.mkdir(parents=True)
        (config_dir / "config.yaml").write_text("existing config")

        setup_config(config_dir)

        assert (config_dir / "config.yaml").read_text() == "existing config"
        assert (config_dir / "prompts" / "cleanup.md").exists()
        assert (config_dir / "prompts" / "extract.md").exists()
