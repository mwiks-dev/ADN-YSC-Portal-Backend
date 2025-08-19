import strawberry
from strawberry.types import Info
from typing import List,Optional
from sqlalchemy.orm import joinedload
from utils.auth_utils import get_current_user
from config.db import SessionLocal
from models.deanery import Deanery
from models.parish import Parish
from models.outstation import Outstation
from schemas.graphql.parish_type import ParishInput,UpdateParishDetails, ParishSearchInput, ParishListResponse
from schemas.graphql.shared_types import UserType, ParishType
from services.parish_service import get_parish_by_id,get_parishes,get_parish_by_name,get_all_users_of_parish,get_parishes_by_deanery,create_parish,delete_parish,update_parish
from utils.auth_utils import is_chaplain, is_ysc_coordinator, is_superuser

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
    def parishes(self, info:Info, input: ParishSearchInput) -> ParishListResponse:
        db=SessionLocal()
        query = db.query(Parish)

        if input.search.strip():
            search = f"%{input.search.strip()}%"
            query = query.filter(Parish.name.ilike(search))

        total_count = query.count()
        offset = (input.page - 1) * input.limit
        parishes = query.offset(offset).limit(input.limit).all()
        return ParishListResponse(parishes=parishes, totalCount=total_count)
    
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
    def create_parish(self, info:Info, input:ParishInput, outstations: Optional[List[str]] = None) -> ParishType:
        db = SessionLocal()
        current_user = get_current_user(info)
        if not current_user:
            raise Exception("Unauthorized!")
        if not is_chaplain(current_user) or is_ysc_coordinator(current_user):
            raise Exception("Unauthorized: Only the Chaplain and Coordinators can create a parish!")
        deanery = db.query(Deanery).filter_by(name = input.deanery).first()
        if not deanery:
            raise Exception("Deanery not found")
        parish = Parish(name= input.name, deanery_id=deanery.id)
        db.add(parish)
        db.commit()
        db.refresh(parish)

        # Optional outstations
        if outstations:
            for outstation_name in outstations:
                outstation = Outstation(name=outstation_name, parish_id=parish.id)
                db.add(outstation)
            db.commit()

        parish = db.query(Parish).options(joinedload(Parish.deanery)).filter_by(id=parish.id).first()

        return parish
    
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
                raise Exception("Only the Chaplain or Coordinator can edit parish details!")

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
    def delete_parish(self,info:Info, id:int) -> Optional[ParishType]:
        db = SessionLocal()
        user = get_current_user(info)
        if not is_chaplain(user) or is_ysc_coordinator(user):
            raise Exception("Only the Chaplain or Coordinator can delete a parish!")
        db.refresh()
        return delete_parish(db,id)
    

schema = strawberry.Schema(query=ParishQuery, mutation=ParishMutation)
