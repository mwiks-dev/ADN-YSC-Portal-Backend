import strawberry
from strawberry.types import Info
from typing import List,Optional
from sqlalchemy.orm import Session
from utils.auth_utils import get_current_user
from config.db import SessionLocal
from models.deanery import Deanery
from models.parish import Parish
from schemas.graphql.parish_type import ParishInput,UpdateParishDetails
from schemas.graphql.shared_types import UserType, ParishType
from services.parish_service import get_parish_by_id,get_parishes,get_parish_by_name,get_all_users_of_parish,get_parishes_by_deanery,create_parish,delete_parish,update_parish
from utils.auth_utils import is_authenticated, is_chaplain, is_ysc_coordinator, is_deanery_moderator, is_parish_moderator, is_parish_member, can_register_users
@strawberry.type
class ParishQuery:
    @strawberry.field
    def parish(self, info: Info, id: Optional[int] = None, name: Optional[str] = None) -> Optional[ParishType]:
        db = SessionLocal()
        if id is not None:
            return get_parish_by_id(db, id)
        elif name is not None:
            return get_parish_by_name(db, name)
        return None  # neither provided
    
    @strawberry.field
    def parishes(self, info:Info) -> List[ParishType]:
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
    def update_parish(self, info:Info, input:UpdateParishDetails) -> Optional[ParishType]:
        db = SessionLocal()
        try:
            parish = get_parish_by_name(db, input.name)
            if not parish:
                raise Exception("Parish not found!")
        
            deanery = db.query(Deanery).filter_by(name=input.deanery).first()
            if not deanery:
                raise Exception("Deanery not found!")
            
            user = get_current_user(info)
            if not is_chaplain(user) or is_ysc_coordinator(user):
                raise Exception("Only the Chaplain or Coordinator can edit parish details")

            parish.name = input.name
            parish.deanery_id = deanery.id
            parish.deanery_name = deanery.name
            parish.deanery = deanery

            db.commit()
            db.refresh(parish)

            return parish
        finally:
            db.close()
    
    @strawberry.mutation
    def delete_parish(self,id:int) -> Optional[ParishType]:
        db = SessionLocal()
        return delete_parish(db,id)
    

schema = strawberry.Schema(query=ParishQuery, mutation=ParishMutation)
