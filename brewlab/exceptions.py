class InsufficientDataError(Exception):
    """
    InsufficientDataError is an Exception that indicates there is not
    enough data to make a meaningful calculation, and that the calculation
    should just be skipped
    """
    pass

class ConnectionError(Exception):
    """
    ConnectionError is an Exception that indicates there is a connection error
    and instead of exiting the program will alert the user there is no connection and
    continue
    """
    pass