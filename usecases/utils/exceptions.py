class DomainExceptionError(Exception):
    pass

class CardCreationError(DomainExceptionError):
    pass

class NonExistentCard(DomainExceptionError):
    pass

class DuplicatedColumnError(DomainExceptionError):
    pass

class DuplicatedCellError(DomainExceptionError):
    pass