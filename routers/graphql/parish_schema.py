import strawberry
from typing import List,Optional

from config.db import SessionLocal
from schemas.graphql.parish_type import ParishType,ParishInput,UpdateParishDetails
from schemas.graphql.user_type import UserType
from services.parish_service import get_parish_by_id,get_parishes,get_parish_by_name,get_all_users_of_parish,get_parishes_by_deanery,create_parish,delete_parish,update_parish

@strawberry.type
class ParishQuery:
    @strawberry.field
    def parish(self,attribute:str) -> Optional[ParishType]:
        db=SessionLocal()
        if isinstance(attribute,int):
            return get_parish_by_id(db,attribute)
        elif isinstance(attribute,str):
            return get_parish_by_name(db,attribute)
    
    @strawberry.field
    def parishes(self) -> List[ParishType]:
        db=SessionLocal()
        return get_parishes(db)
    
    @strawberry.field
    def parishioners(self,id:int)-> List[UserType]:
        db= SessionLocal()
        return get_all_users_of_parish(db,id)
    
    @strawberry.field
    def deaneryParishes(self,deanery:str) -> List[ParishType]:
        db=SessionLocal()
        return get_parishes_by_deanery(db,deanery)
    
@strawberry.type    
class ParishMutation:
    @strawberry.mutation
    def create_parish(self,input:ParishInput) -> ParishType:
        db = SessionLocal()
        return create_parish(db,input.name,input.deanery)
    
    @strawberry.mutation
    def update_parish(self,input:UpdateParishDetails) -> ParishType:
        db = SessionLocal()
        return update_parish(db,input.id,input.name,input.deanery)
    
    @strawberry.mutation
    def delete_parish(self,id:int) -> Optional[ParishType]:
        db = SessionLocal()
        return delete_parish(db,id)
    
    