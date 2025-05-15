class UserActivityException(Exception):
    pass


class UserActivityNotFoundException(UserActivityException):
    pass


class EventNotFoundException(UserActivityException):
    pass
