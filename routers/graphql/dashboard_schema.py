from pprint import pprint
import strawberry
from strawberry.types import Info
from strawberry.types import Info
from sqlalchemy import func, select, text
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from models.deanery import Deanery
from models.parish import Parish
from models.user import User
from schemas.graphql.dashboard import DashboardStats, MemberStats, DeaneryStats, MonthlyMembership
from utils.auth_utils import get_current_user
from config.db import SessionLocal

@strawberry.type
class DashboardQuery:

    @strawberry.field
    def dashboard_stats(self, info: Info) -> DashboardStats:
        user = get_current_user(info)
        db = SessionLocal()
        
        if(user.role == 'parish_member'):
            raise Exception("Unauthorized: Only the Chaplain, Coordinators and moderators can access dashboard stats!")

        totals = db.execute(
            select(
                (select(func.count()).select_from(Deanery)).label("total_deaneries"),
                (select(func.count()).select_from(Parish)).label("total_parishes")
            )
        ).first()

        total_deaneries, total_parishes = totals

        # --- Member stats ---
        current_year = datetime.now().year
        transitioning_yob = current_year - 27

        member_stats = db.execute(
            select(
                func.count(func.nullif(User.status != "active_member", True)).label("active"),
                func.count(func.nullif(User.created_at < datetime.now() - timedelta(days=30), True)).label("new"),
                func.count(func.nullif(func.year(User.dateofbirth) != transitioning_yob, True)).label("transitioning"),
            )
        ).first()       

        active_members, new_members, transitioning_members = member_stats
        member_stats_obj = MemberStats(
            active_members=active_members,
            new_members=new_members,
            transitioning_members=transitioning_members
        )

        # --- Deanery rankings (aggregation + row_number for rank) ---
        deanery_query = db.execute(
            select(
                Deanery.name,
                func.count(User.id).label("total_members"),
                func.row_number().over(order_by=func.count(User.id).desc()).label("rank")
            )
            .join(Parish, Parish.deanery_id == Deanery.id)
            .join(User, User.parish_id == Parish.id)
            .group_by(Deanery.id)
            .order_by(func.count(User.id).desc())
        ).all()

        deanery_rankings = [
            DeaneryStats(name=row.name, total_members=row.total_members, rank=row.rank)
            for row in deanery_query
        ]

        # --- Membership trend (last 6 months, cumulative in SQL) ---
        six_months_ago = datetime.now().replace(day=1) - timedelta(days=180)

        trend_query = db.execute(
            select(
                func.date_format(User.created_at, "%Y-%m").label("month"),
                func.count(User.id).label("new_members"),
                func.sum(func.count(User.id)).over(
                    order_by=func.date_format(User.created_at, "%Y-%m")
                ).label("total_members"),
            )
            .filter(User.created_at >= six_months_ago)
            .group_by(func.date_format(User.created_at, "%Y-%m"))
            .order_by(func.date_format(User.created_at, "%Y-%m"))
        ).all()
        
        membership_trend = [
            MonthlyMembership(
                month=row.month,  # already "YYYY-MM"
                new_members=row.new_members,
                total_members=row.total_members,
            )
            for row in trend_query
        ]
        db.close()

        return DashboardStats(
            total_deaneries=total_deaneries,
            total_parishes=total_parishes,
            total_members=member_stats_obj,
            deanery_rankings=deanery_rankings,
            membership_trend=membership_trend
        )