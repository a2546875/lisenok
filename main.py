from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from config import settings
from database import ConstructorOption, Inquiry, Product, get_db
from schemas import ConstructorOptionsOut, InquiryIn, InquiryOut, ProductOut
from seed import seed_if_empty

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Lisenok API", version="1.0.0")

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()] or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    seed_if_empty()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "project": "lisenok"}


@app.get("/api/catalog", response_model=list[ProductOut])
def get_catalog(db: Session = Depends(get_db)):
    """Возвращает все активные товары для витрины."""
    return db.query(Product).filter(Product.is_active.is_(True)).all()


@app.get("/api/constructor-options", response_model=ConstructorOptionsOut)
def get_options(db: Session = Depends(get_db)):
    """Возвращает варианты для выпадающих списков конструктора."""
    options = db.query(ConstructorOption).all()
    result: dict[str, list[str]] = {"set_type": [], "color": [], "pattern": []}
    for opt in options:
        if opt.category in result:
            result[opt.category].append(opt.name)
    return result


@app.post("/api/inquiry", response_model=InquiryOut)
def create_inquiry(payload: InquiryIn, db: Session = Depends(get_db)):
    """Заявка с сайта: предзаказ, опт или сохранённый дизайн."""
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


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")
