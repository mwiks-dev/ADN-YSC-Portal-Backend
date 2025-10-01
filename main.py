import os
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from routers.graphql.schema import schema
from scripts.seed_deaneries_parishes import seed_data
from scripts.seed_super_user import seed_super_user
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import strawberry

load_dotenv()

app = FastAPI()

graphql_app = GraphQLRouter(schema, multipart_uploads_enabled=True)


app.include_router(graphql_app, prefix="/graphql")

# Serve uploaded profile pictures
app.mount("/static/profile_pics", StaticFiles(directory="static/profile_pics"), name="profile_pics")

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# @app.on_event("startup")
# def on_startup():
#     seed_data()
#     seed_super_user()

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
