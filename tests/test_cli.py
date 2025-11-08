"""Tests for the CLI module."""

import tempfile
import os


def test_main_with_valid_args_dry_run():
    """Test main function with valid arguments using dry-run to avoid workflow execution."""
    from tdd_agents.cli import main

    # Create a temporary file with test content
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write("# Test Kata\n\nThis is a test kata description.")
        temp_file_path = f.name

    try:
        # Test with valid arguments and dry-run
        result = main([temp_file_path, "--dry-run"])
        assert result == 0
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


def test_main_with_model_and_provider_dry_run():
    """Test main function with model and provider arguments using dry-run."""
    from tdd_agents.cli import main

    # Create a temporary file with test content
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
        f.write("# Test Kata\n\nThis is a test kata description.")
        temp_file_path = f.name

    try:
        # Test with model and provider arguments and dry-run
        result = main(
            [
                temp_file_path,
                "--model",
                "test-model",
                "--provider",
                "test-provider",
                "--dry-run",
            ]
        )
        assert result == 0
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)
