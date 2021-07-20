# -*- coding: utf-8 -*-
# @Time    : 2021/7/19 16:53
# @Author  : Yize Wang
# @File    : run_cases.py
# @Software: AutoBladed

import os
import time
import queue
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import QThread

from msg_boxes import FatalError

def check_bladed(parent=None):
	if "BLADED_PATH" not in os.environ.keys():
		fatal_err = FatalError(parent, "BLADED_PATH must be set as an environmental variable!")
	else:
		pass

	return


class RunOneCase(QThread):
	"""
	run one case in one thread
	"""

	start_signal = pyqtSignal(dict)
	finish_signal = pyqtSignal(dict)

	def __init__(self, alias_and_name, alias_and_value):
		super(RunOneCase, self).__init__()

		# self.one_case_finished = pyqtSignal()
		self.bladed_path = os.environ["BLADED_PATH"]

		self.alias_and_name = alias_and_name
		self.alias_and_value = alias_and_value
		self.running, self.succ, self.fail, self.aborted = "Runn.", "Succ.", "Fail.", "Abor."
		self.case_name = self.alias_and_value["Case_name"]

		return

	def run(self):
		# start the task
		self.start_signal.emit({self.case_name: self.running})

		time.sleep(3)
		print(self.alias_and_value)

		# finished the task
		self.finish_signal.emit({self.case_name: self.succ})

		return


class RunCases(QThread):
	"""
	use a thread to encapsulate the thread pool to aviod the app stuck
	"""

	start_signal = pyqtSignal(bool)
	one_case_started_signal = pyqtSignal(dict)
	one_case_finished_signal = pyqtSignal(int, dict)
	one_case_aborted_signal = pyqtSignal(dict)
	finish_signal = pyqtSignal(bool)

	def __init__(self, max_thread: int, alias_and_name, alias_and_values):
		super(RunCases, self).__init__()

		self.max_thread = max_thread
		self.alias_and_name = alias_and_name
		self.alias_and_values = alias_and_values
		self.num_threads = len(self.alias_and_values["Case_name"])
		self.finished_threads = 0

		# record all the threads
		self.threads = queue.Queue()
		self.threads_record = []
		for i in range(self.num_threads):
			temp_thread = RunOneCase(
				alias_and_name,
				{key: alias_and_values[key][i] for key in alias_and_values.keys()}
			)
			temp_thread.finish_signal.connect(self.one_case_finished)
			temp_thread.start_signal.connect(self.one_case_started)
			self.threads.put(temp_thread)
			self.threads_record.append(temp_thread)

		return

	def run(self):
		# emit start signal
		self.start_signal.emit(True)

		# only start this threads
		for i in range(self.max_thread):
			try:
				thread = self.threads.get(block=False)
				thread.start()
			except queue.Empty as exc:
				break

		return

	def stop(self):
		# clear the un-calculated case
		self.threads.queue.clear()

		# terminate the calculating case
		for thread in self.threads_record:
			if thread.isRunning():
				thread.terminate()
				thread.wait()
				self.one_case_aborted_signal.emit({thread.case_name: thread.aborted})

		self.finish_signal.emit(False)

	def one_case_finished(self, succ):
		self.finished_threads += 1
		self.one_case_finished_signal.emit(self.num_threads, succ)

		if self.finished_threads == self.num_threads:
			self.finish_signal.emit(False)

		# start the next thread
		try:
			thread = self.threads.get(block=False)
			thread.start()
		except queue.Empty as exc:
			pass

	def one_case_started(self, status):
		self.one_case_started_signal.emit(status)


if __name__ == '__main__':
    check_bladed()