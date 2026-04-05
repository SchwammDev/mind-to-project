# mind-to-project

A CLI tool that turns a raw brain-dump (`Project_Overview.raw.md`) into a clean project description (`Project_Overview.md`) via a two-step AI pipeline.

## Installation

```bash
uv tool install git+https://github.com/bernhard-raml/mind-to-project.git
```

```
Project_Overview.raw.md
        ↓  [Step 1: cleanup — lightweight model]
Project_Overview.raw.cleaned.md
        ↓  [Step 2: extract — capable model]
Project_Overview.md
```

## Tech stack

- Python, `src/` layout, managed with `uv`
- `argparse` for CLI
- `openai` SDK for all providers (Anthropic, Groq, Ollama, etc. via custom `base_url`)
- `pydantic` for config validation
- `pyyaml` for config loading

## CLI commands

- `init` — run full pipeline (optionally `--dir PATH`, requires `--force` to overwrite existing output); if the cleaned file already exists, step 1 is skipped and the pipeline starts from step 2
- `clean` — step 1 only (requires `--force` to overwrite existing output)
- `extract` — step 2 only (requires cleaned file, requires `--force` to overwrite existing output)
- `setup` — scaffold config dir with defaults

## Config

All config lives in `~/.config/mind-to-project/`:

```
~/.config/mind-to-project/
  config.yaml
  prompts/
    cleanup.md      # Step 1 prompt template
    extract.md      # Step 2 prompt template
```

`config.yaml` defines providers (base URL + API key env var) and pipeline steps (which provider/model for each step). Config is validated at load time using Pydantic models. Prompt templates are markdown files with a single `{{content}}` placeholder.

## Running tests

Run: `./run-tests.sh` or `./run-tests.sh -v` for verbose output or `./run-tests.sh tests/<TEST FILE>` for specific test suits.

## Design decisions

- **Overwrite protection**: all commands that produce output files require `--force` if the target already exists, **except** that `init` silently skips step 1 (cleanup) if the cleaned file already exists — treating it as a cached intermediate
- **Intermediate files**: always written to disk (e.g. `Project_Overview.raw.cleaned.md`) — useful for debugging and re-running individual steps
- **Error handling**: Fail fast on config/prompt issues. Point users to `setup` command when config/prompts are missing. No retries on API failures.