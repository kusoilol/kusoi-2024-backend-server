from enum import Enum, auto


class Language(Enum):
    """
    Represents the language of the submission.
    The number of supported languages may increase.
    """
    PYTHON = ".py"
    # PYPY = ".pypy.py"
    CPP20GPP = ".gpp.cpp"
    # JAVA21 = ".java"
