"""Utility for loading Qt .ui files directly into widget instances."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QFile, QIODevice, QMetaObject
from PySide6.QtUiTools import QUiLoader

if TYPE_CHECKING:
    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import QWidget

_UI_DIR = Path(__file__).parent


class _UiLoader(QUiLoader):
    """Custom QUiLoader that loads a .ui file into an existing widget instance.

    This makes QUiLoader behave similarly to PyQt5's uic.loadUi():
    child widgets are set as attributes on the base instance so they can be
    accessed as ``self.ui.<widget_name>`` after ``self.ui = load_ui(..., self)``.
    """

    def __init__(self, base_instance: QWidget) -> None:
        """Initialise the loader for the given base widget.

        :param base_instance: The existing widget that the UI will be loaded into.
        """
        super().__init__(base_instance)
        self._base_instance = base_instance

    def createWidget(self, class_name: str, parent: QWidget | None = None, name: str = "") -> QWidget:  # noqa: N802
        """Create a widget during .ui loading.

        For the root widget (parent is None) the existing base instance is
        returned so the loader configures it in-place.  All other widgets are
        created normally and additionally stored as attributes on the base
        instance so that ``base_instance.<name>`` works.

        :param class_name: Qt class name of the widget to create.
        :param parent: Parent widget (None for the root widget).
        :param name: Object name of the widget.
        """
        if parent is None and self._base_instance is not None:
            return self._base_instance
        widget = super().createWidget(class_name, parent, name)
        if self._base_instance is not None and name:
            setattr(self._base_instance, name, widget)
        return widget

    def createAction(self, parent: QWidget | None = None, name: str = "") -> QAction:  # noqa: N802
        """Create an action during .ui loading and store it on the base instance.

        :param parent: Parent object of the action.
        :param name: Object name of the action.
        """
        action = super().createAction(parent, name)
        if self._base_instance is not None and name:
            setattr(self._base_instance, name, action)
        return action


def load_ui(ui_name: str, base_instance: QWidget) -> QWidget:
    """Load a .ui file into an existing widget instance.

    Replaces the ``Ui_*`` / ``setupUi`` pattern from generated ui_*.py files.
    After the call, all named child widgets and actions defined in the .ui file
    are accessible as attributes on *base_instance*, so the existing
    ``self.ui.<widget_name>`` access pattern continues to work when the caller
    assigns ``self.ui = load_ui(..., self)``.

    :param ui_name: Filename of the .ui file (e.g. ``"form.ui"``).
    :param base_instance: The widget instance to load the UI into.
    :returns: *base_instance* with child widgets attached as attributes.
    :raises RuntimeError: If the .ui file cannot be opened.
    """
    # avoid circular import (StructureWidget imports load_ui on module level)
    from molara.gui.structure_widget import StructureWidget  # noqa: PLC0415

    loader = _UiLoader(base_instance)
    loader.registerCustomWidget(StructureWidget)

    ui_path = _UI_DIR / ui_name
    ui_file = QFile(str(ui_path))
    if not ui_file.open(QIODevice.OpenModeFlag.ReadOnly):
        msg = f"Cannot open UI file '{ui_path}': {ui_file.errorString()}"
        raise RuntimeError(msg)
    loader.load(ui_file)
    ui_file.close()

    QMetaObject.connectSlotsByName(base_instance)
    return base_instance
