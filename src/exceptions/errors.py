# -*- coding: utf-8 -*-
# @Time    : 2021/7/22 11:40
# @Author  : Yize Wang
# @File    : errors.py
# @Software: AutoBladed

class AliasNameNotFound(Exception):
	"""
	raise the alias and name not found error
	"""

	def __init__(self, filename):
		super(AliasNameNotFound, self).__init__()

		# class name
		self.name = self.__class__.__name__
		self.stop_calculation = True

		self.err_msg = "Alias and name file: {} not found.\n".format(filename)
		self.err_msg += "You should implement this file first before starting the calculations"

		return

	def __str__(self):
		return self.name + ": " + self.err_msg


class AliasNameParseError(Exception):
	"""
	raise the alias and name not found error
	"""

	def __init__(self, filename):
		super(AliasNameParseError, self).__init__()

		# class name
		self.name = self.__class__.__name__
		self.stop_calculation = True

		self.err_msg = "Alias and name file: {} format error\n".format(filename)
		self.err_msg += "You should check the format in this file first before starting the calculations"

		return

	def __str__(self):
		return self.name + ": " + self.err_msg


class SheetNameError(Exception):
	"""
	raise the alias and name not found error
	"""

	def __init__(self, filename):
		super(SheetNameError, self).__init__()

		# class name
		self.name = self.__class__.__name__
		self.stop_calculation = True

		self.err_msg = "Sheet names in {} format error\n".format(filename)
		self.err_msg += "Sheet names here should only use one . to split major and minor case"

		return

	def __str__(self):
		return self.name + ": " + self.err_msg
