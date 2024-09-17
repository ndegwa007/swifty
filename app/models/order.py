from . import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import DateTime, ForeignKey
import uuid
import datetime


class Order(Base):
    __tablename__ =  'orders'

    order_id: Mapped[str] = mapped_column(primary_key=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    item_name: Mapped[str] = mapped_column(nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(nullable=False, index=True)
    order_time: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    user_id = Mapped[str] = mapped_column(ForeignKey('users.userID'), nullable=False)

    # relationship 
    user = relationship('User', back_populates='orders')