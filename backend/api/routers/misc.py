from fastapi import APIRouter


router = APIRouter(prefix="/misc", tags=["misc"])


@router.get("/ping", response_model=str)
async def ping() -> str:
    return "pong"
