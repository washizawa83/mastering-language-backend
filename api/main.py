from fastapi import FastAPI

from api.routers import deck

app = FastAPI()
app.include_router(deck.router)