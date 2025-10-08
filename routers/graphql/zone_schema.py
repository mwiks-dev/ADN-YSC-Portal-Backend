import strawberry
from strawberry.types import Info
from typing import List, Optional
from sqlalchemy.orm import joinedload
from utils.auth_utils import get_current_user
from config.db import SessionLocal
from models.deanery import Deanery
from models.zone import Zone
from models.parish import Parish
from schemas.graphql.zone_type import ZoneInput, UpdateZoneDetails, ZoneSearchInput,ZoneListResponse
from schemas.graphql.shared_types import ZoneType
from services.zone_service import get_zone_by_id, get_zone_by_name, get_deaneries_by_zone,create_zone, update_zone, delete_zone
from utils.auth_utils import is_chaplain, is_ysc_coordinator, is_superuser

@strawberry.type
class ZoneQuery:
    @strawberry.field
    def zone(self,info:Info,id:Optional[int]=None,name:Optional[str]=None) -> Optional[ZoneType]:
        db = SessionLocal()
        if id is not None:
            return get_zone_by_id(db,id)
        elif name is not None:
            return get_zone_by_id(db,name)
        return None
    
    @strawberry.field
    def zones(self, info:Info, input:ZoneSearchInput) -> ZoneListResponse:
        db = SessionLocal()
        query = db.query(Zone)
        
        if input.search.strip():
            search = f"%{input.search.strip()}%"
            query = query.filter(Deanery.name.ilike(search))

        total_count = query.count()
        offset = (input.page - 1) * input.limit
        deaneries = query.offset(offset).limit(input.limit).all()
        return ZoneListResponse(deaneries=deaneries, totalCount=total_count)
    
    @strawberry.field
    def zoneDeaneries(self, zone:str) -> List[ZoneType]:
        db = SessionLocal()
        return get_deaneries_by_zone(db, zone)

@strawberry.type    
class DeaneryMutation:
    @strawberry.mutation
    def create_deanery(self, info:Info, input:ZoneInput, parishes: Optional[List[str]] = None) -> ZoneType:
        db = SessionLocal()
        existing_deanery = get_zone_by_name(db, input.name)
        current_user = get_current_user(info)
        if existing_deanery:
            raise Exception("Deanery with this name already exists!")
        if not current_user:
            raise Exception("Unauthorized!")
        if not(is_chaplain(current_user) or is_ysc_coordinator(current_user) or is_superuser(current_user)):
            raise Exception("Unauthorized: Only the Chaplain and Coordinators can create a parish!")
        zone = db.query(Zone).filter_by(id = input.zone_id).first()
        if not zone:
            raise Exception("Zone not found")
        deanery = create_zone(db, input.name, input.zone_id)

        # Optional parishes
        if parishes:
            for parish_name in parishes:
                parish = Parish(name=parish_name, deanery_id=deanery.id)
                db.add(parish)
            db.commit()

        parish = db.query(Parish).options(joinedload(Parish.deanery)).filter_by(id=parish.id).first()

        return parish
    
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
