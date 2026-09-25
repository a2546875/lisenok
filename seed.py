from sqlalchemy.orm import Session

from database import ConstructorOption, GalleryImage, Product, QrItem, SessionLocal, SiteText


SAMPLE_PRODUCTS = [
    {
        "name": 'Ваза "Мох"',
        "retail_price": 1500,
        "wholesale_price": 850,
        "image_url": "/assets/constructor/set-vase-candle.jpg",
    },
    {
        "name": 'Подсвечник "Кора"',
        "retail_price": 980,
        "wholesale_price": 540,
        "image_url": "/assets/constructor/set-vase-candle.jpg",
    },
    {
        "name": 'Кашпо "Папоротник"',
        "retail_price": 2100,
        "wholesale_price": 1200,
        "image_url": "/assets/constructor/set-planters.jpg",
    },
    {
        "name": 'Тарелка "Листья"',
        "retail_price": 1250,
        "wholesale_price": 690,
        "image_url": "/assets/constructor/set-serving.jpg",
    },
]

DEFAULT_TEXTS = [
    ("home", "home_kicker", "Надзаголовок презентации", "Лесная мастерская"),
    ("home", "home_title", "Заголовок презентации", "ДЫХАНИЕ ЛЕСА"),
    ("home", "home_lead", "Текст презентации", "Авторский гипсовый декор. Экологичный и безопасный продукт — отличное дополнение к дому, витрине и подарку."),
    ("home", "home_eco_title", "Блок 1 заголовок", "Экологично"),
    ("home", "home_eco_text", "Блок 1 текст", "Только натуральный скульптурный гипс. Без токсинов и лишней химии."),
    ("home", "home_safe_title", "Блок 2 заголовок", "Безопасно"),
    ("home", "home_safe_text", "Блок 2 текст", "Подходит для жилых интерьеров. Влагозащитное покрытие."),
    ("home", "home_plus_title", "Блок 3 заголовок", "Отличное дополнение"),
    ("home", "home_plus_text", "Блок 3 текст", "Вазы, кашпо, подсвечники и наборы для дома, кафе и подарка."),
    ("home", "home_workshop_title", "Заголовок фото мастерской", "Фото мастерской"),
    ("home", "home_ready_title", "Заголовок готовых изделий", "Готовые изделия"),
    ("catalog", "catalog_title", "Заголовок каталога", "Каталог"),
    ("catalog", "catalog_lead", "Текст каталога", "Розница — одна позиция. Опт: своя цена и заказ от 50 штук."),
    ("contacts", "contacts_title", "Заголовок контактов", "Контакты"),
    ("contacts", "contacts_lead", "Текст контактов", "Предзаказ и сотрудничество"),
    ("contacts", "contacts_phone", "Телефон", "+7 (999) 123-45-67"),
    ("contacts", "contacts_email", "Электронная почта", "n.3leonora@yandex.ru"),
    ("docs", "docs_title", "Заголовок документации", "Документация"),
    ("docs", "docs_lead", "Текст документации", "Сертификаты и документы мастерской. Нажмите, чтобы открыть крупнее."),
]

DEFAULT_QRS = [
    ("ВКонтакте", "https://vk.com", 1),
    ("Telegram", "https://t.me", 2),
    ("MAX", "https://max.ru", 3),
    ("Сайт", "http://89.110.94.112", 4),
]

DEFAULT_GALLERY = [
    ("workshop", "https://images.unsplash.com/photo-1610701596007-11502861dcfa?q=80&w=700"),
    ("workshop", "https://images.unsplash.com/photo-1452860606245-08befc0ff44b?q=80&w=700"),
    ("workshop", "https://images.unsplash.com/photo-1464375117522-1311d6a5b81f?q=80&w=700"),
    ("product", "https://images.unsplash.com/photo-1578898887932-dce23a595ad4?q=80&w=600"),
    ("product", "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?q=80&w=600"),
    ("product", "https://images.unsplash.com/photo-1485955900006-10f4d324d411?q=80&w=600"),
    ("product", "https://images.unsplash.com/photo-1596073419667-9c79f5d4750c?q=80&w=600"),
    ("background", "/assets/forest-bg.png"),
]

OPTION_IMAGES = {
    ("set_type", "Ваза + подсвечник"): "/assets/constructor/set-vase-candle.jpg",
    ("set_type", "Набор из 3 кашпо"): "/assets/constructor/set-planters.jpg",
    ("set_type", "Сервировочная группа"): "/assets/constructor/set-serving.jpg",
    ("set_type", "Ваза"): "/assets/uploads/product-74b04f00159d439ab451c91847f1bc27.jpg",
    ("set_type", "Шкатулка"): "/assets/uploads/product-f577312e023a415380c4f5f07a5b283d.jpg",
    ("set_type", "Подсвечник"): "/assets/uploads/product-96f7efb7e8314f369dedb7eca23d2c9f.jpg",
    ("set_type", "Тарелка волна"): "/assets/constructor/set-plate-wave.jpg",
    ("set_type", "Тарелка Цветок"): "/assets/constructor/set-plate-flower.jpg",
    ("set_type", "Тарелка Babl"): "/assets/constructor/set-plate-babl.jpg",
    ("set_type", "Поднос"): "/assets/uploads/product-5643ec3c114841eea8af647533389229.png",
    ("color", "Лесной мох"): "/assets/constructor/color-moss.jpg",
    ("color", "Туманное утро"): "/assets/constructor/color-mist.jpg",
    ("color", "Королевский синий кинцуги"): "/assets/constructor/color-kintsugi-blue.jpg",
    ("color", "Тёплая глина"): "/assets/constructor/color-clay.jpg",
    ("color", "Красный"): "/assets/constructor/color-red.jpg",
    ("color", "Синий"): "/assets/constructor/color-kintsugi-blue.jpg",
    ("color", "Оранжевый"): "/assets/constructor/color-orange.jpg",
    ("color", "Черный"): "/assets/constructor/color-black.jpg",
    ("color", "Зеленый"): "/assets/constructor/color-green.jpg",
    ("color", "Лесная зелень"): "/assets/constructor/color-moss.jpg",
    ("color", "Махогор"): "/assets/constructor/color-mahogany.jpg",
    ("pattern", "Золотые прожилки"): "/assets/constructor/pattern-gold.jpg",
    ("pattern", "Отпечаток листа"): "/assets/constructor/pattern-leaf.jpg",
    ("pattern", "Кора дерева"): "/assets/constructor/pattern-bark.jpg",
    ("pattern", "Бохо"): "/assets/uploads/product-19bcb770ba95407eab0390725155e8af.jpg",
    ("pattern", "Капельный"): "/assets/uploads/product-1649c739c0b0431ab28c5354b71bafd6.jpg",
    ("pattern", "Разливка"): "/assets/uploads/product-1649c739c0b0431ab28c5354b71bafd6.jpg",
    ("pattern", "Поталь"): "/assets/constructor/pattern-gold.jpg",
    ("pattern", "Половинная заливка с поталью"): "/assets/constructor/pattern-gold.jpg",
    ("pattern", "Сакура"): "/assets/constructor/pattern-sakura.jpg",
    ("pattern", "Сердечки"): "/assets/uploads/product-50fb7f76ac59428cb14a43ba9cf8a0a1.png",
    ("pattern", "Леопард"): "/assets/constructor/pattern-leopard.jpg",
    ("pattern", "Трафарет"): "/assets/constructor/pattern-stencil.jpg",
    ("pattern", "Трафареты"): "/assets/constructor/pattern-stencil.jpg",
}

SET_PRICES = {
    "Ваза": 250,
    "Шкатулка": 200,
    "Подсвечник": 100,
    "Поднос": 300,
    "Тарелка волна": 200,
    "Тарелка-волна": 200,
    "Тарелка Цветок": 200,
    "Тарелка-цветок": 200,
    "Тарелка Babl": 200,
}

PATTERN_RENAMES = {
    "Поталь": "Половинная заливка с поталью",
    "Капельный": "Разливка",
    "Трафарет": "Трафареты",
}

REQUIRED_PATTERNS = [
    "Бохо",
    "Половинная заливка с поталью",
    "Сакура",
    "Сердечки",
    "Разливка",
    "Леопард",
    "Трафареты",
]


SAMPLE_OPTIONS = [
    ("set_type", "Ваза + подсвечник", "/assets/constructor/set-vase-candle.jpg"),
    ("set_type", "Набор из 3 кашпо", "/assets/constructor/set-planters.jpg"),
    ("set_type", "Сервировочная группа", "/assets/constructor/set-serving.jpg"),
    ("color", "Лесной мох", "/assets/constructor/color-moss.jpg"),
    ("color", "Туманное утро", "/assets/constructor/color-mist.jpg"),
    ("color", "Королевский синий кинцуги", "/assets/constructor/color-kintsugi-blue.jpg"),
    ("color", "Тёплая глина", "/assets/constructor/color-clay.jpg"),
    ("pattern", "Без узора", ""),
    ("pattern", "Золотые прожилки", "/assets/constructor/pattern-gold.jpg"),
    ("pattern", "Отпечаток листа", "/assets/constructor/pattern-leaf.jpg"),
    ("pattern", "Кора дерева", "/assets/constructor/pattern-bark.jpg"),
]


def seed_if_empty() -> None:
    db: Session = SessionLocal()
    try:
        if db.query(Product).count() == 0:
            for item in SAMPLE_PRODUCTS:
                db.add(Product(**item, is_active=True))
        else:
            sample_photos = {item["name"]: item["image_url"] for item in SAMPLE_PRODUCTS}
            for product in db.query(Product).all():
                if product.image_url and "unsplash.com" in product.image_url:
                    product.image_url = sample_photos.get(product.name, product.image_url)

        if db.query(ConstructorOption).count() == 0:
            for category, name, image_url in SAMPLE_OPTIONS:
                db.add(ConstructorOption(category=category, name=name, image_url=image_url, price=SET_PRICES.get(name, 0)))
        else:
            defaults = {**OPTION_IMAGES, **{(category, name): image_url for category, name, image_url in SAMPLE_OPTIONS}}
            for option in db.query(ConstructorOption).all():
                if option.category == "pattern" and option.name in PATTERN_RENAMES:
                    option.name = PATTERN_RENAMES[option.name]
                if not option.image_url:
                    option.image_url = defaults.get((option.category, option.name), "")
                if option.category == "set_type":
                    catalog = db.query(Product).filter(Product.name == option.name, Product.is_active == True).first()
                    if catalog and catalog.retail_price:
                        option.price = catalog.retail_price
                    elif not option.price:
                        option.price = SET_PRICES.get(option.name, 0)
            existing_patterns = {
                opt.name for opt in db.query(ConstructorOption).filter(ConstructorOption.category == "pattern").all()
            }
            for name in REQUIRED_PATTERNS:
                if name not in existing_patterns:
                    db.add(ConstructorOption(
                        category="pattern",
                        name=name,
                        image_url=OPTION_IMAGES.get(("pattern", name), ""),
                    ))

        if db.query(SiteText).count() == 0:
            for page, key, label, value in DEFAULT_TEXTS:
                db.add(SiteText(page=page, key=key, label=label, value=value))
        else:
            existing = {row.key for row in db.query(SiteText).all()}
            for page, key, label, value in DEFAULT_TEXTS:
                if key not in existing:
                    db.add(SiteText(page=page, key=key, label=label, value=value))
            email_row = db.query(SiteText).filter(SiteText.key == "contacts_email").first()
            if email_row and (not email_row.value or "example" in email_row.value):
                email_row.value = "n.3leonora@yandex.ru"

        if db.query(QrItem).count() == 0:
            for title, url, order in DEFAULT_QRS:
                db.add(QrItem(title=title, url=url, image_url="", sort_order=order))

        if db.query(GalleryImage).count() == 0:
            for kind, image_url in DEFAULT_GALLERY:
                db.add(GalleryImage(kind=kind, image_url=image_url))

        db.commit()
    finally:
        db.close()
