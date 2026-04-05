# project-init — Implementation Plan

## What it does

A CLI tool that turns a raw brain-dump (`Project_Overview.raw.md`) into a clean project description (`Project_Overview.md`) via a two-step AI pipeline.

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
- `pytest` + `pytest-mock` for testing

## Config

All config lives in `~/.config/project-init/`:

```
~/.config/project-init/
  config.yaml
  prompts/
    cleanup.md      # Step 1 prompt template
    extract.md      # Step 2 prompt template
```

`config.yaml` defines providers (base URL + API key env var) and pipeline steps (which provider/model for each step). Config is validated at load time using Pydantic models. Prompt templates are markdown files with a single `{{content}}` placeholder.

## CLI commands

- `init` — run full pipeline (optionally `--dir PATH`, requires `--force` to overwrite existing output); if the cleaned file already exists, step 1 is skipped and the pipeline starts from step 2
- `clean` — step 1 only (requires `--force` to overwrite existing output)
- `extract` — step 2 only (requires cleaned file, requires `--force` to overwrite existing output)
- `setup` — scaffold config dir with defaults

## Implementation steps

**Tests first.** Write tests before any production code. We can batch multiple tests upfront, as long as no production code is written before them.

1. Initialise package with `uv init`, configure `pyproject.toml` (src layout, CLI entry point)
2. Write default prompt templates
3. Config & provider loading — load `config.yaml`, validate with Pydantic, build `openai.OpenAI` client per provider
4. Prompt loading — load template, substitute `{{content}}`
5. Pipeline — orchestrate step 1 and step 2, read/write files
6. CLI — wire up `argparse` commands
7. `setup` command — copy defaults to config dir if not present
8. End-to-end smoke test with a real raw file

## Tests

Run: `uv run pytest tests/<TEST FILE>` (or `uv run pytest -v tests/<TEST FILE>` for verbose output).

| File | Covers |
|---|---|
| `test_config.py` | Config loading, Pydantic validation, client building, missing/invalid config errors |
| `test_prompts.py` | Template loading, `{{content}}` substitution, missing template errors |
| `test_pipeline.py` | Cleanup/extract steps, full pipeline, skip-cleanup logic, overwrite protection |
| `test_cli.py` | Argparse parsing, command dispatch, exit code 1 + plain error messages |
| `test_setup.py` | Config dir scaffolding, default files, no-overwrite of existing config |

Tests define the public API:
- `project_init.config` → `load_config()`, `build_client()`
- `project_init.prompts` → `load_prompt()`
- `project_init.pipeline` → `run_cleanup()`, `run_extract()`, `run_pipeline()`
- `project_init.cli` → `parse_args()`, `main()`
- `project_init.setup` → `setup_config()`
- `project_init.errors` → `ProjectInitError`

## Design decisions

- **Overwrite protection**: all commands that produce output files require `--force` if the target already exists, **except** that `init` silently skips step 1 (cleanup) if the cleaned file already exists — treating it as a cached intermediate
- **Intermediate files**: always written to disk (e.g. `Project_Overview.raw.cleaned.md`) — useful for debugging and re-running individual steps
- **API calls**: wait for full completion, no streaming
- **Error handling**:
  - Fail fast on config/prompt issues — missing files, invalid YAML, Pydantic validation errors, missing API key env vars. Validate everything before starting the pipeline.
  - Point users to `setup` command when config/prompts are missing.
  - No retries on API failures — just fail. Intermediate files on disk make re-running individual steps cheap.
  - Single `ProjectInitError` base exception. Plain English error messages, no tracebacks, `sys.exit(1)`.
