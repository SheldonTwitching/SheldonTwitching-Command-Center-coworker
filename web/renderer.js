/* Same renderer runs inside OBS and the visual editor; custom CSS is scoped to Shadow DOM. */
(() => {
  "use strict";
  const ROOT_URL = (window.SL_API_BASE || "").replace(/\/$/, "");
  const BASE_CSS = "overlay.css";
  const clamp = (x, min, max) => Math.min(max, Math.max(min, Number(x) || 0));
  const cssSafe = value => String(value ?? "").replace(/[;{}]/g, "");
  const isImageIcon = icon => typeof icon === "string" && /^data:image\/(png|jpeg|webp|svg\+xml);base64,[a-z\d+/=]+$/i.test(icon);

  function parseValue(item, raw) {
    let result = typeof raw === "string" && raw.trim() ? raw.trim() : String(item.fallback || "");
    const mode = item.parseMode || "raw";
    try {
      if (mode === "split") {
        const parts = result.split(item.delimiter || ":");
        result = (parts[Number(item.part) || 0] || "").trim();
      } else if (mode === "regex") {
        if (item.pattern) {
          const match = result.match(new RegExp(item.pattern));
          result = match ? (match[1] || match[0]) : "";
        }
      } else if (mode === "amount") {
        const match = result.match(/[$€£]\s?[\d,]+(?:\.\d{1,2})?/);
        result = match ? match[0] : result;
      } else if (mode === "before-colon") {
        result = result.split(":")[0].trim();
      }
    } catch (_) { /* Invalid pattern: preserve source value rather than crash. */ }
    return `${item.prefix || ""}${result || item.fallback || ""}${item.suffix || ""}`;
  }

  // Slider styles are generated in a stylesheet BEFORE custom CSS, so raw CSS
  // overrides are allowed without !important. This is shared by editor and OBS.
  function styleRule(item) {
    const vars = {
      "--accent": cssSafe(item.accent || "#e600d9"),
      "--bg": cssSafe(item.bg || "#230934e8"),
      "--value-color": cssSafe(item.textColor || "#fff"),
      "--label-color": cssSafe(item.labelColor || "#e5b7ff"),
      "--font-size": clamp(item.fontSize, 8, 160) + "px",
      "--label-size": clamp(item.labelSize, 7, 80) + "px",
      "--icon-size": clamp(item.iconSize, 8, 140) + "px",
      "--gap": clamp(item.gap, 0, 100) + "px",
      "--pad": clamp(item.pad, 0, 100) + "px",
      "--radius": clamp(item.radius, 0, 100) + "px",
      "--border": clamp(item.border, 0, 20) + "px",
      "--shadow": clamp(item.shadow, 0, 70) + "px",
      "--weight": clamp(item.fontWeight, 100, 1000),
      "--font": cssSafe(item.font || "Impact,sans-serif"),
      "--transition": clamp(item.transitionMs, 100, 4000) + "ms",
      left: clamp(item.x, 0, 3840) + "px",
      top: clamp(item.y, 0, 2160) + "px",
      width: clamp(item.w, 70, 3840) + "px",
      height: clamp(item.h, 30, 2160) + "px",
    };
    const declarations = Object.entries(vars).map(([key, val]) => `${key}:${val}`).join(";");
    // IDs are restricted to [\w-] by the project validator.
    const id = String(item.id || "").replace(/[^a-zA-Z0-9_-]/g, "");
    return `:where(.overlay-card[data-id="${id}"]){${declarations}}`;
  }

  class Stage {
    constructor(host, {editor = false, select = null} = {}) {
      this.host = host;
      this.editor = editor;
      this.onSelect = select;
      this.shadow = host.shadowRoot || host.attachShadow({mode:"open"});
      this.shadow.innerHTML = "";
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = BASE_CSS;
      this.shadow.append(link);
      this.generated = document.createElement("style");
      this.shadow.append(this.generated);
      this.custom = document.createElement("style");
      this.shadow.append(this.custom);
      this.canvas = document.createElement("div");
      this.canvas.className = "stage";
      this.shadow.append(this.canvas);
      this.cards = new Map();
    }

    update(project, live = {}, selectedId = null, showAll = true) {
      this.project = project;
      this.canvas.style.setProperty("--stage-width", (project.width || 900) + "px");
      this.canvas.style.setProperty("--stage-height", (project.height || 180) + "px");
      this.custom.textContent = project.customCSS || "";
      this.generated.textContent = (project.items || []).map(styleRule).join("\n");
      const ids = new Set();
      for (const item of project.items || []) {
        if (item.enabled === false && !this.editor) continue;
        ids.add(item.id);
        let card = this.cards.get(item.id);
        if (!card) {
          card = document.createElement("div");
          card.className = "overlay-card";
          card.dataset.id = item.id;
          const icon = document.createElement("div");
          icon.className = "overlay-icon";
          const text = document.createElement("div");
          text.className = "overlay-text";
          const kicker = document.createElement("div");
          kicker.className = "overlay-kicker";
          const value = document.createElement("div");
          value.className = "overlay-value";
          text.append(kicker, value);
          card.append(icon, text);
          if (this.editor) {
            const grip = document.createElement("div");
            grip.className = "resize-grip";
            card.append(grip);
            card.addEventListener("pointerdown", e => this.onSelect?.(item.id, e));
          }
          this.canvas.append(card);
          this.cards.set(item.id, card);
        }
        const iconBox = card.querySelector(".overlay-icon");
        if (isImageIcon(item.icon)) {
          let img = iconBox.querySelector("img");
          if (!img) { img = document.createElement("img"); iconBox.replaceChildren(img); }
          if (img.src !== item.icon) img.src = item.icon;
          img.alt = "";
        } else if (iconBox.textContent !== (item.icon || "⭐") || iconBox.querySelector("img")) {
          iconBox.textContent = item.icon || "⭐";
        }
        card.querySelector(".overlay-kicker").textContent = item.label || "";
        card.querySelector(".overlay-value").textContent = parseValue(item, live[item.file]);
        card.dataset.align = item.align || "left";
        card.dataset.idle = item.idleAnimation || "none";
        if (this.editor) {
          card.classList.toggle("selected", selectedId === item.id);
          card.classList.toggle("is-hidden", !showAll && selectedId !== item.id);
          card.style.opacity = item.enabled === false ? ".45" : "1";
        }
      }
      for (const [id, card] of this.cards) {
        if (!ids.has(id)) { card.remove(); this.cards.delete(id); }
      }
    }
  }

  function startOverlay() {
    const host = document.getElementById("overlayHost");
    if (!host) return;
    const stage = new Stage(host);
    const labelSource = new URLSearchParams(location.search).get("label");
    let project = window.SL_EMBEDDED_PROJECT || null;
    let live = {};
    let activeId = null;
    let currentIndex = 0;
    let timer = null;
    let exiting = false;
    let lastSig = "";

    function schedule(ms, callback) { clearTimeout(timer); timer = setTimeout(callback, ms); }
    function active() { return (project?.items || []).filter(i => i.enabled !== false); }
    function showItem(index) {
      const items = active();
      if (!items.length) { clearTimeout(timer); activeId=null; stage.update(project, live); return; }
      currentIndex = ((index % items.length) + items.length) % items.length;
      const item = items[currentIndex];
      activeId = item.id;
      exiting = false;
      stage.update(project, live);
      for (const card of stage.cards.values()) { card.style.display = card.dataset.id === activeId ? "flex" : "none"; card.classList.remove(...Array.from(card.classList).filter(k => k.startsWith("enter-") || k.startsWith("exit-"))); }
      const card = stage.cards.get(activeId);
      if (!card) return;
      card.classList.add("enter-" + (item.enter || "fade"));
      if (project.rotation && items.length > 1) {
        schedule(Math.max(800, Number(item.dwell || 5) * 1000), () => {
          exiting = true;
          card.classList.remove("enter-" + (item.enter || "fade"));
          card.classList.add("exit-" + (item.exit || "fade"));
          schedule(Math.max(100, Number(item.transitionMs || 550)), () => showItem(currentIndex + 1));
        });
      }
    }

    async function poll() {
      try {
        const url = `${ROOT_URL}/api/snapshot`;
        const response = await fetch(url, {cache:"no-store"});
        if (!response.ok) throw new Error("Bridge disconnected");
        const data = await response.json();
        live = data.live || {};
        if (!window.SL_EMBEDDED_PROJECT) project = data.project;
        if (!project) return;
        if (labelSource) project={...project,items:(project.items||[]).filter(i=>i.id===labelSource)};
        const sig = JSON.stringify(project);
        const oldActive = activeId;
        if (sig !== lastSig) {
          lastSig = sig;
          document.documentElement.style.width = project.width + "px";
          document.documentElement.style.height = project.height + "px";
          stage.host.style.width = project.width + "px";
          stage.host.style.height = project.height + "px";
          if (!active().some(i => i.id === oldActive)) showItem(0);
          else {
            stage.update(project, live);
            for (const card of stage.cards.values()) card.style.display = card.dataset.id === oldActive ? "flex" : "none";
          }
        } else {
          // Preserve animation classes and timers; update text only.
          for (const item of active()) {
            const card = stage.cards.get(item.id);
            if (card) card.querySelector(".overlay-value").textContent = parseValue(item, live[item.file]);
          }
        }
      } catch (_) { /* Keep last known data during brief disconnects. */ }
    }
    if (project) showItem(0); // Embedded exports can show fallbacks even while the bridge is offline.
    poll();
    setInterval(poll, 900);
  }

  window.SL = {Stage, parseValue};
  document.addEventListener("DOMContentLoaded", startOverlay);
})();
