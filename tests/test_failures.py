"""Tests for checking various failures"""

import pytest

from tools import cat, find, touch, wc


def test_missing_args() -> None:
    """Test for various CWLApps with missing arguments."""

    # Test 1: # missing redirect_to_file, output_file args
    with pytest.raises(Exception):
        find(
            dir=".",
            maxdepth=3,
            name="*.cwl",
        )

    # Test 2: # missing output_files arg
    with pytest.raises(Exception):
        touch(filenames=["touch1.txt", "touch2.txt"])
