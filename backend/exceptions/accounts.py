class AccountsBaseException(Exception):
    pass


class UserNotFoundException(AccountsBaseException):
    pass


class InvalidTokenException(AccountsBaseException):
    pass


class InvalidCredentialsException(AccountsBaseException):
    pass


class UserAlreadyExist(AccountsBaseException):
    pass


class PlaylistNotFoundException(AccountsBaseException):
    pass
