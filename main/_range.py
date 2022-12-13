#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np


class CalcRange:
    def __init__(self, range):
        self._range = range
        self.address = range

    @property
    def name(self):
        """str: Absolute name of the range."""
        return self._range.AbsoluteName

    @property
    def sheet_index(self):
        """int : Index of current sheet."""
        return self.address.Sheet

    def get_sheet(self):
        """XSpreadsheet"""
        return self._range.getSpreadsheet()

    def offset(self, row=0, col=0):
        """Return a new cell range after offset."""
        oSheet = self.get_sheet()
        (_l, _t), (_r, _b) = self.leftTopIndex, self.rightBottomIndex
        return CalcRange(
            oSheet.getCellRangeByPosition(_l + col, _t + row, _r + col,
                                          _b + row))

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, range):
        self._address = range.getRangeAddress()

    @property
    def leftTopIndex(self):
        return self.address.StartColumn, self.address.StartRow

    @property
    def rightBottomIndex(self):
        return self.address.EndColumn, self.address.EndRow

    @property
    def shape(self):
        _l, _t = self.leftTopIndex
        _r, _b = self.rightBottomIndex
        return _b - _t + 1, _r - _l + 1

    @property
    def data(self):
        """ndarray: data array, with both Value and String."""
        return np.array(self._range.getDataArray())

    @data.setter
    def data(self, x):
        if isinstance(x, np.ndarray):
            self._range.setDataArray(x.tolist())
        else:
            self._range.setDataArray(x)

    def auto_width(self):
        """Auto fit the column width."""
        self._range.Columns.OptimalWidth = True

    def auto_height(self):
        """Auto fit the row height."""
        self._range.Rows.OptimalHeight = True

    @property
    def width(self):
        """int : Column width."""
        return self._range.Columns.Width

    @width.setter
    def width(self, i: int):
        self._range.Columns = i

    @property
    def height(self):
        """int : Row height."""
        return self._range.Rows.height

    @height.setter
    def height(self, i: int):
        self._range.Rows = i
