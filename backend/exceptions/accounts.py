class AccountsBaseException(Exception):
    pass


class UserNotFoundException(AccountsBaseException):
    pass


class SubscriptionNotFoundException(AccountsBaseException):
    pass


class SubscriptionAlreadyExist(AccountsBaseException):
    pass


class InvalidTokenException(AccountsBaseException):
    pass


class InvalidCredentialsException(AccountsBaseException):
    pass


class UserAlreadyExist(AccountsBaseException):
    pass


class PlaylistNotFoundException(AccountsBaseException):
    pass


class PlaylistTrackNotFoundException(AccountsBaseException):
    pass


class PlaylistAlreadyExist(AccountsBaseException):
    pass
