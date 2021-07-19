# -*- coding: utf-8 -*-
# @Time    : 2021/7/20 0:41
# @Author  : Yize Wang
# @File    : information.py
# @Software: AutoBladed

from PyQt5.QtWidgets import QMessageBox


class Information(QMessageBox):
	def __init__(self, parent=None, text="Unknown Error"):
		super(Information, self).__init__(parent)

		self.setIcon(QMessageBox.Information)
		self.setStandardButtons(QMessageBox.Ok)
		self.setWindowTitle("Information")
		self.setText(text)

		self.show()

		return
