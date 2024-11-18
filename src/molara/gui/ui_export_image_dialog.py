# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'export_image_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QDoubleSpinBox, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpinBox, QTabWidget,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(402, 266)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(200, 220, 181, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.tabWidget = QTabWidget(Dialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(20, 10, 361, 191))
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.label_2 = QLabel(self.tab)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(0, 70, 91, 16))
        self.heightSpinBox = QDoubleSpinBox(self.tab)
        self.heightSpinBox.setObjectName(u"heightSpinBox")
        self.heightSpinBox.setGeometry(QRect(110, 64, 62, 26))
        self.heightSpinBox.setDecimals(0)
        self.heightSpinBox.setMinimum(1.000000000000000)
        self.heightSpinBox.setMaximum(50000.000000000000000)
        self.checkBox = QCheckBox(self.tab)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setGeometry(QRect(180, 20, 131, 21))
        self.widthSpinBox = QDoubleSpinBox(self.tab)
        self.widthSpinBox.setObjectName(u"widthSpinBox")
        self.widthSpinBox.setGeometry(QRect(110, 20, 62, 26))
        self.widthSpinBox.setDecimals(0)
        self.widthSpinBox.setMinimum(1.000000000000000)
        self.widthSpinBox.setMaximum(50000.000000000000000)
        self.label = QLabel(self.tab)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(0, 20, 91, 16))
        self.filenameInput = QLineEdit(self.tab)
        self.filenameInput.setObjectName(u"filenameInput")
        self.filenameInput.setGeometry(QRect(0, 110, 241, 28))
        self.pushButton = QPushButton(self.tab)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(260, 110, 90, 28))
        self.transparentBackgroundCheckBox = QCheckBox(self.tab)
        self.transparentBackgroundCheckBox.setObjectName(u"transparentBackgroundCheckBox")
        self.transparentBackgroundCheckBox.setGeometry(QRect(180, 40, 171, 20))
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.sphereSubdivisionsSpinBox = QSpinBox(self.tab_2)
        self.sphereSubdivisionsSpinBox.setObjectName(u"sphereSubdivisionsSpinBox")
        self.sphereSubdivisionsSpinBox.setGeometry(QRect(160, 20, 42, 26))
        self.cylinderSubdivisionsSpinBox = QSpinBox(self.tab_2)
        self.cylinderSubdivisionsSpinBox.setObjectName(u"cylinderSubdivisionsSpinBox")
        self.cylinderSubdivisionsSpinBox.setGeometry(QRect(160, 70, 42, 26))
        self.label_3 = QLabel(self.tab_2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 20, 121, 16))
        self.label_4 = QLabel(self.tab_2)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(20, 80, 131, 16))
        self.tabWidget.addTab(self.tab_2, "")
        QWidget.setTabOrder(self.tabWidget, self.widthSpinBox)
        QWidget.setTabOrder(self.widthSpinBox, self.heightSpinBox)
        QWidget.setTabOrder(self.heightSpinBox, self.checkBox)
        QWidget.setTabOrder(self.checkBox, self.filenameInput)
        QWidget.setTabOrder(self.filenameInput, self.pushButton)
        QWidget.setTabOrder(self.pushButton, self.sphereSubdivisionsSpinBox)
        QWidget.setTabOrder(self.sphereSubdivisionsSpinBox, self.cylinderSubdivisionsSpinBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Export Snapshot", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Height (pixels)", None))
        self.checkBox.setText(QCoreApplication.translate("Dialog", u"Keep aspect ratio", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Width (pixels)", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog", u"Change file", None))
        self.transparentBackgroundCheckBox.setText(QCoreApplication.translate("Dialog", u"Transparent Background", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Dialog", u"Export Options", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Sphere Subdivisions", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"Cylinder Subdivisions", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Dialog", u"Rendering Options", None))
    # retranslateUi
