from pathlib import Path


from mind_to_project.config import load_config, build_client
from mind_to_project.prompts import load_prompt
from mind_to_project.errors import ProjectInitError


def call_ai(config, pipeline_step: str, prompt: str) -> str:
    step_config = getattr(config.pipeline, pipeline_step)
    provider_config = config.providers[step_config.provider]

    client = build_client(provider_config)

    response = client.chat.completions.create(
        model=step_config.model,
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message.content
    if content is None:
        raise ProjectInitError(f"AI returned empty response for {pipeline_step}")
    return content


def run_cleanup(raw_file: Path, config_dir: Path, force: bool = False) -> Path:
    raw_file = Path(raw_file)

    if not raw_file.exists():
        raise ProjectInitError(f"Raw file not found: {raw_file}")

    if raw_file.suffix != ".md":
        raise ProjectInitError(f"Expected .md file, got: {raw_file}")

    cleaned_file = raw_file.with_name(f"{raw_file.stem}.cleaned.md")

    if cleaned_file.exists() and not force:
        raise ProjectInitError(
            f"Cleaned file already exists: {cleaned_file}. Use --force to overwrite."
        )

    config = load_config(config_dir)
    template_path = config_dir / "prompts" / "cleanup.md"
    prompt = load_prompt(template_path, raw_file.read_text())

    response = call_ai(config, "cleanup", prompt)
    cleaned_file.write_text(response)

    return cleaned_file


def run_extract(cleaned_file: Path, config_dir: Path, force: bool = False) -> Path:
    cleaned_file = Path(cleaned_file)

    if not cleaned_file.exists():
        raise ProjectInitError(f"Cleaned file not found: {cleaned_file}")

    output_file = cleaned_file.with_name(
        cleaned_file.stem.replace(".raw.cleaned", "") + ".md"
    )

    if output_file.exists() and not force:
        raise ProjectInitError(
            f"Output file already exists: {output_file}. Use --force to overwrite."
        )

    config = load_config(config_dir)
    template_path = config_dir / "prompts" / "extract.md"
    prompt = load_prompt(template_path, cleaned_file.read_text())

    response = call_ai(config, "extract", prompt)
    output_file.write_text(response)

    return output_file


def run_pipeline(directory: Path, config_dir: Path, force: bool = False) -> Path:
    directory = Path(directory)

    raw_file = directory / "Project_Overview.raw.md"

    if not raw_file.exists():
        raise ProjectInitError(f"Raw file not found: {raw_file}")

    cleaned_file = directory / "Project_Overview.raw.cleaned.md"
    output_file = directory / "Project_Overview.md"

    if cleaned_file.exists():
        run_extract(cleaned_file, config_dir, force=force)
    else:
        run_cleanup(raw_file, config_dir, force=force)
        run_extract(cleaned_file, config_dir, force=force)

    return output_file
