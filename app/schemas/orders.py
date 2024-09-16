from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class OrderBase(BaseModel):
    item_name: str
    quantity: int
    order_time: datetime = Field(default_factory=datetime.now)

class OrderCreate(OrderBase):
    pass

class OrderUpdate(OrderBase):
    pass 

class Order(OrderBase):
    order_id: uuid.UUID = Field(default_factory=uuid.uuid4)


