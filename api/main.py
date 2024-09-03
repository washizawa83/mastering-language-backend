from fastapi import FastAPI

from api.routers import deck
from api.routers import auth

app = FastAPI()
app.include_router(deck.router)
app.include_router(auth.router)