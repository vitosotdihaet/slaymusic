class UseCaseException(Exception):
    pass


class InvalidStartException(UseCaseException):
    pass


class MusicFileNotFoundException(UseCaseException):
    pass
