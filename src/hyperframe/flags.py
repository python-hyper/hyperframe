"""
Basic Flag and Flags data structures.
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator, MutableSet
from typing import NamedTuple, TypeVar

_T = TypeVar("_T")


class Flag(NamedTuple):
    name: str
    bit: int


class Flags(MutableSet):  # type: ignore
    """
    A simple MutableSet implementation that will only accept known flags as
    elements.

    Will behave like a regular set(), except that a ValueError will be thrown
    when .add()ing unexpected flags. Non-mutating set operations return
    regular sets.
    """

    def __init__(self, defined_flags: Iterable[Flag]) -> None:
        self._valid_flags = {flag.name for flag in defined_flags}
        self._flags: set[str] = set()

    @classmethod
    def _from_iterable(cls, it: Iterable[_T]) -> set[_T]:
        # The set mixins pass flag names, not the definitions our constructor
        # needs. Results are ordinary sets; in-place operations still validate.
        return set(it)

    def __repr__(self) -> str:
        return repr(sorted(self._flags))

    def __contains__(self, x: object) -> bool:
        return self._flags.__contains__(x)

    def __iter__(self) -> Iterator[str]:
        return self._flags.__iter__()

    def __len__(self) -> int:
        return self._flags.__len__()

    def discard(self, value: str) -> None:
        return self._flags.discard(value)

    def add(self, value: str) -> None:
        if value not in self._valid_flags:
            msg = f"Unexpected flag: {value}. Valid flags are: {self._valid_flags}"
            raise ValueError(msg)
        return self._flags.add(value)
