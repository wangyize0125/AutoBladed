# -*- coding: utf-8 -*-
# @Time    : 2021/7/17 16:53
# @Author  : Yize Wang
# @File    : main.py
# @Software: AutoBladed

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon

from widgets import Entry
from kernels.run_cases import check_bladed


class AutoBladed(QMainWindow):
	"""
	main window of AutoBladed
	"""

	def __init__(self):
		super(AutoBladed, self).__init__()

		# window title
		self.setWindowTitle(QApplication.applicationName())
		# window icon
		self.setWindowIcon(QIcon("./resources/images/logo.ico"))

		# resize the window, for convenience, the size is fixed
		geom = QApplication.desktop().screenGeometry()
		width, height = geom.width(), geom.height()
		self.setFixedSize(int(width * 0.7), int(height * 0.7))

		# move to center
		self.move((width - self.width()) // 2, (height - self.height()) // 2)

		# widgets
		self.main_tab = Entry(self, (self.width(), self.height()))

		return


if __name__ == "__main__":
	# initialize an application instance
	app = QApplication(sys.argv)
	app.setApplicationName("AutoBladed")

	app_gui = AutoBladed()
	app_gui.show()

	# check whether BLADED has been set properly
	check_bladed(app_gui)

	# hook up the current application
	app.exit(app.exec_())
