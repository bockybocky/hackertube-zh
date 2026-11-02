const TYPE_ZH = {
  talk: "演講",
  lecture: "課堂講授",
  course: "課程",
  documentary: "紀錄片",
  explainer: "解說",
  interview: "訪談",
  podcast: "播客",
  tutorial: "教學",
  demo: "示範",
  news: "新聞",
  commentary: "評論",
  comedy: "喜劇",
  music: "音樂",
  other: "其他",
};
const LEVEL_ZH = {
  general: "通識",
  intro: "入門",
  intermediate: "中階",
  advanced: "高階",
};

const LS = {
  liked: "htzh_liked",
  later: "htzh_later",
  history: "htzh_history",
  settings: "htzh_settings",
};

const state = {
  videos: [],
  byVid: new Map(),
  similar: [],
  simAt: new Map(),
  cowatch: {},
  tax: { areas: [] },
  catName: new Map(),
  areaOf: new Map(),
  liked: loadList(LS.liked),
  later: loadList(LS.later),
  history: loadList(LS.history),
  settings: loadSettings(),
  shown: 48,
  lastHist: "",
  mentions: new Map(),
};

const view = document.getElementById("view");
const qInput = document.getElementById("q");

function loadList(key) {
  try {
    const v = JSON.parse(localStorage.getItem(key) || "[]");
    return Array.isArray(v) ? v : [];
  } catch (e) {
    return [];
  }
}
function loadSettings() {
  const d = { showNews: false, showZero: false, theme: "auto" };
  try {
    return Object.assign(d, JSON.parse(localStorage.getItem(LS.settings) || "{}"));
  } catch (e) {
    return d;
  }
}
function save(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}
function applyTheme() {
  document.documentElement.dataset.theme = state.settings.theme || "auto";
}

function route() {
  const raw = (location.hash || "#/").replace(/^#/, "");
  const path = raw.startsWith("/") ? raw : "/" + raw;
  const segs = path.split("/").filter(Boolean);
  const head = segs[0] || "home";
  if (head === "watch") return { name: "watch", vid: decodeURIComponent(segs[1] || "") };
  if (head === "c") return { name: "category", id: decodeURIComponent(segs[1] || "") };
  if (head === "a") return { name: "area", id: decodeURIComponent(segs[1] || "") };
  if (["liked", "later", "history", "settings"].includes(head)) return { name: head };
  return { name: "home" };
}

function el(tag, attrs, kids) {
  const n = document.createElement(tag);
  if (attrs) {
    Object.keys(attrs).forEach((k) => {
      if (attrs[k] == null) return;
      if (k === "class") n.className = attrs[k];
      else if (k === "text") n.textContent = attrs[k];
      else n.setAttribute(k, attrs[k]);
    });
  }
  (kids || []).forEach((c) => {
    if (c) n.appendChild(c);
  });
  return n;
}

function typeLabel(id) { return TYPE_ZH[id] || id || "其他"; }
function levelLabel(id) { return LEVEL_ZH[id] || id || "通識"; }

function haystack(v) {
  const names = [];
  (v.categories || []).forEach((id) => {
    names.push(state.catName.get(id) || "");
    const area = state.areaOf.get(id);
    if (area) names.push(area.name);
  });
  return [v.title, v.channel, v.primary_topic, ...(v.tags || []), ...names]
    .join("\n")
    .toLowerCase();
}

function passesHide(v, library) {
  if (library) return true;
  if (v.shelf_life === "news" && !state.settings.showNews) return false;
  if ((v.hn.recommenders || 0) === 0 && !state.settings.showZero) return false;
  return true;
}

function passesQuery(v) {
  const q = qInput.value.trim().toLowerCase();
  if (!q) return true;
  return (v._hay || "").includes(q);
}

function passesSelect(v) {
  const t = document.getElementById("f-type").value;
  const l = document.getElementById("f-level").value;
  if (t && v.content_type !== t) return false;
  if (l && v.level !== l) return false;
  return true;
}

function thumb(vid) {
  return "https://i.ytimg.com/vi/" + vid + "/hq2.jpg";
}

function card(v) {
  const img = el("img", { alt: "", src: thumb(v.vid), loading: "lazy" });
  img.addEventListener("error", () => { img.remove(); });
  const like = el("button", { class: "icon-btn" + (state.liked.includes(v.vid) ? " on" : ""), type: "button", text: "讚" });
  const later = el("button", { class: "icon-btn" + (state.later.includes(v.vid) ? " on" : ""), type: "button", text: "稍後" });
  like.addEventListener("click", (e) => { e.preventDefault(); toggle(state.liked, LS.liked, v.vid); });
  later.addEventListener("click", (e) => { e.preventDefault(); toggle(state.later, LS.later, v.vid); });
  return el("article", { class: "card" }, [
    el("a", { class: "thumb-link", href: "#/watch/" + v.vid }, [img]),
    el("div", { class: "card-body" }, [
      el("a", { class: "card-title", href: "#/watch/" + v.vid, text: v.title || v.vid }),
      el("div", { class: "channel", text: v.channel || "" }),
      el("div", { class: "card-meta" }, [
        el("span", { text: (v.hn.recommenders || 0) + " 人推薦" }),
        el("span", { class: "icon-row" }, [like, later]),
      ]),
    ]),
  ]);
}

function toggle(list, key, vid) {
  const i = list.indexOf(vid);
  if (i >= 0) list.splice(i, 1);
  else list.unshift(vid);
  save(key, list);
  render();
}

function remember(vid) {
  const i = state.history.indexOf(vid);
  if (i >= 0) state.history.splice(i, 1);
  state.history.unshift(vid);
  if (state.history.length > 400) state.history.length = 400;
  save(LS.history, state.history);
}

function listHeader(title, n) {
  return el("div", { class: "page-head" }, [
    el("h1", { text: title }),
    el("div", { class: "count", text: n.toLocaleString("zh-Hant") + " 支" }),
  ]);
}

function renderList(title, items) {
  view.textContent = "";
  view.appendChild(listHeader(title, items.length));
  if (!items.length) {
    view.appendChild(el("p", { class: "empty", text: "沒有符合的影片。" }));
    return;
  }
  const slice = items.slice(0, state.shown);
  const grid = el("div", { class: "grid" });
  slice.forEach((v) => grid.appendChild(card(v)));
  view.appendChild(grid);
  if (slice.length < items.length) {
    const btn = el("button", { class: "text-btn", type: "button", text: "載入更多" });
    btn.addEventListener("click", () => {
      state.shown += 48;
      render();
    });
    view.appendChild(el("div", { class: "more-wrap" }, [btn]));
  }
}

function currentItems(r) {
  const pinnedCat = state.tax.areas.some((a) => a.featured &&
    ((r.name === "area" && a.id === r.id) || (r.name === "category" && a.categories.some((c) => c.id === r.id))));
  const library = pinnedCat || r.name === "liked" || r.name === "later" || r.name === "history";
  let pool = state.videos;
  if (r.name === "category") pool = pool.filter((v) => (v.categories || []).includes(r.id));
  if (r.name === "area") {
    const area = state.tax.areas.find((a) => a.id === r.id);
    const ids = new Set((area ? area.categories : []).map((c) => c.id));
    pool = pool.filter((v) => (v.categories || []).some((id) => ids.has(id)));
  }
  if (r.name === "liked") pool = state.liked.map((id) => state.byVid.get(id)).filter(Boolean);
  if (r.name === "later") pool = state.later.map((id) => state.byVid.get(id)).filter(Boolean);
  if (r.name === "history") pool = state.history.map((id) => state.byVid.get(id)).filter(Boolean);
  return pool.filter((v) => passesHide(v, library) && passesQuery(v) && passesSelect(v));
}

function titleFor(r) {
  if (r.name === "home") return "全部影片";
  if (r.name === "liked") return "已按讚";
  if (r.name === "later") return "稍後觀看";
  if (r.name === "history") return "觀看紀錄";
  if (r.name === "category") return state.catName.get(r.id) || r.id;
  if (r.name === "area") {
    const area = state.tax.areas.find((a) => a.id === r.id);
    return area ? area.name : r.id;
  }
  return "黑客影片";
}

function mini(v) {
  const img = el("img", { alt: "", src: thumb(v.vid), loading: "lazy" });
  img.addEventListener("error", () => { img.remove(); });
  return el("a", { class: "mini", href: "#/watch/" + v.vid }, [
    img,
    el("span", { text: v.title || v.vid }),
  ]);
}

function rail(titleText, vids) {
  const items = vids.map((id) => state.byVid.get(id)).filter(Boolean);
  if (!items.length) return null;
  const box = el("div");
  box.appendChild(el("h2", { text: titleText }));
  const g = el("div", { class: "rail" });
  items.forEach((v) => g.appendChild(mini(v)));
  box.appendChild(g);
  return box;
}

async function loadMentions(vid) {
  const shard = vid.charAt(0).toLowerCase();
  if (!state.mentions.has(shard)) {
    try {
      const res = await fetch("data/m/" + encodeURIComponent(shard) + ".json");
      state.mentions.set(shard, res.ok ? await res.json() : {});
    } catch (e) {
      state.mentions.set(shard, {});
    }
  }
  return state.mentions.get(shard)[vid] || [];
}

async function renderWatch(vid) {
  const v = state.byVid.get(vid);
  view.textContent = "";
  if (!v) {
    view.appendChild(el("p", { class: "empty", text: "找不到這支影片。" }));
    return;
  }
  if (state.lastHist !== vid) {
    state.lastHist = vid;
    remember(vid);
    markNav();
  }
  const okVid = /^[\w-]{11}$/.test(vid);
  const frame = el("iframe", {
    title: v.title || vid,
    src: okVid ? "https://www.youtube-nocookie.com/embed/" + vid : "",
    allow: "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture",
    allowfullscreen: "true",
  });
  const like = el("button", { class: "text-btn" + (state.liked.includes(vid) ? " on" : ""), type: "button", text: state.liked.includes(vid) ? "已按讚" : "按讚" });
  const later = el("button", { class: "text-btn" + (state.later.includes(vid) ? " on" : ""), type: "button", text: state.later.includes(vid) ? "已加入稍後觀看" : "稍後觀看" });
  like.addEventListener("click", () => toggle(state.liked, LS.liked, vid));
  later.addEventListener("click", () => toggle(state.later, LS.later, vid));
  const years = [v.hn.first_year, v.hn.last_year].filter(Boolean).join("–");
  const chips = el("div", { class: "chips" });
  (v.categories || []).forEach((id) => {
    chips.appendChild(el("a", { class: "chip", href: "#/c/" + id, text: state.catName.get(id) || id }));
  });
  (v.tags || []).forEach((t) => chips.appendChild(el("span", { class: "chip", text: t })));
  const box = el("article", { class: "watch" }, [
    el("div", { class: "player" }, [frame]),
    el("h1", { text: v.title || vid }),
    el("div", { class: "channel", text: v.channel || "" }),
    el("div", { class: "count", text: (v.hn.recommenders || 0) + " 人推薦 · 分數 " + v.score + (years ? " · " + years : "") + " · " + typeLabel(v.content_type) + " · " + levelLabel(v.level) }),
    el("div", { class: "watch-actions" }, [like, later]),
  ]);
  const prose = el("div", { class: "prose" });
  if (v.summary) {
    prose.appendChild(el("h2", { text: "摘要" }));
    prose.appendChild(el("p", { text: v.summary }));
  }
  if (v.why_hn) {
    prose.appendChild(el("h2", { text: "為什麼 Hacker News 推薦它" }));
    prose.appendChild(el("p", { text: v.why_hn }));
  }
  if (v.quote && v.quote.text) {
    prose.appendChild(el("h2", { text: "金句" }));
    const q = el("blockquote", { class: "quote", text: v.quote.text });
    prose.appendChild(q);
    if (v.quote.year) prose.appendChild(el("div", { class: "who", text: String(v.quote.year) }));
  }
  if (v.primary_topic) {
    prose.appendChild(el("h2", { text: "主題" }));
    prose.appendChild(el("p", { text: v.primary_topic }));
  }
  prose.appendChild(chips);
  prose.appendChild(el("h2", { text: "推薦留言" }));
  const mbox = el("div", { id: "mentions" }, [el("p", { class: "note", text: "載入留言…" })]);
  prose.appendChild(mbox);
  const sim = state.simAt.get(vid) || [];
  const simNode = rail("相似影片", sim);
  const coNode = rail("同一群人也推薦", state.cowatch[vid] || []);
  if (simNode) prose.appendChild(simNode);
  if (coNode) prose.appendChild(coNode);
  box.appendChild(prose);
  view.appendChild(box);
  const rows = await loadMentions(vid);
  if (route().name !== "watch" || route().vid !== vid) return;
  mbox.textContent = "";
  if (!rows.length) {
    mbox.appendChild(el("p", { class: "note", text: "這支影片沒有收錄推薦留言。" }));
    return;
  }
  rows.forEach((m) => {
    const who = el("div", { class: "who" });
    who.appendChild(document.createTextNode((m.author || "匿名") + (m.month ? " · " + m.month : "") + " · "));
    if (m.hn_url && m.hn_url.startsWith("https://")) {
      who.appendChild(el("a", { href: m.hn_url, target: "_blank", rel: "noopener", text: "原留言" }));
    }
    mbox.appendChild(el("div", { class: "mention" }, [
      who,
      el("p", { text: m.quote || "" }),
    ]));
  });
}

function renderSettings() {
  view.textContent = "";
  view.appendChild(el("div", { class: "page-head" }, [el("h1", { text: "設定" })]));
  const form = el("div", { class: "settings" });
  const news = el("input", { type: "checkbox", id: "opt-news" });
  news.checked = !!state.settings.showNews;
  const zero = el("input", { type: "checkbox", id: "opt-zero" });
  zero.checked = !!state.settings.showZero;
  news.addEventListener("change", () => {
    state.settings.showNews = news.checked;
    save(LS.settings, state.settings);
  });
  zero.addEventListener("change", () => {
    state.settings.showZero = zero.checked;
    save(LS.settings, state.settings);
  });
  form.appendChild(el("label", null, [news, document.createTextNode("顯示時效僅限當下的新聞影片")]));
  form.appendChild(el("label", null, [zero, document.createTextNode("顯示沒有人推薦、只被引用的影片")]));
  form.appendChild(el("p", { class: "note", text: "這兩類預設隱藏。已按讚、稍後觀看、觀看紀錄仍會顯示你存過的影片。" }));
  const theme = el("select", { id: "opt-theme" });
  [["auto", "跟隨系統"], ["light", "淺色"], ["dark", "深色"]].forEach(([val, label]) => {
    const o = el("option", { value: val, text: label });
    if ((state.settings.theme || "auto") === val) o.selected = true;
    theme.appendChild(o);
  });
  theme.addEventListener("change", () => {
    state.settings.theme = theme.value;
    save(LS.settings, state.settings);
    applyTheme();
  });
  const themeLabel = el("label", null, [document.createTextNode("外觀"), theme]);
  form.appendChild(themeLabel);
  view.appendChild(form);
}

function markNav() {
  const r = route();
  document.querySelectorAll("#nav button").forEach((b) => {
    b.classList.toggle("active", b.dataset.route === r.name);
  });
  document.querySelectorAll(".cat-link").forEach((a) => {
    a.classList.toggle("active", r.name === "category" && a.dataset.id === r.id);
  });
  if (r.name === "category") {
    const area = state.areaOf.get(r.id);
    if (area) {
      const node = document.querySelector('.area[data-id="' + area.id + '"]');
      if (node) node.classList.add("open");
    }
  }
}

function render() {
  const r = route();
  markNav();
  const onList = r.name !== "watch" && r.name !== "settings";
  document.getElementById("top").style.display = onList ? "" : "none";
  if (r.name === "settings") return renderSettings();
  if (r.name === "watch") return renderWatch(r.vid);
  renderList(titleFor(r), currentItems(r));
}

function buildNav() {
  const nav = document.getElementById("nav");
  const items = [
    ["home", "首頁"],
    ["liked", "已按讚"],
    ["later", "稍後觀看"],
    ["history", "觀看紀錄"],
    ["settings", "設定"],
  ];
  items.forEach(([name, label]) => {
    const b = el("button", { type: "button", text: label });
    b.dataset.route = name;
    b.addEventListener("click", () => {
      state.shown = 48;
      location.hash = name === "home" ? "#/" : "#/" + name;
      document.getElementById("side").classList.remove("open");
    });
    nav.appendChild(b);
  });
  const tree = document.getElementById("tree");
  const label = el("div", { class: "brand-sub", text: "分類" });
  tree.appendChild(label);
  state.tax.areas.forEach((area) => {
    const wrap = el("div", { class: "area" + (area.featured ? " featured open" : "") });
    wrap.dataset.id = area.id;
    const btn = el("button", { class: "area-btn", type: "button", text: area.name });
    const ul = el("ul");
    btn.addEventListener("click", () => wrap.classList.toggle("open"));
    area.categories.forEach((c) => {
      const a = el("a", { class: "cat-link", href: "#/c/" + c.id, text: c.name });
      a.dataset.id = c.id;
      a.addEventListener("click", () => {
        state.shown = 48;
        document.getElementById("side").classList.remove("open");
      });
      ul.appendChild(el("li", null, [a]));
    });
    wrap.appendChild(btn);
    wrap.appendChild(ul);
    tree.appendChild(wrap);
  });
}

function fillFilters() {
  const typeSel = document.getElementById("f-type");
  const levelSel = document.getElementById("f-level");
  Object.keys(TYPE_ZH).forEach((k) => typeSel.appendChild(el("option", { value: k, text: TYPE_ZH[k] })));
  Object.keys(LEVEL_ZH).forEach((k) => levelSel.appendChild(el("option", { value: k, text: LEVEL_ZH[k] })));
  const reset = () => { state.shown = 48; render(); };
  typeSel.addEventListener("change", reset);
  levelSel.addEventListener("change", reset);
  qInput.addEventListener("input", reset);
}

async function boot() {
  applyTheme();
  view.appendChild(el("p", { class: "note", text: "載入片單…" }));
  try {
    const [videos, similar, cowatch, tax] = await Promise.all([
      fetch("data/videos.json").then((r) => r.json()),
      fetch("data/similar.json").then((r) => r.json()),
      fetch("data/cowatch.json").then((r) => r.json()),
      fetch("data/taxonomy.json").then((r) => r.json()),
    ]);
    state.videos = videos;
    state.similar = similar;
    state.cowatch = cowatch;
    state.tax = tax;
    videos.forEach((v, i) => {
      state.byVid.set(v.vid, v);
      state.simAt.set(v.vid, similar[i] || []);
    });
    tax.areas.forEach((area) => {
      area.categories.forEach((c) => {
        state.catName.set(c.id, c.name);
        state.areaOf.set(c.id, area);
      });
    });
    videos.forEach((v) => { v._hay = haystack(v); });
    buildNav();
    fillFilters();
    render();
  } catch (e) {
    view.textContent = "";
    view.appendChild(el("p", { class: "empty", text: "資料載入失敗。請在專案根目錄執行 python build_data.py，再用本機伺服器開啟 site/。" }));
  }
}

function setMenu(open) {
  document.getElementById("side").classList.toggle("open", open);
  document.body.classList.toggle("menu-open", open);
}
document.getElementById("menu-btn").addEventListener("click", () => {
  setMenu(!document.getElementById("side").classList.contains("open"));
});
document.getElementById("scrim").addEventListener("click", () => setMenu(false));
document.getElementById("side").addEventListener("click", (e) => {
  if (e.target.closest('a[href^="#"], #nav button')) setMenu(false);
});
window.addEventListener("hashchange", () => {
  setMenu(false);
  state.shown = 48;
  render();
});
boot();
