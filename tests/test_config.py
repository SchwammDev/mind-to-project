from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from project_init.config import build_client, load_config
from project_init.errors import ProjectInitError
from tests.conftest import SAMPLE_CONFIG


class TestLoadConfig:
    def test_loads_providers_and_pipeline_steps(self, config_dir: Path):
        config = load_config(config_dir)

        assert "fast" in config.providers
        assert config.providers["fast"].base_url == "https://api.groq.com/openai/v1"
        assert config.providers["fast"].api_key_env == "GROQ_API_KEY"

        assert config.pipeline.cleanup.provider == "fast"
        assert config.pipeline.cleanup.model == "llama-3.1-70b-versatile"
        assert config.pipeline.extract.provider == "capable"

    def test_fails_when_config_file_is_missing(self, tmp_path: Path):
        empty_config_dir = tmp_path / "config"
        empty_config_dir.mkdir()

        with pytest.raises(ProjectInitError, match="setup"):
            load_config(empty_config_dir)

    def test_fails_on_malformed_yaml(self, tmp_path: Path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "config.yaml").write_text(": invalid: yaml: [")

        with pytest.raises(ProjectInitError):
            load_config(config_dir)

    def test_rejects_provider_without_base_url(self, config_dir: Path):
        broken = SAMPLE_CONFIG.copy()
        broken["providers"] = {"broken": {"api_key_env": "SOME_KEY"}}
        (config_dir / "config.yaml").write_text(yaml.dump(broken))

        with pytest.raises(ProjectInitError):
            load_config(config_dir)

    def test_rejects_provider_without_api_key_env(self, config_dir: Path):
        broken = SAMPLE_CONFIG.copy()
        broken["providers"] = {"broken": {"base_url": "https://example.com"}}
        (config_dir / "config.yaml").write_text(yaml.dump(broken))

        with pytest.raises(ProjectInitError):
            load_config(config_dir)

    def test_rejects_pipeline_step_referencing_unknown_provider(self, config_dir: Path):
        broken = SAMPLE_CONFIG.copy()
        broken["pipeline"] = {
            "cleanup": {"provider": "nonexistent", "model": "some-model"},
            "extract": {"provider": "capable", "model": "some-model"},
        }
        (config_dir / "config.yaml").write_text(yaml.dump(broken))

        with pytest.raises(ProjectInitError, match="nonexistent"):
            load_config(config_dir)

    def test_rejects_pipeline_step_without_model(self, config_dir: Path):
        broken = SAMPLE_CONFIG.copy()
        broken["pipeline"] = {
            "cleanup": {"provider": "fast"},
            "extract": {"provider": "capable", "model": "some-model"},
        }
        (config_dir / "config.yaml").write_text(yaml.dump(broken))

        with pytest.raises(ProjectInitError):
            load_config(config_dir)


class TestBuildClient:
    def test_builds_client_with_correct_base_url_and_api_key(self, config_dir: Path):
        config = load_config(config_dir)
        provider = config.providers["fast"]

        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key-123"}):
            client = build_client(provider)

        assert client.base_url.host == "api.groq.com"

    def test_fails_when_api_key_env_var_is_not_set(self, config_dir: Path):
        config = load_config(config_dir)
        provider = config.providers["fast"]

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ProjectInitError, match="GROQ_API_KEY"):
                build_client(provider)
