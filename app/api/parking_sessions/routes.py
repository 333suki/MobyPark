from fastapi import APIRouter

router = APIRouter(prefix="/parking_sessions", tags=["Parking sessions"])

@router.get("/")
async def root():
    return {"message": "Hello Parkingsessions!"}
