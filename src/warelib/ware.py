"""This file is a part of the source code for warelib.
This project has been licensed under the MIT license.

Copyright (c) 2025-present pygame-community

---

Ware class module for loading and managing ware modules.
"""

import importlib
from os import PathLike
from pathlib import Path
from types import ModuleType
from typing import Callable, Self

from warelib.callbacks import GeneratorWareCallback, WareCallback
from warelib.exceptions import InvalidWareStructure
from warelib.utils import import_module_from_path, unimport_module

type WareNamespaceSchema = dict[str, type | Callable[..., bool]]


class Ware[G, C]:
    """Base class for all ware objects, with foundational functionality
    for managing their module's lifecycle.

    A Ware is a sub-application with a catalog-like main application.

    Wares can be used to create WarioWare-like microgames, each with
    their own assets, logic, and configuration.
    """

    _module: ModuleType
    name: str

    globals: G
    callbacks: C

    @classmethod
    def load_from_path(
        cls,
        path: str | PathLike,
        globals_callbacks_schema: dict[str, type],
        name: str | None = None,
    ) -> Self:
        """Load a compatible module as a Ware from a file path.

        Args:
            path: The file path to load the module from.
            globals_callbacks_schema: A schema dict defining expected
                global variables and callbacks in the module.
            name: An optional name for the ware. If not provided,
                the module's name will be used.

        """
        if not isinstance(path, Path):
            path = Path(path)
        module = import_module_from_path(path.name, file_path=path)
        return cls._load(module, globals_callbacks_schema, name)

    @classmethod
    def load_from_module_name(
        cls,
        name: str,
        ns_schema: WareNamespaceSchema,
        package: str | None = None,
    ) -> Self:
        """Load a compatible module as a Ware from an importable module name.

        Args:
            name: The module name to import.
            ns_schema: A schema dict defining expected global
                variables and ware callbacks in the module.
        """
        module = importlib.import_module(name, package)
        return cls._load(module, ns_schema, name)

    @classmethod
    def _load(
        cls,
        module: ModuleType,
        ns_schema: WareNamespaceSchema,
        name: str | None = None,
    ):
        """Internal method to load a module as a Ware."""
        ware = cls.__new__(cls)
        ware.name = name or module.__name__
        ware._module = module
        ware.globals = {}  # type: ignore
        ware.callbacks = {}  # type: ignore
        for k, v in ns_schema.items():
            if k not in module.__dict__:
                raise InvalidWareStructure(
                    f"Ware module at {module.__name__} doesn't contain a variable named '{k}'"
                )
            mval = module.__dict__[k]
            if isinstance(v, type) and not isinstance(mval, v):
                raise InvalidWareStructure(
                    f"Ware module variable '{k}' is not of type '{v.__name__}'"
                )
            elif callable(v):
                try:
                    if not v(mval):
                        raise InvalidWareStructure(
                            f"Ware module variable '{k}' is not of type '{v.__name__}' according to '{v}' callable check"
                        )
                except TypeError as te:
                    raise InvalidWareStructure(
                        f"Ware module variable '{k}' is not of type '{v.__name__}' according to '{v}' callable check"
                    ) from te

            if isinstance(v, (WareCallback, GeneratorWareCallback)):
                ware.callbacks[k] = v  # type: ignore
            else:
                ware.globals[k] = v  # type: ignore

        return ware

    def __del__(self):
        unimport_module(self._module)
