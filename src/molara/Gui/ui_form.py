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

from molara.MoleculeWidget.molecule_widget import MoleculeWidget


class UiMainwindow:
    def setup_ui(self, main_window):
        if not main_window.objectName():
            main_window.setObjectName("MainWindow")
        main_window.resize(800, 600)
        self.quit = QAction(main_window)
        self.quit.setObjectName("quit")
        self.action_xyz = QAction(main_window)
        self.action_xyz.setObjectName("action_xyz")
        self.action_coord = QAction(main_window)
        self.action_coord.setObjectName("action_coord")
        self.actionCenter_Molecule = QAction(main_window)
        self.actionCenter_Molecule.setObjectName("actionCenter_Molecule")
        self.actionReset_View = QAction(main_window)
        self.actionReset_View.setObjectName("actionReset_View")
        self.actionto_x_axis = QAction(main_window)
        self.actionto_x_axis.setObjectName("actionto_x_axis")
        self.actionto_y_axis = QAction(main_window)
        self.actionto_y_axis.setObjectName("actionto_y_axis")
        self.actionto_z_axis = QAction(main_window)
        self.actionto_z_axis.setObjectName("actionto_z_axis")
        self.actionDraw_Axes = QAction(main_window)
        self.actionDraw_Axes.setObjectName("actionDraw_Axes")
        self.actionCreate_Lattice = QAction(main_window)
        self.actionCreate_Lattice.setObjectName("actionCreate_Lattice")
        self.actioncoord = QAction(main_window)
        self.actioncoord.setObjectName("actioncoord")
        self.actionRead_POSCAR = QAction(main_window)
        self.actionRead_POSCAR.setObjectName("actionRead_POSCAR")
        self.centralwidget = QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.openGLWidget = MoleculeWidget(self.centralwidget)
        self.openGLWidget.setObjectName("openGLWidget")

        self.gridLayout.addWidget(self.openGLWidget, 0, 0, 1, 1)

        main_window.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(main_window)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 37))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuImport = QMenu(self.menuFile)
        self.menuImport.setObjectName("menuImport")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuRotate = QMenu(self.menuEdit)
        self.menuRotate.setObjectName("menuRotate")
        self.menuCrystal = QMenu(self.menubar)
        self.menuCrystal.setObjectName("menuCrystal")
        main_window.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuCrystal.menuAction())
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
        self.menuCrystal.addAction(self.actionRead_POSCAR)
        self.menuCrystal.addAction(self.actionCreate_Lattice)

        self.retranslate_ui(main_window)

        QMetaObject.connectSlotsByName(main_window)

    # setupUi

    def retranslate_ui(self, main_window):
        main_window.setWindowTitle(QCoreApplication.translate("MainWindow", "MainWindow", None))
        self.quit.setText(QCoreApplication.translate("MainWindow", "Quit", None))
        self.action_xyz.setText(QCoreApplication.translate("MainWindow", ".xyz", None))
        self.action_coord.setText(QCoreApplication.translate("MainWindow", "coord", None))
        self.actionCenter_Molecule.setText(QCoreApplication.translate("MainWindow", "Center Molecule", None))
        self.actionReset_View.setText(QCoreApplication.translate("MainWindow", "Reset View", None))
        self.actionto_x_axis.setText(QCoreApplication.translate("MainWindow", "to x axis", None))
        self.actionto_y_axis.setText(QCoreApplication.translate("MainWindow", "to y axis", None))
        self.actionto_z_axis.setText(QCoreApplication.translate("MainWindow", "to z axis", None))
        self.actionDraw_Axes.setText(QCoreApplication.translate("MainWindow", "Draw Axes", None))
        self.actionCreate_Lattice.setText(QCoreApplication.translate("MainWindow", "Create Lattice", None))
        self.actioncoord.setText(QCoreApplication.translate("MainWindow", "coord", None))
        self.actionRead_POSCAR.setText(QCoreApplication.translate("MainWindow", "Read POSCAR", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", "File", None))
        self.menuImport.setTitle(QCoreApplication.translate("MainWindow", "Import", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", "View", None))
        self.menuRotate.setTitle(QCoreApplication.translate("MainWindow", "Rotate", None))
        self.menuCrystal.setTitle(QCoreApplication.translate("MainWindow", "Crystal", None))

    # retranslateUi
