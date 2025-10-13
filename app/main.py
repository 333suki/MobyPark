from fastapi import FastAPI
from app.api.users import routes

app = FastAPI(title="MobyPark API", version="0.1")

app.include_router(routes.router)
