from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from routers.graphql.schema import schema
from scripts.seed_deaneries_parishes import seed_data
from scripts.seed_super_user import seed_super_user
from scripts.generate_deanery_prefixes import generate_deanery_prefixes
from scripts.generate_parish_prefixes import generate_parish_prefixes

from config.db import SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter, BackgroundTasks, Depends

import strawberry

app = FastAPI()
async def get_context(background_tasks: BackgroundTasks) -> dict:
    return {"background_tasks": background_tasks}

graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    multipart_uploads_enabled=True,
)


app.include_router(graphql_app, prefix="/graphql")

# Serve uploaded profile pictures
app.mount("/static/profile_pics", StaticFiles(directory="static/profile_pics"), name="profile_pics")

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.on_event("startup")
def on_startup():
    # ====== Startup tasks ======
    #===========================
    #
    # Uncomment the following lines to seed data and generate prefixes on startup
    #
    #============================
    
    # seed_data()
    # seed_super_user()
     
    # print("--- Prefix generation ---")
    # try:
    #     generate_deanery_prefixes()
    #     generate_parish_prefixes()
    #     print("--- Prefixes OK ---")
    # except Exception as e:
    #     print(f"[STARTUP ERROR] Prefix generation failed: {e}")
    #     raise  # prevent app from starting in a broken state
    
    # print("=== Startup complete ===")
    
    print("=== ADN API is running ===")

#get origins from .env
raw_origins = os.getenv("CORS_ORIGINS", "")
origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
