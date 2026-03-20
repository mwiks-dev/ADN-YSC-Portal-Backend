from .user_schema import UserQuery as UserQuery, UserMutation as UserMutation
from .parish_schema import ParishQuery as ParishQuery, ParishMutation as ParishMutation
from .deanery_schema import DeaneryQuery as DeaneryQuery, DeaneryMutation as DeaneryMutation
from .zone_schema import ZoneQuery as ZoneQuery
from .dashboard_schema import DashboardQuery as DashboardQuery
from .event_schema import EventQuery as EventQuery, EventMutation as EventMutation
from .event_parish_registration_schema import EventParishRegistrationQuery as EventParishRegistrationQuery, EventParishRegistrationMutation as EventParishRegistrationMutation
import strawberry

@strawberry.type
class Query(UserQuery, ParishQuery, DeaneryQuery, DashboardQuery, ZoneQuery, EventQuery, EventParishRegistrationQuery):
    pass

@strawberry.type
class Mutation(UserMutation, ParishMutation, DeaneryMutation, EventMutation,EventParishRegistrationMutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
