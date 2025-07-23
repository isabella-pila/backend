# petfit/main.py

from fastapi import FastAPI
# REMOVER ESTA LINHA: from fastapi.security import HTTPBearer # <--- ESTA LINHA CAUSA O PROBLEMA
from petfit.api.routes import recipe_route, user_route
from petfit.api.openapi_tags import openapi_tags
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Petfit API",
    description="API backend do Petfit com FastAPI e PostgreSQL",
    version="1.0.0",
    contact={"name": "Giovanna", "email": "giovanna@exemplo.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    openapi_tags=openapi_tags,
    redirect_slashes=True,
)

origins = [
    "https://pet-fit.vercel.app",
    "http://localhost:5174",
    "http://localhost:5173",  # Vite local
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # lista de origens confiáveis
    allow_credentials=True,
    allow_methods=["*"],  # ou especifique ["GET", "POST"]
    allow_headers=["*"],
)


@app.get("/")
def ola():
    return {"olá": "fastapi"}


app.include_router(user_route.router, prefix="/users", tags=["Users"])
app.include_router(recipe_route.router, prefix="/recipes", tags=["Recipes"])