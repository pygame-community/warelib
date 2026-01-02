"""This file is a part of the source code for warelib.
This project has been licensed under the MIT license.

Copyright (c) 2025-present pygame-community

---

Warelib - A library for creating WarioWare-like microgame collections.

Warelib provides infrastructure for loading, managing, and orchestrating
multiple independent microgames (wares) in a collaborative game development
framework. Each ware represents a self-contained Python module with callbacks for
setup, rendering, and gameplay logic.

Key components:
- ``Ware`` class for wrapping and validating ware modules
- ``WareManager`` for parallel ware orchestration
- Synchronous and asynchronous callback wrappers
- Exceptions for lifecycle control flow
"""

__title__ = "warelib"
__author__ = "pygame-community"
__license__ = "MIT"
__copyright__ = "Copyright 2025-present pygame-community"
__version__ = "0.1.0"


import warelib.config as config

from .callbacks import *  # noqa: F403
from .config import ExceptionsConfig
from .exceptions import *  # noqa: F403
from .manager import *  # noqa: F403
from .types import *  # noqa: F403
from .ware import *  # noqa: F403


def init(exceptions_config: ExceptionsConfig | None = None):
    """Initializes warelib with optional configuration.
    Not mandatory to call.

    Args:
        exceptions_config: Optional custom exceptions configuration, which allows
            the mapping of default warelib exception class names to custom exception
            classes. This can be used to create 'branded' exception classes for
            projects wrapping warelib.
    """
    if exceptions_config is not None:
        config.exceptions.update(exceptions_config)
