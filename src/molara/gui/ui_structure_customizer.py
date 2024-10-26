# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'structure_customizer.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QDoubleSpinBox,
    QLabel, QPushButton, QSizePolicy, QTextEdit,
    QWidget)

class Ui_structure_customizer(object):
    def setupUi(self, structure_customizer):
        if not structure_customizer.objectName():
            structure_customizer.setObjectName(u"structure_customizer")
        structure_customizer.resize(256, 191)
        structure_customizer.setMinimumSize(QSize(256, 152))
        structure_customizer.setMaximumSize(QSize(256, 191))
        self.viewModeButton = QPushButton(structure_customizer)
        self.viewModeButton.setObjectName(u"viewModeButton")
        self.viewModeButton.setGeometry(QRect(6, 5, 107, 32))
        self.viewModeButton.setAutoDefault(False)
        self.ballSizeSpinBox = QDoubleSpinBox(structure_customizer)
        self.ballSizeSpinBox.setObjectName(u"ballSizeSpinBox")
        self.ballSizeSpinBox.setGeometry(QRect(186, 10, 62, 22))
        self.ballSizeSpinBox.setMinimum(0.100000000000000)
        self.ballSizeSpinBox.setSingleStep(0.100000000000000)
        self.ballSizeSpinBox.setValue(1.000000000000000)
        self.stickSizeSpinBox = QDoubleSpinBox(structure_customizer)
        self.stickSizeSpinBox.setObjectName(u"stickSizeSpinBox")
        self.stickSizeSpinBox.setGeometry(QRect(186, 40, 62, 22))
        self.stickSizeSpinBox.setMinimum(0.100000000000000)
        self.stickSizeSpinBox.setSingleStep(0.100000000000000)
        self.ballSizeLabel = QLabel(structure_customizer)
        self.ballSizeLabel.setObjectName(u"ballSizeLabel")
        self.ballSizeLabel.setGeometry(QRect(118, 10, 71, 20))
        self.stickSizeLabel = QLabel(structure_customizer)
        self.stickSizeLabel.setObjectName(u"stickSizeLabel")
        self.stickSizeLabel.setGeometry(QRect(118, 40, 71, 20))
        self.toggleBondsButton = QPushButton(structure_customizer)
        self.toggleBondsButton.setObjectName(u"toggleBondsButton")
        self.toggleBondsButton.setGeometry(QRect(6, 35, 107, 32))
        self.toggleBondsButton.setAutoDefault(False)
        self.loadSelect = QComboBox(structure_customizer)
        self.loadSelect.setObjectName(u"loadSelect")
        self.loadSelect.setGeometry(QRect(1, 155, 141, 32))
        self.loadButton = QPushButton(structure_customizer)
        self.loadButton.setObjectName(u"loadButton")
        self.loadButton.setGeometry(QRect(6, 125, 61, 32))
        self.loadButton.setAutoDefault(False)
        self.saveButton = QPushButton(structure_customizer)
        self.saveButton.setObjectName(u"saveButton")
        self.saveButton.setGeometry(QRect(140, 125, 108, 32))
        self.saveButton.setAutoDefault(False)
        self.saveName = QTextEdit(structure_customizer)
        self.saveName.setObjectName(u"saveName")
        self.saveName.setGeometry(QRect(140, 159, 107, 21))
        self.deleteButton = QPushButton(structure_customizer)
        self.deleteButton.setObjectName(u"deleteButton")
        self.deleteButton.setGeometry(QRect(74, 125, 61, 32))
        self.deleteButton.setAutoDefault(False)
        self.toggleNumbersButton = QPushButton(structure_customizer)
        self.toggleNumbersButton.setObjectName(u"toggleNumbersButton")
        self.toggleNumbersButton.setGeometry(QRect(6, 65, 107, 32))
        self.toggleNumbersButton.setAutoDefault(False)
        self.indexSizeLabel = QLabel(structure_customizer)
        self.indexSizeLabel.setObjectName(u"indexSizeLabel")
        self.indexSizeLabel.setGeometry(QRect(118, 70, 71, 20))
        self.indexSizeSpinBox = QDoubleSpinBox(structure_customizer)
        self.indexSizeSpinBox.setObjectName(u"indexSizeSpinBox")
        self.indexSizeSpinBox.setGeometry(QRect(186, 70, 62, 22))
        self.indexSizeSpinBox.setMinimum(0.100000000000000)
        self.indexSizeSpinBox.setMaximum(3.000000000000000)
        self.indexSizeSpinBox.setSingleStep(0.050000000000000)
        self.indexSizeSpinBox.setValue(1.000000000000000)
        self.colorSchemeLabel = QLabel(structure_customizer)
        self.colorSchemeLabel.setObjectName(u"colorSchemeLabel")
        self.colorSchemeLabel.setGeometry(QRect(10, 100, 133, 16))
        self.colorSchemeSelect = QComboBox(structure_customizer)
        self.colorSchemeSelect.setObjectName(u"colorSchemeSelect")
        self.colorSchemeSelect.setGeometry(QRect(134, 95, 120, 32))

        self.retranslateUi(structure_customizer)

        QMetaObject.connectSlotsByName(structure_customizer)
    # setupUi

    def retranslateUi(self, structure_customizer):
        structure_customizer.setWindowTitle(QCoreApplication.translate("structure_customizer", u"Structure Customizer", None))
        self.viewModeButton.setText(QCoreApplication.translate("structure_customizer", u"Stick Mode", None))
        self.ballSizeLabel.setText(QCoreApplication.translate("structure_customizer", u"Atom Size:", None))
        self.stickSizeLabel.setText(QCoreApplication.translate("structure_customizer", u"Bond Size:", None))
        self.toggleBondsButton.setText(QCoreApplication.translate("structure_customizer", u"Bonds Off", None))
        self.loadButton.setText(QCoreApplication.translate("structure_customizer", u"Load", None))
        self.saveButton.setText(QCoreApplication.translate("structure_customizer", u"Save", None))
        self.saveName.setHtml(QCoreApplication.translate("structure_customizer", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'.AppleSystemUIFont'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.deleteButton.setText(QCoreApplication.translate("structure_customizer", u"Delete", None))
        self.toggleNumbersButton.setText(QCoreApplication.translate("structure_customizer", u"Show Indices", None))
        self.indexSizeLabel.setText(QCoreApplication.translate("structure_customizer", u"Index Size:", None))
        self.colorSchemeLabel.setText(QCoreApplication.translate("structure_customizer", u"Select Color Scheme:", None))
    # retranslateUi
