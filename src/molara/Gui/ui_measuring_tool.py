# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'measuring_tool.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

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
    QTime,
    QUrl,
    Qt,
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
    QApplication,
    QDialog,
    QFrame,
    QLabel,
    QSizePolicy,
    QWidget,
)


class Ui_measuring_tool(object):
    def setupUi(self, measuring_tool):
        if not measuring_tool.objectName():
            measuring_tool.setObjectName("measuring_tool")
        measuring_tool.resize(434, 271)
        self.info_text = QLabel(measuring_tool)
        self.info_text.setObjectName("info_text")
        self.info_text.setGeometry(QRect(10, 10, 371, 20))
        self.atom1 = QLabel(measuring_tool)
        self.atom1.setObjectName("atom1")
        self.atom1.setGeometry(QRect(10, 70, 21, 16))
        self.x1 = QLabel(measuring_tool)
        self.x1.setObjectName("x1")
        self.x1.setGeometry(QRect(10, 90, 50, 16))
        self.y1 = QLabel(measuring_tool)
        self.y1.setObjectName("y1")
        self.y1.setGeometry(QRect(70, 90, 50, 16))
        self.z1 = QLabel(measuring_tool)
        self.z1.setObjectName("z1")
        self.z1.setGeometry(QRect(130, 90, 50, 16))
        self.y2 = QLabel(measuring_tool)
        self.y2.setObjectName("y2")
        self.y2.setGeometry(QRect(70, 140, 50, 16))
        self.z2 = QLabel(measuring_tool)
        self.z2.setObjectName("z2")
        self.z2.setGeometry(QRect(130, 140, 50, 16))
        self.atom2 = QLabel(measuring_tool)
        self.atom2.setObjectName("atom2")
        self.atom2.setGeometry(QRect(10, 120, 21, 16))
        self.x2 = QLabel(measuring_tool)
        self.x2.setObjectName("x2")
        self.x2.setGeometry(QRect(10, 140, 50, 16))
        self.y3 = QLabel(measuring_tool)
        self.y3.setObjectName("y3")
        self.y3.setGeometry(QRect(70, 190, 50, 16))
        self.z3 = QLabel(measuring_tool)
        self.z3.setObjectName("z3")
        self.z3.setGeometry(QRect(130, 190, 50, 16))
        self.atom3 = QLabel(measuring_tool)
        self.atom3.setObjectName("atom3")
        self.atom3.setGeometry(QRect(10, 170, 21, 16))
        self.x3 = QLabel(measuring_tool)
        self.x3.setObjectName("x3")
        self.x3.setGeometry(QRect(10, 190, 50, 16))
        self.y4 = QLabel(measuring_tool)
        self.y4.setObjectName("y4")
        self.y4.setGeometry(QRect(70, 240, 50, 16))
        self.z4 = QLabel(measuring_tool)
        self.z4.setObjectName("z4")
        self.z4.setGeometry(QRect(130, 240, 50, 16))
        self.atom4 = QLabel(measuring_tool)
        self.atom4.setObjectName("atom4")
        self.atom4.setGeometry(QRect(10, 220, 21, 16))
        self.x4 = QLabel(measuring_tool)
        self.x4.setObjectName("x4")
        self.x4.setGeometry(QRect(10, 240, 50, 16))
        self.fix1 = QLabel(measuring_tool)
        self.fix1.setObjectName("fix1")
        self.fix1.setGeometry(QRect(190, 70, 71, 16))
        self.line = QFrame(measuring_tool)
        self.line.setObjectName("line")
        self.line.setGeometry(QRect(180, 70, 16, 191))
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.atom1_label = QLabel(measuring_tool)
        self.atom1_label.setObjectName("atom1_label")
        self.atom1_label.setGeometry(QRect(30, 70, 16, 16))
        self.atom4_label = QLabel(measuring_tool)
        self.atom4_label.setObjectName("atom4_label")
        self.atom4_label.setGeometry(QRect(30, 220, 16, 16))
        self.atom3_label = QLabel(measuring_tool)
        self.atom3_label.setObjectName("atom3_label")
        self.atom3_label.setGeometry(QRect(30, 170, 16, 16))
        self.atom2_label = QLabel(measuring_tool)
        self.atom2_label.setObjectName("atom2_label")
        self.atom2_label.setGeometry(QRect(30, 120, 16, 16))
        self.fix3 = QLabel(measuring_tool)
        self.fix3.setObjectName("fix3")
        self.fix3.setGeometry(QRect(320, 70, 31, 16))
        self.fix2 = QLabel(measuring_tool)
        self.fix2.setObjectName("fix2")
        self.fix2.setGeometry(QRect(260, 70, 31, 16))
        self.fix4 = QLabel(measuring_tool)
        self.fix4.setObjectName("fix4")
        self.fix4.setGeometry(QRect(380, 70, 31, 16))
        self.d23 = QLabel(measuring_tool)
        self.d23.setObjectName("d23")
        self.d23.setGeometry(QRect(320, 90, 40, 16))
        self.d12 = QLabel(measuring_tool)
        self.d12.setObjectName("d12")
        self.d12.setGeometry(QRect(260, 90, 40, 16))
        self.d34 = QLabel(measuring_tool)
        self.d34.setObjectName("d34")
        self.d34.setGeometry(QRect(380, 90, 40, 16))
        self.fix5 = QLabel(measuring_tool)
        self.fix5.setObjectName("fix5")
        self.fix5.setGeometry(QRect(190, 90, 71, 16))
        self.a234 = QLabel(measuring_tool)
        self.a234.setObjectName("a234")
        self.a234.setGeometry(QRect(350, 160, 50, 30))
        self.fix3_2 = QLabel(measuring_tool)
        self.fix3_2.setObjectName("fix3_2")
        self.fix3_2.setGeometry(QRect(350, 140, 51, 30))
        self.fix5_2 = QLabel(measuring_tool)
        self.fix5_2.setObjectName("fix5_2")
        self.fix5_2.setGeometry(QRect(190, 160, 71, 30))
        self.a123 = QLabel(measuring_tool)
        self.a123.setObjectName("a123")
        self.a123.setGeometry(QRect(270, 160, 50, 30))
        self.fix2_2 = QLabel(measuring_tool)
        self.fix2_2.setObjectName("fix2_2")
        self.fix2_2.setGeometry(QRect(270, 140, 51, 30))
        self.fix1_2 = QLabel(measuring_tool)
        self.fix1_2.setObjectName("fix1_2")
        self.fix1_2.setGeometry(QRect(190, 140, 71, 30))
        self.d1234 = QLabel(measuring_tool)
        self.d1234.setObjectName("d1234")
        self.d1234.setGeometry(QRect(300, 240, 70, 16))
        self.fix1_3 = QLabel(measuring_tool)
        self.fix1_3.setObjectName("fix1_3")
        self.fix1_3.setGeometry(QRect(190, 220, 71, 16))
        self.fix2_3 = QLabel(measuring_tool)
        self.fix2_3.setObjectName("fix2_3")
        self.fix2_3.setGeometry(QRect(300, 220, 71, 16))
        self.fix5_3 = QLabel(measuring_tool)
        self.fix5_3.setObjectName("fix5_3")
        self.fix5_3.setGeometry(QRect(190, 240, 71, 16))
        self.fix_2 = QLabel(measuring_tool)
        self.fix_2.setObjectName("fix_2")
        self.fix_2.setGeometry(QRect(30, 50, 10, 16))
        self.fix_3 = QLabel(measuring_tool)
        self.fix_3.setObjectName("fix_3")
        self.fix_3.setGeometry(QRect(90, 50, 10, 16))
        self.fix_4 = QLabel(measuring_tool)
        self.fix_4.setObjectName("fix_4")
        self.fix_4.setGeometry(QRect(150, 50, 10, 16))
        self.fix = QLabel(measuring_tool)
        self.fix.setObjectName("fix")
        self.fix.setGeometry(QRect(10, 30, 111, 16))

        self.retranslateUi(measuring_tool)

        QMetaObject.connectSlotsByName(measuring_tool)

    # setupUi

    def retranslateUi(self, measuring_tool):
        measuring_tool.setWindowTitle(
            QCoreApplication.translate("measuring_tool", "Measurement Tool", None)
        )
        self.info_text.setText(
            QCoreApplication.translate("measuring_tool", "TextLabel", None)
        )
        self.atom1.setText(
            QCoreApplication.translate("measuring_tool", "TextLabel", None)
        )
        self.x1.setText(QCoreApplication.translate("measuring_tool", "TextLabel", None))
        self.y1.setText(QCoreApplication.translate("measuring_tool", "TextLabel", None))
        self.z1.setText(QCoreApplication.translate("measuring_tool", "TextLabel", None))
        self.y2.setText(QCoreApplication.translate("measuring_tool", "TextLabel", None))
        self.z2.setText(QCoreApplication.translate("measuring_tool", "TextLabel", None))
        self.atom2.setText(
            QCoreApplication.translate("measuring_tool", "TextLabel", None)
        )
        self.x2.setText(QCoreApplication.translate("measuring_tool", "TextLabel", None))
        self.y3.setText(QCoreApplication.translate("measuring_tool", "TextLabel", None))
        self.z3.setText(QCoreApplication.translate("measuring_tool", "TextLabel", None))
        self.atom3.setText(
            QCoreApplication.translate("measuring_tool", "TextLabel", None)
        )
        self.x3.setText(QCoreApplication.translate("measuring_tool", "TextLabel", None))
        self.y4.setText(QCoreApplication.translate("measuring_tool", "TextLabel", None))
        self.z4.setText(QCoreApplication.translate("measuring_tool", "TextLabel", None))
        self.atom4.setText(
            QCoreApplication.translate("measuring_tool", "TextLabel", None)
        )
        self.x4.setText(QCoreApplication.translate("measuring_tool", "TextLabel", None))
        self.fix1.setText(
            QCoreApplication.translate("measuring_tool", "Distances:", None)
        )
        self.atom1_label.setText(
            QCoreApplication.translate("measuring_tool", "1", None)
        )
        self.atom4_label.setText(
            QCoreApplication.translate("measuring_tool", "4", None)
        )
        self.atom3_label.setText(
            QCoreApplication.translate("measuring_tool", "3", None)
        )
        self.atom2_label.setText(
            QCoreApplication.translate("measuring_tool", "2", None)
        )
        self.fix3.setText(QCoreApplication.translate("measuring_tool", "2 - 3", None))
        self.fix2.setText(QCoreApplication.translate("measuring_tool", "1 - 2", None))
        self.fix4.setText(QCoreApplication.translate("measuring_tool", "3 - 4", None))
        self.d23.setText(QCoreApplication.translate("measuring_tool", "d23", None))
        self.d12.setText(QCoreApplication.translate("measuring_tool", "d12", None))
        self.d34.setText(QCoreApplication.translate("measuring_tool", "d34", None))
        self.fix5.setText(
            QCoreApplication.translate("measuring_tool", "in [\u00c5]", None)
        )
        self.a234.setText(QCoreApplication.translate("measuring_tool", "a234", None))
        self.fix3_2.setText(
            QCoreApplication.translate("measuring_tool", "2 - 3 - 4", None)
        )
        self.fix5_2.setText(
            QCoreApplication.translate("measuring_tool", "in [\u00b0]", None)
        )
        self.a123.setText(QCoreApplication.translate("measuring_tool", "a123", None))
        self.fix2_2.setText(
            QCoreApplication.translate("measuring_tool", "1 - 2 - 3", None)
        )
        self.fix1_2.setText(
            QCoreApplication.translate("measuring_tool", "Angles:", None)
        )
        self.d1234.setText(QCoreApplication.translate("measuring_tool", "d1234", None))
        self.fix1_3.setText(
            QCoreApplication.translate("measuring_tool", "Dihedral:", None)
        )
        self.fix2_3.setText(
            QCoreApplication.translate("measuring_tool", "1 - 2 - 3 - 4", None)
        )
        self.fix5_3.setText(
            QCoreApplication.translate("measuring_tool", "in [\u00b0]", None)
        )
        self.fix_2.setText(QCoreApplication.translate("measuring_tool", "x", None))
        self.fix_3.setText(QCoreApplication.translate("measuring_tool", "y", None))
        self.fix_4.setText(QCoreApplication.translate("measuring_tool", "z", None))
        self.fix.setText(
            QCoreApplication.translate(
                "measuring_tool", "Coordinates in [\u00c5]:", None
            )
        )

    # retranslateUi
