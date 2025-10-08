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

schema = strawberry.Schema(query=ZoneQuery)
