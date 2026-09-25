from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    retail_price: float
    wholesale_price: float
    image_url: str | None = None
    description: str | None = ""
    is_active: bool = True


class OptionChoice(BaseModel):
    name: str
    image_url: str = ""
    price: float = 0


class ConstructorOptionsOut(BaseModel):
    set_type: list[OptionChoice] = Field(default_factory=list)
    color: list[OptionChoice] = Field(default_factory=list)
    pattern: list[OptionChoice] = Field(default_factory=list)


class InquiryIn(BaseModel):
    name: str
    contact: str
    message: str = ""
    design: str = ""


class LoginCheckIn(BaseModel):
    email: str


class LoginIn(BaseModel):
    email: str
    password: str = ""


class LoginOut(BaseModel):
    email: str
    is_admin: bool
    token: str


class ProductIn(BaseModel):
    name: str
    retail_price: float = 0
    wholesale_price: float = 0
    image_url: str = ""
    description: str = ""
    is_active: bool = True


class OptionIn(BaseModel):
    category: str
    name: str


class OptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    name: str
    image_url: str | None = ""
    price: float = 0


class VisitIn(BaseModel):
    visitor_id: str


class StatsOut(BaseModel):
    page_views: int
    unique_visitors: int
    logins: int


class TextOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    page: str
    label: str
    value: str


class TextUpdate(BaseModel):
    key: str
    value: str


class QrOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    url: str
    image_url: str | None = None
    sort_order: int = 0


class QrIn(BaseModel):
    title: str
    url: str


class GalleryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: str
    image_url: str


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    file_url: str
    kind: str = "image"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_admin: bool = False


class TicketIn(BaseModel):
    subject: str
    message: str


class MessageIn(BaseModel):
    text: str


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    author_email: str
    is_admin: bool
    text: str
    created_at: datetime | None = None


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_email: str
    subject: str
    status: str
    created_at: datetime | None = None
    messages: list[MessageOut] = Field(default_factory=list)


class InquiryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    contact: str
    message: str | None = None
    design: str | None = None
    created_at: datetime | None = None


# -- Orders --
class OrderItemIn(BaseModel):
    product_id: int
    name: str
    qty: int
    price: float


class OrderIn(BaseModel):
    items: list[OrderItemIn]
    total: float
    delivery_method: str
    delivery_address: str
    payment_type: str
    payment_details: str = ""


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_email: str
    items: str
    total: float
    delivery_method: str
    delivery_address: str
    payment_type: str
    payment_details: str
    status: str
    created_at: datetime | None = None


# -- Reviews --
class ReviewIn(BaseModel):
    product_id: int
    rating: int = Field(ge=1, le=5)
    text: str


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    user_email: str
    rating: int
    text: str
    created_at: datetime | None = None


# -- Payment Methods --
class PaymentMethodOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    client_type: str
    is_active: bool
    details: str | None = None
    sort_order: int = 0


class PaymentMethodIn(BaseModel):
    name: str
    client_type: str
    details: str = ""
    is_active: bool = True
    sort_order: int = 0


# -- Delivery Companies --
class DeliveryCompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    display_name: str
    is_active: bool
    sort_order: int = 0


class DeliveryCompanyIn(BaseModel):
    name: str
    display_name: str
    is_active: bool = True
    sort_order: int = 0
