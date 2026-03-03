from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    balance: Mapped[float] = mapped_column(Float, default=100.0)
