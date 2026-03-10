import uuid
from datetime import datetime, timezone
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, SmallInteger
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database.base import Base


class Slot(Base):
    __tablename__ = "slots"

    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        primary_key=True,
    )

    slot_index: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True,
    )

    # nullable = empty slot
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # optional ORM relationships (nice for querying)
    team = relationship("Team", back_populates="slots")
    user = relationship("User")
