import strawberry
from typing import List

@strawberry.type
class MemberStats:
    active_members: int
    new_members: int
    transitioning_members: int

@strawberry.type
class DeaneryStats:
    name: str
    total_members: int
    rank: int  # computed

@strawberry.type
class MonthlyMembership:
    month: str  # e.g. "2025-05" or "May 2025"
    total_members: int
    new_members: int

@strawberry.type
class DashboardStats:
    total_deaneries: int
    total_parishes: int
    total_members: MemberStats
    deanery_rankings: List[DeaneryStats]
    membership_trend: List[MonthlyMembership]  # 👈 last 6 months
