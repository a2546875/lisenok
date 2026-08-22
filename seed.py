from sqlalchemy.orm import Session

from database import ConstructorOption, Product, SessionLocal


SAMPLE_PRODUCTS = [
    {
        "name": 'Ваза "Мох"',
        "retail_price": 1500,
        "wholesale_price": 850,
        "image_url": "https://images.unsplash.com/photo-1578898887932-dce23a595ad4?q=80&w=800",
    },
    {
        "name": 'Подсвечник "Кора"',
        "retail_price": 980,
        "wholesale_price": 540,
        "image_url": "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?q=80&w=800",
    },
    {
        "name": 'Кашпо "Папоротник"',
        "retail_price": 2100,
        "wholesale_price": 1200,
        "image_url": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?q=80&w=800",
    },
    {
        "name": 'Тарелка "Листья"',
        "retail_price": 1250,
        "wholesale_price": 690,
        "image_url": "https://images.unsplash.com/photo-1610701596007-11502861dcfa?q=80&w=800",
    },
]

SAMPLE_OPTIONS = [
    ("set_type", "Ваза + подсвечник"),
    ("set_type", "Набор из 3 кашпо"),
    ("set_type", "Сервировочная группа"),
    ("color", "Лесной мох"),
    ("color", "Туманное утро"),
    ("color", "Королевский синий кинцуги"),
    ("color", "Тёплая глина"),
    ("pattern", "Без узора"),
    ("pattern", "Золотые прожилки"),
    ("pattern", "Отпечаток листа"),
    ("pattern", "Кора дерева"),
]


def seed_if_empty() -> None:
    db: Session = SessionLocal()
    try:
        if db.query(Product).count() == 0:
            for item in SAMPLE_PRODUCTS:
                db.add(Product(**item, is_active=True))

        if db.query(ConstructorOption).count() == 0:
            for category, name in SAMPLE_OPTIONS:
                db.add(ConstructorOption(category=category, name=name))

        db.commit()
    finally:
        db.close()
