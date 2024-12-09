from functools import reduce, partial
from dataclasses import dataclass
from typing import Callable, Any, Iterable
from abc import ABC, abstractmethod
from enum import auto
from enum import Enum


class Magic:
    ...


@dataclass
class Result:
    result: Any = None
    error: Exception | None = None


class Unwrap(Magic):
    def __init__(self, single: bool = False) -> None:
        self.single = single

    def __call__(self, to_unwrap: "UFO") -> Any:
        values = list(to_unwrap.values)
        if self.single:
            assert len(values) == 1, "Must reduce first to gain single element"
            return values[0]
        return values


class UnwrapResults(Magic):
    def __init__(self, coerce_into: Any, mask: list[Exception] | None = None) -> None:
        self.coerce_into = coerce_into
        self.mask = mask if mask is not None else []

    def __call__(self, to_unwrap: "UFO") -> Any:
        values = list(to_unwrap.values)
        if self.single:
            assert len(values) == 1, "Must reduce first to gain single element"
            return values[0]
        return values


class Reduce(Magic):
    def __init__(self, func: Callable, initial: Any = None) -> None:
        self.func = func
        self.initial = initial

    def __call__(self, to_reduce: "UFO") -> "UFO":
        if self.initial is None:
            return UFO(reduce(self.func, to_reduce.values, self.initial))
        return UFO(reduce(self.func, to_reduce.values))


class Filter(Magic):
    def __init__(self, func: Callable) -> None:
        self.func = func

    def __call__(self, to_filter: "UFO") -> "UFO":
        to_filter.values = [i for i in to_filter.values if self.func(i)]
        return to_filter


def _compose(a: Callable, b: Callable):
    def new(*args, **kwargs):
        return a(b(*args, **kwargs))

    return new


def compose(*funcs: Callable):
    return reduce(_compose, funcs)


def identity(x: Any) -> Any:
    return x


def skip_if_none(func: Callable):
    def newfunc(value, *args, **kwargs):
        if value is None:
            return None
        return func(value, *args, **kwargs)

    return newfunc


def use_result_types(func: Callable):
    def newfunc(value, *args, **kwargs):
        value = value if isinstance(value, Result) else Result(value)
        if value.error is not None:
            return value
        try:
            value.result = func(value.result, *args, **kwargs)
        except Exception as e:
            value.error = e
        return value

    return newfunc


class UFO:
    def __init__(self, *items, composers: list[Callable] | None = None) -> None:
        self.values = [i for i in items]
        composers = composers or [identity]
        self.wrapper = compose(*composers)

    def __or__(self, func: Callable) -> "UFO":
        if isinstance(func, Magic):
            return func(self)
        self.values = [self.wrapper(func)(i) for i in self.values]
        return self
