from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from routers.graphql.user_schema import schema
from config.db import Base, engine

app = FastAPI()

graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")
Base.metadata.create_all(bind=engine)
