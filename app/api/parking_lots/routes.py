from fastapi import APIRouter

router = APIRouter(prefix="/parking_lots", tags=["Parking lots"])

@router.get("/")
async def root():
    return {"message": "Hello Parkinglots!"}
