# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QMainWindow, QMenu,
    QMenuBar, QSizePolicy, QStatusBar, QWidget)

from molara.Gui.structure_widget import StructureWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.quit = QAction(MainWindow)
        self.quit.setObjectName(u"quit")
        self.action_xyz = QAction(MainWindow)
        self.action_xyz.setObjectName(u"action_xyz")
        self.actionCenter_Molecule = QAction(MainWindow)
        self.actionCenter_Molecule.setObjectName(u"actionCenter_Molecule")
        self.actionReset_View = QAction(MainWindow)
        self.actionReset_View.setObjectName(u"actionReset_View")
        self.actionto_x_axis = QAction(MainWindow)
        self.actionto_x_axis.setObjectName(u"actionto_x_axis")
        self.actionto_y_axis = QAction(MainWindow)
        self.actionto_y_axis.setObjectName(u"actionto_y_axis")
        self.actionto_z_axis = QAction(MainWindow)
        self.actionto_z_axis.setObjectName(u"actionto_z_axis")
        self.actionDraw_Axes = QAction(MainWindow)
        self.actionDraw_Axes.setObjectName(u"actionDraw_Axes")
        self.actionCreate_Lattice = QAction(MainWindow)
        self.actionCreate_Lattice.setObjectName(u"actionCreate_Lattice")
        self.actionRead_POSCAR = QAction(MainWindow)
        self.actionRead_POSCAR.setObjectName(u"actionRead_POSCAR")
        self.action_coord = QAction(MainWindow)
        self.action_coord.setObjectName(u"action_coord")
        self.actionOpen_Trajectory_Dialog = QAction(MainWindow)
        self.actionOpen_Trajectory_Dialog.setObjectName(u"actionOpen_Trajectory_Dialog")
        self.actionImport = QAction(MainWindow)
        self.actionImport.setObjectName(u"actionImport")
        self.actionToggle_Bonds = QAction(MainWindow)
        self.actionToggle_Bonds.setObjectName(u"actionToggle_Bonds")
        self.actionMeasure = QAction(MainWindow)
        self.actionMeasure.setObjectName(u"actionMeasure")
        self.actionSupercell = QAction(MainWindow)
        self.actionSupercell.setObjectName(u"actionSupercell")
        self.actionBuilder = QAction(MainWindow)
        self.actionBuilder.setObjectName(u"actionBuilder")
        self.actionExport = QAction(MainWindow)
        self.actionExport.setObjectName(u"actionExport")
        self.actionExport_Snapshot = QAction(MainWindow)
        self.actionExport_Snapshot.setObjectName(u"actionExport_Snapshot")
        self.actionToggle_UnitCellBoundaries = QAction(MainWindow)
        self.actionToggle_UnitCellBoundaries.setObjectName(u"actionToggle_UnitCellBoundaries")
        self.actionToggle_Projection = QAction(MainWindow)
        self.actionToggle_Projection.setObjectName(u"actionToggle_Projection")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.openGLWidget = StructureWidget(self.centralwidget)
        self.openGLWidget.setObjectName(u"openGLWidget")

        self.gridLayout.addWidget(self.openGLWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuRotate = QMenu(self.menuEdit)
        self.menuRotate.setObjectName(u"menuRotate")
        self.menuCrystal = QMenu(self.menubar)
        self.menuCrystal.setObjectName(u"menuCrystal")
        self.menuTools = QMenu(self.menubar)
        self.menuTools.setObjectName(u"menuTools")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuCrystal.menuAction())
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addAction(self.actionExport_Snapshot)
        self.menuFile.addAction(self.quit)
        self.menuEdit.addAction(self.actionCenter_Molecule)
        self.menuEdit.addAction(self.actionReset_View)
        self.menuEdit.addAction(self.menuRotate.menuAction())
        self.menuEdit.addAction(self.actionToggle_Projection)
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
        self.menuCrystal.addAction(self.actionToggle_UnitCellBoundaries)
        self.menuTools.addAction(self.actionMeasure)
        self.menuTools.addAction(self.actionBuilder)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.quit.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
        self.action_xyz.setText(QCoreApplication.translate("MainWindow", u".xyz", None))
        self.actionCenter_Molecule.setText(QCoreApplication.translate("MainWindow", u"Center Molecule", None))
        self.actionReset_View.setText(QCoreApplication.translate("MainWindow", u"Reset View", None))
        self.actionto_x_axis.setText(QCoreApplication.translate("MainWindow", u"to x axis", None))
        self.actionto_y_axis.setText(QCoreApplication.translate("MainWindow", u"to y axis", None))
        self.actionto_z_axis.setText(QCoreApplication.translate("MainWindow", u"to z axis", None))
        self.actionDraw_Axes.setText(QCoreApplication.translate("MainWindow", u"Toggle Axes", None))
        self.actionCreate_Lattice.setText(QCoreApplication.translate("MainWindow", u"Create Lattice", None))
        self.actionRead_POSCAR.setText(QCoreApplication.translate("MainWindow", u"Read POSCAR", None))
        self.action_coord.setText(QCoreApplication.translate("MainWindow", u"coord", None))
        self.actionOpen_Trajectory_Dialog.setText(QCoreApplication.translate("MainWindow", u"Open Trajectory Dialog", None))
        self.actionImport.setText(QCoreApplication.translate("MainWindow", u"Import", None))
        self.actionToggle_Bonds.setText(QCoreApplication.translate("MainWindow", u"Toggle Bonds", None))
        self.actionMeasure.setText(QCoreApplication.translate("MainWindow", u"Measure", None))
        self.actionSupercell.setText(QCoreApplication.translate("MainWindow", u"Supercell", None))
        self.actionBuilder.setText(QCoreApplication.translate("MainWindow", u"Builder", None))
        self.actionExport.setText(QCoreApplication.translate("MainWindow", u"Export", None))
        self.actionExport_Snapshot.setText(QCoreApplication.translate("MainWindow", u"Export Snapshot", None))
        self.actionToggle_UnitCellBoundaries.setText(QCoreApplication.translate("MainWindow", u"Toggle Unit Cell Boundaries", None))
        self.actionToggle_Projection.setText(QCoreApplication.translate("MainWindow", u"Toggle Projection (Perspective/Ortho)", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuRotate.setTitle(QCoreApplication.translate("MainWindow", u"Rotate", None))
        self.menuCrystal.setTitle(QCoreApplication.translate("MainWindow", u"Crystal", None))
        self.menuTools.setTitle(QCoreApplication.translate("MainWindow", u"Tools", None))
    # retranslateUi
