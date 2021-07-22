# -*- coding: utf-8 -*-
# @Time    : 2021/7/19 16:53
# @Author  : Yize Wang
# @File    : run_cases.py
# @Software: AutoBladed

import os
import queue
import shutil
import psutil
import subprocess
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import QThread
from PyQt5.QtWidgets import QApplication

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

	def __init__(self, alias_and_name, alias_and_value, output_folder, bladed_file, case_id):
		super(RunOneCase, self).__init__()

		# self.one_case_finished = pyqtSignal()
		self.case_id = case_id
		self.bladed_exe_path = os.path.join(os.environ["BLADED_PATH"], "dtbladed.exe")
		self.output_folder = os.path.join(output_folder, alias_and_value["Case_name"]).replace("/", "\\")
		self.case_folder = os.path.join(self.output_folder, "project")
		self.result_folder = os.path.join(self.output_folder, "results")
		self.bladed_file = bladed_file
		self.bladed_folder = os.path.dirname(self.bladed_file)
		self.bladed_file = os.path.join(self.case_folder, os.path.basename(self.bladed_file))
		self.bat_file = os.path.join(self.case_folder, "{}.bat".format(QApplication.applicationName()))
		self.log_file = None

		self.sub_process = None

		self.alias_and_name = alias_and_name
		self.alias_and_value = alias_and_value
		self.running, self.succ, self.fail, self.aborted = "Runn.", "Succ.", "Fail.", "Abor."
		self.case_name = self.alias_and_value["Case_name"]

		return

	def generate_signal(self, flag: str) -> dict:
		return {self.case_id: flag}

	def run(self):
		# start the task
		self.start_signal.emit(self.generate_signal(self.running))

		self.make_folders()					# make folder first
		flag = self.copy_files()			# copy files into this folder
		if flag:
			flag = self.modify_file()			# modify the project file correspondingly
			if flag:
				flag = self.call_bladed()			# call dtbladed.exe
				if flag:
					self.finish_signal.emit(self.generate_signal(self.succ))
				else:
					self.finish_signal.emit(self.generate_signal(self.fail))
			else:
				# finished the task
				self.finish_signal.emit(self.generate_signal(self.fail))
		else:
			# finished the task
			self.finish_signal.emit(self.generate_signal(self.fail))

		# close the log file when it is deleted
		self.log_file.close()

		return

	def make_folders(self):
		if not os.path.exists(self.case_folder):
			os.makedirs(self.case_folder)
		if not os.path.exists(self.result_folder):
			os.makedirs(self.result_folder)

		return

	def copy_files(self) -> bool:
		self.log_file = open(os.path.join(self.case_folder, "{}_log.txt".format(QApplication.applicationName())), "w")

		try:
			# following codes may throw exceptions
			# only copy files
			for root, dirs, files in os.walk(self.bladed_folder):
				for file in files:
					src_file = os.path.join(self.bladed_folder, file)
					shutil.copy(src_file, self.case_folder)

			# write a bat file under this folder
			with open(self.bat_file, "w") as file:
				file.write("cd /d \"{}\"\n".format(self.case_folder))
				file.write("\"{}\" \"{}\"\n".format(self.bladed_exe_path, self.bladed_file))
		except Exception as exc:
			self.log_file.write("{} (When copying files and generating bat file): {}".format(self.case_name, repr(exc)))
			return False

		return True

	def modify_file(self) -> bool:
		"""
		modify the project file according to the configurations
		"""

		try:
			var_names, var_values = [], []
			# load the original configurations first
			with open(self.bladed_file, "r") as file:
				for line in file.readlines():
					temp_data = line.split("\t")

					var_names.append(temp_data[0].strip())						# first is the variable name
					var_values.append("\t".join(temp_data[1:]).strip())			# the last are the values
		except Exception as exc:
			self.log_file.write("{} (When read DTBLADED.IN): {}\n".format(self.case_name, repr(exc)))
			return False

		try:
			# change the values
			var_values[var_names.index("PATH")] = self.result_folder			# change path
			for alias, name in self.alias_and_name.items():
				var_values[var_names.index(name)] = self.alias_and_value[alias]
		except Exception as exc:
			self.log_file.write("{} (When substituting values in DTBLADED.IN): {}\n".format(self.case_name, repr(exc)))
			return False

		# re-write the file
		with open(self.bladed_file, "w") as file:
			for name, value in zip(var_names, var_values):
				file.write(name + "\t" + value + "\n")

		return True

	def call_bladed(self) -> bool:
		try:
			self.sub_process = subprocess.Popen("call \"{}\"".format(self.bat_file), shell=True)
			ok = self.sub_process.wait()
		except Exception as exc:
			self.log_file.write("{} (When calling bat): {}\n".format(self.case_name, repr(exc)))
			return False

		if ok == 0:
			return True
		elif ok == 7:
			self.log_file.write("{}: {}\n".format(self.case_name, "Need to run the dtbladed.exe as Administer!"))
			return False
		else:
			self.log_file.write("{} (When calling dtbladed.exe): {}\n".format(self.case_name, "Unknown error!"))
			return False

	def get_fail_flag(self):
		return self.fail

	def stop_sub_process(self):
		# root thread id
		pid = self.sub_process.pid
		father = psutil.Process(pid)

		for child in father.children():
			child.terminate()


class RunCases(QThread):
	"""
	use a thread to encapsulate the thread pool to aviod the app stuck
	"""

	start_signal = pyqtSignal(bool)
	one_case_started_signal = pyqtSignal(dict)
	one_case_finished_signal = pyqtSignal(int, dict)
	one_case_aborted_signal = pyqtSignal(dict)
	finish_signal = pyqtSignal(bool)

	def __init__(self, max_thread: int, alias_and_name, alias_and_values, output_folder, bladed_file):
		super(RunCases, self).__init__()

		self.max_thread = max_thread
		self.alias_and_name = alias_and_name
		self.alias_and_values = alias_and_values
		self.num_threads = len(self.alias_and_values.keys())
		self.case_ids = list(self.alias_and_values.keys())
		self.finished_threads = 0
		self.output_folder = output_folder
		self.bladed_file = bladed_file

		# record all the threads
		self.threads = queue.Queue()
		self.threads_record = []
		for i in range(self.num_threads):
			temp_thread = RunOneCase(
				alias_and_name,
				self.alias_and_values[self.case_ids[i]],
				self.output_folder,
				self.bladed_file,
				self.case_ids[i]
			)
			temp_thread.finish_signal.connect(self.one_case_finished)
			temp_thread.start_signal.connect(self.one_case_started)
			self.threads.put(temp_thread)
			self.threads_record.append(temp_thread)

		return

	def run(self):
		# emit start signal
		self.start_signal.emit(True)

		# only start num_max_thread threads
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
				thread.terminate()			# terminate the thread itself
				thread.wait()
				thread.stop_sub_process()	# terminate its children
				self.one_case_aborted_signal.emit(thread.generate_signal(thread.aborted))

		self.finish_signal.emit(False)

	def one_case_finished(self, succ):
		self.finished_threads += 1
		self.one_case_finished_signal.emit(self.num_threads, succ)

		if self.finished_threads == self.num_threads:
			self.finish_signal.emit(False)
		else:
			# start the next thread
			try:
				thread = self.threads.get(block=False)
				thread.start()
			except queue.Empty as exc:
				pass

	def one_case_started(self, status):
		self.one_case_started_signal.emit(status)

	def get_fail_flag(self):
		return self.threads_record[0].get_fail_flag()


if __name__ == '__main__':
    check_bladed()