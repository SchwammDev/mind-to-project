from pathlib import Path

from mind_to_project.errors import ProjectInitError


def load_prompt(template_path: Path, content: str) -> str:
    template_path = Path(template_path)

    if not template_path.exists():
        raise ProjectInitError(
            f"Prompt template not found: {template_path}. Run 'mind-to-project setup' to initialize."
        )

    template = template_path.read_text()
    return template.replace("{{content}}", content)
