/* library.js -- the parts of the library page that come from this browser: where you
   stopped reading, how far you are in each deck, and your highlights. */
(function () {
  "use strict";
  var KEY = "wcbook.v1", CH = window.ISO_CHAPTERS || {};
  var s = {};
  try { s = JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) {}
  var hs = s.highlights || [], decks = s.decks || {};
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  // continue reading
  var r = s.reading, b = document.getElementById("resume");
  if (r && b && r.title) {
    b.hidden = false;
    b.innerHTML = "Continue: <small>" + esc(r.title.replace(/^\s*\w+\s+/, "")) + "</small>";
    b.title = "Back to where you stopped reading";
  }
  // per chapter: highlights and deck progress
  var count = {};
  hs.forEach(function (h) { if (!h.orphan) count[h.chapter] = (count[h.chapter] || 0) + 1; });
  document.querySelectorAll("[data-hlc]").forEach(function (e) {
    var n = count[e.getAttribute("data-hlc")];
    if (n) e.textContent = n + " highlight" + (n > 1 ? "s" : "");
  });
  document.querySelectorAll("[data-deck]").forEach(function (e) {
    var d = decks[e.getAttribute("data-deck")], n = +e.getAttribute("data-n");
    if (d) e.textContent = "slide " + (d.h + 1) + " of " + (d.total || n);
  });
  // my highlights
  var box = document.getElementById("myhl");
  if (!box || !hs.length) return;
  var filt = "";
  function render() {
    var list = hs.filter(function (h) { return !filt || h.color === filt; })
      .sort(function (a, b) { return (a.orphan ? 1e12 : a.pos || 0) - (b.orphan ? 1e12 : b.pos || 0); });
    var out = ['<div class="hlbar"><span class="muted">' + hs.length + " highlight" + (hs.length > 1 ? "s" : "") + "</span>"];
    out.push('<button type="button" data-c="" class="' + (filt ? "" : "on") + '">All</button>');
    ["yellow", "green", "blue", "pink", "purple"].forEach(function (c) {
      out.push('<button type="button" class="dot d-' + c + (filt === c ? " on" : "") + '" data-c="' + c + '" title="Only ' + c + '"></button>');
    });
    out.push('<button type="button" id="hlexp">Export</button></div>');
    var last = null;
    list.forEach(function (h) {
      var ch = h.orphan ? "_" : h.chapter;
      if (ch !== last) {
        var c = CH[h.chapter];
        out.push('<div class="hlch">' + (h.orphan ? "Not found in this version of the book" :
          c ? "Chapter " + esc(c[0]) + " · " + esc(c[1]) : esc(h.chapter)) + "</div>");
        last = ch;
      }
      out.push('<a class="hli b-' + esc(h.color) + '" href="notebook.html#hl-' + esc(h.id) + '"><span class="q">' +
        esc(h.exact.length > 260 ? h.exact.slice(0, 260) + "…" : h.exact) + "</span>" +
        (h.note ? '<span class="n">' + esc(h.note) + "</span>" : "") + "</a>");
    });
    box.innerHTML = out.join("");
    box.querySelectorAll("button[data-c]").forEach(function (b) {
      b.addEventListener("click", function () { filt = b.getAttribute("data-c"); render(); });
    });
    document.getElementById("hlexp").addEventListener("click", function () {
      var a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([JSON.stringify({ app: "notebook", version: 1, exported: new Date().toISOString(),
        highlights: hs, prefs: s.prefs, decks: decks, reading: s.reading }, null, 1)], { type: "application/json" }));
      a.download = "notebook-highlights.json";
      document.body.appendChild(a); a.click(); a.remove();
    });
  }
  render();
})();
