from .user_schema import UserQuery as UserQuery, UserMutation as UserMutation
from .parish_schema import ParishQuery as ParishQuery, ParishMutation as ParishMutation
import strawberry

@strawberry.type
class Query(UserQuery, ParishQuery):
    pass

@strawberry.type
class Mutation(UserMutation, ParishMutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
