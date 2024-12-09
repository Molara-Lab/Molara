# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'builder.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QDoubleSpinBox, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QTableWidget, QTableWidgetItem, QWidget)

class Ui_builder(object):
    def setupUi(self, builder):
        if not builder.objectName():
            builder.setObjectName(u"builder")
        builder.resize(451, 279)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(builder.sizePolicy().hasHeightForWidth())
        builder.setSizePolicy(sizePolicy)
        self.Box_1BondDistance = QDoubleSpinBox(builder)
        self.Box_1BondDistance.setObjectName(u"Box_1BondDistance")
        self.Box_1BondDistance.setGeometry(QRect(70, 230, 61, 31))
        self.Box_1BondDistance.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.Box_1BondDistance.setMaximum(99999.000000000000000)
        self.Box_1BondDistance.setSingleStep(0.100000000000000)
        self.Box_2BondAngle = QDoubleSpinBox(builder)
        self.Box_2BondAngle.setObjectName(u"Box_2BondAngle")
        self.Box_2BondAngle.setGeometry(QRect(160, 230, 61, 31))
        self.Box_2BondAngle.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.Box_2BondAngle.setMinimum(0.000000000000000)
        self.Box_2BondAngle.setMaximum(180.000000000000000)
        self.Box_3DihedralAngle = QDoubleSpinBox(builder)
        self.Box_3DihedralAngle.setObjectName(u"Box_3DihedralAngle")
        self.Box_3DihedralAngle.setGeometry(QRect(250, 230, 61, 31))
        self.Box_3DihedralAngle.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.Box_3DihedralAngle.setMinimum(-180.000000000000000)
        self.Box_3DihedralAngle.setMaximum(180.000000000000000)
        self.AddAtomButton = QPushButton(builder)
        self.AddAtomButton.setObjectName(u"AddAtomButton")
        self.AddAtomButton.setGeometry(QRect(330, 230, 51, 31))
        self.Box_0Element = QLineEdit(builder)
        self.Box_0Element.setObjectName(u"Box_0Element")
        self.Box_0Element.setGeometry(QRect(10, 230, 41, 31))
        self.Box_0Element.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.tableWidget = QTableWidget(builder)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(10, 10, 430, 161))
        self.DeleteAtomButton = QPushButton(builder)
        self.DeleteAtomButton.setObjectName(u"DeleteAtomButton")
        self.DeleteAtomButton.setGeometry(QRect(390, 230, 51, 31))
        self.label = QLabel(builder)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 210, 51, 16))
        self.label_2 = QLabel(builder)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(70, 210, 80, 16))
        self.label_3 = QLabel(builder)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(160, 210, 58, 16))
        self.label_4 = QLabel(builder)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(250, 210, 71, 16))
        self.error_messageLabel = QLabel(builder)
        self.error_messageLabel.setObjectName(u"error_messageLabel")
        self.error_messageLabel.setGeometry(QRect(10, 180, 421, 16))
        QWidget.setTabOrder(self.tableWidget, self.Box_0Element)
        QWidget.setTabOrder(self.Box_0Element, self.Box_1BondDistance)
        QWidget.setTabOrder(self.Box_1BondDistance, self.Box_2BondAngle)
        QWidget.setTabOrder(self.Box_2BondAngle, self.Box_3DihedralAngle)
        QWidget.setTabOrder(self.Box_3DihedralAngle, self.AddAtomButton)
        QWidget.setTabOrder(self.AddAtomButton, self.DeleteAtomButton)

        self.retranslateUi(builder)

        QMetaObject.connectSlotsByName(builder)
    # setupUi

    def retranslateUi(self, builder):
        builder.setWindowTitle(QCoreApplication.translate("builder", u"Z-Matrix Builder", None))
        self.AddAtomButton.setText(QCoreApplication.translate("builder", u"Add", None))
        self.DeleteAtomButton.setText(QCoreApplication.translate("builder", u"Delete", None))
        self.label.setText(QCoreApplication.translate("builder", u"Element", None))
        self.label_2.setText(QCoreApplication.translate("builder", u"Distance / \u00c5", None))
        self.label_3.setText(QCoreApplication.translate("builder", u"Angle / \u00b0", None))
        self.label_4.setText(QCoreApplication.translate("builder", u"Dihedral / \u00b0", None))
        self.error_messageLabel.setText("")
    # retranslateUi
