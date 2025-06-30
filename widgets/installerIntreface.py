# -*- coding: utf-8 -*-
################################################################################
## Form converted and customized for Altify Installer using PySide6
################################################################################

from PySide6.QtCore import Qt, QRect, QCoreApplication, QMetaObject
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFrame, QLabel, QProgressBar , QPushButton
)


class Ui_SplashScreen(object):
    def setupUi(self, SplashScreen):
        SplashScreen.setObjectName("SplashScreen")
        SplashScreen.resize(680, 400)
        SplashScreen.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        SplashScreen.setAttribute(Qt.WA_TranslucentBackground)

        self.centralwidget = QWidget(SplashScreen)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.setSpacing(0)

        self.dropShadowFrame = QFrame(self.centralwidget)
        self.dropShadowFrame.setStyleSheet("""
            QFrame {
                background-color: rgb(56, 58, 89);
                color: rgb(220, 220, 220);
                border-radius: 10px;
            }
        """)

        self.label_title = QLabel(self.dropShadowFrame)
        self.label_title.setGeometry(QRect(0, 50, 661, 61))
        font = QFont("Segoe UI", 28)
        self.label_title.setFont(font)
        self.label_title.setStyleSheet("color: rgb(254, 121, 199);")
        self.label_title.setAlignment(Qt.AlignCenter)

        self.start_button = QPushButton("Start Install", self.dropShadowFrame)
        self.start_button.setGeometry(QRect(260, 130, 150, 40))
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(85, 170, 255);
                border-radius: 8px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgb(100, 180, 255);
            }
        """)

        self.label_description = QLabel(self.dropShadowFrame)
        self.label_description.setGeometry(QRect(0, 190, 661, 31))
        font1 = QFont("Segoe UI", 14)
        self.label_description.setFont(font1)
        self.label_description.setStyleSheet("color: rgb(98, 114, 164);")
        self.label_description.setAlignment(Qt.AlignCenter)

        self.progressBar = QProgressBar(self.dropShadowFrame)
        self.progressBar.setGeometry(QRect(50, 260, 561, 23))
        self.progressBar.setStyleSheet("""
            QProgressBar {
                background-color: rgb(98, 114, 164);
                color: rgb(200, 200, 200);
                border-style: none;
                border-radius: 10px;
                text-align: center;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0.511364, x2:1, y2:0.523,
                    stop:0 rgba(254, 121, 199, 255),
                    stop:1 rgba(170, 85, 255, 255)
                );
            }
        """)
        self.progressBar.setValue(0)

        self.label_loading = QLabel(self.dropShadowFrame)
        self.label_loading.setGeometry(QRect(0, 300, 661, 21))
        font2 = QFont("Segoe UI", 12)
        self.label_loading.setFont(font2)
        self.label_loading.setStyleSheet("color: rgb(98, 114, 164);")
        self.label_loading.setAlignment(Qt.AlignCenter)

        self.label_credits = QLabel(self.dropShadowFrame)
        self.label_credits.setGeometry(QRect(20, 350, 621, 21))
        font3 = QFont("Segoe UI", 10)
        self.label_credits.setFont(font3)
        self.label_credits.setStyleSheet("color: rgb(98, 114, 164);")
        self.label_credits.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.verticalLayout.addWidget(self.dropShadowFrame)
        SplashScreen.setCentralWidget(self.centralwidget)
        self.retranslateUi(SplashScreen)
        QMetaObject.connectSlotsByName(SplashScreen)

    def retranslateUi(self, SplashScreen):
        SplashScreen.setWindowTitle("Altify Installer")
        self.label_title.setText("<strong>ALTIFY</strong> INSTALLER")
        self.label_description.setText("Click Start Install to begin")
        self.label_loading.setText("")
        self.label_credits.setText("<strong>Version</strong>: 1.0.0 | <strong>Developed by</strong>: TRI-X Team")

