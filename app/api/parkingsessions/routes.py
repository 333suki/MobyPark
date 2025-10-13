from fastapi import APIRouter

router = APIRouter(prefix="/parkingsessions")

@router.get("/")
async def root():
    return {"message": "Hello Parkingsessions!"}

@router.get("/ping")
async def root():
    return {"status": "ok"}
