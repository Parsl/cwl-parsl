"""This package provides a CWLApp class to run CWL Command Line Tools."""

from cwl.cwl_app.cwl_app import CWLApp
from cwl.cwl_app.validate import validate

__all__ = ['CWLApp', 'validate']