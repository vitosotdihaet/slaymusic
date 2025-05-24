from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
)
from dto.music import GenreID, Genre, NewGenre, GenreSearchParams, UpdateGenre
from services.music import MusicService
from configs.depends import get_music_service
from exceptions.music import GenreNameAlreadyExistsException, GenreNotFoundException

router = APIRouter(prefix="/genre", tags=["genre"])


@router.post(
    "/",
    response_model=Genre,
    status_code=status.HTTP_201_CREATED,
)
async def create_genre(
    new_genre: NewGenre = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.create_genre(new_genre)
    except GenreNameAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=Genre)
async def get_genre(
    genre_id: GenreID = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.get_genre(genre_id)
    except GenreNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("s/", response_model=list[Genre])
async def get_genres(
    params: GenreSearchParams = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.get_genres(params)
    except GenreNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/", response_model=Genre)
async def update_metadata(
    genre: UpdateGenre = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        return await music_service.update_genre(genre)
    except GenreNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except GenreNameAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(
    genre_id: GenreID = Depends(),
    music_service: MusicService = Depends(get_music_service),
):
    try:
        await music_service.delete_genre(genre_id)
    except GenreNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
