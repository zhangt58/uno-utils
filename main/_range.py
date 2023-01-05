#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from com.sun.star.awt import FontWeight
from com.sun.star.table import BorderLine2


class CalcRange:

    _ATTRS = "_range", "_address", "address", "data", "width", "height"

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
        """Return a new cell range of the same shape after offset."""
        oSheet = self.get_sheet()
        (_l, _t), (_r, _b) = self.leftTopIndex, self.rightBottomIndex
        return CalcRange(
            oSheet.getCellRangeByPosition(_l + col, _t + row, _r + col,
                                          _b + row))

    def new_range(self, left_top_index=None, shape=None):
        """Return a new cell range from the given left top index to the
        given shape.

        Parameters
        ----------
        left_top_index : tuple
            A tuple of index of column and row as the starting cell
            position, defaults to the same left top index as current CalcRange.
        shape : tuple
            A tuple of total number of rows and columns, defaults to the
            same shape as curren CalcRange.
        """
        oSheet = self.get_sheet()
        if left_top_index is None:
            left_top_index = self.leftTopIndex
        if shape is None:
            shape = self.shape
        _l, _t = left_top_index
        nrow, ncol = shape
        return CalcRange(
                oSheet.getCellRangeByPosition(_l, _t,
                    _l + ncol - 1, _t + nrow -1))

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

    def bold_font(self):
        """Set font weight as bold.
        """
        self._range.CharWeight = FontWeight.BOLD

    def set_back_color(self, color=-1):
        """Set background color.
        """
        self._range.CellBackColor = color

    def __getattribute__(self, k):
        try:
            return super().__getattribute__(k)
        except AttributeError as init_err:
            try:
                return getattr(self._range, k)
            except AttributeError:
                raise init_err

    def __setattr__(self, k, v):
        if k not in self._ATTRS:
            setattr(self._range, k, v)
        else:
            super().__setattr__(k, v)

    def set_border_line(self, position='bottom', color=0, lw=20, ls=0):
        # ls: https://api.libreoffice.org/docs/idl/ref/namespacecom_1_1sun_1_1star_1_1table_1_1BorderLineStyle.html
        # https://api.libreoffice.org/docs/idl/ref/structcom_1_1sun_1_1star_1_1table_1_1BorderLine2.html#details
        bl = BorderLine2()
        bl.Color = color
        bl.LineWidth = lw
        bl.LineStyle = ls
        border_name = f'{position.capitalize()}Border'
        setattr(self._range, border_name, bl)
