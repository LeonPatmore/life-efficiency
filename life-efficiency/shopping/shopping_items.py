import enum


class ShoppingItems(enum.Enum):
    """
    Represents a shopping item.
    """

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _: str):
        pass

    def __str__(self):
        return self.value

    CHOCOLATE_MILKSHAKE = 'chocolate milkshake'
