from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import auth
from api.routers import user
from api.routers import deck
from api.routers import card

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(deck.router)
app.include_router(card.router)
