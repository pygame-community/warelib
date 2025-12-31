"""This file is a part of the source code for warelib.
This project has been licensed under the MIT license.

Copyright (c) 2025-present pygame-community

---

Ware manager module for parallel ware orchestration.
"""

from collections.abc import Sequence
from typing import Any, Callable, Mapping

import warelib.config as config
from warelib.callbacks import (
    AsyncGeneratorWareCallback,
    AsyncWareCallback,
    GeneratorWareCallback,
    WareCallback,
)
from warelib.exceptions import WareCallbackMustEnd
from warelib.ware import Ware


class WareManager[W: Ware]:
    """Manager for orchestrating multiple wares in parallel.

    Acts as a multiplexer that advances callbacks across multiple wares
    simultaneously, enabling parallel execution of microgames.
    Returns separate success and error dictionaries for granular control.
    """

    def __init__(self, wares: Sequence[W], resetter: Callable[[W], bool]) -> None:
        """
        Initialize this WareManager.

        Args:
            resetter: WareResetter[W]Args:
            wares: Sequence of Ware instances to manage
            resetter: Callable to save/reset ware state externally right before
                internal reset operations are performed by a ware's module
        """
        self.wares: dict[str, W] = {ware.name: ware for ware in wares}
        self.resetter = resetter

    def _select_wares(self, w_names: Sequence[str] | None = None) -> dict[str, W]:
        """Helper to select wares by name or return all wares."""
        if w_names is None:
            return self.wares
        return {name: self.wares[name] for name in w_names if name in self.wares}

    def _execute_on_wares(
        self,
        w_names: Sequence[str] | None,
        executor: Any,  # Callable[[str, W], T] but kept generic for sync/async
    ) -> tuple[dict[str, Any], dict[str, Exception]]:
        """Execute a function on selected wares, collecting successes and errors."""
        successes = {}
        errors = {}
        for name, ware in self._select_wares(w_names).items():
            try:
                successes[name] = executor(name, ware)
            except Exception as e:
                errors[name] = e
        return successes, errors

    async def _aexecute_on_wares(
        self,
        w_names: Sequence[str] | None,
        executor: Any,  # Callable[[str, W], Awaitable[T]] but kept generic
    ) -> tuple[dict[str, Any], dict[str, Exception]]:
        """Async execute a function on selected wares, collecting successes and errors."""
        successes = {}
        errors = {}
        for name, ware in self._select_wares(w_names).items():
            try:
                successes[name] = await executor(name, ware)
            except Exception as e:
                errors[name] = e
        return successes, errors

    def begin(
        self,
        wc_name: str,
        wc_args: tuple[Any, ...] = (),
        wc_kwargs: Mapping[str, Any] = {},
        w_names: Sequence[str] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Exception]]:
        """Begin a generator ware callback for specified wares.

        Args:
            wc_name: Name of the generator callback to begin
            wc_args: Args to pass to all wares
            wc_kwargs: Kwargs to pass to all wares
            w_names: Optional list of ware names to begin, or None for all wares

        Returns:
            Tuple of (successes dict, errors dict) mapping ware names to results or exceptions
        """

        def executor(ware: W) -> Any:
            callback = ware.callbacks[wc_name]
            if not isinstance(callback, GeneratorWareCallback) or isinstance(
                callback, AsyncGeneratorWareCallback
            ):
                raise TypeError(
                    f"Ware '{ware.name}' callback '{wc_name}' is not a GeneratorWareCallback"
                )
            return callback.begin(*wc_args, **wc_kwargs)

        return self._execute_on_wares(w_names, executor)

    async def abegin(
        self,
        wc_name: str,
        wc_args: tuple[Any, ...] = (),
        wc_kwargs: Mapping[str, Any] = {},
        w_names: Sequence[str] | None = None,
    ) -> tuple[dict[str, None], dict[str, Exception]]:
        """Begin an async generator ware callback for specified wares.

        Args:
            wc_name: Name of the async generator callback to begin
            wc_args: Args to pass to all wares
            wc_kwargs: Kwargs to pass to all wares
            w_names: Optional list of ware names to begin, or None for all wares

        Returns:
            Tuple of (successes dict, errors dict) mapping ware names to None or exceptions
        """

        async def executor(ware: W) -> None:
            callback = ware.callbacks[wc_name]
            if not isinstance(callback, AsyncGeneratorWareCallback):
                raise TypeError(
                    f"Ware '{ware.name}' callback '{wc_name}' is not an AsyncGeneratorWareCallback"
                )
            return callback.begin(*wc_args, **wc_kwargs)

        return await self._aexecute_on_wares(w_names, executor)

    def run_once(
        self,
        wc_name: str,
        wc_args: tuple[Any, ...] | None = None,
        wc_kwargs: Mapping[str, Any] | None = None,
        w_names: Sequence[str] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Exception]]:
        """Run a non-generator ware callback once for specified wares.

        Args:
            wc_name: Name of the callback to run
            wc_args: Args to pass to all wares
            wc_kwargs: Kwargs to pass to all wares
            w_names: Optional list of ware names to run, or None for all wares

        Returns:
            Tuple of (successes dict, errors dict) mapping ware names to results or exceptions
        """
        if wc_args is None:
            wc_args = ()
        if wc_kwargs is None:
            wc_kwargs = {}

        def executor(ware: W) -> Any:
            callback = ware.callbacks[wc_name]
            if not isinstance(callback, WareCallback) or isinstance(
                callback,
                GeneratorWareCallback | AsyncWareCallback | AsyncGeneratorWareCallback,
            ):
                raise TypeError(
                    f"Ware '{ware.name}' callback '{wc_name}' is not a simple WareCallback"
                )
            return callback.run_once(*wc_args, **wc_kwargs)

        return self._execute_on_wares(w_names, executor)

    def gen_run_once(
        self,
        wc_name: str,
        wc_sendval: Any,
        w_names: Sequence[str] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Exception]]:
        """
        Run a generator ware callback once for specified wares.

        Automatically begins inactive callbacks. Returns yielded values or exceptions per ware.

        Args:
            wc_name: Name of the generator callback to run
            wc_sendval: Value to send to all wares
            w_names: Optional list of ware names to run, or None for all wares

        Returns:
            Tuple of (successes dict, errors dict) mapping ware names to yielded values or exceptions
        """

        def executor(ware: W) -> Any:
            callback = ware.callbacks[wc_name]
            if not isinstance(callback, GeneratorWareCallback) or isinstance(
                callback, AsyncGeneratorWareCallback
            ):
                raise TypeError(
                    f"Ware '{ware.name}' callback '{wc_name}' is not a GeneratorWareCallback"
                )

            if not callback.is_active():
                return callback.begin(wc_sendval)
            else:
                return callback.run_once(wc_sendval)

        return self._execute_on_wares(w_names, executor)

    async def agen_run_once(
        self,
        wc_name: str,
        wc_sendval: Any,
        w_names: Sequence[str] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Exception]]:
        """
        Run an async generator ware callback once for specified wares.

        Automatically begins inactive callbacks. Returns yielded values or exceptions per ware.

        Args:
            wc_name: Name of the async generator callback to run
            wc_sendval: Value to send to all wares
            w_names: Optional list of ware names to run, or None for all wares

        Returns:
            Tuple of (successes dict, errors dict) mapping ware names to yielded values or exceptions
        """

        async def executor(name: str, ware: W) -> Any:
            callback = ware.callbacks[wc_name]
            if not isinstance(callback, AsyncGeneratorWareCallback):
                raise TypeError(
                    f"Ware '{name}' callback '{wc_name}' is not an AsyncGeneratorWareCallback"
                )

            if not callback.is_active():
                callback.begin(wc_sendval)  # begin returns None for async generators
                return None
            else:
                return await callback.run_once(wc_sendval)

        return await self._aexecute_on_wares(w_names, executor)

    def reset(
        self, w_names: Sequence[str] | None = None
    ) -> tuple[dict[str, None], dict[str, Exception]]:
        """Reset specified wares by saving state, closing generators, and calling reset callback.

        Args:
            w_names: Optional list of ware names to reset, or None for all wares

        Returns:
            Tuple of (successes dict, errors dict) mapping ware names to None or exceptions
        """

        def executor(ware: W) -> None:
            # 1. Save state via game program's resetter
            self.resetter(ware)
            # 2. Close active generators that have ended with WareCallbackMustEnd
            for callback_name, callback in ware.callbacks.items():
                if callback_name != "reset" and isinstance(
                    callback, GeneratorWareCallback
                ):
                    if not callback.has_ended() and callback.is_active():
                        callback.reset(
                            config.exceptions.get(
                                "WareCallbackMustEnd", WareCallbackMustEnd
                            )
                        )

            # 3. Call reset callback if it exists
            if "reset" in ware.callbacks:
                reset_callback = ware.callbacks["reset"]
                if isinstance(reset_callback, WareCallback):
                    try:
                        reset_callback.run_once()
                    except Exception:
                        pass  # Ignore exceptions from reset callback
                else:
                    raise TypeError(
                        f"Ware '{ware.name}' reset callback must be a simple WareCallback"
                    )
            return None

        return self._execute_on_wares(w_names, executor)

    async def areset(
        self, w_names: Sequence[str] | None = None
    ) -> tuple[dict[str, None], dict[str, Exception]]:
        """Reset specified wares asynchronously by saving state, closing generators, and calling reset callback.

        Args:
            w_names: Optional list of ware names to reset, or None for all wares

        Returns:
            Tuple of (successes dict, errors dict) mapping ware names to None or exceptions
        """

        async def executor(name: str, ware: W) -> None:
            # 1. Save state via game program's resetter
            self.resetter(ware)

            # 2. Close active generators with WareCallbackMustEnd
            for callback_name, callback in ware.callbacks.items():
                if callback_name != "reset":
                    if isinstance(callback, AsyncGeneratorWareCallback):
                        if not callback.has_ended() and callback.is_active():
                            await callback.reset()
                    elif isinstance(callback, GeneratorWareCallback):
                        if not callback.has_ended() and callback.is_active():
                            callback.reset(
                                config.exceptions.get(
                                    "WareCallbackMustEnd", WareCallbackMustEnd
                                )
                            )

            # 3. Call reset callback if it exists
            if "reset" in ware.callbacks:
                reset_callback = ware.callbacks["reset"]
                if isinstance(reset_callback, WareCallback):
                    try:
                        reset_callback.run_once()
                    except Exception:
                        pass  # Ignore exceptions from reset callback
                else:
                    raise TypeError(
                        f"Ware '{name}' reset callback must be a simple WareCallback"
                    )
            return None

        return await self._aexecute_on_wares(w_names, executor)
