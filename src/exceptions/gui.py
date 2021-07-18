# -*- coding: utf-8 -*-
# @Time    : 2021/7/18 13:45
# @Author  : Yize Wang
# @File    : gui.py
# @Software: AutoBladed

class GuiException(Exception):
	"""
	raise the gui errors
	"""

	def __init__(self, err_msg: str):
		super(GuiException, self).__init__(self)

		# class name
		self.name = self.__class__.__name__

		self.err_msg = err_msg

	def __str__(self):
		return self.name + ": " + self.err_msg
