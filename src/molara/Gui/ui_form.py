# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
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
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QMainWindow,
    QMenu,
    QMenuBar,
    QSizePolicy,
    QStatusBar,
    QWidget,
)

from molara.StructureWidget.structure_widget import MoleculeWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.quit = QAction(MainWindow)
        self.quit.setObjectName("quit")
        self.action_xyz = QAction(MainWindow)
        self.action_xyz.setObjectName("action_xyz")
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
        self.actionCreate_Lattice = QAction(MainWindow)
        self.actionCreate_Lattice.setObjectName("actionCreate_Lattice")
        self.actionRead_POSCAR = QAction(MainWindow)
        self.actionRead_POSCAR.setObjectName("actionRead_POSCAR")
        self.action_coord = QAction(MainWindow)
        self.action_coord.setObjectName("action_coord")
        self.actionOpen_Trajectory_Dialog = QAction(MainWindow)
        self.actionOpen_Trajectory_Dialog.setObjectName("actionOpen_Trajectory_Dialog")
        self.actionImport = QAction(MainWindow)
        self.actionImport.setObjectName("actionImport")
        self.actionToggle_Bonds = QAction(MainWindow)
        self.actionToggle_Bonds.setObjectName("actionToggle_Bonds")
        self.actionMeasure = QAction(MainWindow)
        self.actionMeasure.setObjectName("actionMeasure")
        self.actionSupercell = QAction(MainWindow)
        self.actionSupercell.setObjectName("actionSupercell")
        self.actionExport = QAction(MainWindow)
        self.actionExport.setObjectName("actionExport")
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
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuRotate = QMenu(self.menuEdit)
        self.menuRotate.setObjectName("menuRotate")
        self.menuCrystal = QMenu(self.menubar)
        self.menuCrystal.setObjectName("menuCrystal")
        self.menuTools = QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuCrystal.menuAction())
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addAction(self.quit)
        self.menuEdit.addAction(self.actionCenter_Molecule)
        self.menuEdit.addAction(self.actionReset_View)
        self.menuEdit.addAction(self.menuRotate.menuAction())
        self.menuEdit.addAction(self.actionDraw_Axes)
        self.menuEdit.addAction(self.actionOpen_Trajectory_Dialog)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionToggle_Bonds)
        self.menuRotate.addAction(self.actionto_x_axis)
        self.menuRotate.addAction(self.actionto_y_axis)
        self.menuRotate.addAction(self.actionto_z_axis)
        self.menuCrystal.addAction(self.actionRead_POSCAR)
        self.menuCrystal.addAction(self.actionCreate_Lattice)
        self.menuCrystal.addAction(self.actionSupercell)
        self.menuTools.addAction(self.actionMeasure)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "MainWindow", None)
        )
        self.quit.setText(QCoreApplication.translate("MainWindow", "Quit", None))
        self.action_xyz.setText(QCoreApplication.translate("MainWindow", ".xyz", None))
        self.actionCenter_Molecule.setText(
            QCoreApplication.translate("MainWindow", "Center Structure", None)
        )
        self.actionReset_View.setText(
            QCoreApplication.translate("MainWindow", "Reset View", None)
        )
        self.actionto_x_axis.setText(
            QCoreApplication.translate("MainWindow", "to x axis", None)
        )
        self.actionto_y_axis.setText(
            QCoreApplication.translate("MainWindow", "to y axis", None)
        )
        self.actionto_z_axis.setText(
            QCoreApplication.translate("MainWindow", "to z axis", None)
        )
        self.actionDraw_Axes.setText(
            QCoreApplication.translate("MainWindow", "Toggle Axes", None)
        )
        self.actionCreate_Lattice.setText(
            QCoreApplication.translate("MainWindow", "Create Lattice", None)
        )
        self.actionRead_POSCAR.setText(
            QCoreApplication.translate("MainWindow", "Read POSCAR", None)
        )
        self.action_coord.setText(
            QCoreApplication.translate("MainWindow", "coord", None)
        )
        self.actionOpen_Trajectory_Dialog.setText(
            QCoreApplication.translate("MainWindow", "Open Trajectory Dialog", None)
        )
        self.actionImport.setText(
            QCoreApplication.translate("MainWindow", "Import", None)
        )
        self.actionToggle_Bonds.setText(
            QCoreApplication.translate("MainWindow", "Toggle Bonds", None)
        )
        self.actionMeasure.setText(
            QCoreApplication.translate("MainWindow", "Measure", None)
        )
        self.actionSupercell.setText(
            QCoreApplication.translate("MainWindow", "Supercell", None)
        )
        self.actionExport.setText(
            QCoreApplication.translate("MainWindow", "Export", None)
        )
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", "File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", "View", None))
        self.menuRotate.setTitle(
            QCoreApplication.translate("MainWindow", "Rotate", None)
        )
        self.menuCrystal.setTitle(
            QCoreApplication.translate("MainWindow", "Crystal", None)
        )
        self.menuTools.setTitle(QCoreApplication.translate("MainWindow", "Tools", None))

    # retranslateUi
