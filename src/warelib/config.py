from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from warelib.exceptions import (
        AsyncWareCallbackEnded,
        InvalidWareStructure,
        WareCallbackBegun,
        WareCallbackEnded,
        WareCallbackMustEnd,
        WareCallbackNotBegun,
        WareMustEnd,
    )

    class ExceptionsConfig(TypedDict):
        WareMustEnd: type[WareMustEnd]
        WareCallbackMustEnd: type[WareCallbackMustEnd]
        WareCallbackEnded: type[WareCallbackEnded]
        AsyncWareCallbackEnded: type[AsyncWareCallbackEnded]
        WareCallbackBegun: type[WareCallbackBegun]
        WareCallbackNotBegun: type[WareCallbackNotBegun]
        InvalidWareStructure: type[InvalidWareStructure]


exceptions: ExceptionsConfig = {}  # type: ignore
