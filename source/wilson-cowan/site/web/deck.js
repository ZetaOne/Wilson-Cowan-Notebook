/* deck.js -- remembers the last slide of each deck (localStorage "wcbook.v1", same as the
   book), offers to resume there, and adds a link back to the library. */
(function () {
  "use strict";
  var me = document.currentScript, id = me.getAttribute("data-deck"), KEY = "wcbook.v1";
  if (me.getAttribute("data-title")) document.title = me.getAttribute("data-title");
  function load() { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } }
  function save(s) { try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) {} }

  var a = document.createElement("a");
  a.href = "../../index.html#c-" + id;
  a.textContent = "← Library";
  a.title = "Book, slides, code and study kit";
  a.style.cssText = "position:fixed;top:10px;left:10px;z-index:40;padding:6px 12px;border-radius:999px;" +
    "background:rgba(0,0,0,.55);color:#ddd;font:13px system-ui,sans-serif;text-decoration:none;opacity:.55";
  a.onmouseenter = function () { a.style.opacity = 1; };
  a.onmouseleave = function () { a.style.opacity = .55; };
  document.body.appendChild(a);

  function hook() {
    if (!window.Reveal) return;
    var total = Reveal.getTotalSlides ? Reveal.getTotalSlides() : 0;
    var d = (load().decks || {})[id];
    if (d && d.h > 0 && !location.hash) Reveal.slide(d.h, d.v || 0);
    Reveal.on("slidechanged", function (e) {
      var s = load();
      s.decks = s.decks || {};
      var old = s.decks[id] || {};
      s.decks[id] = { h: e.indexh, v: e.indexv || 0, total: total, max: Math.max(old.max || 0, e.indexh + 1),
                      t: new Date().toISOString() };
      save(s);
    });
  }
  if (window.Reveal && Reveal.isReady && Reveal.isReady()) hook();
  else if (window.Reveal) Reveal.on("ready", hook);
})();
