"""This file is a part of the source code for warelib.
This project has been licensed under the MIT license.

Copyright (c) 2025-present pygame-community

---

Callback classes for ware lifecycle management.

Provides callback wrapper classes for different execution models:
- WareCallback: Simple synchronous functions
- GeneratorWareCallback: Synchronous generators for cooperative execution
- AsyncWareCallback: Asynchronous functions
- AsyncGeneratorWareCallback: Asynchronous generators

These enable wares to be run cooperatively, similar to asyncio tasks.
"""

from collections.abc import AsyncGenerator, Coroutine, Generator
from typing import Any, Callable, Optional

import warelib.config as config
from warelib.exceptions import (
    AsyncWareCallbackEnded,
    WareCallbackBegun,
    WareCallbackEnded,
    WareCallbackMustEnd,
    WareCallbackNotBegun,
)


class WareCallback[**P, R]:
    """Base class for all ware callbacks"""

    def __init__(
        self, callback: Callable[P, R], metadata: dict[str, Any] | None = None
    ):
        self._callback = callback
        self.metadata = metadata or {}

    def run_once(self, *args: P.args, **kwds: P.kwargs) -> R:
        """Run the ware callback once, passing the provided arguments to it."""
        return self._callback(*args, **kwds)

    __call__ = run_once


class GeneratorWareCallback[**P, Y, S, R](WareCallback[P, Generator[Y, S, R]]):
    """Base class for callbacks that are generator functions"""

    # _callback: Callable[P, Generator[Y, S, R]]

    def __init__(
        self,
        callback: Callable[P, Generator[Y, S, R]],
        metadata: dict[str, Any] | None = None,
    ):
        super().__init__(callback, metadata)
        self._gen: Generator[Y, S, R] | None = None
        self._ended: bool = False

    def is_active(self) -> bool:
        """Check if the callback has an active generator (has begun and has not ended)."""
        return self._gen is not None and not self._ended

    def has_ended(self) -> bool:
        """Check if the generator has ended."""
        return self._ended

    def begin(self, *args: P.args, **kwargs: P.kwargs) -> Y:
        """Creates a new ware callback generator instance and runs it once, passing the provided arguments to it."""

        if self._gen:
            raise config.exceptions.get("WareCallbackBegun", WareCallbackBegun)(
                "Generator callback has already begun a generator"
            )

        self._gen = self._callback(*args, **kwargs)
        return self.run_once(None)  # type: ignore # convenience

    def run_once(self, arg: S) -> Y:
        """Runs the ware's callback current generator once, with values to send to it.

        Args:
            arg: The value to send to the generator.

        Returns:
            The value yielded by the generator.

        Raises:
            WareCallbackNotBegun: The generator ware callback was not started.
            WareCallbackEnded: The generator ware callback ended.
        """
        if self._gen is None:
            raise config.exceptions.get("WareCallbackNotBegun", WareCallbackNotBegun)(
                "Generator ware callback has not begun a generator"
            )

        try:
            return self._gen.send(arg)
        except StopIteration as s:
            self._ended = True
            exc = config.exceptions.get("WareCallbackEnded", WareCallbackEnded)()
            exc.value = s.value
            raise exc from None

    def reset(
        self, exc_class: type[WareCallbackMustEnd] = WareCallbackMustEnd
    ) -> Y | None:
        """Resets the ware callback by throwing a ``WareCallbackMustEnd``
        derived exception into its current generator, before deleting it.

        Args:
            exc_class: The exception to throw to close the generator.

        Returns:
            The value returned by the generator when it was closed, if any.
        """
        if self._gen is not None:
            try:
                return self._gen.throw(
                    config.exceptions.get(exc_class.__name__, exc_class)
                )
            except StopIteration as s:
                return s.value
            finally:
                self._gen = None

    __call__ = run_once


class AsyncWareCallback[**P, R](WareCallback[P, Coroutine[Any, Any, R]]):
    """Base class for callbacks that are async functions"""

    def __init__(
        self,
        callback: Callable[P, Coroutine[Any, Any, R]],
        metadata: dict[str, Any] | None = None,
    ):
        super().__init__(callback, metadata)

    async def run_once(self, *args: P.args, **kwds: P.kwargs) -> R:
        return await super().run_once(*args, **kwds)

    __call__ = run_once


class AsyncGeneratorWareCallback[**P, Y, S](GeneratorWareCallback[P, Y, S, None]):
    """Base class for callbacks that are async generator functions"""

    def __init__(
        self,
        callback: Callable[P, AsyncGenerator[Y, S]],
        metadata: dict[str, Any] | None = None,
    ):
        super().__init__(callback, metadata)  # type: ignore
        self._callback: Callable[P, AsyncGenerator[Y, S]]
        self._gen: Optional[AsyncGenerator[Y, S]]

    def begin(self, *args: P.args, **kwargs: P.kwargs) -> None:
        if self._gen is not None:
            raise config.exceptions.get("WareCallbackBegun", WareCallbackBegun)(
                "Async generator callback has already begun a generator"
            )

        self._gen = self._callback(*args, **kwargs)
        return self.run_once(None)  # type: ignore # convenience

    async def run_once(self, arg: S) -> Y:
        """
        Runs the ware's callback current async generator once, with values to send to it.

        Args:
            arg: The value to send to the generator.

        Returns:
            The value yielded by the generator.

        Raises:
            WareCallbackNotBegun: The generator ware callback was not started.
            AsyncWareCallbackEnded: The generator ware callback ended.
        """
        if self._gen is None:
            raise config.exceptions.get("WareCallbackNotBegun", WareCallbackNotBegun)(
                "Async generator ware callback has not begun a generator"
            )

        try:
            return await self._gen.asend(arg)
        except StopAsyncIteration:
            raise config.exceptions.get(
                "AsyncWareCallbackEnded", AsyncWareCallbackEnded
            )() from None

    async def reset(self) -> None:
        """Resets the ware callback by closing its async generator, before deleting it."""

        if self._gen is not None:
            try:
                await self._gen.aclose()
            except (StopAsyncIteration, RuntimeError):
                pass  # Ignore any errors during cleanup
            self._gen = None

    __call__ = run_once
