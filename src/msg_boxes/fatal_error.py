# -*- coding: utf-8 -*-
# @Time    : 2021/7/19 16:59
# @Author  : Yize Wang
# @File    : fatal_error.py
# @Software: AutoBladed

import sys
from PyQt5.QtWidgets import QMessageBox, QApplication


class FatalError(QMessageBox):
	def __init__(self, parent=None, text="Unknown Error"):
		super(FatalError, self).__init__(parent)

		self.setIcon(QMessageBox.Critical)
		self.setStandardButtons(QMessageBox.Ok)
		self.setWindowTitle("Fatal error")
		self.setText(text)
		self.buttonClicked.connect(self.button_clicked)

		self.show()

		return

	def button_clicked(self, button):
		QApplication.instance().quit()