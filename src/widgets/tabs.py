# -*- coding: utf-8 -*-
# @Time    : 2021/7/19 10:05
# @Author  : Yize Wang
# @File    : tabs.py
# @Software: AutoBladed

import os
import yaml
from PyQt5.QtWidgets import QTabWidget, QWidget
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QProgressBar

from msg_boxes import Error
from kernels import RunCases
from msg_boxes import Information
from find_file import RESOURCE_ROOT
from widgets.tables import TableWithButton


def check_selected_and_alias(selected: dict, alias: dict) -> bool:
	s_alias = list(selected.keys())
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
	bar_max = 1E5

	def __init__(self, major, minor, parent=None, size=(800, 600)):
		super(TabWidget, self).__init__(parent)

		# resize it self
		self.setFixedSize(*size)

		# case name and tab name
		self.name = "{}.{}".format(major, minor)
		self.alias_and_name_file = os.path.join(RESOURCE_ROOT, "configs/{}.yml".format(self.name))

		# record the thread, otherwise it will be released
		self.run_cases_thread = None

		# table list
		self.table_with_btn = TableWithButton(self, size)

		# widget list
		self.label_parallel_task = QLabel(self)
		self.line_parallel_task = QLineEdit(self)
		self.btn_run_selected = QPushButton(self)
		self.p_bar = QProgressBar(self)
		self.btn_abort = QPushButton(self)

		self.ui_settings()

		return

	def ui_settings(self):
		# button space
		space = 1.05
		base_height = self.btn_run_selected.height()

		self.label_parallel_task.setText("Parallel core:")
		self.label_parallel_task.setFixedSize(self.width() * 0.18, self.label_parallel_task.height())
		self.label_parallel_task.move(self.width() * 0.82, base_height * space * 3.1)

		self.line_parallel_task.setPlaceholderText("Default: {}".format(self.default_num_parallel))
		self.line_parallel_task.setFixedSize(self.width() * 0.18, self.line_parallel_task.height())
		self.line_parallel_task.move(self.width() * 0.82, base_height * space * 4.1)

		self.btn_run_selected.setText("Run selected")
		self.btn_run_selected.setFixedSize(self.width() * 0.18, self.btn_run_selected.height())
		self.btn_run_selected.move(self.width() * 0.82, base_height * space * 5.2)
		self.btn_run_selected.clicked.connect(self.run_cases)

		self.p_bar.setFixedSize(self.width() * 0.18, self.p_bar.height())
		self.p_bar.move(self.width() * 0.82, base_height * space * 6.2)
		self.p_bar.setRange(0, self.bar_max)
		self.p_bar.setVisible(False)

		self.btn_abort.setText("Abort")
		self.btn_abort.setFixedSize(self.width() * 0.18, self.btn_abort.height())
		self.btn_abort.move(self.width() * 0.82, base_height * space * 7.2)
		self.btn_abort.clicked.connect(self.stop_cases)
		self.btn_abort.setVisible(False)

		return

	def set_calculating(self, flag: bool):
		self.table_with_btn.setEnabled(not flag)
		self.label_parallel_task.setEnabled(not flag)
		self.line_parallel_task.setEnabled(not flag)
		self.btn_run_selected.setEnabled(not flag)

		self.p_bar.setValue(0)
		self.p_bar.setVisible(flag)
		self.btn_abort.setVisible(flag)

		return

	def load_alias_and_name(self) -> dict:
		file = open(self.alias_and_name_file, "r")
		alias_and_name = yaml.load(file, Loader=yaml.FullLoader)

		return alias_and_name

	def run_cases(self):
		"""
		run the cases in parallel
		"""

		# get selected configs first
		selected = self.table_with_btn.table.get_selected()

		# get alias and name dictionary
		alias_and_name = self.load_alias_and_name()

		if len(selected["Case_name"]) != 0:
			# selected configs
			if alias_and_name:
				if check_selected_and_alias(selected, alias_and_name):
					mt = self.line_parallel_task.text() if self.line_parallel_task.text() else self.default_num_parallel

					# create the thread
					self.run_cases_thread = RunCases(int(mt), alias_and_name, selected)
					self.run_cases_thread.start_signal.connect(self.set_calculating)
					self.run_cases_thread.one_case_started_signal.connect(self.one_case_started)
					self.run_cases_thread.one_case_finished_signal.connect(self.update_bar)
					self.run_cases_thread.finish_signal.connect(self.set_calculating)
					self.run_cases_thread.one_case_aborted_signal.connect(self.one_case_aborted)
					self.run_cases_thread.start()
				else:
					err = Error(self, "Alias in {} does not match the configurations".format(self.alias_and_name_file))
			else:
				err = Error(self, "Load {} failed. Calculation is Aborted".format(self.alias_and_name_file))
		else:
			info = Information(self, "No case selected!")

		return

	def update_bar(self, num_threads, success_flag: dict):
		self.p_bar.setValue(self.p_bar.value() + self.bar_max / num_threads)

		# change the success flag
		self.table_with_btn.table.update_status(success_flag)

	def stop_cases(self):
		self.run_cases_thread.stop()

	def one_case_started(self, status: dict):
		# change the success flag
		self.table_with_btn.table.update_status(status)

	def one_case_aborted(self, status: dict):
		# change the success flag
		self.table_with_btn.table.update_status(status)


class MinorTab(QTabWidget):
	"""
	minor tab widget is the sub-case of IEC
	"""

	def __init__(self, major, minors: list, parent=None, size=(800, 600)):
		super(MinorTab, self).__init__(parent)

		self.setFixedSize(*size)

		# minor tab name
		self.name = "{}.*".format(major)

		# all minors stored here
		self.major = major
		self.minors = minors
		self.num_minor = len(minors)

		# implement them one-by-one
		for i in range(self.num_minor):
			temp_tab = TabWidget(major, self.minors[i], self, size)
			self.addTab(temp_tab, temp_tab.name)

		return


class MajorTab(QTabWidget):
	"""
	major tab is the major case of IEC
	"""

	def __init__(self, majors, minors, parent=None, size=(800, 600)):
		super(MajorTab, self).__init__(parent)

		self.setFixedSize(*size)

		# all majors and minors stored here
		self.num_major = len(majors)
		self.majors = majors
		self.minors = minors

		# implement them one-by-one
		for i in range(self.num_major):
			temp_tab = MinorTab(self.majors[i], self.minors[i], self, size)
			self.addTab(temp_tab, temp_tab.name)

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
			tab.widget(i).widget(j).table_with_btn.table.set_head(["Vhub", "Yaw_error", "Case_name"])
			tab.widget(i).widget(j).table_with_btn.table.set_items([
				["abc", 1, ""],
				["def", 2, "  "],
				["7865", 34, "ada"]
			])

	window.show()

	sys.exit(app.exec_())

