from enum import Enum

class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((i.value, i.name) for i in cls)
