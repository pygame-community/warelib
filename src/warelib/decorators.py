"""This file is a part of the source code for warelib.
This project has been licensed under the MIT license.

Copyright (c) 2025-present pygame-community

---

Decorators for marking ware callback functions.

Provides decorators that wrap functions into WareCallback instances,
enabling them to be recognized and managed by the ware lifecycle system.
"""

from typing import Callable

from warelib.callbacks import WareCallback


def reset(
    func: Callable[[], None],
) -> WareCallback[[], None]:
    """
    Decorator to mark a function as a "reset" ware callback, used to signal
    that the state of a ware should be reset.

    Args:
        func: The function to be decorated.
    Returns:
        An instance of WareCallback wrapping the provided function.
    """
    return WareCallback(func)
