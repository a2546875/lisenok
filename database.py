from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

from config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    auth_provider = Column(String)  # vk, google, mail, max
    is_admin = Column(Boolean, default=False)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, default="")
    retail_price = Column(Float)
    wholesale_price = Column(Float)
    image_url = Column(String)
    is_active = Column(Boolean, default=True)


class ConstructorOption(Base):
    __tablename__ = "constructor_options"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)  # 'set_type', 'color', 'pattern'
    name = Column(String)
    image_url = Column(String, default="")
    price = Column(Float, default=0)


class Inquiry(Base):
    __tablename__ = "inquiries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    contact = Column(String)
    message = Column(Text)
    design = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class SiteStats(Base):
    __tablename__ = "site_stats"

    id = Column(Integer, primary_key=True)
    page_views = Column(Integer, default=0)
    unique_visitors = Column(Integer, default=0)
    logins = Column(Integer, default=0)


class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True)
    visitor_id = Column(String, unique=True, index=True)
    first_seen = Column(DateTime, server_default=func.now())


class SiteText(Base):
    __tablename__ = "site_texts"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    page = Column(String, index=True)
    label = Column(String)
    value = Column(Text)


class QrItem(Base):
    __tablename__ = "qr_items"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)
    image_url = Column(String)
    sort_order = Column(Integer, default=0)


class GalleryImage(Base):
    __tablename__ = "gallery_images"

    id = Column(Integer, primary_key=True)
    kind = Column(String, index=True)  # workshop, product, background
    image_url = Column(String)


class SiteDocument(Base):
    __tablename__ = "site_documents"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    file_url = Column(String)
    kind = Column(String, default="image")  # image, pdf


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True)
    user_email = Column(String, index=True)
    subject = Column(String)
    status = Column(String, default="open")
    created_at = Column(DateTime, server_default=func.now())


class SupportMessage(Base):
    __tablename__ = "support_messages"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, index=True)
    author_email = Column(String)
    is_admin = Column(Boolean, default=False)
    text = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class CustomerOrder(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    items = Column(Text)
    total = Column(Float)
    delivery_method = Column(String)
    delivery_address = Column(Text)
    payment_type = Column(String)
    payment_details = Column(Text)
    status = Column(String, default="new")
    created_at = Column(DateTime, server_default=func.now())


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, index=True)
    user_email = Column(String)
    rating = Column(Integer)
    text = Column(Text)
    is_visible = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    client_type = Column(String)
    is_active = Column(Boolean, default=True)
    details = Column(Text)
    sort_order = Column(Integer, default=0)


class DeliveryCompany(Base):
    __tablename__ = "delivery_companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    display_name = Column(String)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)


Base.metadata.create_all(bind=engine)


def migrate_schema() -> None:
    with engine.begin() as conn:
        if engine.dialect.name == "sqlite":
            product_cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(products)")]
            if "description" not in product_cols:
                conn.exec_driver_sql("ALTER TABLE products ADD COLUMN description TEXT DEFAULT ''")
            option_cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(constructor_options)")]
            if "image_url" not in option_cols:
                conn.exec_driver_sql("ALTER TABLE constructor_options ADD COLUMN image_url TEXT DEFAULT ''")
            if "price" not in option_cols:
                conn.exec_driver_sql("ALTER TABLE constructor_options ADD COLUMN price FLOAT DEFAULT 0")
        else:
            conn.exec_driver_sql("ALTER TABLE products ADD COLUMN IF NOT EXISTS description TEXT DEFAULT ''")
            conn.exec_driver_sql("ALTER TABLE constructor_options ADD COLUMN IF NOT EXISTS image_url TEXT DEFAULT ''")
            conn.exec_driver_sql("ALTER TABLE constructor_options ADD COLUMN IF NOT EXISTS price FLOAT DEFAULT 0")


migrate_schema()


def seed_payment_defaults() -> None:
    db = SessionLocal()
    try:
        if db.query(DeliveryCompany).count() == 0:
            db.add(DeliveryCompany(name="ozon", display_name="Озон (маркетплейс)", is_active=True, sort_order=1))
            db.add(DeliveryCompany(name="5post", display_name="5Post (X5 Group)", is_active=True, sort_order=2))
        if db.query(PaymentMethod).count() == 0:
            db.add(PaymentMethod(name="Оплата картой", client_type="individual", is_active=True, details="{}", sort_order=1))
            db.add(PaymentMethod(name="QR-код", client_type="individual", is_active=True, details="{}", sort_order=2))
            db.add(PaymentMethod(name="Счёт для юрлиц", client_type="legal", is_active=True, details="{}", sort_order=3))
        db.commit()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
