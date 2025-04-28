"""
Simple module with some utils
"""

import sys


def enforce_trailing_slash(path):
    """
    Helper method to enforce '/' at the and of directory name

    Parameters
    ------------------------------------------------
    - path: str
        Some path

    Returns
    ------------------------------------------------
    - path: str
        Path with a trailing slash at the end if it was not there yet
    """

    if path is not None and path[-1] != "/":
        path += "/"

    return path


def get_name_columns(df):
    """
    Helper method to get the column names of a dataframe

    Parameters
    ------------------------------------------------
    - df: pandas.DataFrame
        Some data frame

    Returns
    ------------------------------------------------
    - list[str]
        Names of the columns of a given dataframe
    """
    return list(df.columns)


# pylint: disable=too-few-public-methods
class Logger:
    """
    Class to print in colour
    """

    DEBUG = "\033[96m"
    INFO = "\033[92m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"
    FATAL = "\33[101m"
    ENDC = "\033[0m"

    def __init__(self, text, level):
        """
        Initialize the class
        Parameters
        ------------------------------------------------
        text: str
            Text to be printed
        level: str
            Level of logger, possible values [DEBUG, INFO, WARNING, ERROR, FATAL, RESULT]
        """
        self._text_ = text
        self._level_ = level

        if level == "DEBUG":
            print(f"{Logger.DEBUG}DEBUG{Logger.ENDC}: {text}")
        elif level == "INFO":
            print(f"{Logger.INFO}INFO{Logger.ENDC}: {text}")
        elif level == "WARNING":
            print(f"{Logger.WARNING}WARNING{Logger.ENDC}: {text}")
        elif level == "ERROR":
            print(f"{Logger.ERROR}ERROR{Logger.ENDC}: {text}")
        elif level == "FATAL":
            print(f"{Logger.FATAL}FATAL{Logger.ENDC}: {text}")
            sys.exit(0)
        elif level == "RESULT":
            print(f"\n\n{text}\n\n")
        else:
            print(text)
