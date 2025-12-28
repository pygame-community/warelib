"""This file is a part of the source code for warelib.
This project has been licensed under the MIT license.

Copyright (c) 2025-present pygame-community

---

Exception classes for warelib.

Provides exception types for ware and ware callback lifecycle management,
including generator control flow and error handling.
"""


class WareMustEnd(GeneratorExit):
    """Exception raised when an entire ware is requested to end"""


class WareCallbackMustEnd(GeneratorExit):
    """Exception raised when a ware callback is requested to end"""


class WareCallbackEnded(StopIteration):
    """Exception raised when a ware callback has ended"""


class AsyncWareCallbackEnded(StopAsyncIteration):
    """Exception raised when an async ware callback has ended"""


class WareCallbackBegun(RuntimeError):
    """Exception raised when a ware callbacks has already begun a generator"""


class WareCallbackNotBegun(RuntimeError):
    """Exception raised when a ware callback has not begun a generator"""


class InvalidWareStructure(ValueError):
    """Exception raised when a ware module structure is invalid"""
