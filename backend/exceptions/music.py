class MusicBaseException(Exception):
    pass


class InvalidStartException(MusicBaseException):
    pass


class MusicFileNotFoundException(MusicBaseException):
    pass


class ImageFileNotFoundException(MusicBaseException):
    pass


class ArtistNotFoundException(MusicBaseException):
    pass


class TrackNotFoundException(MusicBaseException):
    pass


class AlbumNotFoundException(MusicBaseException):
    pass


class GenreNotFoundException(MusicBaseException):
    pass


class GenreNameAlreadyExistsException(MusicBaseException):
    pass
