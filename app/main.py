from fastapi import FastAPI
from api.users.routes import router as users_router
from api.auth.routes import router as auth_router
from api.parking_lots.routes import router as parking_lots_router
from api.parking_sessions.routes import router as parking_sessions_router

app = FastAPI(title="MobyPark API", version="0.1")

app.include_router(auth_router)
app.include_router(parking_lots_router)
app.include_router(parking_sessions_router)
app.include_router(users_router)
