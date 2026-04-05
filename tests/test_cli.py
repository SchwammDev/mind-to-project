from pathlib import Path
from unittest.mock import patch

import pytest

from project_init.cli import parse_args


class TestParseArgs:
    def test_init_is_the_default_when_no_subcommand_given(self):
        args = parse_args(["init"])
        assert args.command == "init"

    def test_init_uses_current_directory_by_default(self):
        args = parse_args(["init"])
        assert args.dir == "."

    def test_init_accepts_custom_directory(self):
        args = parse_args(["init", "--dir", "/some/path"])
        assert args.dir == "/some/path"

    def test_init_force_flag_defaults_to_false(self):
        args = parse_args(["init"])
        assert args.force is False

    def test_init_accepts_force_flag(self):
        args = parse_args(["init", "--force"])
        assert args.force is True

    def test_clean_command(self):
        args = parse_args(["clean"])
        assert args.command == "clean"

    def test_clean_accepts_dir_and_force(self):
        args = parse_args(["clean", "--dir", "/tmp", "--force"])
        assert args.dir == "/tmp"
        assert args.force is True

    def test_extract_command(self):
        args = parse_args(["extract"])
        assert args.command == "extract"

    def test_extract_accepts_dir_and_force(self):
        args = parse_args(["extract", "--dir", "/tmp", "--force"])
        assert args.dir == "/tmp"
        assert args.force is True

    def test_setup_command(self):
        args = parse_args(["setup"])
        assert args.command == "setup"


class TestCliDispatch:
    def test_init_runs_full_pipeline(self, raw_file: Path, config_dir: Path):
        with (
            patch("project_init.cli.run_pipeline") as mock_pipeline,
            patch("project_init.cli.load_config"),
            patch("project_init.cli.get_config_dir", return_value=config_dir),
        ):
            from project_init.cli import main

            main(["init", "--dir", str(raw_file.parent)])

        mock_pipeline.assert_called_once()

    def test_clean_runs_cleanup_only(self, raw_file: Path, config_dir: Path):
        with (
            patch("project_init.cli.run_cleanup") as mock_cleanup,
            patch("project_init.cli.load_config"),
            patch("project_init.cli.get_config_dir", return_value=config_dir),
        ):
            from project_init.cli import main

            main(["clean", "--dir", str(raw_file.parent)])

        mock_cleanup.assert_called_once()

    def test_extract_runs_extract_only(self, cleaned_file: Path, config_dir: Path):
        with (
            patch("project_init.cli.run_extract") as mock_extract,
            patch("project_init.cli.load_config"),
            patch("project_init.cli.get_config_dir", return_value=config_dir),
        ):
            from project_init.cli import main

            main(["extract", "--dir", str(cleaned_file.parent)])

        mock_extract.assert_called_once()

    def test_setup_scaffolds_config(self, tmp_path: Path):
        with patch("project_init.cli.setup_config") as mock_setup:
            from project_init.cli import main

            main(["setup"])

        mock_setup.assert_called_once()

    def test_exits_with_code_1_on_project_init_error(self, tmp_path: Path):
        with (
            patch(
                "project_init.cli.run_pipeline",
                side_effect=__import__(
                    "project_init.errors", fromlist=["ProjectInitError"]
                ).ProjectInitError("something broke"),
            ),
            patch("project_init.cli.load_config"),
            patch("project_init.cli.get_config_dir", return_value=tmp_path),
            pytest.raises(SystemExit, match="1"),
        ):
            from project_init.cli import main

            main(["init", "--dir", str(tmp_path)])

    def test_shows_plain_error_message_without_traceback(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ):
        with (
            patch(
                "project_init.cli.run_pipeline",
                side_effect=__import__(
                    "project_init.errors", fromlist=["ProjectInitError"]
                ).ProjectInitError("config file not found"),
            ),
            patch("project_init.cli.load_config"),
            patch("project_init.cli.get_config_dir", return_value=tmp_path),
            pytest.raises(SystemExit),
        ):
            from project_init.cli import main

            main(["init", "--dir", str(tmp_path)])

        captured = capsys.readouterr()
        assert "config file not found" in captured.err
        assert "Traceback" not in captured.err
