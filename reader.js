/* reader.js -- highlights, notes, reading position and display settings for the
   Wilson–Cowan book.  Everything is kept in this browser (localStorage, key "wcbook.v1");
   nothing is sent anywhere.  Highlights are anchored by their text (plus a little text
   before and after), so they survive small changes to the book. */
(function () {
  "use strict";
  var KEY = "wcbook.v1";
  var COLORS = [["yellow", "Yellow"], ["green", "Green"], ["blue", "Blue"], ["pink", "Pink"], ["purple", "Purple"]];
  var CTX = 40;
  var root = document.querySelector("main");
  if (!root) return;

  // ---- storage -----------------------------------------------------------------------
  function load() {
    var s = null;
    try { s = JSON.parse(localStorage.getItem(KEY)); } catch (e) {}
    s = s || {};
    s.highlights = s.highlights || [];
    s.prefs = s.prefs || {};
    s.decks = s.decks || {};
    return s;
  }
  var state = load();
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
  }
  function pref(k, d) { return state.prefs[k] === undefined ? d : state.prefs[k]; }

  // ---- a text index of <main>: visible text nodes and their offsets --------------------
  var index = null;
  function skip(n) {
    for (var p = n.parentNode; p && p !== root; p = p.parentNode) {
      if (p.nodeType !== 1) continue;
      var t = p.tagName;
      if (t === "SCRIPT" || t === "STYLE" || t === "NOSCRIPT") return true;
      if (p.classList && (p.classList.contains("katex-mathml") || p.classList.contains("hl-ui"))) return true;
    }
    return false;
  }
  function build() {
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var nodes = [], parts = [], pos = 0, n;
    while ((n = w.nextNode())) {
      if (skip(n)) continue;
      nodes.push({ n: n, s: pos });
      parts.push(n.data);
      pos += n.data.length;
    }
    index = { nodes: nodes, text: parts.join("") };
    return index;
  }
  function idx() { return index || build(); }

  // global offset of a boundary point (container, offset)
  function offsetOf(c, o) {
    var I = idx();
    if (c.nodeType === 3) {
      for (var i = 0; i < I.nodes.length; i++) if (I.nodes[i].n === c) return I.nodes[i].s + o;
    }
    var r = document.createRange();
    try { r.setStart(c, o); } catch (e) { return -1; }
    for (var j = 0; j < I.nodes.length; j++) {
      if (r.comparePoint(I.nodes[j].n, 0) >= 0) return I.nodes[j].s;
    }
    return I.text.length;
  }

  function chapterAt(node) {
    for (var p = node; p && p !== root; p = p.parentNode) {
      if (p.nodeType === 1 && p.tagName === "SECTION" && p.id) return p.id;
    }
    return "";
  }
  function sectionAt(node) {
    // the nearest h2 with an id before this node
    var hs = root.querySelectorAll("h2[id], section[id]"), best = null;
    for (var i = 0; i < hs.length; i++) {
      if (hs[i].compareDocumentPosition(node) & Node.DOCUMENT_POSITION_FOLLOWING) best = hs[i];
      else if (!hs[i].contains(node)) break;
    }
    return best ? best.id : "";
  }

  // ---- wrap / unwrap ---------------------------------------------------------------------
  var BLOCKY = /^(TABLE|TBODY|THEAD|TR|UL|OL|DL|SECTION|MAIN|NAV|FIGURE|DIV|HEADER)$/;
  function wrap(a, b, h) {
    var I = idx(), first = null;
    for (var i = 0; i < I.nodes.length; i++) {
      var e = I.nodes[i], len = e.n.data.length, s = e.s;
      if (s + len <= a || s >= b) continue;
      var from = Math.max(a - s, 0), to = Math.min(b - s, len);
      if (from >= to) continue;
      var t = e.n;
      if (!/\S/.test(t.data.slice(from, to)) && BLOCKY.test(t.parentNode.tagName)) continue;
      if (to < len) t.splitText(to);
      if (from > 0) t = t.splitText(from);
      var m = document.createElement("mark");
      m.className = "hl hl-" + h.color + (h.note ? " hl-has-note" : "");
      m.setAttribute("data-hid", h.id);
      if (h.note) m.title = h.note;
      t.parentNode.insertBefore(m, t);
      m.appendChild(t);
      if (!first) first = m;
    }
    index = null;
    return first;
  }
  function unwrap(id) {
    var ms = root.querySelectorAll('mark[data-hid="' + id + '"]');
    for (var i = 0; i < ms.length; i++) {
      var m = ms[i], p = m.parentNode;
      while (m.firstChild) p.insertBefore(m.firstChild, m);
      p.removeChild(m);
      p.normalize();
    }
    index = null;
  }
  function restyle(h) {
    var ms = root.querySelectorAll('mark[data-hid="' + h.id + '"]');
    for (var i = 0; i < ms.length; i++) {
      ms[i].className = "hl hl-" + h.color + (h.note ? " hl-has-note" : "");
      if (h.note) ms[i].title = h.note; else ms[i].removeAttribute("title");
    }
  }

  // ---- find a stored highlight in the current text ---------------------------------------
  function score(text, at, h) {
    var sc = 0, i;
    var pre = text.slice(Math.max(0, at - h.prefix.length), at);
    var suf = text.slice(at + h.exact.length, at + h.exact.length + h.suffix.length);
    for (i = 1; i <= Math.min(pre.length, h.prefix.length); i++) {
      if (pre[pre.length - i] === h.prefix[h.prefix.length - i]) sc++; else break;
    }
    for (i = 0; i < Math.min(suf.length, h.suffix.length); i++) {
      if (suf[i] === h.suffix[i]) sc++; else break;
    }
    return sc;
  }
  function locate(h) {
    var text = idx().text, best = -1, bsc = -1, at = text.indexOf(h.exact);
    while (at !== -1) {
      var sc = score(text, at, h);
      if (h.pos !== undefined) sc -= Math.min(Math.abs(at - h.pos) / 1e5, 1);
      if (sc > bsc) { bsc = sc; best = at; }
      at = text.indexOf(h.exact, at + 1);
    }
    return best;
  }
  function paintAll() {
    var sorted = state.highlights.slice();
    sorted.forEach(function (h) {
      var a = locate(h);
      h.orphan = a < 0;
      if (a >= 0) { h.pos = a; wrap(a, a + h.exact.length, h); }
    });
  }

  // ---- UI helpers -----------------------------------------------------------------------
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }
  function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 7); }
  function chapterTitle(id) {
    var a = document.querySelector('#side a[href="#' + id + '"]');
    if (!a) return id;
    a = a.cloneNode(true);
    var b = a.querySelector(".hl-cnt");
    if (b) b.remove();
    return a.textContent.trim();
  }
  function swatches(onpick, current) {
    var row = el("div", "hl-sw");
    COLORS.forEach(function (c) {
      var b = el("button", "hl-dot hl-" + c[0] + (c[0] === current ? " on" : ""));
      b.type = "button";
      b.title = c[1];
      b.setAttribute("aria-label", "Highlight " + c[1]);
      b.addEventListener("mousedown", function (e) { e.preventDefault(); });
      b.addEventListener("click", function (e) { e.preventDefault(); onpick(c[0]); });
      row.appendChild(b);
    });
    return row;
  }

  // ---- the selection toolbar --------------------------------------------------------------
  var bar = el("div", "hl-ui hl-bar");
  bar.hidden = true;
  document.body.appendChild(bar);
  var pending = null;

  function selectionInfo() {
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) return null;
    var r = sel.getRangeAt(0);
    if (!root.contains(r.commonAncestorContainer)) return null;
    if (bar.contains(r.commonAncestorContainer)) return null;
    var a = offsetOf(r.startContainer, r.startOffset), b = offsetOf(r.endContainer, r.endOffset);
    var text = idx().text;
    if (a < 0 || b <= a) return null;
    while (a < b && /\s/.test(text[a])) a++;
    while (b > a && /\s/.test(text[b - 1])) b--;
    if (b <= a) return null;
    return { a: a, b: b, rect: r.getBoundingClientRect(), node: r.startContainer };
  }
  function placeBar(rect) {
    bar.hidden = false;
    var x = rect.left + rect.width / 2 - bar.offsetWidth / 2;
    x = Math.max(8, Math.min(x, window.innerWidth - bar.offsetWidth - 8));
    var y = rect.top - bar.offsetHeight - 10;
    if (y < 8) y = rect.bottom + 10;
    bar.style.left = x + "px";
    bar.style.top = y + "px";
  }
  function showNewBar() {
    var info = selectionInfo();
    if (!info) { hideBar(); return; }
    pending = info;
    bar.innerHTML = "";
    bar.appendChild(swatches(function (c) { create(c, false); }, pref("color", "yellow")));
    var note = el("button", "hl-btn", "Note");
    note.type = "button";
    note.title = "Highlight and add a note";
    note.addEventListener("mousedown", function (e) { e.preventDefault(); });
    note.addEventListener("click", function () { create(pref("color", "yellow"), true); });
    bar.appendChild(note);
    placeBar(info.rect);
  }
  function hideBar() { bar.hidden = true; pending = null; }

  function create(color, withNote) {
    var p = pending;
    if (!p) return;
    var text = idx().text;
    var h = {
      id: uid(), color: color, note: "",
      exact: text.slice(p.a, p.b),
      prefix: text.slice(Math.max(0, p.a - CTX), p.a),
      suffix: text.slice(p.b, p.b + CTX),
      chapter: chapterAt(p.node), section: sectionAt(p.node),
      pos: p.a, created: new Date().toISOString()
    };
    state.prefs.color = color;
    state.highlights.push(h);
    save();
    window.getSelection().removeAllRanges();
    var m = wrap(p.a, p.b, h);
    hideBar();
    refreshDrawer();
    if (withNote && m) editNote(h, m);
  }

  // clicking an existing highlight
  function showEditBar(h, m) {
    bar.innerHTML = "";
    bar.appendChild(swatches(function (c) {
      h.color = c; state.prefs.color = c; save(); restyle(h); refreshDrawer(); hideBar();
    }, h.color));
    var note = el("button", "hl-btn", h.note ? "Edit note" : "Note");
    note.type = "button";
    note.addEventListener("click", function () { hideBar(); editNote(h, m); });
    var del = el("button", "hl-btn hl-del", "Remove");
    del.type = "button";
    del.addEventListener("click", function () { removeH(h.id); hideBar(); });
    bar.appendChild(note);
    bar.appendChild(del);
    placeBar(m.getBoundingClientRect());
  }
  function removeH(id) {
    unwrap(id);
    state.highlights = state.highlights.filter(function (x) { return x.id !== id; });
    save();
    refreshDrawer();
  }

  // note editor (small dialog)
  var dlg = el("div", "hl-ui hl-dlg");
  dlg.hidden = true;
  document.body.appendChild(dlg);
  function editNote(h, m) {
    dlg.innerHTML = "";
    dlg.appendChild(el("div", "hl-dlg-q", "“" + esc(h.exact.length > 160 ? h.exact.slice(0, 160) + "…" : h.exact) + "”"));
    var ta = el("textarea");
    ta.value = h.note || "";
    ta.placeholder = "Your note";
    ta.rows = 4;
    dlg.appendChild(ta);
    var row = el("div", "hl-dlg-row");
    var ok = el("button", "hl-btn hl-primary", "Save");
    var cancel = el("button", "hl-btn", "Cancel");
    ok.type = cancel.type = "button";
    ok.addEventListener("click", function () {
      h.note = ta.value.trim(); save(); restyle(h); refreshDrawer(); dlg.hidden = true;
    });
    cancel.addEventListener("click", function () { dlg.hidden = true; });
    row.appendChild(cancel);
    row.appendChild(ok);
    dlg.appendChild(row);
    dlg.hidden = false;
    var r = (m || bar).getBoundingClientRect();
    var y = Math.min(r.bottom + 10, window.innerHeight - dlg.offsetHeight - 10);
    dlg.style.top = Math.max(10, y) + "px";
    dlg.style.left = Math.max(10, Math.min(r.left, window.innerWidth - dlg.offsetWidth - 10)) + "px";
    ta.focus();
  }

  document.addEventListener("mouseup", function (e) {
    if (bar.contains(e.target) || dlg.contains(e.target) || drawer.contains(e.target)) return;
    setTimeout(function () {
      var m = e.target.closest && e.target.closest("mark.hl");
      var sel = window.getSelection();
      if (m && sel && sel.isCollapsed) {
        var h = find(m.getAttribute("data-hid"));
        if (h) { showEditBar(h, m); return; }
      }
      showNewBar();
    }, 10);
  });
  var tsel = null;
  document.addEventListener("selectionchange", function () {
    // touch devices: show the bar after a long-press selection
    if (!("ontouchstart" in window)) return;
    clearTimeout(tsel);
    tsel = setTimeout(showNewBar, 350);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    // Esc: drop the text selection (and its colour bar), close the note box and the drawer
    var sel = window.getSelection();
    if (sel && !sel.isCollapsed) sel.removeAllRanges();
    hideBar(); dlg.hidden = true; closeDrawer();
    var fl = root.querySelectorAll("mark.hl-flash");
    for (var i = 0; i < fl.length; i++) fl[i].classList.remove("hl-flash");
  });
  window.addEventListener("scroll", function () { if (!bar.hidden && !pending) hideBar(); }, { passive: true });
  function find(id) {
    for (var i = 0; i < state.highlights.length; i++) if (state.highlights[i].id === id) return state.highlights[i];
    return null;
  }

  // ---- the drawer: my highlights + display settings -----------------------------------------
  var fab = document.getElementById("hl-open");
  if (!fab) {
    fab = el("button", "hl-ui hl-fab", 'Highlights <span class="hl-fab-n"></span>');
    fab.type = "button";
    document.body.appendChild(fab);
  }

  var drawer = el("aside", "hl-ui hl-drawer");
  drawer.hidden = true;
  drawer.setAttribute("aria-label", "My highlights");
  document.body.appendChild(drawer);
  var filter = { color: "", q: "" };

  function openDrawer() { refreshDrawer(); drawer.hidden = false; }
  function closeDrawer() { drawer.hidden = true; }
  fab.addEventListener("click", function () { drawer.hidden ? openDrawer() : closeDrawer(); });

  function refreshDrawer() {
    fab.querySelector(".hl-fab-n").textContent = state.highlights.length ? state.highlights.length : "";
    drawer.innerHTML = "";
    var head = el("div", "hl-dh");
    head.appendChild(el("b", "", "My highlights"));
    var x = el("button", "hl-x", "×");
    x.type = "button";
    x.title = "Close";
    x.addEventListener("click", closeDrawer);
    head.appendChild(x);
    drawer.appendChild(head);

    drawer.appendChild(labelled("New highlights", swatches(function (c) { state.prefs.color = c; save(); refreshDrawer(); }, pref("color", "yellow"))));

    // filters
    var fr = el("div", "hl-filt");
    var q = el("input");
    q.type = "search";
    q.placeholder = "Search highlights and notes";
    q.value = filter.q;
    q.addEventListener("input", function () { filter.q = q.value; renderList(list); });
    fr.appendChild(q);
    var cr = el("div", "hl-sw hl-sw-f");
    var all = el("button", "hl-all" + (filter.color ? "" : " on"), "All");
    all.type = "button";
    all.addEventListener("click", function () { filter.color = ""; refreshDrawer(); });
    cr.appendChild(all);
    COLORS.forEach(function (c) {
      var b = el("button", "hl-dot hl-" + c[0] + (filter.color === c[0] ? " on" : ""));
      b.type = "button";
      b.title = "Only " + c[1];
      b.addEventListener("click", function () { filter.color = filter.color === c[0] ? "" : c[0]; refreshDrawer(); });
      cr.appendChild(b);
    });
    fr.appendChild(cr);
    drawer.appendChild(fr);

    var list = el("div", "hl-list");
    drawer.appendChild(list);
    renderList(list);

    // export / import / clear
    var io = el("div", "hl-io");
    var ex = el("button", "hl-btn", "Export");
    ex.type = "button";
    ex.title = "Save your highlights, notes and settings to a file";
    ex.addEventListener("click", exportAll);
    var im = el("button", "hl-btn", "Import");
    im.type = "button";
    im.title = "Load highlights from an exported file (merged with these)";
    im.addEventListener("click", importAll);
    var cl = el("button", "hl-btn hl-del", "Clear all");
    cl.type = "button";
    cl.addEventListener("click", function () {
      if (!state.highlights.length || !confirm("Remove all " + state.highlights.length + " highlights from this browser?")) return;
      state.highlights.forEach(function (h) { unwrap(h.id); });
      state.highlights = [];
      save();
      refreshDrawer();
    });
    io.appendChild(ex);
    io.appendChild(im);
    io.appendChild(cl);
    drawer.appendChild(io);
    drawer.appendChild(el("p", "hl-fine", "Kept in this browser only. Use Export to move them to another device."));
  }
  function labelled(t, node) {
    var d = el("div", "hl-lab");
    d.appendChild(el("span", "", t));
    d.appendChild(node);
    return d;
  }
  function renderList(list) {
    list.innerHTML = "";
    var q = filter.q.toLowerCase();
    var hs = state.highlights.filter(function (h) {
      if (filter.color && h.color !== filter.color) return false;
      if (q && (h.exact + " " + (h.note || "")).toLowerCase().indexOf(q) < 0) return false;
      return true;
    }).sort(function (a, b) { return (a.orphan ? 1e12 : a.pos) - (b.orphan ? 1e12 : b.pos); });
    if (!hs.length) {
      list.appendChild(el("p", "hl-empty", state.highlights.length ? "Nothing matches." :
        "Select text in the book and pick a colour to highlight it. Click a highlight to change its colour, add a note or remove it."));
      return;
    }
    var last = null;
    hs.forEach(function (h) {
      var ch = h.orphan ? "_orphan" : h.chapter;
      if (ch !== last) {
        list.appendChild(el("div", "hl-ch", h.orphan ? "Not found in this version of the book" : esc(chapterTitle(h.chapter))));
        last = ch;
      }
      var it = el("div", "hl-item hl-b-" + h.color);
      var t = el("div", "hl-q", esc(h.exact.length > 220 ? h.exact.slice(0, 220) + "…" : h.exact));
      it.appendChild(t);
      if (h.note) it.appendChild(el("div", "hl-n", esc(h.note)));
      var acts = el("div", "hl-acts");
      if (!h.orphan) {
        var go = el("button", "", "Go to");
        go.type = "button";
        go.addEventListener("click", function () { jump(h.id); });
        acts.appendChild(go);
      }
      var del = el("button", "", "Remove");
      del.type = "button";
      del.addEventListener("click", function () { removeH(h.id); });
      acts.appendChild(del);
      it.appendChild(acts);
      t.addEventListener("click", function () { if (!h.orphan) jump(h.id); });
      list.appendChild(it);
    });
  }
  function jump(id) {
    var m = root.querySelector('mark[data-hid="' + id + '"]');
    if (!m) return;
    if (window.innerWidth < 900) closeDrawer();
    m.scrollIntoView({ behavior: "smooth", block: "center" });
    var ms = root.querySelectorAll('mark[data-hid="' + id + '"]');
    for (var i = 0; i < ms.length; i++) ms[i].classList.add("hl-flash");
    setTimeout(function () { for (var i = 0; i < ms.length; i++) ms[i].classList.remove("hl-flash"); }, 1600);
  }
  function exportAll() {
    var data = JSON.stringify({ app: "notebook", version: 1, exported: new Date().toISOString(),
      highlights: state.highlights.map(function (h) { var c = {}; for (var k in h) if (k !== "orphan") c[k] = h[k]; return c; }),
      prefs: state.prefs, decks: state.decks, reading: state.reading }, null, 1);
    var a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([data], { type: "application/json" }));
    a.download = "notebook-highlights.json";
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }
  function importAll() {
    var inp = document.createElement("input");
    inp.type = "file";
    inp.accept = "application/json,.json";
    inp.addEventListener("change", function () {
      var f = inp.files[0];
      if (!f) return;
      f.text().then(function (txt) {
        var d;
        try { d = JSON.parse(txt); } catch (e) { alert("That file is not an export of this book."); return; }
        var have = {}, added = 0;
        state.highlights.forEach(function (h) { have[h.id] = 1; });
        (d.highlights || []).forEach(function (h) {
          if (!h || !h.exact || have[h.id]) return;
          h.color = h.color || "yellow";
          h.prefix = h.prefix || ""; h.suffix = h.suffix || "";
          state.highlights.push(h);
          var a = locate(h);
          h.orphan = a < 0;
          if (a >= 0) { h.pos = a; wrap(a, a + h.exact.length, h); }
          added++;
        });
        if (d.prefs) for (var k in d.prefs) if (state.prefs[k] === undefined) state.prefs[k] = d.prefs[k];
        save();
        refreshDrawer();
        alert(added + " highlight" + (added === 1 ? "" : "s") + " imported.");
      });
    });
    inp.click();
  }

  // ---- reading position ----------------------------------------------------------------------
  var heads = null;
  function currentHead() {
    heads = heads || Array.prototype.slice.call(root.querySelectorAll("section[id], h2[id]"));
    var best = null;
    for (var i = 0; i < heads.length; i++) {
      if (heads[i].getBoundingClientRect().top <= 90) best = heads[i]; else if (best) break;
    }
    return best;
  }
  var tsave = null;
  window.addEventListener("scroll", function () {
    clearTimeout(tsave);
    tsave = setTimeout(function () {
      var h = currentHead();
      if (!h) return;
      var ch = h.tagName === "SECTION" ? h.id : chapterAt(h);
      var doc = document.documentElement;
      state = (function (s) { s.highlights = state.highlights; return s; })(load());  // pick up deck progress from other tabs
      state.reading = { id: h.id, chapter: ch, title: chapterTitle(ch), dy: Math.round(h.getBoundingClientRect().top),
        frac: Math.round(1000 * window.scrollY / Math.max(1, doc.scrollHeight - innerHeight)) / 1000,
        t: new Date().toISOString() };
      var seen = state.prefs.seen || {};
      if (ch) seen[ch] = 1;
      state.prefs.seen = seen;
      save();
      markSide();
    }, 400);
  }, { passive: true });
  function markSide() {
    var seen = state.prefs.seen || {};
    var as = document.querySelectorAll("#side a[href^='#']");
    for (var i = 0; i < as.length; i++) {
      var id = as[i].getAttribute("href").slice(1);
      as[i].classList.toggle("hl-seen", !!seen[id]);
      var n = state.highlights.filter(function (h) { return h.chapter === id && !h.orphan; }).length;
      var b = as[i].querySelector(".hl-cnt");
      if (n && !b) { b = el("span", "hl-cnt"); as[i].appendChild(b); }
      if (b) { if (n) b.textContent = n; else b.remove(); }
    }
  }
  function restore() {
    var want = location.hash.slice(1);
    if (want.indexOf("hl-") === 0) { setTimeout(function () { jump(want.slice(3)); }, 50); return; }
    if (want === "resume" && state.reading) {
      var t = document.getElementById(state.reading.id);
      if (t) {
        history.replaceState(null, "", location.pathname);
        window.scrollTo(0, t.getBoundingClientRect().top + window.scrollY - (state.reading.dy || 0));
      }
    }
  }

  // ---- go --------------------------------------------------------------------------------------
  function start() {
    build();
    paintAll();
    save();
    refreshDrawer();
    markSide();
    restore();
  }
  if (document.readyState === "complete") start();
  else window.addEventListener("load", start);
})();
