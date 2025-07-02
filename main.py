from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from routers.graphql.user_schema import schema
from routers.graphql.parish_schema import schema
from scripts.seed_deaneries_parishes import seed_data

app = FastAPI()

graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")

@app.on_event("startup")
def on_startup():
    seed_data()


