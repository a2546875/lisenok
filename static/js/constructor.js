const SLOT_COUNT = 6;

const REQUIRED_POSITIONS = [
    { name: "Ваза", aliases: ["Ваза"], price: 250, image_url: "/assets/constructor/set-vase-candle.jpg" },
    { name: "Шкатулка", aliases: ["Шкатулка"], price: 200, image_url: "/assets/constructor/set-serving.jpg" },
    { name: "Подсвечник", aliases: ["Подсвечник"], price: 100, image_url: "/assets/constructor/set-vase-candle.jpg" },
    { name: "Поднос", aliases: ["Поднос"], price: 300, image_url: "/assets/constructor/set-serving.jpg" },
    { name: "Тарелка-волна", aliases: ["Тарелка-волна", "Тарелка волна"], price: 200, image_url: "/assets/constructor/set-plate-wave.jpg" },
    { name: "Тарелка-цветок", aliases: ["Тарелка-цветок", "Тарелка Цветок"], price: 200, image_url: "/assets/constructor/set-plate-flower.jpg" },
    { name: "Тарелка Babl", aliases: ["Тарелка Babl"], price: 200, image_url: "/assets/constructor/set-plate-babl.jpg" }
];

const REQUIRED_PATTERNS = [
    { name: "Бохо", aliases: ["Бохо"], image_url: "/assets/constructor/pattern-leaf.jpg" },
    { name: "Половинная заливка с поталью", aliases: ["Половинная заливка с поталью", "Поталь"], image_url: "/assets/constructor/pattern-gold.jpg" },
    { name: "Сакура", aliases: ["Сакура"], image_url: "/assets/constructor/pattern-sakura.jpg" },
    { name: "Сердечки", aliases: ["Сердечки"], image_url: "/assets/constructor/pattern-leaf.jpg" },
    { name: "Разливка", aliases: ["Разливка", "Капельный"], image_url: "/assets/constructor/color-clay.jpg" },
    { name: "Леопард", aliases: ["Леопард"], image_url: "/assets/constructor/pattern-leopard.jpg" },
    { name: "Трафареты", aliases: ["Трафареты", "Трафарет"], image_url: "/assets/constructor/pattern-stencil.jpg" }
];

const COLOR_HEX = {
    "Красный": "#b33a3a",
    "Синий": "#2f4d7a",
    "Оранжевый": "#d4783a",
    "Черный": "#1c1c1c",
    "Зеленый": "#3d6b45",
    "Лесная зелень": "#4a5d3a",
    "Махогор": "#6b3a2a",
    "Лесной мох": "#6b7d6e",
    "Туманное утро": "#9aa7a1",
    "Королевский синий кинцуги": "#2f4d7a",
    "Тёплая глина": "#b08968"
};

const STENCILS = [
    ["leaf", "Лист"],
    ["fern", "Папоротник"],
    ["heart", "Сердце"],
    ["star", "Звезда"],
    ["fox", "Лиса"],
    ["flower", "Цветок"],
    ["butterfly", "Бабочка"],
    ["feather", "Перо"],
    ["moon", "Луна"],
    ["drop", "Капля"],
    ["circle", "Круг"],
    ["diamond", "Ромб"],
    ["branch", "Ветка"],
    ["acorn", "Жёлудь"],
    ["snow", "Снежинка"],
    ["wave", "Волна"],
    ["mushroom", "Гриб"],
    ["bird", "Птица"]
];

const ctor = {
    positions: REQUIRED_POSITIONS,
    colors: [],
    patterns: REQUIRED_PATTERNS,
    slots: Array.from({ length: SLOT_COUNT }, () => null),
    openSlot: -1,
    selectedSlot: -1,
    selectedColor: null,
    colorMode: "all",
    selectedPattern: null,
    selectedStencil: null,
    painting: false
};

function findByAlias(list, name) {
    return list.find((item) => item.name === name || (item.aliases || []).includes(name));
}

function mergeOptions(required, incoming) {
    return required.map((base) => {
        const match = (incoming || []).find((item) => (base.aliases || [base.name]).includes(item.name));
        return {
            ...base,
            image_url: match?.image_url || base.image_url,
            price: match?.price || base.price
        };
    });
}

function filledSlots() {
    return ctor.slots.map((slot, index) => ({ slot, index })).filter((item) => item.slot);
}

function currentSlot() {
    if (ctor.selectedSlot >= 0 && ctor.slots[ctor.selectedSlot]) return ctor.slots[ctor.selectedSlot];
    const first = ctor.slots.find(Boolean);
    return first || null;
}

function currentSlotIndex() {
    if (ctor.selectedSlot >= 0 && ctor.slots[ctor.selectedSlot]) return ctor.selectedSlot;
    return ctor.slots.findIndex(Boolean);
}

function escapeAttr(value) {
    return String(value || "").replace(/"/g, "&quot;");
}

function renderSlots() {
    const box = document.getElementById("ctor-slots");
    if (!box) return;
    box.innerHTML = ctor.slots.map((slot, index) => {
        if (!slot) {
            return `<button type="button" class="ctor-slot" data-slot="${index}"><span class="ctor-slot-plus">+</span></button>`;
        }
        return `
            <button type="button" class="ctor-slot filled ${ctor.selectedSlot === index ? "selected" : ""}" data-slot="${index}">
                <span class="ctor-slot-clear" data-clear="${index}">×</span>
                <div class="ctor-item-visual">
                    <img src="${slot.image_url}" alt="${escapeAttr(slot.name)}">
                    ${slot.colorHex ? `<div class="wash" style="background:${slot.colorHex}"></div>` : ""}
                    ${slot.pattern === "Половинная заливка с поталью" ? '<div class="potal"></div>' : ""}
                </div>
                <span class="ctor-slot-name">${slot.name}</span>
            </button>`;
    }).join("");
}

function renderPicker() {
    const box = document.getElementById("ctor-picker");
    if (!box) return;
    if (ctor.openSlot < 0) {
        box.classList.add("hidden");
        box.innerHTML = "";
        return;
    }
    box.classList.remove("hidden");
    box.innerHTML = `
        <p class="text-sm mb-3">Выберите позицию для окошка ${ctor.openSlot + 1}</p>
        <div class="ctor-picker-grid">
            ${ctor.positions.map((item) => `
                <button type="button" class="ctor-pick-item" data-name="${escapeAttr(item.name)}">
                    <img src="${item.image_url}" alt="${escapeAttr(item.name)}">
                    <span>${item.name}<br>${Math.round(item.price)} ₽</span>
                </button>
            `).join("")}
        </div>`;
}

function renderColors() {
    const box = document.getElementById("ctor-colors");
    if (!box) return;
    box.innerHTML = ctor.colors.map((color) => `
        <button type="button" class="ctor-swatch ${ctor.selectedColor === color.name ? "active" : ""}"
            data-color="${escapeAttr(color.name)}"
            title="${escapeAttr(color.name)}"
            style="background:${color.hex}"></button>
    `).join("");
}

function renderPatterns() {
    const box = document.getElementById("ctor-patterns");
    if (!box) return;
    box.innerHTML = ctor.patterns.map((pattern) => `
        <button type="button" class="ctor-pattern ${ctor.selectedPattern === pattern.name ? "active" : ""}" data-pattern="${escapeAttr(pattern.name)}">
            ${pattern.image_url ? `<img src="${pattern.image_url}" alt="">` : ""}
            <span>${pattern.name}</span>
        </button>
    `).join("");
}

function renderStencils() {
    const box = document.getElementById("ctor-stencils");
    if (!box) return;
    const show = ctor.selectedPattern === "Трафареты";
    box.classList.toggle("hidden", !show);
    if (!show) return;
    box.innerHTML = STENCILS.map(([id, name]) => `
        <button type="button" class="ctor-stencil ${ctor.selectedStencil === id ? "active" : ""}" data-stencil="${id}">
            <img src="/assets/constructor/stencils/${id}.svg" alt="${name}">
            <span>${name}</span>
        </button>
    `).join("");
}

function itemVisual(slot) {
    const extras = [];
    if (slot.colorHex) extras.push(`<div class="wash" style="background:${slot.colorHex}"></div>`);
    if (slot.pattern === "Половинная заливка с поталью") extras.push('<div class="potal"></div>');
    else if (slot.pattern && slot.pattern !== "Трафареты") {
        const pattern = findByAlias(ctor.patterns, slot.pattern);
        if (pattern?.image_url) extras.push(`<img src="${pattern.image_url}" alt="" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;mix-blend-mode:overlay;opacity:.45">`);
    }
    if (slot.paint) extras.push(`<img src="${slot.paint}" alt="" style="position:absolute;inset:0;width:100%;height:100%;object-fit:contain">`);
    return `
        <div class="ctor-item-visual">
            <img src="${slot.image_url}" alt="${escapeAttr(slot.name)}">
            ${extras.join("")}
        </div>`;
}

function renderSet() {
    const box = document.getElementById("ctor-set");
    const total = document.getElementById("ctor-total");
    const preview = document.getElementById("design-preview");
    const items = filledSlots();
    if (box) {
        box.innerHTML = items.length
            ? items.map(({ slot, index }) => `
                <button type="button" class="ctor-set-card ${ctor.selectedSlot === index ? "selected" : ""}" data-set="${index}">
                    ${itemVisual(slot)}
                    <span>${slot.name}${slot.color ? ` · ${slot.color}` : ""}</span>
                </button>`)
            .join("")
            : '<p class="text-sm opacity-70">Добавьте позиции плюсиками выше — здесь соберётся комплект.</p>';
    }
    const sum = items.reduce((acc, item) => acc + (Number(item.slot.price) || 0), 0);
    if (total) total.textContent = `${Math.round(sum)} ₽`;
    if (preview) {
        preview.textContent = items.length
            ? items.map(({ slot }) => `${slot.name}${slot.color ? `/${slot.color}` : ""}${slot.pattern ? `/${slot.pattern}` : ""}`).join(" + ") + ` = ${Math.round(sum)} ₽`
            : "Набор пока пуст";
    }
}

function updatePaintStudio() {
    const paint = document.getElementById("ctor-paint");
    const photo = document.getElementById("ctor-paint-photo");
    const color = document.getElementById("ctor-paint-color");
    const stencil = document.getElementById("ctor-paint-stencil");
    const canvas = document.getElementById("ctor-paint-layer");
    const slot = currentSlot();
    const show = ctor.selectedPattern === "Трафареты" && ctor.selectedStencil && slot;
    if (!paint) return;
    paint.classList.toggle("hidden", !show);
    if (!show || !photo || !canvas) return;
    photo.src = slot.image_url;
    if (color) color.style.background = slot.colorHex || "transparent";
    if (stencil) stencil.src = `/assets/constructor/stencils/${ctor.selectedStencil}.svg`;
    const size = canvas.getBoundingClientRect();
    const w = Math.max(280, Math.round(size.width) || 420);
    canvas.width = w;
    canvas.height = w;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, w, w);
    if (slot.paint) {
        const img = new Image();
        img.onload = () => ctx.drawImage(img, 0, 0, w, w);
        img.src = slot.paint;
    }
}

function savePaint() {
    const canvas = document.getElementById("ctor-paint-layer");
    const index = currentSlotIndex();
    if (!canvas || index < 0 || !ctor.slots[index]) return;
    ctor.slots[index].paint = canvas.toDataURL("image/png");
    renderSlots();
    renderSet();
}

function paintAt(event) {
    const canvas = document.getElementById("ctor-paint-layer");
    const stencilImg = document.getElementById("ctor-paint-stencil");
    if (!canvas || !stencilImg?.src) return;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const point = event.touches ? event.touches[0] : event;
    const x = (point.clientX - rect.left) * scaleX;
    const y = (point.clientY - rect.top) * scaleY;
    const tmp = document.createElement("canvas");
    tmp.width = canvas.width;
    tmp.height = canvas.height;
    const tctx = tmp.getContext("2d");
    tctx.fillStyle = "#111";
    tctx.beginPath();
    tctx.arc(x, y, 13, 0, Math.PI * 2);
    tctx.fill();
    tctx.globalCompositeOperation = "destination-in";
    tctx.drawImage(stencilImg, 0, 0, tmp.width, tmp.height);
    canvas.getContext("2d").drawImage(tmp, 0, 0);
    savePaint();
}

function moveBrush(event) {
    const stage = document.getElementById("ctor-paint-stage");
    const brush = document.getElementById("ctor-brush");
    if (!stage || !brush) return;
    const rect = stage.getBoundingClientRect();
    const point = event.touches ? event.touches[0] : event;
    brush.classList.remove("hidden");
    brush.style.left = `${point.clientX - rect.left}px`;
    brush.style.top = `${point.clientY - rect.top}px`;
}

function applyColorToSlot(index) {
    if (index < 0 || !ctor.slots[index] || !ctor.selectedColor) return;
    const color = ctor.colors.find((item) => item.name === ctor.selectedColor);
    ctor.slots[index].color = ctor.selectedColor;
    ctor.slots[index].colorHex = color?.hex || COLOR_HEX[ctor.selectedColor] || "#6b7d6e";
}

function applyPatternToSlot(index) {
    if (index < 0 || !ctor.slots[index] || !ctor.selectedPattern) return;
    ctor.slots[index].pattern = ctor.selectedPattern;
    if (ctor.selectedPattern !== "Трафареты") ctor.slots[index].stencil = null;
}

function selectSlot(index, forPicker = false) {
    if (forPicker && !ctor.slots[index]) {
        ctor.openSlot = index;
        ctor.selectedSlot = index;
    } else if (ctor.slots[index]) {
        ctor.selectedSlot = index;
        ctor.openSlot = -1;
        if (ctor.colorMode === "pick" && ctor.selectedColor) {
            applyColorToSlot(index);
            ctor.colorMode = "all";
            document.body.classList.remove("ctor-pick");
            document.getElementById("ctor-color-hint").textContent = `Цвет «${ctor.selectedColor}» нанесён на ${ctor.slots[index].name}`;
        }
    }
    renderAll();
}

function renderAll() {
    renderSlots();
    renderPicker();
    renderColors();
    renderPatterns();
    renderStencils();
    renderSet();
    updatePaintStudio();
    document.getElementById("ctor-color-all")?.classList.toggle("active", ctor.colorMode === "all");
    document.getElementById("ctor-color-one")?.classList.toggle("active", ctor.colorMode === "pick");
}

function bindConstructor() {
    document.getElementById("ctor-slots")?.addEventListener("click", (event) => {
        const clear = event.target.closest("[data-clear]");
        if (clear) {
            event.stopPropagation();
            const index = Number(clear.dataset.clear);
            ctor.slots[index] = null;
            if (ctor.selectedSlot === index) ctor.selectedSlot = -1;
            ctor.openSlot = -1;
            renderAll();
            return;
        }
        const slot = event.target.closest("[data-slot]");
        if (!slot) return;
        const index = Number(slot.dataset.slot);
        selectSlot(index, !ctor.slots[index]);
    });

    document.getElementById("ctor-picker")?.addEventListener("click", (event) => {
        const item = event.target.closest("[data-name]");
        if (!item || ctor.openSlot < 0) return;
        const position = ctor.positions.find((pos) => pos.name === item.dataset.name);
        ctor.slots[ctor.openSlot] = {
            name: position.name,
            image_url: position.image_url,
            price: position.price,
            color: null,
            colorHex: "",
            pattern: null,
            stencil: null,
            paint: ""
        };
        ctor.selectedSlot = ctor.openSlot;
        ctor.openSlot = -1;
        renderAll();
    });

    document.getElementById("ctor-colors")?.addEventListener("click", (event) => {
        const swatch = event.target.closest("[data-color]");
        if (!swatch) return;
        ctor.selectedColor = swatch.dataset.color;
        if (ctor.colorMode === "all") {
            filledSlots().forEach(({ index }) => applyColorToSlot(index));
            document.getElementById("ctor-color-hint").textContent = `Цвет «${ctor.selectedColor}» нанесён на весь набор`;
        } else {
            document.getElementById("ctor-color-hint").textContent = "Нажмите на изделие в наборе, чтобы раскрасить только его";
        }
        renderAll();
    });

    document.getElementById("ctor-color-all")?.addEventListener("click", () => {
        ctor.colorMode = "all";
        document.body.classList.remove("ctor-pick");
        if (ctor.selectedColor) filledSlots().forEach(({ index }) => applyColorToSlot(index));
        document.getElementById("ctor-color-hint").textContent = ctor.selectedColor
            ? `Цвет «${ctor.selectedColor}» нанесён на весь набор`
            : "Сначала выберите цвет квадратиком";
        renderAll();
    });

    document.getElementById("ctor-color-one")?.addEventListener("click", () => {
        ctor.colorMode = "pick";
        document.body.classList.add("ctor-pick");
        document.getElementById("ctor-color-hint").textContent = "Указатель активен: нажмите на конкретное изделие";
        renderAll();
    });

    document.getElementById("ctor-patterns")?.addEventListener("click", (event) => {
        const box = event.target.closest("[data-pattern]");
        if (!box) return;
        ctor.selectedPattern = box.dataset.pattern;
        const index = currentSlotIndex();
        if (index < 0) {
            document.getElementById("ctor-color-hint").textContent = "Сначала добавьте изделие плюсиком";
        } else {
            applyPatternToSlot(index);
            ctor.slots[index].stencil = ctor.selectedPattern === "Трафареты" ? ctor.selectedStencil : null;
        }
        if (ctor.selectedPattern !== "Трафареты") ctor.selectedStencil = null;
        renderAll();
    });

    document.getElementById("ctor-stencils")?.addEventListener("click", (event) => {
        const item = event.target.closest("[data-stencil]");
        if (!item) return;
        ctor.selectedStencil = item.dataset.stencil;
        const index = currentSlotIndex();
        if (index >= 0) {
            ctor.slots[index].pattern = "Трафареты";
            ctor.slots[index].stencil = ctor.selectedStencil;
        }
        renderAll();
    });

    document.getElementById("ctor-set")?.addEventListener("click", (event) => {
        const card = event.target.closest("[data-set]");
        if (!card) return;
        selectSlot(Number(card.dataset.set));
    });

    const stage = document.getElementById("ctor-paint-stage");
    stage?.addEventListener("pointerdown", (event) => {
        ctor.painting = true;
        stage.setPointerCapture(event.pointerId);
        paintAt(event);
        moveBrush(event);
    });
    stage?.addEventListener("pointermove", (event) => {
        moveBrush(event);
        if (ctor.painting) paintAt(event);
    });
    stage?.addEventListener("pointerup", () => { ctor.painting = false; });
    stage?.addEventListener("pointerleave", () => {
        ctor.painting = false;
        document.getElementById("ctor-brush")?.classList.add("hidden");
    });
    document.getElementById("ctor-paint-clear")?.addEventListener("click", () => {
        const index = currentSlotIndex();
        if (index >= 0 && ctor.slots[index]) ctor.slots[index].paint = "";
        updatePaintStudio();
        renderSlots();
        renderSet();
    });
}

window.getConstructorDesign = function getConstructorDesign() {
    return {
        text: document.getElementById("design-preview")?.textContent || "",
        total: filledSlots().reduce((acc, item) => acc + (Number(item.slot.price) || 0), 0)
    };
};

window.initConstructor = function initConstructor(data, catalog) {
    if (!document.getElementById("constructor-app")) return;
    ctor.positions = mergeOptions(REQUIRED_POSITIONS, data?.set_type || []);
    if (catalog?.length) {
        ctor.positions = ctor.positions.map((pos) => {
            const product = catalog.find((item) => pos.aliases.includes(item.name) || item.name === pos.name);
            return product ? { ...pos, price: product.retail_price || pos.price, image_url: product.image_url || pos.image_url } : pos;
        });
    }
    const incomingColors = (data?.color || []).map((item) => ({
        name: item.name,
        hex: COLOR_HEX[item.name] || "#6b7d6e",
        image_url: item.image_url
    }));
    ctor.colors = incomingColors.length ? incomingColors : Object.entries(COLOR_HEX).slice(0, 7).map(([name, hex]) => ({ name, hex }));
    ctor.patterns = mergeOptions(REQUIRED_PATTERNS, data?.pattern || []);
    ctor.selectedColor = ctor.colors[0]?.name || null;
    bindConstructor();
    renderAll();
};
