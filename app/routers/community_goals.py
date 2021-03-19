from typing import Generator, List

from fastapi import APIRouter, Depends

from app.models.community_goals import CommunityGoal
from app.routers.helpers.responses import dataclass_response
from app.services.community_goals import CommunityGoalsService

router = APIRouter()


@router.get(
    "/community_goals",
    tags=["Community Goals"],
    response_model=List[CommunityGoal],
)
@dataclass_response
async def get_community_goals(
    community_goals_service: CommunityGoalsService = Depends(),
) -> Generator[CommunityGoal, None, None]:
    """Get latest community goals informations."""
    return community_goals_service.get_community_goals()
