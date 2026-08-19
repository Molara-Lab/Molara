"""Tests for Qt .ui loader helpers."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest
from PySide6.QtWidgets import QWidget

from molara.gui.layouts.loader import load_ui

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


def test_load_ui_missing_ui_file(qtbot: QtBot) -> None:
    """Should raise RuntimeError when .ui file cannot be opened."""
    base_widget = QWidget()
    qtbot.addWidget(base_widget)

    missing_ui = "molera.ui"
    msg = re.escape("Cannot open UI file '") + r".*" + re.escape(missing_ui) + re.escape("':")

    with pytest.raises(RuntimeError, match=msg):
        load_ui(missing_ui, base_widget)
