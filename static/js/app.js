const API_BASE = window.location.protocol === "file:" ? "http://127.0.0.1:8000" : "";

const FALLBACK_OPTIONS = {
    set_type: [
        { name: "Ваза + подсвечник", image_url: "/assets/constructor/set-vase-candle.jpg" },
        { name: "Набор из 3 кашпо", image_url: "/assets/constructor/set-planters.jpg" },
        { name: "Сервировочная группа", image_url: "/assets/constructor/set-serving.jpg" }
    ],
    color: [
        { name: "Лесной мох", image_url: "/assets/constructor/color-moss.jpg" },
        { name: "Туманное утро", image_url: "/assets/constructor/color-mist.jpg" },
        { name: "Королевский синий кинцуги", image_url: "/assets/constructor/color-kintsugi-blue.jpg" },
        { name: "Тёплая глина", image_url: "/assets/constructor/color-clay.jpg" }
    ],
    pattern: [
        { name: "Без узора", image_url: "" },
        { name: "Золотые прожилки", image_url: "/assets/constructor/pattern-gold.jpg" },
        { name: "Отпечаток листа", image_url: "/assets/constructor/pattern-leaf.jpg" },
        { name: "Кора дерева", image_url: "/assets/constructor/pattern-bark.jpg" }
    ]
};

let constructorData = FALLBACK_OPTIONS;

const COLOR_MAP = {
    "Лесной мох": "#6b7d6e",
    "Туманное утро": "#9aa7a1",
    "Королевский синий кинцуги": "#2f4d7a",
    "Тёплая глина": "#b08968",
    "Красный": "#b33a3a",
    "Синий": "#2f4d7a",
    "Оранжевый": "#d4783a",
    "Черный": "#1c1c1c",
    "Зеленый": "#3d6b45",
    "Лесная зелень": "#4a5d3a",
    "Махогор": "#6b3a2a"
};

const cart = JSON.parse(localStorage.getItem("lisenok-cart") || "[]");
let wholesaleMode = false;
let session = JSON.parse(localStorage.getItem("lisenok-session") || "null");
let currentUser = session?.email || localStorage.getItem("lisenok-user");

function visitorId() {
    let id = localStorage.getItem("lisenok-visitor");
    if (!id) {
        id = (crypto.randomUUID && crypto.randomUUID()) || `v-${Date.now()}-${Math.random().toString(16).slice(2)}`;
        localStorage.setItem("lisenok-visitor", id);
    }
    return id;
}

function saveSession(next) {
    session = next;
    currentUser = next?.email || null;
    if (next) localStorage.setItem("lisenok-session", JSON.stringify(next));
    else localStorage.removeItem("lisenok-session");
    localStorage.removeItem("lisenok-user");
}

function authHeaders(json = true) {
    const headers = {};
    if (json) headers["Content-Type"] = "application/json";
    if (session?.token) headers.Authorization = `Bearer ${session.token}`;
    return headers;
}

async function applySite() {
    try {
        const site = await fetch(`${API_BASE}/api/site`).then((r) => r.json());
        document.querySelectorAll("[data-content]").forEach((el) => {
            if (site.texts[el.dataset.content]) el.textContent = site.texts[el.dataset.content];
        });
        const phone = document.getElementById("contacts-phone");
        if (phone && site.texts.contacts_phone) {
            phone.textContent = site.texts.contacts_phone;
            phone.href = `tel:${site.texts.contacts_phone.replace(/[^\d+]/g, "")}`;
        }
        const bg = document.querySelector(".site-bg");
        if (bg && site.background_url) {
            bg.style.setProperty("--site-bg-image", `url('${site.background_url}')`);
        }
        const email = document.getElementById("contacts-email");
        if (email && site.texts.contacts_email) {
            email.textContent = site.texts.contacts_email;
            email.href = `mailto:${site.texts.contacts_email}`;
        }
        const workshop = document.getElementById("workshop-photos");
        if (workshop) {
            workshop.innerHTML = (site.gallery.workshop || []).map((img) =>
                `<img src="${img.image_url}" alt="Мастерская" class="photo-frame js-zoom">`
            ).join("");
        }
        const ready = document.getElementById("ready-photos");
        if (ready) {
            ready.innerHTML = (site.gallery.product || []).map((img) =>
                `<img src="${img.image_url}" alt="Изделие" class="photo-frame js-zoom">`
            ).join("");
        }
        const qrs = document.getElementById("qr-list");
        if (qrs) {
            qrs.innerHTML = (site.qrs || []).map((item) => `
                <div>
                    <a href="${item.url}" class="block mb-3 hover:text-brand-light">${item.title} ↗</a>
                    <img src="${item.image_url}" alt="${item.title}" class="w-24 h-24 rounded border border-white/20 p-1 bg-black/20">
                </div>
            `).join("");
        }
    } catch (error) {
        console.log("site content skip");
    }
}

async function trackVisit() {
    try {
        await fetch(`${API_BASE}/api/visit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ visitor_id: visitorId() })
        });
    } catch (error) {
        console.log("visit skip");
    }
}

function saveCart() {
    localStorage.setItem("lisenok-cart", JSON.stringify(cart));
    const counter = document.getElementById("cart-count");
    if (counter) counter.textContent = cart.reduce((sum, item) => sum + item.qty, 0);
}

function formatPrice(value) {
    return `${Math.round(value)} ₽`;
}

function addToCart(product) {
    const existing = cart.find((item) => item.id === product.id);
    if (existing) existing.qty += 1;
    else cart.push({ id: product.id, name: product.name, retail: product.retail_price, wholesale: product.wholesale_price, qty: 1 });
    saveCart();
    renderCart();
}

function renderCart() {
    const box = document.getElementById("cart-items");
    if (!box) return;
    if (!cart.length) {
        box.innerHTML = '<p class="text-sm opacity-70">Корзина пуста</p>';
        return;
    }
    box.innerHTML = cart.map((item) => `
        <div class="flex justify-between gap-4 text-sm border-b border-white/10 pb-2">
            <span>${item.name} × ${item.qty}</span>
            <span>${formatPrice((wholesaleMode ? item.wholesale : item.retail) * item.qty)}</span>
        </div>
    `).join("");
}

function fillSelect(select, values) {
    select.innerHTML = values.map((opt) => {
        const name = typeof opt === "string" ? opt : opt.name;
        const image = typeof opt === "string" ? "" : (opt.image_url || "");
        return `<option value="${name}" data-image="${image}">${name}</option>`;
    }).join("");
}

function optionByName(list, name) {
    return (list || []).find((item) => (item.name || item) === name) || {};
}

function openLightbox(src, kind = "") {
    if (!src) return;
    let box = document.getElementById("lightbox");
    if (!box) {
        document.body.insertAdjacentHTML("beforeend", '<div id="lightbox" class="lightbox"></div>');
        box = document.getElementById("lightbox");
        box.addEventListener("click", (event) => {
            if (event.target === box || event.target.closest("[data-close-light]")) box.classList.remove("open");
        });
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") box.classList.remove("open");
        });
    }
    const isPdf = kind === "pdf" || /\.pdf($|\?)/i.test(src);
    const media = isPdf
        ? `<iframe id="doc-media" src="${src}" title="Документ"></iframe>`
        : `<img id="doc-media" src="${src}" alt="Просмотр">`;
    box.innerHTML = `
        ${media}
        <div class="doc-zoom-bar">
            <button type="button" data-doc-zoom="-">−</button>
            <button type="button" data-doc-zoom="+">+</button>
            <button type="button" data-close-light>×</button>
        </div>`;
    let scale = 1;
    const applyZoom = () => {
        const el = document.getElementById("doc-media");
        if (el) el.style.transform = `scale(${scale})`;
    };
    box.querySelectorAll("[data-doc-zoom]").forEach((btn) => {
        btn.addEventListener("click", (event) => {
            event.stopPropagation();
            scale = btn.dataset.docZoom === "+" ? Math.min(3, scale + 0.25) : Math.max(0.6, scale - 0.25);
            applyZoom();
        });
    });
    box.classList.add("open");
}

function renderOptionThumbs(containerId, values, selectId) {
    const box = document.getElementById(containerId);
    const select = document.getElementById(selectId);
    if (!box || !select) return;
    box.innerHTML = values.filter((opt) => opt.image_url).map((opt) =>
        `<img src="${opt.image_url}" alt="${opt.name}" data-name="${opt.name}" class="${select.value === opt.name ? "active" : ""}">`
    ).join("");
    box.querySelectorAll("img").forEach((img) => {
        img.addEventListener("click", () => {
            select.value = img.dataset.name;
            updateDesignPreview();
        });
    });
}

function patternClass(name) {
    if (!name || name.toLowerCase().includes("без")) return "";
    if (name.toLowerCase().includes("золот")) return "gold";
    if (name.toLowerCase().includes("лист")) return "leaf";
    if (name.toLowerCase().includes("кор")) return "bark";
    return "admin";
}

function updateDesignPreview() {
    const setType = document.getElementById("select-set")?.value;
    const color = document.getElementById("select-color")?.value;
    const pattern = document.getElementById("select-pattern")?.value;
    const preview = document.getElementById("design-preview");
    const vase = document.getElementById("vase-preview");
    const overlay = document.getElementById("vase-pattern");
    const stage = document.getElementById("design-stage");
    const setImg = document.getElementById("preview-set");
    const colorWash = document.getElementById("preview-color");
    const patternImg = document.getElementById("preview-pattern");
    if (preview && setType) preview.textContent = `${setType} · ${color} · ${pattern}`;
    const setOpt = optionByName(constructorData.set_type, setType);
    const colorOpt = optionByName(constructorData.color, color);
    const patternOpt = optionByName(constructorData.pattern, pattern);
    const hasPhoto = Boolean(setOpt.image_url);
    if (stage) stage.classList.toggle("hidden", !hasPhoto);
    if (vase) {
        vase.classList.toggle("hidden", hasPhoto);
        vase.style.background = COLOR_MAP[color] || "#6b7d6e";
    }
    if (overlay) overlay.className = `vase-pattern ${patternClass(pattern)}`;
    if (setImg) {
        setImg.src = setOpt.image_url || "";
        setImg.classList.toggle("hidden", !setOpt.image_url);
    }
    if (colorWash) {
        if (colorOpt.image_url) {
            colorWash.style.backgroundImage = `url('${colorOpt.image_url}')`;
            colorWash.style.backgroundColor = "transparent";
        } else {
            colorWash.style.backgroundImage = "";
            colorWash.style.backgroundColor = COLOR_MAP[color] || "#6b7d6e";
        }
    }
    if (patternImg) {
        patternImg.src = patternOpt.image_url || "";
        patternImg.classList.toggle("hidden", !patternOpt.image_url);
    }
    renderOptionThumbs("thumbs-set", constructorData.set_type, "select-set");
    renderOptionThumbs("thumbs-color", constructorData.color, "select-color");
    renderOptionThumbs("thumbs-pattern", constructorData.pattern, "select-pattern");
}

function renderCatalog(products) {
    const grid = document.getElementById("products-grid");
    if (!grid) return;
    if (!products.length) {
        grid.innerHTML = '<p class="opacity-70 text-sm">Каталог пока пуст. Добавьте товары в админке.</p>';
        return;
    }
    grid.innerHTML = products.map((product) => `
        <div class="glass-card rounded-2xl p-4 transition group">
            <img src="${product.image_url || "/assets/constructor/set-vase-candle.jpg"}" alt="${product.name}" class="catalog-photo js-zoom">
            <h3 class="font-medium mb-1">${product.name}</h3>
            ${product.description ? `<p class="text-sm opacity-70 mb-2">${product.description}</p>` : ""}
            <p class="text-xl font-bold price-val"
               data-retail="${formatPrice(product.retail_price)}"
               data-opt="${formatPrice(product.wholesale_price)} / шт от 50">
               ${wholesaleMode ? formatPrice(product.wholesale_price) + " / шт от 50" : formatPrice(product.retail_price)}
            </p>
            <button class="w-full mt-4 py-2 bg-brand-green/80 rounded-lg text-sm font-medium hover:bg-brand-green"
                    onclick='addToCart(${JSON.stringify(product)})'>
                В корзину
            </button>
            <div class="mt-3 pt-3 border-t border-white/10" data-reviews-product="${product.id}">
                <button type="button" class="w-full py-2 bg-white/10 rounded-lg text-xs font-medium hover:bg-white/20 inline-review-toggle" data-product-id="${product.id}">Отзывы</button>
                <div id="inline-reviews-${product.id}" class="hidden mt-2 space-y-2"></div>
            </div>
            <button class="w-full mt-2 py-2 bg-brand-green/80 rounded-lg text-sm font-medium hover:bg-brand-green opt-btn ${wholesaleMode ? "" : "hidden"}">
                Заказать опт от 50 шт
            </button>
        </div>
    `).join("");
}

async function loadInlineReviews(productId) {
    const container = document.getElementById("inline-reviews-" + productId);
    if (!container) return;
    container.textContent = "Загрузка отзывов...";
    try {
        const response = await fetch(`${API_BASE}/api/products/${productId}/reviews`);
        if (!response.ok) throw new Error("reviews");
        const reviews = await response.json();
        container.innerHTML = reviews.length ? reviews.map((review) => `
            <div class="rounded-lg bg-black/20 p-2 text-xs">
                <p class="font-medium">${review.user_email} <span class="text-amber-300">${"★".repeat(review.rating)}</span></p>
                <p class="mt-1 opacity-80 whitespace-pre-wrap">${review.text}</p>
            </div>
        `).join("") : '<p class="text-xs opacity-70">Пока нет отзывов</p>';
        if (!currentUser) return;
        const form = document.createElement("form");
        form.className = "space-y-2 pt-1";
        form.innerHTML = `
            <select name="rating" class="w-full bg-black/40 border border-white/20 rounded-lg p-2 text-xs outline-none">
                <option value="5">5 ★</option><option value="4">4 ★</option><option value="3">3 ★</option><option value="2">2 ★</option><option value="1">1 ★</option>
            </select>
            <textarea required name="text" placeholder="Ваш отзыв" class="w-full bg-black/40 border border-white/20 rounded-lg p-2 text-xs outline-none min-h-20"></textarea>
            <button class="w-full py-2 bg-brand-green hover:bg-brand-hover rounded-lg text-xs font-medium">Отправить отзыв</button>
        `;
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const data = new FormData(form);
            const submit = form.querySelector("button");
            submit.disabled = true;
            try {
                const result = await fetch(`${API_BASE}/api/products/${productId}/reviews`, { method: "POST", headers: authHeaders(), body: JSON.stringify({ rating: Number(data.get("rating")), text: data.get("text") }) });
                if (!result.ok) throw new Error("review");
                loadInlineReviews(productId);
            } catch (error) {
                submit.disabled = false;
                submit.textContent = "Не удалось отправить";
            }
        });
        container.appendChild(form);
    } catch (error) {
        container.textContent = "Не удалось загрузить отзывы";
    }
}

async function loadConstructorOptions() {
    if (!document.getElementById("constructor-app") && !document.getElementById("select-set")) return;
    let data = FALLBACK_OPTIONS;
    let catalog = [];
    try {
        const response = await fetch(`${API_BASE}/api/constructor-options`);
        if (response.ok) data = await response.json();
        const products = await fetch(`${API_BASE}/api/catalog`);
        if (products.ok) catalog = await products.json();
    } catch (error) {
        console.log("Ожидание запуска FastAPI сервера...");
    }
    constructorData = data;
    if (window.initConstructor) {
        window.initConstructor(data, catalog);
        return;
    }
    fillSelect(document.getElementById("select-set"), data.set_type);
    fillSelect(document.getElementById("select-color"), data.color);
    fillSelect(document.getElementById("select-pattern"), data.pattern);
    updateDesignPreview();
}

async function loadCatalog() {
    const status = document.getElementById("catalog-status");
    if (!document.getElementById("products-grid")) return;
    try {
        const response = await fetch(`${API_BASE}/api/catalog`);
        if (!response.ok) throw new Error("catalog");
        renderCatalog(await response.json());
        if (status) status.textContent = "";
    } catch (error) {
        if (status) status.textContent = "Не удалось загрузить каталог. Обновите страницу чуть позже.";
    }
}

function bindSharedUi() {
    const loginModal = document.getElementById("login-modal");
    const cartModal = document.getElementById("cart-modal");
    const loginBtn = document.getElementById("login-btn");
    if (!loginBtn) return;

    function refreshLoginButton() {
        loginBtn.textContent = currentUser ? currentUser : "Войти";
        const adminLink = document.getElementById("admin-link");
        const supportLink = document.getElementById("support-link");
        if (adminLink) adminLink.classList.toggle("hidden", !session?.is_admin);
        if (supportLink) supportLink.classList.toggle("hidden", !currentUser);
    }

    loginBtn.addEventListener("click", () => {
        if (currentUser) {
            saveSession(null);
            refreshLoginButton();
            return;
        }
        loginModal.showModal();
    });
    document.getElementById("login-close")?.addEventListener("click", () => loginModal.close());
    document.getElementById("cart-btn")?.addEventListener("click", () => {
        renderCart();
        cartModal.showModal();
    });
    document.getElementById("cart-close")?.addEventListener("click", () => cartModal.close());
    document.getElementById("checkout-btn")?.addEventListener("click", () => {
        if (!cart.length) return;
        window.location.href = "/checkout";
    });
    document.getElementById("login-form")?.addEventListener("submit", async (event) => {
        event.preventDefault();
        const form = event.target;
        const email = new FormData(form).get("email");
        const passwordBox = document.getElementById("admin-pass-wrap");
        const password = form.password?.value || "";
        const status = document.getElementById("login-status");
        try {
            if (passwordBox.classList.contains("hidden")) {
                const check = await fetch(`${API_BASE}/api/auth/check`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email })
                });
                const data = await check.json();
                if (data.needs_password) {
                    passwordBox.classList.remove("hidden");
                    if (status) status.textContent = "Для этой почты нужен пароль администратора";
                    form.password.focus();
                    return;
                }
            }
            const response = await fetch(`${API_BASE}/api/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });
            const data = await response.json();
            if (!response.ok) {
                const detail = Array.isArray(data.detail) ? data.detail[0]?.msg : data.detail;
                if (status) status.textContent = detail || "Не удалось войти";
                return;
            }
            saveSession(data);
            refreshLoginButton();
            loginModal.close();
            if (data.is_admin) window.location.href = "/admin";
        } catch (error) {
            if (status) status.textContent = "Сервер недоступен";
        }
    });
    document.getElementById("inquiry-form")?.addEventListener("submit", async (event) => {
        event.preventDefault();
        const form = new FormData(event.target);
        const design = document.getElementById("design-preview")?.textContent || "";
        const payload = {
            name: form.get("name"),
            contact: form.get("contact"),
            message: form.get("message") || cart.map((item) => `${item.name} × ${item.qty}`).join(", "),
            design
        };
        const status = document.getElementById("inquiry-status");
        try {
            const response = await fetch(`${API_BASE}/api/inquiry`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error("inquiry");
            cart.splice(0, cart.length);
            saveCart();
            renderCart();
            event.target.reset();
            if (status) status.textContent = "Заявка отправлена. Мы свяжемся с вами.";
        } catch (error) {
            if (status) status.textContent = "Не удалось отправить заявку. Проверьте, что сервер запущен.";
        }
    });
    document.getElementById("mobile-menu-btn")?.addEventListener("click", () => {
        document.getElementById("mobile-menu")?.classList.toggle("open");
    });
    document.addEventListener("click", (event) => {
        const reviewToggle = event.target.closest(".inline-review-toggle");
        if (reviewToggle) {
            const productId = reviewToggle.dataset.productId;
            const container = document.getElementById("inline-reviews-" + productId);
            if (!container) return;
            container.classList.toggle("hidden");
            if (!container.classList.contains("hidden")) loadInlineReviews(productId);
            return;
        }
        const doc = event.target.closest(".js-doc");
        if (doc) {
            event.preventDefault();
            openLightbox(doc.dataset.src || doc.href || doc.src, doc.dataset.kind || "");
            return;
        }
        const img = event.target.closest(".js-zoom");
        if (img?.src) openLightbox(img.src);
    });
    refreshLoginButton();
}

function bindPageScripts() {
    document.getElementById("mode-toggle")?.addEventListener("change", function () {
        wholesaleMode = this.checked;
        const label = document.getElementById("mode-label");
        if (label) label.textContent = wholesaleMode ? "Опт, заказ от 50 шт" : "Розница";
        document.querySelectorAll(".price-val").forEach((price) => {
            price.textContent = wholesaleMode ? price.dataset.opt : price.dataset.retail;
        });
        document.querySelectorAll(".opt-btn").forEach((btn) => btn.classList.toggle("hidden", !wholesaleMode));
        renderCart();
    });
    ["select-set", "select-color", "select-pattern"].forEach((id) => {
        document.getElementById(id)?.addEventListener("change", updateDesignPreview);
    });
    document.getElementById("save-design-btn")?.addEventListener("click", () => {
        const design = window.getConstructorDesign?.().text || document.getElementById("design-preview")?.textContent;
        if (!currentUser) {
            document.getElementById("login-modal")?.showModal();
            return;
        }
        const message = document.querySelector('#inquiry-form [name="message"]');
        if (message) message.value = `Сохранённый дизайн: ${design}`;
        renderCart();
        document.getElementById("cart-modal")?.showModal();
    });
}

function injectShell(active) {
    const links = [
        ["/", "Презентация", "home"],
        ["/catalog", "Каталог", "catalog"],
        ["/docs", "Документация", "docs"],
        ["/contacts", "Контакты", "contacts"]
    ];
    if (currentUser) links.push(["/support", "Поддержка", "support"]);
    if (active === "admin") links.push(["/admin", "Админка", "admin"]);
    const nav = links.map(([href, label, key]) =>
        `<a href="${href}" class="nav-link hover:text-white transition ${active === key ? "active" : "opacity-80"}">${label}</a>`
    ).join("");

    if (!document.querySelector('link[rel="icon"]')) {
        const icon = document.createElement("link");
        icon.rel = "icon";
        icon.href = "/assets/logo.png";
        document.head.appendChild(icon);
    }
    document.body.insertAdjacentHTML("afterbegin", `
        <div class="fixed inset-0 z-[-1] bg-black site-bg"></div>
        <div class="forest-mist"></div>
        <div class="forest-leaves"></div>
        <header class="w-full px-6 md:px-8 py-6 flex justify-between items-center max-w-7xl mx-auto">
            <a href="/" class="flex items-center">
                <img src="/assets/logo.png" alt="Лисёнок" class="site-logo">
            </a>
            <nav class="hidden md:flex flex-wrap gap-x-6 gap-y-2 text-sm uppercase tracking-wider">${nav}</nav>
            <div class="flex items-center gap-3 text-sm font-medium">
                <a id="support-link" href="/support" class="hidden px-3 py-2 bg-white/10 rounded-full hover:bg-white/20 transition">Поддержка</a>
                <a id="admin-link" href="/admin" class="hidden px-3 py-2 bg-white/10 rounded-full hover:bg-white/20 transition">Админка</a>
                <button id="login-btn" class="px-4 py-2 bg-white/10 rounded-full hover:bg-white/20 transition">Войти</button>
                <button id="cart-btn" class="cursor-pointer hover:text-white">Корзина 🛒 <span id="cart-count" class="opacity-80">0</span></button>
                <button id="mobile-menu-btn" class="md:hidden px-3 py-2 bg-white/10 rounded-full">Меню</button>
            </div>
        </header>
        <div id="mobile-menu">${nav}</div>
        <dialog id="login-modal" class="glass-panel rounded-3xl p-8 w-[min(420px,92vw)] text-slate-100">
            <h3 class="text-xl font-semibold mb-2">Вход</h3>
            <p class="text-sm opacity-70 mb-6">Сохраните дизайн и историю заявок.</p>
            <form id="login-form" class="space-y-3">
                <input required type="email" name="email" placeholder="email@example.com" class="w-full bg-black/40 border border-white/20 rounded-lg p-3 text-sm outline-none">
                <div id="admin-pass-wrap" class="hidden">
                    <input type="password" name="password" placeholder="Пароль администратора" class="w-full bg-black/40 border border-white/20 rounded-lg p-3 text-sm outline-none">
                </div>
                <p id="login-status" class="text-sm opacity-80"></p>
                <button class="w-full py-3 bg-brand-green hover:bg-brand-hover rounded-lg font-medium">Продолжить</button>
            </form>
            <button id="login-close" class="mt-4 text-sm opacity-70 hover:opacity-100">Закрыть</button>
        </dialog>
        <dialog id="cart-modal" class="glass-panel rounded-3xl p-8 w-[min(520px,92vw)] text-slate-100">
            <h3 class="text-xl font-semibold mb-4">Корзина</h3>
            <div id="cart-items" class="space-y-3 mb-6"></div>
            <button id="checkout-btn" class="w-full py-3 bg-brand-green hover:bg-brand-hover rounded-lg font-medium mb-3">Оформить заказ</button>
            <form id="inquiry-form" class="space-y-3">
                <p class="text-sm opacity-70 mb-2">Или напишите на почту: <a href="mailto:n.3leonora@yandex.ru" class="underline">n.3leonora@yandex.ru</a></p>
                <input required name="name" placeholder="Имя" class="w-full bg-black/40 border border-white/20 rounded-lg p-3 text-sm outline-none">
                <input required name="contact" placeholder="Телефон или Telegram" class="w-full bg-black/40 border border-white/20 rounded-lg p-3 text-sm outline-none">
                <textarea name="message" placeholder="Комментарий к заказу" class="w-full bg-black/40 border border-white/20 rounded-lg p-3 text-sm outline-none min-h-24"></textarea>
                <button class="w-full py-3 bg-brand-green hover:bg-brand-hover rounded-lg font-medium">Отправить заявку</button>
            </form>
            <p id="inquiry-status" class="text-sm mt-3 opacity-80"></p>
            <button id="cart-close" class="mt-4 text-sm opacity-70 hover:opacity-100">Закрыть</button>
        </dialog>
    `);
}

function boot(active) {
    injectShell(active);
    bindSharedUi();
    bindPageScripts();
    saveCart();
    loadCatalog();
    loadConstructorOptions();
    applySite();
    trackVisit();
}
