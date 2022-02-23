from fastapi import APIRouter, Depends

from app.models.community_goals import CommunityGoal
from app.services.community_goals import CommunityGoalsService

router = APIRouter(prefix="/community_goals", tags=["Community Goals"])


@router.get("", response_model=list[CommunityGoal])
async def get_community_goals(
    community_goals_service: CommunityGoalsService = Depends(),
) -> list[CommunityGoal]:
    """Get latest community goals informations."""
    ret = community_goals_service.get_community_goals()
    return ret
