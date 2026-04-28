/* =========================================================
   Figma → dmbUi Agent — UI logic (vanilla JS, no deps)
   ========================================================= */

const API = "/api/v1";

/* ----- DOM helpers ----- */
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === "class") node.className = v;
    else if (k === "html") node.innerHTML = v;
    else if (k.startsWith("on") && typeof v === "function") {
      node.addEventListener(k.slice(2).toLowerCase(), v);
    } else if (k === "dataset") {
      for (const [dk, dv] of Object.entries(v)) node.dataset[dk] = dv;
    } else {
      node.setAttribute(k, v);
    }
  }
  for (const c of children.flat()) {
    if (c == null || c === false) continue;
    node.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return node;
}

/* ----- LocalStorage prefs ----- */
const Prefs = {
  KEY: "figma-dmb-ui-prefs.v1",
  load() {
    try { return JSON.parse(localStorage.getItem(this.KEY) || "{}"); }
    catch { return {}; }
  },
  save(patch) {
    const cur = this.load();
    const next = { ...cur, ...patch };
    try { localStorage.setItem(this.KEY, JSON.stringify(next)); } catch {}
    return next;
  },
};

/* ----- Toast ----- */
function toast(message, type = "ok", title) {
  const t = $("#toast");
  t.className = "toast toast--" + (type === "err" ? "err" : "ok");
  t.innerHTML = "";
  t.append(
    el("div", { class: "row", style: "flex-direction:column; align-items:flex-start;" },
      title && el("div", { class: "toast__title" }, title),
      el("div", { class: "toast__msg" }, message),
    )
  );
  t.classList.remove("hidden");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => t.classList.add("hidden"), 4000);
}

/* ----- API helper ----- */
async function api(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!res.ok) {
    const detail = (data && (data.detail || data.message)) || res.statusText;
    throw new Error(`${res.status} — ${detail}`);
  }
  return data;
}

/* ----- Tabs ----- */
function bindTabs() {
  $$(".tab").forEach(btn => btn.addEventListener("click", () => {
    const name = btn.dataset.tab;
    $$(".tab").forEach(b => b.classList.toggle("is-active", b === btn));
    $$("[data-tabpane]").forEach(p =>
      p.classList.toggle("hidden", p.dataset.tabpane !== name)
    );
    Prefs.save({ tab: name });
  }));
  // restore
  const tab = Prefs.load().tab || "components";
  const btn = $(`.tab[data-tab="${tab}"]`);
  if (btn) btn.click();
}

/* ----- Catalog UI ----- */
async function refreshCatalog() {
  try {
    const items = await api("/catalog/components");
    $("#catalog-count").textContent = items.length;
    $("#catalog-status").textContent = items.length
      ? `${items.length} componenti pronti per il match`
      : "Catalogo vuoto. Avvia il bootstrap o aggiungi a mano.";
  } catch (e) { toast(e.message, "err", "Errore catalogo"); }
}

async function bootstrapCatalog(mode) {
  const btn = mode === "merge" ? $("#btn-bootstrap-merge") : $("#btn-bootstrap-replace");
  const original = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Sto importando…";
  Progress.show("Lettura sorgente Kotlin…");
  Progress.phase("fetch", "Parsing dello showcaseUi.kt");
  try {
    const r = await api("/catalog/components/bootstrap", {
      method: "POST",
      body: JSON.stringify({ mode }),
    });
    Progress.done(true,
      `Catalogo aggiornato: +${r.created.length} nuovi, ~${r.updated.length} aggiornati`
    );
    toast(`+${r.created.length} nuovi · ~${r.updated.length} aggiornati`, "ok", "Bootstrap completato");
    refreshCatalog();
  } catch (e) {
    Progress.done(false, e.message);
    toast(e.message, "err", "Bootstrap fallito");
  } finally {
    btn.disabled = false;
    btn.textContent = original;
  }
}

async function createCatalogComponent() {
  const name = $("#new-name").value.trim();
  if (!name) return toast("Inserisci il nome canonico", "err");
  const aliases = $("#new-aliases").value.split(",").map(s => s.trim()).filter(Boolean);
  const tags = $("#new-tags").value.split(",").map(s => s.trim()).filter(Boolean);
  try {
    await api("/catalog/components", {
      method: "POST",
      body: JSON.stringify({ name, aliases, tags, properties: [] }),
    });
    toast(name, "ok", "Componente creato");
    $("#new-name").value = $("#new-aliases").value = $("#new-tags").value = "";
    refreshCatalog();
  } catch (e) { toast(e.message, "err"); }
}

/* ----- Progress card with phases ----- */
const Progress = (() => {
  const PHASES = ["fetch", "extract", "match", "done"];
  let timer = null;
  let start = 0;

  const show = (msg = "Avvio…") => {
    $("#progress-card").classList.remove("hidden");
    $("#progress-msg").textContent = msg;
    $("#progress-elapsed").textContent = "0.0s";
    $("#progress-bar").classList.add("is-indet");
    $("#progress-bar > span").style.width = "0%";
    $$(".phase").forEach(p => p.classList.remove("is-active", "is-done", "is-error"));
    start = performance.now();
    clearInterval(timer);
    timer = setInterval(() => {
      const s = (performance.now() - start) / 1000;
      $("#progress-elapsed").textContent = s.toFixed(1) + "s";
    }, 100);
  };
  const phase = (name, msg) => {
    const idx = PHASES.indexOf(name);
    $$(".phase").forEach(p => {
      const i = PHASES.indexOf(p.dataset.phase);
      p.classList.toggle("is-done", i >= 0 && i < idx);
      p.classList.toggle("is-active", p.dataset.phase === name);
    });
    if (msg) $("#progress-msg").textContent = msg;
    if (idx >= 1) {
      $("#progress-bar").classList.remove("is-indet");
      $("#progress-bar > span").style.width = ((idx + 1) / PHASES.length * 100) + "%";
    }
  };
  const done = (success, msg) => {
    clearInterval(timer);
    if (success) {
      phase("done", msg || "Fatto.");
      $("#progress-bar").classList.remove("is-indet");
      $("#progress-bar > span").style.width = "100%";
    } else {
      $$(".phase.is-active").forEach(p => p.classList.replace("is-active", "is-error"));
      $("#progress-msg").textContent = msg || "Errore.";
      $("#progress-bar").classList.remove("is-indet");
    }
    setTimeout(() => $("#progress-card").classList.add("hidden"), success ? 1500 : 4500);
  };
  return { show, phase, done };
})();

/* ----- SSE consumer for /figma/components/stream ----- */
async function analyzeComponentsStream(payload) {
  Progress.show("Contatto Figma…");
  Progress.phase("fetch", "Contatto Figma…");

  const res = await fetch(API + "/figma/components/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json", "Accept": "text/event-stream" },
    body: JSON.stringify(payload),
  });
  if (!res.ok || !res.body) {
    const txt = await res.text();
    throw new Error(`${res.status} — ${txt || res.statusText}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let result = null;
  let errorMsg = null;

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let idx;
    while ((idx = buffer.indexOf("\n\n")) >= 0) {
      const raw = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      let event = "message";
      const dataLines = [];
      for (const line of raw.split("\n")) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
      }
      let data = null;
      try { data = JSON.parse(dataLines.join("\n")); } catch { data = dataLines.join("\n"); }

      if (event === "phase") Progress.phase(data.phase, data.message);
      else if (event === "progress" && data.total) {
        const pct = Math.min(100, Math.round((data.current / data.total) * 100));
        $("#progress-bar").classList.remove("is-indet");
        $("#progress-bar > span").style.width = pct + "%";
      }
      else if (event === "result") result = data;
      else if (event === "error") errorMsg = data.message || "errore sconosciuto";
    }
  }
  if (errorMsg) throw new Error(errorMsg);
  if (!result) throw new Error("Il server non ha restituito un risultato");
  return result;
}

/* ----- Render helpers ----- */
function payloadFromForm() {
  return {
    figma_url: $("#figma-url").value.trim(),
    use_node_id: $("#use-node-id").checked,
    confidence_threshold: parseFloat($("#threshold").value || "0.6"),
    include_unmatched: $("#include-unmatched").checked,
    only_instances: $("#only-instances").checked,
  };
}

function setBusy(busy) {
  ["#btn-analyze-components", "#btn-analyze-styles"].forEach(s => $(s).disabled = busy);
}

function confidenceClass(c) {
  if (c >= 0.85) return "confidence--high";
  if (c >= 0.6) return "confidence--med";
  return "confidence--low";
}

function renderConfidence(c) {
  if (c == null) return el("span", { class: "muted" }, "—");
  const wrap = el("span", { class: `confidence ${confidenceClass(c)}` });
  const bar = el("span", { class: "confidence__bar" }, el("span", { style: `width:${Math.round(c * 100)}%` }));
  wrap.append(bar, el("span", {}, c.toFixed(2)));
  return wrap;
}

/* ----- Components results ----- */
let LAST_RESULT = null;

const ResultsState = {
  filter: "all", // all | matched | unmatched
  query: "",
  groupBy: "none", // none | name
};

function applyFilters(items) {
  const q = ResultsState.query.toLowerCase().trim();
  return items.filter(m => {
    const e = m.extracted;
    if (ResultsState.filter === "matched" && !m.matched) return false;
    if (ResultsState.filter === "unmatched" && m.matched) return false;
    if (!q) return true;
    return (
      e.figma_name.toLowerCase().includes(q) ||
      (e.text_content || "").toLowerCase().includes(q) ||
      (m.best_match && m.best_match.dmbui_name.toLowerCase().includes(q))
    );
  });
}

function renderComponents(data) {
  LAST_RESULT = data;

  // stats
  const stats = $("#components-stats");
  stats.innerHTML = "";
  stats.append(
    el("span", { class: "pill" }, "File ", el("strong", {}, data.file_key || "—")),
    el("span", { class: "pill pill--success" }, el("strong", {}, String(data.matched_count)), " matched"),
    el("span", { class: "pill pill--warning" }, el("strong", {}, String(data.unmatched_count)), " da mappare"),
    el("span", { class: "pill pill--info" }, "Totale ", el("strong", {}, String(data.total_extracted))),
  );

  // raw
  $("#raw-json").textContent = JSON.stringify(data, null, 2);

  redrawTable();
}

function redrawTable() {
  const data = LAST_RESULT;
  const tbody = $("#components-table tbody");
  tbody.innerHTML = "";
  if (!data || !data.components) {
    showEmpty("components-empty", true);
    $("#components-table-wrap").classList.add("hidden");
    return;
  }
  const filtered = applyFilters(data.components);
  $("#filtered-count").textContent = filtered.length === data.components.length
    ? `${data.components.length} elementi`
    : `${filtered.length} di ${data.components.length}`;

  if (!filtered.length) {
    showEmpty("components-empty", true, "Nessun risultato per i filtri attuali.");
    $("#components-table-wrap").classList.add("hidden");
    return;
  }
  showEmpty("components-empty", false);
  $("#components-table-wrap").classList.remove("hidden");

  // Optionally group by figma_name
  if (ResultsState.groupBy === "name") {
    const groups = new Map();
    for (const m of filtered) {
      const key = m.extracted.figma_name || "—";
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(m);
    }
    for (const [name, list] of [...groups.entries()].sort((a, b) => b[1].length - a[1].length)) {
      const sample = list[0];
      tbody.append(buildRow(sample, list.length));
    }
  } else {
    for (const m of filtered) tbody.append(buildRow(m, 1));
  }
}

function buildRow(m, occurrences) {
  const e = m.extracted;
  const matchCell = m.matched && m.best_match
    ? el("span", { class: "badge badge--ok" }, m.best_match.dmbui_name)
    : el("span", { class: "badge badge--warn" }, "da mappare");

  const propBits = [];
  if (Object.keys(e.variants || {}).length) {
    propBits.push(el("div", { class: "kv" },
      el("span", { class: "k" }, "variants"),
      el("span", { class: "v" }, JSON.stringify(e.variants))
    ));
  }
  if (Object.keys(e.properties || {}).length) {
    propBits.push(el("div", { class: "kv" },
      el("span", { class: "k" }, "properties"),
      el("span", { class: "v" }, JSON.stringify(e.properties))
    ));
  }
  if (e.text_content) {
    propBits.push(el("div", { class: "kv" },
      el("span", { class: "k" }, "text"),
      el("span", { class: "v" }, e.text_content)
    ));
  }
  if (occurrences > 1) {
    propBits.unshift(el("div", { class: "kv" },
      el("span", { class: "k" }, "occorrenze"),
      el("span", { class: "v" }, "× " + occurrences)
    ));
  }

  // Suggestions chips when unmatched
  const suggBox = el("div");
  if (!m.matched && (m.suggestions || []).length) {
    const ul = el("ul", { class: "suggest-list" });
    for (const s of m.suggestions) {
      ul.append(el("li", { class: "chip" },
        el("code", {}, s.dmbui_name),
        " · " + s.confidence.toFixed(2)
      ));
    }
    suggBox.append(ul);
  }

  // Actions
  const actions = el("div", { class: "btn-group" });
  if (!m.matched) {
    const select = el("select", { class: "input", style: "max-width:220px" });
    select.append(el("option", { value: "" }, "— mappa su…"));
    for (const s of (m.suggestions || [])) {
      select.append(el("option", { value: s.dmbui_name },
        `${s.dmbui_name} (${s.confidence.toFixed(2)})`
      ));
    }
    const customInput = el("input", {
      class: "input", type: "text",
      placeholder: "o digita nome dmbUi", style: "max-width:200px"
    });
    const btn = el("button", { class: "btn btn--primary btn--sm" }, "Conferma");
    btn.addEventListener("click", async () => {
      const name = (customInput.value || select.value || "").trim();
      if (!name) return toast("Scegli o digita un nome dmbUi", "err");
      try {
        await api(`/catalog/components/${encodeURIComponent(name)}/aliases`, {
          method: "POST",
          body: JSON.stringify({ alias: e.figma_name }),
        });
        toast(`${e.figma_name} → ${name}`, "ok", "Mapping salvato");
        btn.disabled = true;
        btn.textContent = "Salvato";
      } catch (err) {
        toast(err.message, "err");
      }
    });
    actions.append(select, customInput, btn);
  } else {
    actions.append(el("span", { class: "muted" }, "—"));
  }

  return el("tr", {},
    el("td", {},
      el("div", { class: "row", style: "gap:8px" },
        el("code", {}, e.figma_name || "(unnamed)"),
      ),
      suggBox,
    ),
    el("td", {}, el("span", { class: "badge" }, e.figma_type)),
    el("td", {}, matchCell),
    el("td", {}, renderConfidence(m.best_match ? m.best_match.confidence : null)),
    el("td", {}, ...propBits),
    el("td", {}, actions),
  );
}

function showEmpty(id, show, message) {
  const node = $("#" + id);
  if (!node) return;
  node.classList.toggle("hidden", !show);
  if (show && message) node.querySelector(".empty-msg").textContent = message;
}

/* ----- Styles tab ----- */
function renderStyles(data) {
  const grid = $("#colors-grid");
  grid.innerHTML = "";
  if (!data.colors || !data.colors.length) {
    grid.append(el("span", { class: "muted" }, "Nessun colore."));
  }
  for (const c of (data.colors || [])) {
    grid.append(el("span", { class: "swatch", title: c.hex },
      el("span", { class: "swatch__chip", style: `background:${c.hex}` }),
      el("code", {}, c.hex),
    ));
  }
  const tbody = $("#styles-table tbody");
  tbody.innerHTML = "";
  for (const s of (data.text_styles || [])) {
    tbody.append(el("tr", {},
      el("td", {}, s.font_family || "—"),
      el("td", {}, String(s.font_size ?? "—")),
      el("td", {}, String(s.font_weight ?? "—")),
      el("td", {}, String(s.line_height_px ?? "—")),
      el("td", {}, String(s.letter_spacing ?? "—")),
    ));
  }
  $("#styles-empty").classList.toggle("hidden", (data.colors || []).length || (data.text_styles || []).length);
  $("#styles-content").classList.toggle("hidden", !((data.colors || []).length || (data.text_styles || []).length));
  $("#raw-json").textContent = JSON.stringify(data, null, 2);
}

/* ----- Whoami quick check ----- */
async function checkToken() {
  const status = $("#token-status");
  status.textContent = "Verifica…";
  status.className = "pill";
  try {
    const me = await api("/figma/whoami");
    status.textContent = `Token OK · ${me.handle || me.email || "user"}`;
    status.className = "pill pill--success";
  } catch (e) {
    status.textContent = "Token non valido";
    status.className = "pill pill--danger";
  }
}

/* ----- Boot ----- */
function init() {
  bindTabs();

  // Restore prefs
  const p = Prefs.load();
  if (p.figmaUrl) $("#figma-url").value = p.figmaUrl;
  if (typeof p.useNodeId === "boolean") $("#use-node-id").checked = p.useNodeId;
  if (typeof p.threshold === "number") $("#threshold").value = p.threshold;

  ["figma-url", "threshold", "use-node-id", "include-unmatched", "only-instances"]
    .forEach(id => $("#" + id).addEventListener("change", () => {
      Prefs.save({
        figmaUrl: $("#figma-url").value,
        useNodeId: $("#use-node-id").checked,
        threshold: parseFloat($("#threshold").value || "0.6"),
      });
    }));

  // Catalog
  $("#btn-refresh-catalog").addEventListener("click", refreshCatalog);
  $("#btn-bootstrap-merge").addEventListener("click", () => bootstrapCatalog("merge"));
  $("#btn-bootstrap-replace").addEventListener("click", () => bootstrapCatalog("replace"));
  $("#btn-create-component").addEventListener("click", createCatalogComponent);

  // Analyze
  $("#btn-analyze-components").addEventListener("click", async () => {
    const p = payloadFromForm();
    if (!p.figma_url) return toast("Inserisci l'URL Figma", "err");
    setBusy(true);
    try {
      const data = await analyzeComponentsStream(p);
      renderComponents(data);
      $$(".tab[data-tab='components']")[0].click();
      Progress.done(true, `Analisi completata: ${data.matched_count}/${data.total_extracted} matchati`);
      toast(`${data.matched_count}/${data.total_extracted} matchati`, "ok", "Analisi completata");
    } catch (e) {
      Progress.done(false, e.message);
      toast(e.message, "err", "Errore analisi");
    } finally { setBusy(false); }
  });

  $("#btn-analyze-styles").addEventListener("click", async () => {
    const p = payloadFromForm();
    if (!p.figma_url) return toast("Inserisci l'URL Figma", "err");
    setBusy(true);
    Progress.show("Estraggo stili…");
    Progress.phase("fetch", "Contatto Figma…");
    try {
      const data = await api("/figma/analyze", {
        method: "POST",
        body: JSON.stringify({ figma_url: p.figma_url, use_node_id: p.use_node_id }),
      });
      renderStyles(data);
      $$(".tab[data-tab='styles']")[0].click();
      Progress.done(true,
        `${(data.colors || []).length} colori · ${(data.text_styles || []).length} text styles`
      );
    } catch (e) {
      Progress.done(false, e.message);
      toast(e.message, "err");
    } finally { setBusy(false); }
  });

  // Result filters
  $("#search").addEventListener("input", (e) => {
    ResultsState.query = e.target.value;
    redrawTable();
  });
  $("#filter-status").addEventListener("change", (e) => {
    ResultsState.filter = e.target.value;
    redrawTable();
  });
  $("#group-by").addEventListener("change", (e) => {
    ResultsState.groupBy = e.target.value;
    redrawTable();
  });

  $("#btn-check-token").addEventListener("click", checkToken);

  refreshCatalog();
  checkToken();
}

document.addEventListener("DOMContentLoaded", init);

