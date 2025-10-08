import strawberry
from strawberry.types import Info
from typing import List, Optional
from sqlalchemy.orm import joinedload
from utils.auth_utils import get_current_user
from config.db import SessionLocal
from models.deanery import Deanery
from models.zone import Zone
from models.parish import Parish
from schemas.graphql.deanery_type import DeaneryInput, UpdateDeaneryDetails, DeanerySearchInput, DeaneryListResponse, CreateDeaneryResponse
from schemas.graphql.shared_types import DeaneryType
from services.deanery_service import get_deanery_by_id, get_deanery_by_name,get_deaneries_by_zone,create_deanery, update_deanery, delete_deanery
from utils.auth_utils import is_chaplain, is_ysc_coordinator, is_superuser


@strawberry.type
class DeaneryQuery:
    @strawberry.field
    def deanery(self,info:Info,id:Optional[int]=None,name:Optional[str]=None) -> Optional[DeaneryType]:
        db = SessionLocal()
        if id is not None:
            return get_deanery_by_id(db,id)
        elif name is not None:
            return get_deanery_by_name(db,name)
        return None
    
    @strawberry.field
    def deaneries(self, info:Info, input:DeanerySearchInput) -> DeaneryListResponse:
        db = SessionLocal()
        query = (
            db.query(Deanery)
            .join(Deanery.zone)  
            .options(joinedload(Deanery.zone)) 
        )

        # Apply search filter if provided
        if input.search and input.search.strip():
            search = f"%{input.search.strip()}%"
            query = query.filter(Deanery.name.ilike(search))

        # Order by zone name, then deanery name
        query = query.order_by(Zone.name.asc(), Deanery.name.asc())

        # Count and paginate
        total_count = query.count()
        offset = (input.page - 1) * input.limit
        deaneries = query.offset(offset).limit(input.limit).all()
        
        return DeaneryListResponse(deaneries=deaneries, totalCount=total_count)
    
    @strawberry.field
    def zoneDeaneries(self, zone:str) -> List[DeaneryType]:
        db = SessionLocal()
        return get_deaneries_by_zone(db, zone)

@strawberry.type    
class DeaneryMutation:
    @strawberry.mutation
    def create_deanery(self, info:Info, input:DeaneryInput) -> DeaneryType:
        db = SessionLocal()
        existing_deanery = get_deanery_by_name(db, input.name)
        current_user = get_current_user(info)

        if existing_deanery:
            raise Exception("Deanery with this name already exists!")
        if not current_user:
            raise Exception("Unauthorized!")
        if not (is_chaplain(current_user) or is_ysc_coordinator(current_user) or is_superuser(current_user)):
            raise Exception("Unauthorized: Only the Chaplain and Coordinators can create a parish!")

        zone = db.query(Zone).filter_by(id=input.zone_id).first()
        if not zone:
            raise Exception("Zone not found")

        deanery = create_deanery(db, input.name, input.zone_id)

        # Optionally create parishes
        if input.parishes:
            for parish_name in input.parishes:
                new_parish = Parish(name=parish_name, deanery_id=deanery.id)
                db.add(new_parish)

        db.commit()
        db.refresh(deanery)  
        return deanery
    
    @strawberry.mutation
    def update_deanery(self, info:Info, input:UpdateDeaneryDetails) -> Optional[DeaneryType]:
        db = SessionLocal()
        parish = get_deanery_by_name(db, input.name)
        if not parish:
            raise Exception("Deanery not found!")
    
        zone = db.query(Zone).filter_by(id=input.zone_id).first()
        if not zone:
            raise Exception("Zone not found!")
        
        user = get_current_user(info)
        if not( is_chaplain(user) or is_ysc_coordinator(user) or is_superuser(user)):
            raise Exception("Only the Chaplain or Coordinator can edit deanery details!")

        return update_deanery(db, input.id, input.name, input.zone_id)
    
    @strawberry.mutation
    def delete_deanery(self,info:Info, id:int) -> Optional[DeaneryType]:
        user = get_current_user(info)
        if not (is_chaplain(user) or is_ysc_coordinator(user) or is_superuser(user)):
            raise Exception("Only the Chaplain or Coordinator can delete a deanery!")
        db = SessionLocal()
        return delete_deanery(db,id)

schema = strawberry.Schema(query=DeaneryQuery, mutation=DeaneryMutation)
