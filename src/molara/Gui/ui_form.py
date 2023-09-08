# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.5.0
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
    Qt,
    QTime,
    QUrl,
)
from PySide6.QtGui import (
    QAction,
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
from PySide6.QtWidgets import QApplication, QGridLayout, QMainWindow, QMenu, QMenuBar, QSizePolicy, QStatusBar, QWidget

from molara.MoleculeWidget.MoleculeWidget import MoleculeWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")

        MainWindow.resize(800, 600)

        self.quit = QAction(MainWindow)
        self.quit.setObjectName("quit")

        self.action_xyz = QAction(MainWindow)
        self.action_xyz.setObjectName("action_xyz")

        self.action_coord = QAction(MainWindow)
        self.action_coord.setObjectName("action_coord")

        self.actionCenter_Molecule = QAction(MainWindow)
        self.actionCenter_Molecule.setObjectName("actionCenter_Molecule")

        self.actionReset_View = QAction(MainWindow)
        self.actionReset_View.setObjectName("actionReset_View")

        self.actionto_x_axis = QAction(MainWindow)
        self.actionto_x_axis.setObjectName("actionto_x_axis")
        self.actionto_y_axis = QAction(MainWindow)
        self.actionto_y_axis.setObjectName("actionto_y_axis")
        self.actionto_z_axis = QAction(MainWindow)
        self.actionto_z_axis.setObjectName("actionto_z_axis")
        self.actionDraw_Axes = QAction(MainWindow)
        self.actionDraw_Axes.setObjectName("actionDraw_Axes")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.openGLWidget = MoleculeWidget(self.centralwidget)
        self.openGLWidget.setObjectName("openGLWidget")

        self.gridLayout.addWidget(self.openGLWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuImport = QMenu(self.menuFile)
        self.menuImport.setObjectName("menuImport")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuRotate = QMenu(self.menuEdit)
        self.menuRotate.setObjectName("menuRotate")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menuFile.addAction(self.menuImport.menuAction())
        self.menuFile.addAction(self.quit)
        self.menuImport.addAction(self.action_xyz)
        self.menuImport.addAction(self.action_coord)
        self.menuEdit.addAction(self.actionCenter_Molecule)
        self.menuEdit.addAction(self.actionReset_View)
        self.menuEdit.addAction(self.menuRotate.menuAction())
        self.menuEdit.addAction(self.actionDraw_Axes)
        self.menuRotate.addAction(self.actionto_x_axis)
        self.menuRotate.addAction(self.actionto_y_axis)
        self.menuRotate.addAction(self.actionto_z_axis)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "MainWindow", None))
        self.quit.setText(QCoreApplication.translate("MainWindow", "Quit", None))
        self.action_xyz.setText(QCoreApplication.translate("MainWindow", ".xyz", None))
        self.action_coord.setText(QCoreApplication.translate("MainWindow", "coord", None))
        self.actionCenter_Molecule.setText(QCoreApplication.translate("MainWindow", "Center Molecule", None))
        self.actionReset_View.setText(QCoreApplication.translate("MainWindow", "Reset View", None))
        self.actionto_x_axis.setText(QCoreApplication.translate("MainWindow", "to x axis", None))
        self.actionto_y_axis.setText(QCoreApplication.translate("MainWindow", "to y axis", None))
        self.actionto_z_axis.setText(QCoreApplication.translate("MainWindow", "to z axis", None))
        self.actionDraw_Axes.setText(QCoreApplication.translate("MainWindow", "Draw Axes", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", "File", None))
        self.menuImport.setTitle(QCoreApplication.translate("MainWindow", "Import", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", "View", None))
        self.menuRotate.setTitle(QCoreApplication.translate("MainWindow", "Rotate", None))

    # retranslateUi

    # retranslateUi
