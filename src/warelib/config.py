from typing import TypedDict

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


exceptions: ExceptionsConfig = {
    "WareMustEnd": WareMustEnd,
    "WareCallbackMustEnd": WareCallbackMustEnd,
    "WareCallbackEnded": WareCallbackEnded,
    "AsyncWareCallbackEnded": AsyncWareCallbackEnded,
    "WareCallbackBegun": WareCallbackBegun,
    "WareCallbackNotBegun": WareCallbackNotBegun,
    "InvalidWareStructure": InvalidWareStructure,
}
