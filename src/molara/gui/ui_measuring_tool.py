# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'measuring_tool.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
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
    QHeaderView,
    QLabel,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)


class Ui_measuring_tool(object):
    def setupUi(self, measuring_tool):
        if not measuring_tool.objectName():
            measuring_tool.setObjectName("measuring_tool")
        measuring_tool.resize(431, 438)
        measuring_tool.setMinimumSize(QSize(431, 438))
        measuring_tool.setMaximumSize(QSize(431, 438))
        self.info_text = QLabel(measuring_tool)
        self.info_text.setObjectName("info_text")
        self.info_text.setGeometry(QRect(10, 10, 371, 20))
        self.tableDistances = QTableWidget(measuring_tool)
        self.tableDistances.setObjectName("tableDistances")
        self.tableDistances.setGeometry(QRect(10, 280, 250, 140))
        self.labelAngles = QLabel(measuring_tool)
        self.labelAngles.setObjectName("labelAngles")
        self.labelAngles.setGeometry(QRect(270, 260, 58, 16))
        self.tableAngles = QTableWidget(measuring_tool)
        self.tableAngles.setObjectName("tableAngles")
        self.tableAngles.setGeometry(QRect(270, 280, 150, 140))
        self.tablePositions = QTableWidget(measuring_tool)
        self.tablePositions.setObjectName("tablePositions")
        self.tablePositions.setGeometry(QRect(10, 90, 410, 141))
        self.labelPositions = QLabel(measuring_tool)
        self.labelPositions.setObjectName("labelPositions")
        self.labelPositions.setGeometry(QRect(10, 70, 91, 16))
        self.labelDistances = QLabel(measuring_tool)
        self.labelDistances.setObjectName("labelDistances")
        self.labelDistances.setGeometry(QRect(10, 260, 81, 16))
        self.info_text_2 = QLabel(measuring_tool)
        self.info_text_2.setObjectName("info_text_2")
        self.info_text_2.setGeometry(QRect(10, 40, 371, 20))
        QWidget.setTabOrder(self.tablePositions, self.tableDistances)
        QWidget.setTabOrder(self.tableDistances, self.tableAngles)

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
        self.labelAngles.setText(
            QCoreApplication.translate("measuring_tool", "Angles:", None)
        )
        self.labelPositions.setText(
            QCoreApplication.translate("measuring_tool", "Atom Positions", None)
        )
        self.labelDistances.setText(
            QCoreApplication.translate("measuring_tool", "Distances:", None)
        )
        self.info_text_2.setText(
            QCoreApplication.translate("measuring_tool", "TextLabel", None)
        )

    # retranslateUi
