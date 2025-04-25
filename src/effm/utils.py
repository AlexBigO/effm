"""
Simple module with some utils
"""


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
