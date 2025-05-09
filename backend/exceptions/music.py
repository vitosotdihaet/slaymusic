class UseCaseException(Exception):
    pass


class InvalidStartException(UseCaseException):
    pass


class MusicFileNotFoundException(UseCaseException):
    pass


class ArtistNotFoundException(UseCaseException):
    pass


class TrackNotFoundException(UseCaseException):
    pass


class AlbumNotFoundException(UseCaseException):
    pass
