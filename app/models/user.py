
import uuid
from . import Base
from sqlalchemy.orm import mapped_column, Mapped


class  User(Base):
    __tablename__ = 'users'

    userID: Mapped[str] = mapped_column(primary_key=True, nullable=False, index=True, default=lambda:  str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(nullable=False, index=True)
    password: Mapped[str] = mapped_column(nullable=True, index=True)
    email: Mapped[str] = mapped_column(nullable=False, index=True)
    