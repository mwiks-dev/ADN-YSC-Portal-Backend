from .user_schema import UserQuery as UserQuery, UserMutation as UserMutation
from .parish_schema import ParishQuery as ParishQuery, ParishMutation as ParishMutation
from .deanery_schema import DeaneryQuery as DeaneryQuery, DeaneryMutation as DeaneryMutation
import strawberry

@strawberry.type
class Query(UserQuery, ParishQuery,DeaneryQuery):
    pass

@strawberry.type
class Mutation(UserMutation, ParishMutation, DeaneryMutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
