from fastapi import APIRouter

router = APIRouter(prefix="/users")

@router.get("/")
async def root():
    return {"message": "Hello World!"}

@router.get("/ping")
async def root():
    return {"status": "ok"}
