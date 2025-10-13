from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Authorization"])

@router.get("/")
async def root():
    return {"message": "Hello World!"}
