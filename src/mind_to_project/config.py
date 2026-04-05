import os
from pathlib import Path

import openai
import pydantic
import yaml
from pydantic import BaseModel

from mind_to_project.errors import ProjectInitError


class Provider(BaseModel):
    base_url: str
    api_key_env: str


class PipelineStep(BaseModel):
    provider: str
    model: str


class Pipeline(BaseModel):
    cleanup: PipelineStep
    extract: PipelineStep


class Config(BaseModel):
    providers: dict[str, Provider]
    pipeline: Pipeline


def load_config(config_dir_path: Path) -> Config:
    config_file = config_dir_path / "config.yaml"

    if not config_file.exists():
        raise ProjectInitError(
            "Config not found. Run 'mind-to-project setup' to initialize."
        )

    try:
        raw_config = yaml.safe_load(config_file.read_text())
    except yaml.YAMLError as e:
        raise ProjectInitError(f"Invalid YAML in config file: {e}")

    try:
        config = Config(**raw_config)
    except pydantic.ValidationError as e:
        raise ProjectInitError(f"Config validation error: {e}")

    for step_name, step in [
        ("cleanup", config.pipeline.cleanup),
        ("extract", config.pipeline.extract),
    ]:
        if step.provider not in config.providers:
            raise ProjectInitError(
                f"Unknown provider '{step.provider}' in pipeline.{step_name}"
            )

    return config


def build_client(provider: Provider) -> openai.OpenAI:
    api_key = os.environ.get(provider.api_key_env)

    if not api_key:
        raise ProjectInitError(f"API key not found for {provider.api_key_env}")

    return openai.OpenAI(base_url=provider.base_url, api_key=api_key)
