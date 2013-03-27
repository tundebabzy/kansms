class InvalidTransaction(Exception):
    """ Standardized exception when suspicious arithmetic is detected """
    pass 

class NumberTooBig(Exception):
    """
    Raised when a number that is higher messaging.models.MAXIMUM_VALUE
    is detected.
    """
    pass 
