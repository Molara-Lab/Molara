################################################################################
## Form generated from reading UI file 'supercell_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################
from __future__ import annotations

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    QTime,
    QUrl,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QSizePolicy,
    QSpinBox,
    QWidget,
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Annotated
    intvec3 = Annotated[Sequence[int], 3]

class Ui_Dialog:
    """Class for supercell dialog Gui."""
    def setupUi(self, Dialog):
        """Setup of supercell dialog Gui."""
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setGeometry(QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.inputSupercell_a = QSpinBox(Dialog)
        self.inputSupercell_a.setObjectName("inputSupercell_a")
        self.inputSupercell_a.setGeometry(QRect(50, 50, 42, 26))
        self.inputSupercell_a.setMinimum(1)
        self.inputSupercell_b = QSpinBox(Dialog)
        self.inputSupercell_b.setObjectName("inputSupercell_b")
        self.inputSupercell_b.setGeometry(QRect(130, 50, 42, 26))
        self.inputSupercell_b.setMinimum(1)
        self.inputSupercell_c = QSpinBox(Dialog)
        self.inputSupercell_c.setObjectName("inputSupercell_c")
        self.inputSupercell_c.setGeometry(QRect(210, 50, 42, 26))
        self.inputSupercell_c.setMinimum(1)
        self.labelSupercell_a = QLabel(Dialog)
        self.labelSupercell_a.setObjectName("labelSupercell_a")
        self.labelSupercell_a.setGeometry(QRect(50, 80, 58, 16))
        self.labelSupercell_b = QLabel(Dialog)
        self.labelSupercell_b.setObjectName("labelSupercell_b")
        self.labelSupercell_b.setGeometry(QRect(130, 80, 58, 16))
        self.labelSupercell_c = QLabel(Dialog)
        self.labelSupercell_c.setObjectName("labelSupercell_c")
        self.labelSupercell_c.setGeometry(QRect(210, 80, 58, 16))
        self.labelNumAtoms = QLabel(Dialog)
        self.labelNumAtoms.setObjectName("labelNumAtoms")
        self.labelNumAtoms.setGeometry(QRect(70, 170, 58, 16))

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)

    # setupUi

    def set_supercell_dims(self, supercell_dims: intvec3) -> None:
        """Set supercell dimensions in input boxes."""
        self.inputSupercell_a.setValue(supercell_dims[0])
        self.inputSupercell_b.setValue(supercell_dims[1])
        self.inputSupercell_c.setValue(supercell_dims[2])

    def retranslateUi(self, Dialog):
        """Set labels in dialog."""
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Dialog", None))
        self.labelSupercell_a.setText(
            QCoreApplication.translate("Dialog", "N<sub>a</sub>", None)
        )
        self.labelSupercell_b.setText(
            QCoreApplication.translate("Dialog", "N<sub>b</sub>", None)
        )
        self.labelSupercell_c.setText(
            QCoreApplication.translate("Dialog", "N<sub>c</sub>", None)
        )
        self.labelNumAtoms.setText(
            QCoreApplication.translate("Dialog", "TextLabel", None)
        )

    # retranslateUi
