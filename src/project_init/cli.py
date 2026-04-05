import argparse
import sys
from pathlib import Path

from project_init.config import load_config  # noqa: F401 - imported for test mocking
from project_init.config_scaffold import setup_config
from project_init.errors import ProjectInitError
from project_init.pipeline import run_cleanup, run_extract, run_pipeline


def get_config_dir() -> Path:
    return Path.home() / ".config" / "project-init"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        "project-init",
        description="Convert raw brain-dump into clean project description",
    )

    commands = parser.add_subparsers(dest="command", title="commands")

    init_parser = commands.add_parser("init", help="Run full transformation pipeline")
    init_parser.add_argument("--dir", default=".", help="Directory containing raw file")
    init_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing output"
    )

    clean_parser = commands.add_parser("clean", help="Run cleanup step only")
    clean_parser.add_argument(
        "--dir", default=".", help="Directory containing raw file"
    )
    clean_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing output"
    )

    extract_parser = commands.add_parser("extract", help="Run extract step only")
    extract_parser.add_argument(
        "--dir", default=".", help="Directory containing cleaned file"
    )
    extract_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing output"
    )

    commands.add_parser("setup", help="Initialize config directory")

    args = parser.parse_args(argv)

    if args.command is None:
        args = parser.parse_args(["init"])

    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    config_dir = get_config_dir()

    try:
        match args.command:
            case "init":
                run_pipeline(args.dir, config_dir, force=args.force)
            case "clean":
                run_cleanup(
                    Path(args.dir) / "Project_Overview.raw.md",
                    config_dir,
                    force=args.force,
                )
            case "extract":
                run_extract(
                    Path(args.dir) / "Project_Overview.raw.cleaned.md",
                    config_dir,
                    force=args.force,
                )
            case "setup":
                setup_config(config_dir)
    except ProjectInitError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
