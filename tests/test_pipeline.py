from pathlib import Path
from unittest.mock import patch

import pytest

from mind_to_project.pipeline import run_cleanup, run_extract, run_pipeline
from mind_to_project.errors import ProjectInitError
from tests.conftest import CLEANED_BRAIN_DUMP, EXTRACTED_PROJECT_OVERVIEW


def fake_ai_response(text: str):
    """Create a mock that simulates an OpenAI chat completion response."""
    mock_message = type("Message", (), {"content": text})()
    mock_choice = type("Choice", (), {"message": mock_message})()
    return type("Response", (), {"choices": [mock_choice]})()


class TestCleanupStep:
    def test_reads_raw_file_and_writes_cleaned_output(
        self, raw_file: Path, config_dir: Path
    ):
        with patch("mind_to_project.pipeline.call_ai", return_value=CLEANED_BRAIN_DUMP):
            result_path = run_cleanup(raw_file, config_dir)

        assert result_path.name == "Project_Overview.raw.cleaned.md"
        assert result_path.exists()
        assert result_path.read_text() == CLEANED_BRAIN_DUMP

    def test_refuses_to_overwrite_existing_cleaned_file(
        self, raw_file: Path, cleaned_file: Path, config_dir: Path
    ):
        with pytest.raises(ProjectInitError, match="force"):
            run_cleanup(raw_file, config_dir)

    def test_overwrites_existing_cleaned_file_with_force(
        self, raw_file: Path, cleaned_file: Path, config_dir: Path
    ):
        with patch("mind_to_project.pipeline.call_ai", return_value="new cleaned text"):
            result_path = run_cleanup(raw_file, config_dir, force=True)

        assert result_path.read_text() == "new cleaned text"

    def test_fails_when_raw_file_does_not_exist(self, tmp_path: Path, config_dir: Path):
        missing_raw = tmp_path / "Project_Overview.raw.md"

        with pytest.raises(ProjectInitError):
            run_cleanup(missing_raw, config_dir)


class TestExtractStep:
    def test_reads_cleaned_file_and_writes_final_output(
        self, cleaned_file: Path, config_dir: Path
    ):
        with patch(
            "mind_to_project.pipeline.call_ai", return_value=EXTRACTED_PROJECT_OVERVIEW
        ):
            result_path = run_extract(cleaned_file, config_dir)

        assert result_path.name == "Project_Overview.md"
        assert result_path.exists()
        assert result_path.read_text() == EXTRACTED_PROJECT_OVERVIEW

    def test_refuses_to_overwrite_existing_output(
        self, cleaned_file: Path, output_file: Path, config_dir: Path
    ):
        with pytest.raises(ProjectInitError, match="force"):
            run_extract(cleaned_file, config_dir)

    def test_overwrites_existing_output_with_force(
        self, cleaned_file: Path, output_file: Path, config_dir: Path
    ):
        with patch("mind_to_project.pipeline.call_ai", return_value="new overview"):
            result_path = run_extract(cleaned_file, config_dir, force=True)

        assert result_path.read_text() == "new overview"

    def test_fails_when_cleaned_file_does_not_exist(
        self, tmp_path: Path, config_dir: Path
    ):
        missing_cleaned = tmp_path / "Project_Overview.raw.cleaned.md"

        with pytest.raises(ProjectInitError):
            run_extract(missing_cleaned, config_dir)


class TestFullPipeline:
    def test_runs_cleanup_then_extract(self, raw_file: Path, config_dir: Path):
        ai_responses = iter([CLEANED_BRAIN_DUMP, EXTRACTED_PROJECT_OVERVIEW])

        with patch("mind_to_project.pipeline.call_ai", side_effect=ai_responses):
            run_pipeline(raw_file.parent, config_dir)

        cleaned = raw_file.parent / "Project_Overview.raw.cleaned.md"
        output = raw_file.parent / "Project_Overview.md"
        assert cleaned.exists()
        assert output.exists()
        assert output.read_text() == EXTRACTED_PROJECT_OVERVIEW

    def test_skips_cleanup_when_cleaned_file_already_exists(
        self, raw_file: Path, cleaned_file: Path, config_dir: Path
    ):
        with patch(
            "mind_to_project.pipeline.call_ai", return_value=EXTRACTED_PROJECT_OVERVIEW
        ) as mock_ai:
            run_pipeline(raw_file.parent, config_dir)

        mock_ai.assert_called_once()
        output = raw_file.parent / "Project_Overview.md"
        assert output.read_text() == EXTRACTED_PROJECT_OVERVIEW

    def test_refuses_to_overwrite_final_output_without_force(
        self, raw_file: Path, cleaned_file: Path, output_file: Path, config_dir: Path
    ):
        with pytest.raises(ProjectInitError, match="force"):
            run_pipeline(raw_file.parent, config_dir)

    def test_overwrites_final_output_with_force(
        self, raw_file: Path, cleaned_file: Path, output_file: Path, config_dir: Path
    ):
        with patch("mind_to_project.pipeline.call_ai", return_value="fresh overview"):
            run_pipeline(raw_file.parent, config_dir, force=True)

        assert output_file.read_text() == "fresh overview"

    def test_fails_when_raw_file_does_not_exist_in_directory(
        self, tmp_path: Path, config_dir: Path
    ):
        with pytest.raises(ProjectInitError):
            run_pipeline(tmp_path, config_dir)
