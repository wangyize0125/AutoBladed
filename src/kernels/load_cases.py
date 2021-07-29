# -*- coding: utf-8 -*-
# @Time    : 2021/7/19 13:45
# @Author  : Yize Wang
# @File    : load_cases.py
# @Software: AutoBladed

import numpy as np
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal

from exceptions import SheetNameError


class CasesConfig(QThread):
	"""
	when the cases configuration is large, the parse time would be so long
	hence, here I use thread to encapsulate this calculations
	"""

	head = "head"
	items = "items"

	finish_signal = pyqtSignal(bool, str)

	def __init__(self, filename: str):
		super(CasesConfig, self).__init__()

		# record input
		self.filename = filename

		# use dictionary to store the cases configurations
		self.majors = []			# major cases
		self.minors = []			# minor cases
		self.cases_config = []		# their configurations

		return

	def run(self):
		raw_data = pd.read_excel(self.filename, sheet_name=None, engine="openpyxl")

		# parse majors of the cases
		self.parse_majors(raw_data)

		try:
			# parse minors of the cases
			self.parse_minors(raw_data)
		except Exception as exc:
			self.finish_signal.emit(False, str(exc))
		else:
			# parse configurations
			self.parse_configs(raw_data)

			self.finish_signal.emit(True, "Successful")

		return

	def parse_majors(self, raw_data: dict):
		# all the sheets
		sheets = raw_data.keys()
		# at the left of dot
		self.majors = list(set([sheet.split(".")[0].strip() for sheet in sheets]))
		# sort them
		self.majors.sort()

		return

	def parse_minors(self, raw_data: dict):
		num_majors = len(self.majors)
		# initialize the minors array
		self.minors = [[] for i in range(num_majors)]

		sheets = raw_data.keys()
		for sheet in sheets:
			major_and_minor = sheet.split(".")
			if len(major_and_minor) != 2:
				raise SheetNameError(self.filename)

			# loop for each sheet
			idx = self.majors.index(major_and_minor[0].strip())
			# append this sheet
			self.minors[idx].append(major_and_minor[1].strip())

		for i in range(num_majors):
			# sort them
			self.minors[i].sort()

		return

	def parse_configs(self, raw_data: dict):
		# initialize the empty configuration list
		num_major = len(self.majors)
		for i in range(num_major):
			temp = [1 for j in range(len(self.minors[i]))]
			self.cases_config.append(temp)

		for sheet, value in raw_data.items():
			major, minor = sheet.split(".")
			idx_major = self.majors.index(major.strip())
			idx_minor = self.minors[idx_major].index(minor.strip())

			head = value.columns
			value = np.array(value).tolist()
			self.cases_config[idx_major][idx_minor] = {self.head: head, self.items: value}

		return


if __name__ == '__main__':
	import sys
	from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

	# initialize an application instance
	app = QApplication(sys.argv)

	window = QMainWindow()
	window.setFixedSize(800, 300)
	btn = QPushButton(window)

	work = CasesConfig("../../data/LoadCases.xlsx")
	btn.clicked.connect(work.start)

	window.show()

	sys.exit(app.exec_())