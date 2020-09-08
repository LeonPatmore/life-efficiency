import enum


class ShoppingItems(enum.Enum):
    """
    Represents a shopping item.
    """

    def __new__(cls, *args, **kwargs):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, name):
        self.name = name

    CHOCOLATE_MILKSHAKE = 'chocolate milkshake'
