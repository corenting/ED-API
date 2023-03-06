from datetime import datetime
from sqlalchemy import Integer
from sqlalchemy.orm import mapped_column, Mapped

from app.database.database import Base


class CommunityGoalStatus(Base):
    __tablename__ = "community_goal_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    last_update: Mapped[datetime]
    is_finished: Mapped[bool]
    current_tier: Mapped[int]
    title: Mapped[str]
