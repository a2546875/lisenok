from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    retail_price: float
    wholesale_price: float
    image_url: str | None = None
    is_active: bool = True


class ConstructorOptionsOut(BaseModel):
    set_type: list[str] = Field(default_factory=list)
    color: list[str] = Field(default_factory=list)
    pattern: list[str] = Field(default_factory=list)


class InquiryIn(BaseModel):
    name: str
    contact: str
    message: str = ""
    design: str = ""


class InquiryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    contact: str
    message: str | None = None
    design: str | None = None
    created_at: datetime | None = None
