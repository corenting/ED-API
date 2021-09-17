from typing import Generator

from fastapi import APIRouter, Depends

from app.models.community_goals import CommunityGoal
from app.services.community_goals import CommunityGoalsService

router = APIRouter()


@router.get(
    "/community_goals",
    tags=["Community Goals"],
    response_model=list[CommunityGoal],
)
async def get_community_goals(
    community_goals_service: CommunityGoalsService = Depends(),
) -> Generator[CommunityGoal, None, None]:
    """Get latest community goals informations."""
    return community_goals_service.get_community_goals()
