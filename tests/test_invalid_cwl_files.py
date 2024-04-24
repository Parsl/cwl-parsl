"""Tests for invalid CWL files"""

import os

import pytest

from cwl.CWLApp import CWLApp

invalid_cwl_files = os.path.join(os.getcwd(), "tests", "invalid-cwl-files")


def test_invalid_output_type() -> None:
    """Test for the wc CWL CommandLineTool with invalid output type."""
    with pytest.raises(Exception):
        CWLApp(os.path.join(invalid_cwl_files, "wc_invalid.cwl"))


def test_invalid_dict_keys() -> None:
    """Test for the wc CWL CommandLineTool with invalid variable names as dict keys."""
    with pytest.raises(Exception):
        CWLApp(os.path.join(invalid_cwl_files, "touch_invalid.cwl"))
