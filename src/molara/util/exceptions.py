"""Exceptions for the structure module."""

from __future__ import annotations


class FileImporterError(Exception):
    """base class for errors occurring when loading molecules from file."""


class FileExporterError(Exception):
    """Base class for errors occurring when loading molecules from file."""


class FileFormatError(ValueError):
    """raised when the file format is wrong or unsupported."""
