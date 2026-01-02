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

# Track which sys.path entries were added for each module
_module_path_registry: dict[str, str] = {}


def import_module_from_path(
    module_name: str, file_path: str | os.PathLike, register_dir: bool = True
) -> ModuleType:
    """Import a module from a file path, optionally registering its directory in sys.path
    (useful for ``__init__.py`` files which contain relative imports).

    Args:
        module_name: The name of the module to import
        file_path: The path to the file to import
        register_dir: If True, register the module's directory in sys.path

    Returns:
        The imported module

    Raises:
        ImportError: The module cannot be imported.
        ModuleNotFoundError: The module cannot be found.
    """
    abs_file_path = os.path.abspath(file_path)
    module_dir = os.path.dirname(abs_file_path)

    if register_dir and module_dir not in sys.path:
        sys.path.insert(0, module_dir)
        _module_path_registry[module_name] = module_dir

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
    If the module's directory was added to ``sys.path`` during import, it will
    also be removed. Note that this will not remove any existing outer references
    to the module.

    Args:
        module: The module object.
    """
    module_name = module.__name__
    if module_name in sys.modules:
        del sys.modules[module_name]

    # Remove the path from sys.path if it was added for this module
    if module_name in _module_path_registry:
        module_dir = _module_path_registry.pop(module_name)
        if module_dir in sys.path:
            sys.path.remove(module_dir)
