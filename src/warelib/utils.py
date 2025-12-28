"""This file is a part of the source code for warelib.
This project has been licensed under the MIT license.

Copyright (c) 2025-present pygame-community

---

Utility functions for warelib.
"""

import importlib
import importlib.util
import os
import sys
from types import ModuleType


def import_module_from_path(
    module_name: str, file_path: str | os.PathLike
) -> ModuleType:
    """Import a module from a file path.

    Args:
        module_name: The name of the module to import
        file_path: The path to the file to import

    Returns:
        The imported module

    Raises:
        ImportError: The module cannot be imported.
        ModuleNotFoundError: The module cannot be found.
    """
    abs_file_path = os.path.abspath(file_path)
    spec = importlib.util.spec_from_file_location(module_name, abs_file_path)  # type: ignore
    if spec is None:
        raise ImportError(
            f"failed to generate module spec for module named '{module_name}' at '{abs_file_path}'"
        )
    module = importlib.util.module_from_spec(spec)  # type: ignore
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)  # type: ignore
    except FileNotFoundError as fnf:
        del sys.modules[module_name]
        raise ModuleNotFoundError(
            f"failed to find code for module named '{module_name}' at '{abs_file_path}'"
        ) from fnf
    except Exception:
        del sys.modules[module_name]
        raise

    return module


def unimport_module(module: ModuleType) -> None:
    """Unimport a module, by deleting it from ``sys.modules`` if it exists there.
    Note that this will not remove any existing outer references
    to the module.

    Args:
        module: The module object.
    """
    if module.__name__ in sys.modules:
        del sys.modules[module.__name__]
