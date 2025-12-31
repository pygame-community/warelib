"""This file is a part of the source code for warelib.
This project has been licensed under the MIT license.

Copyright (c) 2025-present pygame-community

---

Useful type definitions for warelib.
"""

from warelib.callbacks import (
    AsyncGeneratorWareCallback,
    AsyncWareCallback,
    GeneratorWareCallback,
    WareCallback,
)

type WareCallbackT[**P, Y, S, R] = (
    WareCallback[P, R]
    | GeneratorWareCallback[P, Y, S, R]
    | AsyncWareCallback[P, R]
    | AsyncGeneratorWareCallback[P, Y, S]
)
