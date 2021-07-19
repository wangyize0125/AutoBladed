# -*- coding: utf-8 -*-
# @Time    : 2021/7/20 0:33
# @Author  : Yize Wang
# @File    : error.py
# @Software: AutoBladed

from PyQt5.QtWidgets import QMessageBox


class Error(QMessageBox):
	def __init__(self, parent=None, text="Unknown Error"):
		super(Error, self).__init__(parent)

		self.setIcon(QMessageBox.Warning)
		self.setStandardButtons(QMessageBox.Ok)
		self.setWindowTitle("Error")
		self.setText(text)

		self.show()

		return
