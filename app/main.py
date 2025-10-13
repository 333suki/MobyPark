from fastapi import FastAPI
from api.users import routes # change this again??

app = FastAPI(title="MobyPark API", version="0.1")

app.include_router(routes.router)
