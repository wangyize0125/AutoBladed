# -*- coding: utf-8 -*-
# @Time    : 2021/7/17 23:14
# @Author  : Yize Wang
# @File    : tables.py
# @Software: AutoBladed

from PyQt5.QtWidgets import QWidget, QTableWidget, QAbstractItemView, QTableWidgetItem
from PyQt5.QtGui import QFont, QDropEvent
from PyQt5.QtCore import Qt

# make python know where is the exceptions package
if __name__ == '__main__':
	import sys
	import os
	sys.path.append(os.path.dirname(__file__) + os.sep + '../')

from exceptions import GuiException


class TableWidget(QTableWidget):
	"""
	This is the table widget inherited from QTableWidget
	"""

	selected, unselected = ">>>", "   "

	def __init__(self, parent: QWidget) -> None:
		"""
		:param parent: father widget
		"""

		super(TableWidget, self).__init__(parent)

		# cell clicked signal-slot
		self.cellClicked.connect(self.cell_clicked)

		# set edit trigger to be double click
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)

		# set drag event
		self.setDragEnabled(True)
		self.setAcceptDrops(True)
		self.viewport().setAcceptDrops(True)
		self.setDragDropOverwriteMode(False)
		self.setDropIndicatorShown(True)
		self.setSelectionMode(QAbstractItemView.SingleSelection)
		self.setSelectionBehavior(QAbstractItemView.SelectItems)
		self.setDragDropMode(QAbstractItemView.InternalMove)
		self.dropEvent = self.drop_event

		return

	def cell_clicked(self, row, col) -> None:
		"""
		Built-in check-box exists problems, implement the choose function manually
		"""

		if self.item(row, 0).text() == self.selected:
			self.item(row, 0).setText(self.unselected)
		else:
			self.item(row, 0).setText(self.selected)

		return

	def drop_event(self, event: QDropEvent) -> None:
		# the items can only be moved in this table and in the same column
		original_row, original_col = self.selectedItems()[0].row(), self.selectedItems()[0].column()  # original one
		original_text = self.item(original_row, original_col).text()

		target_row, target_col = self.indexAt(event.pos()).row(), self.indexAt(event.pos()).column()  # drop where
		target_text = self.item(target_row, target_col).text()

		# drag to blank area
		if target_row != -1 and target_col != -1:
			# change the values
			if original_col == target_col and original_col != 0:
				# change the values
				self.item(target_row, target_col).setText(original_text)
				self.item(original_row, original_col).setText(target_text)

				# set tooltips
				if original_text.strip() != "":
					self.item(target_row, target_col).setToolTip(original_text)
				else:
					self.item(target_row, target_col).setToolTip("")
				if target_text.strip() != "":
					self.item(original_row, original_col).setToolTip(target_text)
				else:
					self.item(original_row, original_col).setToolTip("")

		return

	def set_head(self, heads: list) -> None:
		"""
		set head line of the table, the heads parameter should include the names of the heads
		"""

		# add a flag column at the head of them
		self.setColumnCount(len(heads) + 1)
		self.setColumnWidth(0, self.width() * 0.1)		# the first column is the flags, don't need too much spaces
		self.setHorizontalHeaderLabels([""] + heads)

		# set font
		font = QFont()
		font.setBold(True)						# bold
		self.horizontalHeader().setFont(font)

		return

	def set_items(self, items: list) -> None:
		"""
		set the items in the table, items should be a 2D array
		"""

		row, col = len(items), len(items[0])

		if col != self.columnCount() - 1:
			raise GuiException("Dimension of items does not match the table")
		else:
			col = self.columnCount()

		# font of flag (bold)
		font = QFont()
		font.setBold(True)

		# set new rows
		self.setRowCount(row)
		for i in range(row):
			# add the flag into the table
			flag = QTableWidgetItem(self.selected)
			flag.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
			flag.setFont(font)
			self.setItem(i, 0, flag)

			for j in range(1, col):
				# add the item into the table
				content = str(items[i][j - 1]).strip()
				temp_item = QTableWidgetItem(content)
				temp_item.setToolTip(content)
				temp_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
				self.setItem(i, j, temp_item)

		return


if __name__ == '__main__':
	from PyQt5.QtWidgets import QApplication, QMainWindow

	# initialize an application instance
	app = QApplication(sys.argv)

	window = QMainWindow()
	window.setFixedSize(600, 300)

	table = TableWidget(window)
	table.setFixedSize(500, 260)
	table.set_head(["wind file", "wind direction", "test"])
	table.set_items([
		["abc", 1, ""],
		["def", 2, "  "],
		["7865", 34, "ada"]
	])

	window.show()

	sys.exit(app.exec_())

