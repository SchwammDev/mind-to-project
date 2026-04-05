from pathlib import Path

from project_init.errors import ProjectInitError


def load_prompt(template_path: Path, content: str) -> str:
    template_path = Path(template_path)

    if not template_path.exists():
        raise ProjectInitError(
            f"Prompt template not found: {template_path}. Run 'project-init setup' to initialize."
        )

    template = template_path.read_text()
    return template.replace("{{content}}", content)
