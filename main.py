from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from routers.graphql.schema import schema
from scripts.seed_deaneries_parishes import seed_data
from scripts.seed_super_user import seed_super_user

app = FastAPI()

graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")

@app.on_event("startup")
def on_startup():
    seed_data()
    seed_super_user()
