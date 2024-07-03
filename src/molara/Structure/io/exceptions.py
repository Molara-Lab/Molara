"""Exceptions for the Structure module."""

from __future__ import annotations

class FileImporterError(Exception):
    """base class for errors occurring when loading molecules from file."""


class FileFormatError(FileImporterError):
    """raised when the file format is wrong or unsupported."""