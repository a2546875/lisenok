from pathlib import Path
import json
from urllib.parse import quote

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from auth import check_admin_password, current_user, get_admin, is_admin_email, make_token
from config import settings
from database import (
    ConstructorOption,
    CustomerOrder,
    DeliveryCompany,
    GalleryImage,
    Inquiry,
    PaymentMethod,
    Product,
    QrItem,
    Review,
    SiteDocument,
    SiteStats,
    SiteText,
    SupportMessage,
    SupportTicket,
    User,
    Visitor,
    get_db,
    seed_payment_defaults,
    update_wholesale_site_texts,
)
from schemas import (
    ConstructorOptionsOut,
    DeliveryCompanyIn,
    DeliveryCompanyOut,
    DocumentOut,
    GalleryOut,
    InquiryIn,
    InquiryOut,
    LoginCheckIn,
    LoginIn,
    LoginOut,
    MessageIn,
    MessageOut,
    OptionIn,
    OptionOut,
    OrderIn,
    OrderOut,
    PaymentMethodIn,
    PaymentMethodOut,
    ProductIn,
    ProductOut,
    QrIn,
    QrOut,
    ReviewIn,
    ReviewOut,
    StatsOut,
    TextOut,
    TextUpdate,
    TicketIn,
    TicketOut,
    UserOut,
    VisitIn,
)
from seed import seed_if_empty
from uploads import save_upload

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Lisenok API", version="1.0.0", docs_url="/api/swagger", redoc_url="/api/redoc")

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()] or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def ensure_stats(db: Session) -> SiteStats:
    stats = db.query(SiteStats).filter(SiteStats.id == 1).first()
    if not stats:
        stats = SiteStats(id=1, page_views=0, unique_visitors=0, logins=0)
        db.add(stats)
        db.commit()
        db.refresh(stats)
    return stats


@app.on_event("startup")
def on_startup() -> None:
    seed_if_empty()
    update_wholesale_site_texts()
    seed_payment_defaults()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "project": "lisenok"}


@app.post("/api/auth/check")
def auth_check(payload: LoginCheckIn) -> dict:
    return {"needs_password": is_admin_email(payload.email)}


@app.post("/api/login", response_model=LoginOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Укажите почту")

    admin = is_admin_email(email)
    if admin:
        if not payload.password:
            raise HTTPException(status_code=401, detail="Введите пароль администратора")
        if not check_admin_password(payload.password):
            raise HTTPException(status_code=401, detail="Неверный пароль администратора")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, auth_provider="mail", is_admin=admin)
        db.add(user)
    else:
        user.is_admin = admin

    stats = ensure_stats(db)
    stats.logins = (stats.logins or 0) + 1
    db.commit()
    return LoginOut(email=email, is_admin=admin, token=make_token(email, admin))


@app.post("/api/visit")
def track_visit(payload: VisitIn, db: Session = Depends(get_db)) -> StatsOut:
    stats = ensure_stats(db)
    stats.page_views = (stats.page_views or 0) + 1
    visitor_id = payload.visitor_id.strip()[:80]
    if visitor_id and not db.query(Visitor).filter(Visitor.visitor_id == visitor_id).first():
        db.add(Visitor(visitor_id=visitor_id))
        stats.unique_visitors = (stats.unique_visitors or 0) + 1
    db.commit()
    return StatsOut(
        page_views=stats.page_views,
        unique_visitors=stats.unique_visitors,
        logins=stats.logins or 0,
    )


@app.get("/api/admin/stats", response_model=StatsOut)
def admin_stats(_admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    stats = ensure_stats(db)
    return StatsOut(
        page_views=stats.page_views or 0,
        unique_visitors=stats.unique_visitors or 0,
        logins=stats.logins or 0,
    )


@app.get("/api/catalog", response_model=list[ProductOut])
def get_catalog(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.is_active.is_(True)).all()


@app.get("/api/admin/products", response_model=list[ProductOut])
def admin_products(_admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.id.desc()).all()


@app.post("/api/admin/products", response_model=ProductOut)
def add_product(payload: ProductIn, _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    product = Product(
        name=payload.name.strip(),
        description=payload.description.strip(),
        retail_price=payload.retail_price,
        wholesale_price=payload.wholesale_price,
        image_url=payload.image_url.strip(),
        is_active=payload.is_active,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.post("/api/admin/products/{product_id}/toggle", response_model=ProductOut)
def toggle_product(product_id: int, _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    product.is_active = not product.is_active
    db.commit()
    db.refresh(product)
    return product


@app.delete("/api/admin/products/{product_id}")
def delete_product(product_id: int, _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    db.delete(product)
    db.commit()
    return {"ok": True}


@app.get("/api/constructor-options", response_model=ConstructorOptionsOut)
def get_options(db: Session = Depends(get_db)):
    options = db.query(ConstructorOption).all()
    result: dict[str, list] = {"set_type": [], "color": [], "pattern": []}
    for opt in options:
        if opt.category in result:
            result[opt.category].append({
                "name": opt.name,
                "image_url": opt.image_url or "",
                "price": opt.price or 0,
            })
    return result


@app.get("/api/admin/options", response_model=list[OptionOut])
def admin_options(_admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    return db.query(ConstructorOption).order_by(ConstructorOption.category, ConstructorOption.id).all()


@app.post("/api/admin/options", response_model=OptionOut)
def add_option(
    category: str = Form(...),
    name: str = Form(...),
    file: UploadFile | None = File(None),
    _admin: dict = Depends(get_admin),
    db: Session = Depends(get_db),
):
    if category not in {"set_type", "color", "pattern"}:
        raise HTTPException(status_code=400, detail="Неверная категория")
    image_url = save_upload(file, "option") if file and file.filename else ""
    option = ConstructorOption(category=category, name=name.strip(), image_url=image_url)
    db.add(option)
    db.commit()
    db.refresh(option)
    return option


@app.post("/api/admin/options/{option_id}/photo")
def option_photo(
    option_id: int,
    file: UploadFile = File(...),
    _admin: dict = Depends(get_admin),
    db: Session = Depends(get_db),
):
    option = db.query(ConstructorOption).filter(ConstructorOption.id == option_id).first()
    if not option:
        raise HTTPException(status_code=404, detail="Опция не найдена")
    option.image_url = save_upload(file, "option")
    db.commit()
    return {"url": option.image_url}


@app.delete("/api/admin/options/{option_id}")
def delete_option(option_id: int, _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    option = db.query(ConstructorOption).filter(ConstructorOption.id == option_id).first()
    if not option:
        raise HTTPException(status_code=404, detail="Опция не найдена")
    db.delete(option)
    db.commit()
    return {"ok": True}


@app.post("/api/inquiry", response_model=InquiryOut)
def create_inquiry(payload: InquiryIn, db: Session = Depends(get_db)):
    inquiry = Inquiry(
        name=payload.name.strip(),
        contact=payload.contact.strip(),
        message=payload.message.strip(),
        design=payload.design.strip(),
    )
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    return inquiry


@app.get("/api/admin/inquiries", response_model=list[InquiryOut])
def admin_inquiries(_admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    return db.query(Inquiry).order_by(Inquiry.id.desc()).all()


@app.delete("/api/admin/inquiries/{inquiry_id}")
def delete_inquiry(inquiry_id: int, _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    db.delete(inquiry)
    db.commit()
    return {"ok": True}


def qr_image(item: QrItem) -> str:
    if item.image_url:
        return item.image_url
    return (
        "https://api.qrserver.com/v1/create-qr-code/?size=160x160&data="
        f"{quote(item.url or '', safe='')}&color=ffffff&bgcolor=141c16"
    )


@app.get("/api/site")
def public_site(db: Session = Depends(get_db)):
    texts = {row.key: row.value for row in db.query(SiteText).all()}
    qrs = [
        {
            "id": item.id,
            "title": item.title,
            "url": item.url,
            "image_url": qr_image(item),
        }
        for item in db.query(QrItem).order_by(QrItem.sort_order, QrItem.id).all()
    ]
    gallery = {"workshop": [], "product": []}
    background = "/assets/forest-bg.png"
    for image in db.query(GalleryImage).order_by(GalleryImage.id).all():
        if image.kind == "background":
            background = image.image_url
        elif image.kind in gallery:
            gallery[image.kind].append({"id": image.id, "image_url": image.image_url})
    return {"texts": texts, "qrs": qrs, "gallery": gallery, "background_url": background}


@app.get("/api/admin/texts", response_model=list[TextOut])
def admin_texts(_admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    return db.query(SiteText).order_by(SiteText.page, SiteText.id).all()


@app.post("/api/admin/texts")
def save_texts(items: list[TextUpdate], _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    by_key = {row.key: row for row in db.query(SiteText).all()}
    for item in items:
        if item.key in by_key:
            by_key[item.key].value = item.value
    db.commit()
    return {"ok": True}


@app.get("/api/admin/qrs", response_model=list[QrOut])
def admin_qrs(_admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    items = db.query(QrItem).order_by(QrItem.sort_order, QrItem.id).all()
    return [QrOut(id=i.id, title=i.title, url=i.url, image_url=qr_image(i), sort_order=i.sort_order or 0) for i in items]


@app.post("/api/admin/qrs")
def add_qr(
    title: str = Form(...),
    url: str = Form(...),
    file: UploadFile | None = File(None),
    _admin: dict = Depends(get_admin),
    db: Session = Depends(get_db),
):
    image_url = save_upload(file, "qr") if file and file.filename else ""
    item = QrItem(title=title.strip(), url=url.strip(), image_url=image_url, sort_order=99)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id}


@app.delete("/api/admin/qrs/{qr_id}")
def delete_qr(qr_id: int, _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    item = db.query(QrItem).filter(QrItem.id == qr_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="QR не найден")
    db.delete(item)
    db.commit()
    return {"ok": True}


@app.get("/api/admin/gallery", response_model=list[GalleryOut])
def admin_gallery(_admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    return db.query(GalleryImage).order_by(GalleryImage.kind, GalleryImage.id).all()


@app.post("/api/admin/gallery")
def add_gallery(
    kind: str = Form(...),
    file: UploadFile = File(...),
    _admin: dict = Depends(get_admin),
    db: Session = Depends(get_db),
):
    if kind not in {"workshop", "product", "background"}:
        raise HTTPException(status_code=400, detail="Неверный тип фото")
    image_url = save_upload(file, kind)
    if kind == "background":
        for old in db.query(GalleryImage).filter(GalleryImage.kind == "background").all():
            db.delete(old)
    db.add(GalleryImage(kind=kind, image_url=image_url))
    db.commit()
    return {"url": image_url}


@app.delete("/api/admin/gallery/{image_id}")
def delete_gallery(image_id: int, _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    item = db.query(GalleryImage).filter(GalleryImage.id == image_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Фото не найдено")
    db.delete(item)
    db.commit()
    return {"ok": True}


@app.get("/api/documents", response_model=list[DocumentOut])
def public_documents(db: Session = Depends(get_db)):
    return db.query(SiteDocument).order_by(SiteDocument.id.desc()).all()


@app.get("/api/admin/documents", response_model=list[DocumentOut])
def admin_documents(_admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    return db.query(SiteDocument).order_by(SiteDocument.id.desc()).all()


@app.post("/api/admin/documents", response_model=DocumentOut)
def add_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    _admin: dict = Depends(get_admin),
    db: Session = Depends(get_db),
):
    file_url = save_upload(file, "doc", documents=True)
    suffix = (file.filename or "").lower()
    kind = "pdf" if suffix.endswith(".pdf") else "image"
    item = SiteDocument(title=title.strip() or "Документ", file_url=file_url, kind=kind)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/api/admin/documents/{doc_id}")
def delete_document(doc_id: int, _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    item = db.query(SiteDocument).filter(SiteDocument.id == doc_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Документ не найден")
    db.delete(item)
    db.commit()
    return {"ok": True}


@app.put("/api/admin/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductIn, _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    product.name = payload.name.strip()
    product.description = payload.description.strip()
    product.retail_price = payload.retail_price
    product.wholesale_price = payload.wholesale_price
    if payload.image_url:
        product.image_url = payload.image_url.strip()
    db.commit()
    db.refresh(product)
    return product


@app.post("/api/admin/products/{product_id}/photo")
def product_photo(
    product_id: int,
    file: UploadFile = File(...),
    _admin: dict = Depends(get_admin),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    product.image_url = save_upload(file, "product")
    db.commit()
    return {"url": product.image_url}


@app.get("/api/admin/users", response_model=list[UserOut])
def admin_users(_admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id.desc()).all()


def ticket_out(db: Session, ticket: SupportTicket) -> TicketOut:
    messages = (
        db.query(SupportMessage)
        .filter(SupportMessage.ticket_id == ticket.id)
        .order_by(SupportMessage.id)
        .all()
    )
    return TicketOut(
        id=ticket.id,
        user_email=ticket.user_email,
        subject=ticket.subject,
        status=ticket.status,
        created_at=ticket.created_at,
        messages=[MessageOut.model_validate(msg) for msg in messages],
    )


@app.get("/api/support/tickets", response_model=list[TicketOut])
def my_tickets(user: dict = Depends(current_user), db: Session = Depends(get_db)):
    query = db.query(SupportTicket).order_by(SupportTicket.id.desc())
    if not user.get("is_admin"):
        query = query.filter(SupportTicket.user_email == user["email"])
    return [ticket_out(db, ticket) for ticket in query.all()]


@app.post("/api/support/tickets", response_model=TicketOut)
def create_ticket(payload: TicketIn, user: dict = Depends(current_user), db: Session = Depends(get_db)):
    ticket = SupportTicket(user_email=user["email"], subject=payload.subject.strip(), status="open")
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    db.add(SupportMessage(ticket_id=ticket.id, author_email=user["email"], is_admin=False, text=payload.message.strip()))
    db.commit()
    return ticket_out(db, ticket)


@app.post("/api/support/tickets/{ticket_id}/messages", response_model=TicketOut)
def reply_ticket(ticket_id: int, payload: MessageIn, user: dict = Depends(current_user), db: Session = Depends(get_db)):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Обращение не найдено")
    if not user.get("is_admin") and ticket.user_email != user["email"]:
        raise HTTPException(status_code=403, detail="Нет доступа")
    db.add(
        SupportMessage(
            ticket_id=ticket.id,
            author_email=user["email"],
            is_admin=bool(user.get("is_admin")),
            text=payload.text.strip(),
        )
    )
    db.commit()
    return ticket_out(db, ticket)


def page(name: str) -> FileResponse:
    return FileResponse(STATIC_DIR / name)


@app.get("/")
def index() -> FileResponse:
    return page("index.html")


@app.get("/about")
def about() -> FileResponse:
    return page("about.html")


@app.get("/catalog")
def catalog_page() -> FileResponse:
    return page("catalog.html")


@app.get("/constructor")
def constructor_page() -> FileResponse:
    return page("constructor.html")


@app.get("/contacts")
def contacts_page() -> FileResponse:
    return page("contacts.html")


@app.get("/docs")
def docs_page() -> FileResponse:
    return page("docs.html")


@app.get("/admin")
def admin_page() -> FileResponse:
    return page("admin.html")


@app.get("/support")
def support_page() -> FileResponse:
    return page("support.html")


@app.get("/checkout")
def checkout_page() -> FileResponse:
    return page("checkout.html")

# ─── Доставка (публичный) ────────────────────────────────────────────────────
@app.get("/api/delivery")
def public_delivery(db: Session = Depends(get_db)):
    return db.query(DeliveryCompany).filter(DeliveryCompany.is_active.is_(True)).order_by(DeliveryCompany.sort_order).all()


# ─── Способы оплаты (публичный) ──────────────────────────────────────────────
@app.get("/api/payment-methods")
def public_payment_methods(client_type: str = "individual", db: Session = Depends(get_db)):
    return db.query(PaymentMethod).filter(
        PaymentMethod.is_active.is_(True),
        PaymentMethod.client_type == client_type
    ).order_by(PaymentMethod.sort_order).all()


# ─── Заказы ──────────────────────────────────────────────────────────────────
@app.post("/api/orders", response_model=OrderOut)
def create_order(payload: OrderIn, user: dict = Depends(current_user), db: Session = Depends(get_db)):
    order = CustomerOrder(
        user_email=user["email"],
        items=json.dumps([item.model_dump() for item in payload.items], ensure_ascii=False),
        total=payload.total,
        delivery_method=payload.delivery_method,
        delivery_address=payload.delivery_address,
        payment_type=payload.payment_type,
        payment_details=payload.payment_details,
        status="new",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@app.get("/api/orders", response_model=list[OrderOut])
def my_orders(user: dict = Depends(current_user), db: Session = Depends(get_db)):
    return db.query(CustomerOrder).filter(
        CustomerOrder.user_email == user["email"]
    ).order_by(CustomerOrder.id.desc()).all()


# ─── Отзывы ──────────────────────────────────────────────────────────────────
@app.get("/api/products/{product_id}/reviews", response_model=list[ReviewOut])
def product_reviews(product_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(
        Review.product_id == product_id,
        Review.is_visible.is_(True),
    ).order_by(Review.id.desc()).all()


@app.post("/api/products/{product_id}/reviews", response_model=ReviewOut)
def create_review(product_id: int, payload: ReviewIn, user: dict = Depends(current_user), db: Session = Depends(get_db)):
    review = Review(
        product_id=product_id,
        user_email=user["email"],
        rating=payload.rating,
        text=payload.text,
        is_visible=True,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


# ─── АДМИН: Заказы ───────────────────────────────────────────────────────────
@app.get("/api/admin/orders", response_model=list[OrderOut])
def admin_orders(_admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    return db.query(CustomerOrder).order_by(CustomerOrder.id.desc()).all()


@app.post("/api/admin/orders/{order_id}/status")
def update_order_status(order_id: int, status: str = Form(...), _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    order = db.query(CustomerOrder).filter(CustomerOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    order.status = status
    db.commit()
    return {"ok": True}


# ─── АДМИН: Отзывы ───────────────────────────────────────────────────────────
@app.delete("/api/admin/reviews/{review_id}")
def hide_review(review_id: int, _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    review.is_visible = False
    db.commit()
    return {"ok": True}


# ─── АДМИН: Способы оплаты ───────────────────────────────────────────────────
@app.get("/api/admin/payment-methods", response_model=list[PaymentMethodOut])
def admin_payment_methods(_admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    return db.query(PaymentMethod).order_by(PaymentMethod.sort_order).all()


@app.post("/api/admin/payment-methods", response_model=PaymentMethodOut)
def add_payment_method(payload: PaymentMethodIn, _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    pm = PaymentMethod(**payload.model_dump())
    db.add(pm)
    db.commit()
    db.refresh(pm)
    return pm


@app.put("/api/admin/payment-methods/{method_id}", response_model=PaymentMethodOut)
def update_payment_method(method_id: int, payload: PaymentMethodIn, _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    pm = db.query(PaymentMethod).filter(PaymentMethod.id == method_id).first()
    if not pm:
        raise HTTPException(status_code=404, detail="Метод не найден")
    for key, value in payload.model_dump().items():
        setattr(pm, key, value)
    db.commit()
    db.refresh(pm)
    return pm


@app.delete("/api/admin/payment-methods/{method_id}")
def delete_payment_method(method_id: int, _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    pm = db.query(PaymentMethod).filter(PaymentMethod.id == method_id).first()
    if not pm:
        raise HTTPException(status_code=404, detail="Метод не найден")
    db.delete(pm)
    db.commit()
    return {"ok": True}


# ─── АДМИН: Службы доставки ──────────────────────────────────────────────────
@app.get("/api/admin/delivery", response_model=list[DeliveryCompanyOut])
def admin_delivery(_admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    return db.query(DeliveryCompany).order_by(DeliveryCompany.sort_order).all()


@app.post("/api/admin/delivery", response_model=DeliveryCompanyOut)
def add_delivery(payload: DeliveryCompanyIn, _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    dc = DeliveryCompany(**payload.model_dump())
    db.add(dc)
    db.commit()
    db.refresh(dc)
    return dc


@app.put("/api/admin/delivery/{company_id}", response_model=DeliveryCompanyOut)
def update_delivery(company_id: int, payload: DeliveryCompanyIn, _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    dc = db.query(DeliveryCompany).filter(DeliveryCompany.id == company_id).first()
    if not dc:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    for key, value in payload.model_dump().items():
        setattr(dc, key, value)
    db.commit()
    db.refresh(dc)
    return dc


@app.delete("/api/admin/delivery/{company_id}")
def delete_delivery(company_id: int, _admin: dict = Depends(get_admin), db: Session = Depends(get_db)):
    dc = db.query(DeliveryCompany).filter(DeliveryCompany.id == company_id).first()
    if not dc:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    db.delete(dc)
    db.commit()
    return {"ok": True}

if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")
