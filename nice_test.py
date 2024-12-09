from ufo_tools.ufo import UFO, Unwrap, Reduce, Filter, skip_if_none, use_result_types

x: int = (
    UFO(1, 2, 3, composers=[use_result_types, skip_if_none])
    | (lambda x: x * 2)
    | (lambda x: x if x != 2 else None)
    | (lambda x: x + 1)
    | Filter(lambda x: x is not None)
    | Reduce(lambda x, y: x + y, initial=3)
    | Unwrap(single=True)
)

print(f"x is: {x}")
