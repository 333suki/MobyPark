from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Authorization"])

# http://127.0.0.1:8000/auth/
@router.get("/")
async def root():
    return {"message": "Hello World!"}

