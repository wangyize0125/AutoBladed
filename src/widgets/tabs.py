# -*- coding: utf-8 -*-
# @Time    : 2021/7/19 10:05
# @Author  : Yize Wang
# @File    : tabs.py
# @Software: AutoBladed

import os
import yaml
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTabWidget, QWidget, QFileDialog, QApplication
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QProgressBar

from msg_boxes import Error
from kernels import RunCases
from msg_boxes import Information
from find_file import RESOURCE_ROOT
from widgets.tables import TableWithButton
from exceptions import AliasNameNotFound, AliasNameParseError


def check_selected_and_alias(selected: dict, alias: dict) -> bool:
	"""
	check the pre-defined alias and selected cases' alias is matched
	pre-defined alias is in the .yml file
	"""

	s_alias = list(selected[list(selected.keys())[0]].keys())
	s_alias.remove("Case_name")
	a_alias = alias.keys()

	for temp_s_alias in s_alias:
		if temp_s_alias not in a_alias:
			return False

	return True


class TabWidget(QWidget):
	"""
	developed table widget with some buttons
	"""

	default_num_parallel = 3
	bar_max = 1E6
	file_format = "DTBLADED (*.IN)"

	start_signal = pyqtSignal()
	finish_signal = pyqtSignal()

	def __init__(self, major, minor, output_folder, parent=None, size=(800, 600)):
		super(TabWidget, self).__init__(parent)

		# resize it self
		self.setFixedSize(*size)

		# case name and tab name
		self.name = "{}.{}".format(major, minor)
		self.output_folder = os.path.join(output_folder, self.name)
		self.alias_and_name_file = os.path.join(RESOURCE_ROOT, "configs/{}.yml".format(self.name))

		# record the thread, otherwise it will be released
		self.run_cases_thread = None

		# table list
		self.table = TableWithButton(self, size)

		# widget list
		self.label_parallel = QLabel(self)
		self.line_parallel = QLineEdit(self)
		self.btn_run_selected = QPushButton(self)
		self.p_bar = QProgressBar(self)
		self.btn_abort = QPushButton(self)
		self.btn_choose_project = QPushButton(self)
		self.line_project = QLineEdit(self)

		self.ui_settings()

		return

	def ui_settings(self):
		# button space
		base_height = self.btn_run_selected.height() * 1.05
		btn_width = self.width() * 0.17

		self.label_parallel.setText("Parallel core:")
		self.label_parallel.setFixedSize(btn_width, self.label_parallel.height())
		self.label_parallel.move(self.width() * 0.82, base_height * 3.1)

		self.line_parallel.setPlaceholderText("Default: {}".format(self.default_num_parallel))
		self.line_parallel.setFixedSize(btn_width, self.line_parallel.height())
		self.line_parallel.move(self.width() * 0.82, base_height * 4.1)
		self.line_parallel.setValidator(QtGui.QIntValidator())

		self.btn_run_selected.setText("Run selected")
		self.btn_run_selected.setFixedSize(btn_width, self.btn_run_selected.height())
		self.btn_run_selected.move(self.width() * 0.82, base_height * 5.2)
		self.btn_run_selected.clicked.connect(self.run_cases)
		self.btn_run_selected.setEnabled(False)

		self.p_bar.setFixedSize(btn_width, self.p_bar.height())
		self.p_bar.move(self.width() * 0.82, base_height * 6.2)
		self.p_bar.setRange(0, self.bar_max)
		self.p_bar.setVisible(False)

		self.btn_abort.setText("Abort")
		self.btn_abort.setFixedSize(btn_width, self.btn_abort.height())
		self.btn_abort.move(self.width() * 0.82, base_height * 7.2)
		self.btn_abort.clicked.connect(self.stop_cases)
		self.btn_abort.setVisible(False)

		self.btn_choose_project.setText("Choose DTBLADED.IN")
		self.btn_choose_project.setFixedSize(btn_width, self.btn_choose_project.height())
		self.btn_choose_project.move(self.width() * 0.82, base_height * 8.2)
		self.btn_choose_project.clicked.connect(self.choose_bladed_file)

		self.line_project.setFixedSize(btn_width, self.line_parallel.height())
		self.line_project.move(self.width() * 0.82, base_height * 9.2)
		self.line_project.setFocusPolicy(Qt.NoFocus)
		self.line_project.textChanged.connect(self.bladed_changed)

		return

	def choose_bladed_file(self):
		file, ok = QFileDialog.getOpenFileName(self, "Choose Bladed file", os.getcwd(), self.file_format)

		if not ok:
			pass
		else:
			self.update_file(file)

		return

	def update_file(self, filename: str):
		self.line_project.setText(filename)

		return

	def bladed_changed(self, filename: str):
		if self.line_project.text():
			self.btn_run_selected.setEnabled(True)
		else:
			self.btn_run_selected.setEnabled(False)

		return

	def set_calculating(self, flag: bool):
		self.table.setEnabled(not flag)
		self.label_parallel.setEnabled(not flag)
		self.line_parallel.setEnabled(not flag)
		self.btn_run_selected.setEnabled(not flag)
		self.btn_choose_project.setEnabled(not flag)
		self.line_project.setEnabled(not flag)

		self.p_bar.setValue(0)
		self.p_bar.setVisible(flag)
		self.btn_abort.setVisible(flag)

		if flag:
			self.start_signal.emit()
		else:
			self.finish_signal.emit()

		# this function will always be called after the calculations done
		# so check the status of the threads here
		if not flag:
			# finish the calculations, check the flags of the tasks
			status = self.table.get_status()
			if self.run_cases_thread.get_fail_flag() in status:
				info = Information(self, "{}\n{}".format(
					"Failed calculation detected!",
					"Log can be found in {}_log.txt in each case folder.".format(QApplication.applicationName())
				))

		return

	def load_alias_and_name(self) -> dict:
		try:
			file = open(self.alias_and_name_file, "r")
		except Exception as exc:
			# fatal error which will stop the calculations
			raise AliasNameNotFound(self.alias_and_name_file)

		try:
			alias_and_name = yaml.load(file, Loader=yaml.FullLoader)
		except Exception as exc:
			raise AliasNameParseError(self.alias_and_name_file)

		return alias_and_name

	def run_cases(self):
		"""
		run the cases in parallel
		"""

		# get selected configs first
		selected = self.table.table.get_selected()

		try:
			# get alias and name dictionary
			alias_and_name = self.load_alias_and_name()
		except AliasNameNotFound as exc:
			err = Error(self, str(exc))
			return
		except AliasNameParseError as exc:
			err = Error(self, str(exc))
			return

		if len(selected.keys()) != 0:
			# there have selected configs
			if check_selected_and_alias(selected, alias_and_name):
				mt = self.line_parallel.text() if self.line_parallel.text() else self.default_num_parallel

				try:
					# create the thread
					self.run_cases_thread = RunCases(
						int(mt),						# parallel task number
						alias_and_name,					# alias and name in .yml file
						selected,						# selected cases
						self.output_folder,				# output folder local
						self.line_project.text()		# bladed project file
					)
					self.run_cases_thread.start_signal.connect(self.set_calculating)
					self.run_cases_thread.one_case_started_signal.connect(self.one_case_started)
					self.run_cases_thread.one_case_finished_signal.connect(self.update_bar)
					self.run_cases_thread.finish_signal.connect(self.set_calculating)
					self.run_cases_thread.one_case_aborted_signal.connect(self.one_case_aborted)
					self.run_cases_thread.start()
				except Exception as exc:
					err = Error(self, repr(exc))
			else:
				err = Error(self, "Alias in {} does not match the configurations".format(self.alias_and_name_file))
		else:
			info = Information(self, "No case selected!")

		return

	def update_bar(self, num_threads: int, success_flag: dict):
		self.p_bar.setValue(self.p_bar.value() + self.bar_max / num_threads)

		# change the success flag
		self.table.table.update_status(success_flag)

	def stop_cases(self):
		self.run_cases_thread.stop()

	def one_case_started(self, status: dict):
		# change the success flag
		self.table.table.update_status(status)

	def one_case_aborted(self, status: dict):
		# change the success flag
		self.table.table.update_status(status)


class MinorTab(QTabWidget):
	"""
	minor tab widget is the sub-case of IEC
	"""

	start_signal = pyqtSignal()
	finish_signal = pyqtSignal()

	def __init__(self, major, minors: list, output_folder, parent=None, size=(800, 600)):
		super(MinorTab, self).__init__(parent)

		self.setFixedSize(*size)

		# minor tab name
		self.name = "{}.*".format(major)
		self.output_folder = output_folder

		# all minors stored here
		self.major = major
		self.minors = minors
		self.num_minor = len(minors)
		self.running_tabs = 0

		# implement them one-by-one
		for minor in self.minors:
			try:
				temp_tab = TabWidget(major, minor, self.output_folder, self, size)
				temp_tab.start_signal.connect(self.one_tab_start)
				temp_tab.finish_signal.connect(self.one_tab_finish)
				self.addTab(temp_tab, temp_tab.name)
			except Exception as exc:
				err = Error(self, "When loading {}.{} occurred: {}".format(self.major, minor, str(exc)))

		return

	def one_tab_start(self):
		if self.running_tabs == 0:
			# emit one time only
			self.start_signal.emit()

		self.running_tabs += 1

		return

	def one_tab_finish(self):
		self.running_tabs -= 1

		if self.running_tabs == 0:
			# emit finish when all the tabs finished
			self.finish_signal.emit()

		return


class MajorTab(QTabWidget):
	"""
	major tab is the major case of IEC
	"""

	start_signal = pyqtSignal()
	finish_signal = pyqtSignal()

	def __init__(self, majors: list, minors: list, output_folder, parent=None, size=(800, 600)):
		super(MajorTab, self).__init__(parent)

		self.setFixedSize(*size)

		# all majors and minors stored here
		self.num_major = len(majors)
		self.majors = majors
		self.minors = minors
		self.output_folder = output_folder
		self.running_tabs = 0

		# implement them one-by-one
		for idx in range(self.num_major):
			try:
				temp_tab = MinorTab(self.majors[idx], self.minors[idx], self.output_folder, self, size)
				temp_tab.start_signal.connect(self.one_tab_start)
				temp_tab.finish_signal.connect(self.one_tab_finish)
				self.addTab(temp_tab, temp_tab.name)
			except Exception as exc:
				err = Error(self, "When loading {}.* occurred: {}".format(self.majors[idx], str(exc)))

		return

	def one_tab_start(self):
		if self.running_tabs == 0:
			# emit one time only
			self.start_signal.emit()

		self.running_tabs += 1

		return

	def one_tab_finish(self):
		self.running_tabs -= 1

		if self.running_tabs == 0:
			# emit finish when all the tabs finished
			self.finish_signal.emit()

		return


if __name__ == '__main__':
	import sys
	from PyQt5.QtWidgets import QApplication, QMainWindow

	# initialize an application instance
	app = QApplication(sys.argv)

	window = QMainWindow()
	window.setFixedSize(800, 300)

	# table = TableWidget(window)
	# table.setFixedSize(500, 260)
	tab = MajorTab([1, 2, 3, 4], [[2, 3, 4, 5], [2, 3, 4, 5], [2, 3, 4, 5], [2, 3, 4, 5]], window, (600, 260))
	for i in range(tab.count()):
		for j in range(tab.widget(i).count()):
			tab.widget(i).widget(j).table.table.set_head(["Vhub", "Yaw_error", "Case_name"])
			tab.widget(i).widget(j).table.table.set_items([
				["abc", 1, ""],
				["def", 2, "  "],
				["7865", 34, "ada"]
			])

	window.show()

	sys.exit(app.exec_())

