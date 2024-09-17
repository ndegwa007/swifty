
import uuid
from . import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship


class  User(Base):
    __tablename__ = 'users'

    userID: Mapped[str] = mapped_column(primary_key=True, nullable=False, index=True, default=lambda:  str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(nullable=False, index=True)
    email: Mapped[str] = mapped_column(nullable=False, index=True)

    # one to many a user can have many orders
    orders =  relationship('Order', back_populates="user")
    