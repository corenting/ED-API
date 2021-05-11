from sqlalchemy import Boolean, Column, DateTime, Integer, Text

from app.database.database import Base


class CommunityGoalStatus(Base):
    __tablename__ = "community_goal_status"

    id = Column(Integer, primary_key=True)
    last_update = Column(DateTime, nullable=False)
    is_finished = Column(Boolean, nullable=False)
    current_tier = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
