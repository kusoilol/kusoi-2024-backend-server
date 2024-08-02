from enum import Enum, auto


class Language(Enum):
    """
    Represents the language of the submission.
    The number of supported languages may increase.
    """
    PYTHON = auto()
    # PYPY = auto()
    CPP20_GPP = auto()
    # JAVA21 = auto()