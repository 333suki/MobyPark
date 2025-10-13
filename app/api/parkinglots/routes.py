from fastapi import APIRouter

router = APIRouter(prefix="/parkinglots")

@router.get("/")
async def root():
    return {"message": "Hello Parkinglots!"}

@router.get("/ping")
async def root():
    return {"status": "ok"}
