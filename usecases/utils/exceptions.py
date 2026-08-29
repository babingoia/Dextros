class CardCreationError(Exception):
    pass

class DomainExceptionError(Exception):
    pass


class NonExistentCard(DomainExceptionError):
    pass