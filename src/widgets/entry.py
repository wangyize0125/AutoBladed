# -*- coding: utf-8 -*-
# @Time    : 2021/7/19 11:13
# @Author  : Yize Wang
# @File    : entry.py
# @Software: AutoBladed

import os
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QFileDialog
from PyQt5.QtCore import Qt

from msg_boxes import Error
from kernels import CasesConfig
from widgets.tabs import MajorTab
from exceptions import SheetNameError


class Entry(QWidget):
	"""
	entry of the application
	"""

	file_format = "Excel file (*.xlsx);;Excel file (*.xls)"

	def __init__(self, parent=None, size=(800, 600)):
		super(Entry, self).__init__(parent)

		self.setFixedSize(*size)

		# these variables should be set first then the cases will be loaded automatically
		self.config_file = ""
		self.config_file_changed = False
		self.output_folder = ""

		# configurations
		self.majors = []
		self.minors = []
		self.heads = []
		self.items = []
		self.case_configs = []
		self.load_success = True

		# widgets
		self.btn_choose_file = QPushButton(self)
		self.line_file = QLineEdit(self)
		self.btn_reload_file = QPushButton(self)
		self.btn_choose_folder = QPushButton(self)
		self.line_folder = QLineEdit(self)
		self.tabs = None

		self.ui_settings()

		return

	def ui_settings(self):
		base_height = self.line_file.height()
		first_row, second_row = 0.3, 1.5

		self.btn_choose_file.setText("Choose file")
		self.btn_choose_file.setFixedSize(self.width() * 0.18, self.btn_choose_file.height())
		self.btn_choose_file.move(self.width() * 0.02, base_height * first_row)
		self.btn_choose_file.clicked.connect(self.choose_file)

		self.line_file.setFixedSize(self.width() * 0.56, self.line_file.height())
		self.line_file.move(self.width() * 0.22, base_height * first_row)
		self.line_file.setFocusPolicy(Qt.NoFocus)
		self.line_file.textChanged.connect(self.can_release_load)

		self.btn_reload_file.setText("Reload file")
		self.btn_reload_file.setFixedSize(self.width() * 0.18, self.btn_reload_file.height())
		self.btn_reload_file.move(self.width() * 0.80, base_height * first_row)
		self.btn_reload_file.clicked.connect(self.load_file)
		self.btn_reload_file.setEnabled(False)

		self.btn_choose_folder.setText("Choose folder")
		self.btn_choose_folder.setFixedSize(self.width() * 0.18, self.btn_choose_folder.height())
		self.btn_choose_folder.move(self.width() * 0.02, base_height * second_row)
		self.btn_choose_folder.clicked.connect(self.choose_folder)

		self.line_folder.setFixedSize(self.width() * 0.76, self.line_folder.height())
		self.line_folder.move(self.width() * 0.22, base_height * second_row)
		self.line_folder.setFocusPolicy(Qt.NoFocus)
		self.line_folder.textChanged.connect(self.can_release_load)

		return

	def choose_file(self):
		file, ok = QFileDialog.getOpenFileName(self, "Choose file", os.getcwd(), self.file_format)

		if not ok:
			pass
		else:
			self.update_file(file)

		return

	def update_file(self, filename: str):
		# set the change flag
		self.config_file_changed = True if self.config_file != filename else False

		self.config_file = filename				  # record
		self.line_file.setText(self.config_file)  # show

		return

	def can_release_load(self, text: str):
		if not self.btn_reload_file.isEnabled():
			# when it is not enabled, this logic should be done
			if self.config_file and self.output_folder:
				self.btn_reload_file.setEnabled(True)
				# load the data
				self.load_file()
			else:
				self.btn_reload_file.setEnabled(False)
		else:
			# it has been enabled, no need to set its status
			# however, if the trigger is the file line edit, the data should be reload
			if self.config_file_changed:
				# load the data
				self.load_file()

		return

	def choose_folder(self):
		# open folder
		output_folder = QFileDialog.getExistingDirectory(self, "Choose Output Folder", os.getcwd())

		if not output_folder:
			pass
		else:
			self.update_folder(output_folder)

		return

	def update_folder(self, folder: str):
		self.output_folder = folder					  # record
		self.line_folder.setText(self.output_folder)  # show

		return

	def load_file(self):
		# clear the change flag to avoid reload the file
		self.config_file_changed = False

		# load the configurations first
		try:
			self.case_configs = CasesConfig(self.config_file)
			self.case_configs.finished.connect(self.load_finished)
			self.case_configs.start()
		except SheetNameError as exc:
			self.load_success = False
			err = Error(self, str(exc))
		except Exception as exc:
			self.load_success = False
			err = Error(self, "Error when loading {}: {}".format(self.config_file, repr(exc)))
		else:
			self.load_success = True

		return

	def load_finished(self):
		if self.load_success:
			self.majors = self.case_configs.majors
			self.minors = self.case_configs.minors
			self.heads = self.case_configs.head
			self.items = self.case_configs.items
			self.case_configs = self.case_configs.cases_config

			self.show_case()

		return

	def show_case(self):
		size = (self.width() * 0.96, self.height() * 0.98 - self.line_file.height() * 2.7)

		# initialize and render
		self.tabs = MajorTab(self.majors, self.minors, self.output_folder, self, size)
		self.tabs.start_signal.connect(self.start)
		self.tabs.finish_signal.connect(self.finish)
		for i in range(self.tabs.count()):
			for j in range(self.tabs.widget(i).count()):
				self.tabs.widget(i).widget(j).table.table.set_head(self.case_configs[i][j][self.heads])
				self.tabs.widget(i).widget(j).table.table.set_items(self.case_configs[i][j][self.items])

		# ui setting for the tabs
		self.tabs.move(int(self.width() * 0.02), int(self.line_file.height() * 2.7))
		self.tabs.show()

		return

	def start(self):
		self.btn_reload_file.setEnabled(False)
		self.btn_choose_file.setEnabled(False)
		self.btn_choose_folder.setEnabled(False)
		self.line_file.setEnabled(False)
		self.line_folder.setEnabled(False)

		return

	def finish(self):
		self.btn_reload_file.setEnabled(True)
		self.btn_choose_file.setEnabled(True)
		self.btn_choose_folder.setEnabled(True)
		self.line_file.setEnabled(True)
		self.line_folder.setEnabled(True)

		return


if __name__ == '__main__':
	import sys
	from PyQt5.QtWidgets import QApplication, QMainWindow

	# initialize an application instance
	app = QApplication(sys.argv)

	window = QMainWindow()
	window.setFixedSize(800, 300)

	entry = Entry(window, (800, 300))

	window.show()

	sys.exit(app.exec_())