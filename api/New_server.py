import hashlib
from fastapi import FastAPI
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from storage_utils import *
from session_manager import add_session, remove_session, get_session
import session_calculator as sc

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}
