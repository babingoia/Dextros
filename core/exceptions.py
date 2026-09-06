class CoreException(Exception):
    pass

class ParseError(CoreException):
    pass

class InvalidCardId(CoreException):
    pass