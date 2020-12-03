#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020/3/31 10:38 AM
# @Author  : w8ay
# @File    : datatype.py
import copy
import time
import types


class AttribDict(dict):
    """
    This class defines the dictionary with added capability to access members as attributes
    (该类定义具有附加功能的字典，以作为属性访问成员)
    """

    def __init__(self, indict=None, attribute=None):
        if indict is None:
            indict = {}

        # Set any attributes here - before initialisation(在这里设置任何属性——在初始化之前)
        # these remain as normal attributes(这些仍然是正常的属性)
        self.attribute = attribute
        dict.__init__(self, indict)
        self.__initialised = True

        # After initialisation, setting attributes(初始化后，设置属性)
        # is the same as setting an item(与设置项相同)

    def __getattr__(self, item):
        """
        Maps values to attributes（将值映射到属性）
        Only called if there *is NOT* an attribute with this name(只有在*没有*属性时才调用)
        """

        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError("unable to access item '%s'" % item)

    def __setattr__(self, item, value):
        """
        Maps attributes to values(将属性映射到值)
        Only if we are initialised(只有我们被初始化了)
        """

        # This test allows attributes to be set in the __init__ method
        if "_AttribDict__initialised" not in self.__dict__:
            return dict.__setattr__(self, item, value)

        # Any normal attributes are handled normally
        elif item in self.__dict__:
            dict.__setattr__(self, item, value)

        else:
            self.__setitem__(item, value)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, dict):
        self.__dict__ = dict

    def __deepcopy__(self, memo):
        retVal = self.__class__()
        memo[id(self)] = retVal

        for attr in dir(self):
            if not attr.startswith('_'):
                value = getattr(self, attr)
                if not isinstance(value, (types.BuiltinFunctionType, types.FunctionType, types.MethodType)):
                    setattr(retVal, attr, copy.deepcopy(value, memo))

        for key, value in self.items():
            retVal.__setitem__(key, copy.deepcopy(value, memo))

        return retVal
