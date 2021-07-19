# -*- coding: utf-8 -*-
# @Time    : 2021/7/19 16:53
# @Author  : Yize Wang
# @File    : run_cases.py
# @Software: AutoBladed

import os
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import QThread, QObject, QRunnable, QThreadPool

from msg_boxes import FatalError

def check_bladed(parent=None):
	if "BLADED_PATH" not in os.environ.keys():
		fatal_err = FatalError(parent, "BLADED_PATH must be set as an environmental variable!")
	else:
		pass

	return


class RunOneCase(QRunnable):
	"""
	run one case in one thread
	"""

	def __init__(self, alias_and_name, alias_and_value):
		super(RunOneCase, self).__init__()

		# self.one_case_finished = pyqtSignal()
		self.bladed_path = os.environ["BLADED_PATH"]

		self.alias_and_name = alias_and_name
		self.alias_and_value = alias_and_value

		return

	def run(self):
		print(self.alias_and_name)
		print(self.alias_and_value)

		# # finished the task
		# self.one_case_finished.emit()

		return


class CasePool(QObject):
	"""
	use thread pool to manage the threads
	"""

	def __init__(self, max_thread, alias_and_name: dict, alias_and_values: dict):
		super(CasePool, self).__init__()

		# self.one_case_finished_signal = pyqtSignal(int)

		self.max_thread = max_thread
		self.alias_and_name = alias_and_name
		self.alias_and_values = alias_and_values
		self.num_threads = len(self.alias_and_values["Case_name"])

		# pool
		self.thread_pool = QThreadPool()

		return

	def start(self):
		# set the maximum thread number
		self.thread_pool.setMaxThreadCount(self.max_thread)

		for i in range(self.num_threads):
			one_case = RunOneCase(
				self.alias_and_name,
				{key: self.alias_and_values[key][i] for key in self.alias_and_values.keys()}
			)
			# one_case.one_case_finished.connect(self.one_case_finished)
			one_case.setAutoDelete(True)
			self.thread_pool.start(one_case)

		return

	# def one_case_finished(self):
	# 	# self.one_case_finished_signal.emit(self.num_threads)
	# 	print("yes")

class RunCases(QThread):
	"""
	use a thread to encapsulate the thread pool to aviod the app stuck
	"""

	def __init__(self, max_thread: int, alias_and_name, alias_and_values):
		super(RunCases, self).__init__()

		# self.one_case_finished_signal = pyqtSignal(int)

		self.max_thread = max_thread
		self.alias_and_name = alias_and_name
		self.alias_and_values = alias_and_values

		self.thread_pool = CasePool(self.max_thread, self.alias_and_name, self.alias_and_values)
		# self.thread_pool.one_case_finished_signal.connect(self.one_case_finished)

		return

	def run(self):
		self.thread_pool.start()

		return
	#
	# def one_case_finished(self, num_threads):
	# 	self.one_case_finished_signal.emit(num_threads)


if __name__ == '__main__':
    check_bladed()