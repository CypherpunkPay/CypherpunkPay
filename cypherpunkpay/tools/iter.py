from typing import Callable, Iterable


def first(
    pred: Callable[[object], bool],
    iterable: Iterable,
    default=None
):
    """Returns the first item for which pred(item) is True.

    Otherwise, returns None or *default*.
    """
    try:
        return next(x for x in iterable if pred(x))
    except StopIteration:
        return default
