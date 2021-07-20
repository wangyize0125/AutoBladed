# -*- coding: utf-8 -*-
# @Time    : 2021/7/17 23:14
# @Author  : Yize Wang
# @File    : tables.py
# @Software: AutoBladed

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDropEvent
from PyQt5.QtWidgets import QWidget, QAbstractItemView
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QPushButton

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

	def check_selected(self, row: int) -> bool:
		"""
		check whether the current row is selected
		:param row:
		:return: is selected?
		"""

		return True if self.item(row, 0).text() == self.selected else False

	def cell_clicked(self, row, col) -> None:
		"""
		Built-in check-box exists problems, implement the choose function manually
		"""

		text = self.selected if not self.check_selected(row) else self.unselected
		self.item(row, 0).setText(text)

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
				self.item(target_row, target_col).setToolTip(original_text.strip())
				self.item(original_row, original_col).setToolTip(target_text.strip())

		return

	def set_head(self, heads: list) -> None:
		"""
		set head line of the table, the heads parameter should include the names of the heads
		"""

		# add a flag column at the head of them
		self.setColumnCount(len(heads) + 1)
		self.setColumnWidth(0, int(self.width() * 0.1))  # the first column is the flags, don't need too much spaces
		self.setHorizontalHeaderLabels([" "] + list(heads))

		# set font
		font = QFont()
		font.setBold(True)						# bold
		self.horizontalHeader().setFont(font)

		return

	def set_items(self, items: list) -> None:
		"""
		set the items in the table, items should be a 2D array
		"""

		row = len(items)
		col = len(items[0]) if row != 0 else 0

		if col != self.columnCount() - 1 and row != 0:
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

	def get_selected(self) -> dict:
		"""
		return the selected items as a dictionary
		"""

		row, col = self.rowCount(), self.columnCount()

		# yield the dictionary first
		selected = {}
		for i in range(1, col):
			# use a list to store the values, the values are in the same order
			selected[self.horizontalHeaderItem(i).text()] = []

		# append the selected items
		for i in range(row):
			if self.check_selected(i):
				for j in range(1, col):
					selected[self.horizontalHeaderItem(j).text()].append(self.item(i, j).text())

		return selected

	def update_status(self, success_flag: dict):
		name_col = 0
		for i in range(self.columnCount()):
			if self.horizontalHeaderItem(i).text() == "Case_name":
				name_col = i
				break

		for i in range(self.rowCount()):
			if self.item(i, name_col).text() in success_flag.keys():
				self.item(i, 0).setText(success_flag[self.item(i, name_col).text()])

		return


class TableWithButton(QWidget):
	"""
	encapsulate the table widget with kinds of buttons
	"""

	def __init__(self, parent=None, size=(500, 260)):
		super(TableWithButton, self).__init__(parent)

		# set fix size of the widget
		self.setFixedSize(*size)

		# variable list table
		self.table = TableWidget(self)

		# buttons
		self.btn_select_all = QPushButton(self)
		self.btn_unselect_all = QPushButton(self)
		self.btn_delete_selected = QPushButton(self)

		self.ui_setting()

		return

	def ui_setting(self):
		"""
		ui settings of the buttons
		"""

		# button space
		space = 1.05
		base_height = self.btn_select_all.height()

		self.table.setFixedSize(int(self.width() * 0.8), self.height())
		self.table.move(0, 0)

		self.btn_select_all.setText("Select all")
		self.btn_select_all.setFixedSize(self.width() * 0.18, self.btn_select_all.height())
		self.btn_select_all.move(self.width() * 0.82, 0)
		self.btn_select_all.clicked.connect(self.select_all)

		self.btn_unselect_all.setText("Unselect all")
		self.btn_unselect_all.setFixedSize(self.width() * 0.18, self.btn_unselect_all.height())
		self.btn_unselect_all.move(self.width() * 0.82, base_height * space)
		self.btn_unselect_all.clicked.connect(self.unselect_all)

		self.btn_delete_selected.setText("Delete selected")
		self.btn_delete_selected.setFixedSize(self.width() * 0.18, self.btn_delete_selected.height())
		self.btn_delete_selected.move(self.width() * 0.82, base_height * space * 2)
		self.btn_delete_selected.clicked.connect(self.delete_selected)

		return

	def select_all(self):
		row = self.table.rowCount()

		for i in range(row):
			self.table.item(i, 0).setText(self.table.selected)

		return

	def unselect_all(self):
		row = self.table.rowCount()

		for i in range(row):
			self.table.item(i, 0).setText(self.table.unselected)

		return

	def delete_selected(self):
		row, col = self.table.rowCount(), self.table.columnCount()

		# record the unselected items into a new items list
		items = []
		for i in range(row):
			if not self.table.check_selected(i):
				# if this row is not selected, record it
				temp_item = []
				for j in range(1, col):
					temp_item.append(self.table.item(i, j).text())
				# record the current row
				items.append(temp_item)

		self.table.set_items(items)

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
	table_with_button = TableWithButton(window, (600, 260))
	table_with_button.table.set_head(["wind file", "wind direction", "test"])
	table_with_button.table.set_items([
		["abc", 1, ""],
		["def", 2, "  "],
		["7865", 34, "ada"]
	])

	window.show()

	sys.exit(app.exec_())

