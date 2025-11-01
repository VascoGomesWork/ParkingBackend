from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#from routes import router
from routes.parks import router as parks_router

app = FastAPI(title="Hackaton_Park")
#app.include_router(router)
app.include_router(parks_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React app origin
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
)