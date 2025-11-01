from fastapi import FastAPI
#from routes import router
from routes.parks import router as parks_router

app = FastAPI(title="Hackaton_Park")
#app.include_router(router)
app.include_router(parks_router)