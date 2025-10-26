from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from api.users.routes import router as users_router
from api.auth.routes import router as auth_router
from api.parking_lots.routes import router as parking_lots_router
from api.parking_sessions.routes import router as parking_sessions_router

# Explicitly enable Swagger UI and ReDoc endpoints
app = FastAPI(
    title="MobyPark API",
    version="0.1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Optional: redirect root to Swagger UI for convenience
@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/docs")

app.include_router(auth_router)
app.include_router(parking_lots_router)
app.include_router(parking_sessions_router)
app.include_router(users_router)

if __name__ == "__main__":
    # Allow starting the server by running: `python app/main.py` or `python -m app.main`
    import uvicorn
    # Using the string import path enables autoreload support when running as a module
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
