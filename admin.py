from contextlib import contextmanager

import streamlit as st

from database import ConstructorOption, Inquiry, Product, SessionLocal
from seed import seed_if_empty

seed_if_empty()

CATEGORY_LABELS = {
    "set_type": "Состав набора",
    "color": "Цвет гипса",
    "pattern": "Узор / Декор",
}


@contextmanager
def db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


st.set_page_config(page_title="Админка Лисёнок", layout="wide")
st.title("🦊 Панель управления: Лисёнок")

tab1, tab2, tab3 = st.tabs(["🛍️ Управление каталогом", "🎨 Настройки конструктора", "✉️ Заявки"])

with tab1:
    st.header("Добавить новый товар")
    with st.form("new_product_form", clear_on_submit=True):
        name = st.text_input("Название (например: Ваза 'Мох')")
        retail = st.number_input("Розничная цена (₽)", min_value=0.0, step=100.0)
        wholesale = st.number_input("Оптовая цена от 100 шт (₽)", min_value=0.0, step=100.0)
        img_url = st.text_input("URL картинки товара")

        if st.form_submit_button("Добавить в каталог") and name:
            with db_session() as db:
                db.add(
                    Product(
                        name=name,
                        retail_price=retail,
                        wholesale_price=wholesale,
                        image_url=img_url,
                        is_active=True,
                    )
                )
            st.success(f"Товар «{name}» успешно добавлен на сайт!")
            st.rerun()

    st.divider()
    st.header("Товары на витрине")

    with db_session() as db:
        products = db.query(Product).order_by(Product.id.desc()).all()

        if not products:
            st.info("Каталог пуст. Добавьте первый товар выше.")
        else:
            for product in products:
                cols = st.columns([3, 1.2, 1.2, 1, 1, 1])
                cols[0].write(f"**{product.name}**")
                cols[1].write(f"{product.retail_price:.0f} ₽")
                cols[2].write(f"{product.wholesale_price:.0f} ₽")
                cols[3].write("Активен" if product.is_active else "Скрыт")

                if cols[4].button("Скрыть" if product.is_active else "Показать", key=f"toggle-{product.id}"):
                    product.is_active = not product.is_active
                    db.add(product)
                    db.commit()
                    st.rerun()

                if cols[5].button("Удалить", key=f"del-{product.id}"):
                    db.delete(product)
                    db.commit()
                    st.rerun()

with tab2:
    st.header("Опции 3D-конструктора")
    with st.form("new_option_form", clear_on_submit=True):
        category = st.selectbox(
            "Категория",
            ["set_type", "color", "pattern"],
            format_func=lambda x: CATEGORY_LABELS[x],
        )
        opt_name = st.text_input("Название опции (например: Королевский синий кинцуги)")

        if st.form_submit_button("Добавить опцию") and opt_name:
            with db_session() as db:
                db.add(ConstructorOption(category=category, name=opt_name))
            st.success(f"Опция «{opt_name}» добавлена в меню конструктора!")
            st.rerun()

    st.divider()
    with db_session() as db:
        options = db.query(ConstructorOption).order_by(ConstructorOption.category, ConstructorOption.id).all()
        if not options:
            st.info("Опций пока нет.")
        else:
            for option in options:
                left, right = st.columns([5, 1])
                left.write(f"**{CATEGORY_LABELS.get(option.category, option.category)}** — {option.name}")
                if right.button("Удалить", key=f"opt-del-{option.id}"):
                    db.delete(option)
                    db.commit()
                    st.rerun()

with tab3:
    st.header("Заявки с сайта")
    with db_session() as db:
        inquiries = db.query(Inquiry).order_by(Inquiry.id.desc()).all()
        if not inquiries:
            st.info("Заявок пока нет.")
        else:
            for item in inquiries:
                with st.expander(f"{item.name} · {item.contact}"):
                    st.write(item.message or "Без комментария")
                    if item.design:
                        st.caption(f"Дизайн: {item.design}")
                    if item.created_at:
                        st.caption(str(item.created_at))
                    if st.button("Удалить заявку", key=f"inq-del-{item.id}"):
                        db.delete(item)
                        db.commit()
                        st.rerun()
