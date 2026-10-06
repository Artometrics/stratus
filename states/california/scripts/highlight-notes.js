(function () {
  "use strict";

  // Scope: everything in <body> except the site chrome this script itself
  // adds, plus the existing nav bar and listen-card, so selections there
  // can't accidentally turn into highlights.
  var EXCLUDE_SELECTOR = ".rf-sitenav, .wp-listen-card, .rf-notes-fab, .rf-notes-panel, .rf-highlight-btn, .rf-note-popover";
  var STORAGE_KEY = "rf-highlights-v1";
  var CONTEXT_LEN = 24;

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }
  function $$(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function loadAll() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function saveAll(list) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    } catch (e) {
      /* storage blocked (private mode, quota, etc.) -- degrade silently */
    }
  }

  function uid() {
    return "h" + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
  }

  function isInsideExcluded(node) {
    var el = node.nodeType === 1 ? node : node.parentElement;
    return !!(el && el.closest(EXCLUDE_SELECTOR));
  }

  // ---- text-node walking, for both capturing context and relocating on load ----

  function articleTextNodes() {
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        if (isInsideExcluded(node)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    var nodes = [];
    var n;
    while ((n = walker.nextNode())) nodes.push(n);
    return nodes;
  }

  function fullArticleText(nodes) {
    return nodes.map(function (n) { return n.nodeValue; }).join("");
  }

  // ---- capturing a new highlight from the current selection ----

  function captureSelectionContext(range) {
    var nodes = articleTextNodes();
    var full = fullArticleText(nodes);
    var text = range.toString();
    if (!text.trim()) return null;

    // Find where the selection's start node sits inside the concatenated
    // text, so we can pull a stable prefix/suffix around it.
    var offset = 0;
    for (var i = 0; i < nodes.length; i++) {
      if (nodes[i] === range.startContainer) {
        offset += range.startOffset;
        break;
      }
      offset += nodes[i].nodeValue.length;
    }
    var prefix = full.slice(Math.max(0, offset - CONTEXT_LEN), offset);
    var suffix = full.slice(offset + text.length, offset + text.length + CONTEXT_LEN);
    return { text: text, prefix: prefix, suffix: suffix };
  }

  function wrapRange(range, id) {
    try {
      var mark = document.createElement("mark");
      mark.className = "rf-highlight";
      mark.dataset.highlightId = id;
      range.surroundContents(mark);
      return mark;
    } catch (e) {
      // Selection spans multiple elements (e.g. across a paragraph break);
      // surroundContents() can't wrap that in one shot. Skip the inline
      // wrap for this case -- the highlight is still saved and exportable,
      // it just won't render with a <mark> until a more careful multi-node
      // wrap is worth building.
      return null;
    }
  }

  // ---- re-locating saved highlights in the DOM on page load ----

  function relocateHighlight(entry) {
    var nodes = articleTextNodes();
    var full = fullArticleText(nodes);
    var needle = entry.prefix + entry.text + entry.suffix;
    var idx = full.indexOf(needle);
    var textStart;
    if (idx >= 0) {
      textStart = idx + entry.prefix.length;
    } else {
      // Context drifted (surrounding copy changed). Fall back to the bare
      // highlighted text if it's still unique enough to find once.
      var bare = full.indexOf(entry.text);
      if (bare < 0 || full.indexOf(entry.text, bare + 1) >= 0) return; // absent or ambiguous
      textStart = bare;
    }
    var textEnd = textStart + entry.text.length;

    var pos = 0;
    var startNode, startOffset, endNode, endOffset;
    for (var i = 0; i < nodes.length; i++) {
      var len = nodes[i].nodeValue.length;
      if (startNode === undefined && textStart < pos + len) {
        startNode = nodes[i];
        startOffset = textStart - pos;
      }
      if (endNode === undefined && textEnd <= pos + len) {
        endNode = nodes[i];
        endOffset = textEnd - pos;
        break;
      }
      pos += len;
    }
    if (!startNode || !endNode) return;

    var range = document.createRange();
    range.setStart(startNode, startOffset);
    range.setEnd(endNode, endOffset);
    wrapRange(range, entry.id);
  }

  function relocateAllForThisPage() {
    var all = loadAll();
    var mine = all.filter(function (h) { return h.pageUrl === location.pathname; });
    mine.forEach(relocateHighlight);
  }

  // ---- floating "Highlight" button on selection ----

  function removeFloatingBtn() {
    var btn = $(".rf-highlight-btn");
    if (btn) btn.remove();
  }

  function showFloatingBtn(range) {
    removeFloatingBtn();
    var rect = range.getBoundingClientRect();
    if (!rect || (!rect.width && !rect.height)) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "rf-highlight-btn";
    btn.textContent = "Highlight";
    btn.style.position = "absolute";
    btn.style.top = window.scrollY + rect.top - 36 + "px";
    btn.style.left = window.scrollX + rect.left + "px";
    btn.addEventListener("mousedown", function (e) {
      // mousedown, not click -- fires before the selection collapses.
      e.preventDefault();
      var id = uid();
      var ctx = captureSelectionContext(range.cloneRange());
      if (!ctx) return;
      var mark = wrapRange(range.cloneRange(), id);
      var all = loadAll();
      all.push({
        id: id,
        pageTitle: document.title,
        pageUrl: location.pathname,
        text: ctx.text,
        prefix: ctx.prefix,
        suffix: ctx.suffix,
        note: "",
        createdAt: new Date().toISOString(),
      });
      saveAll(all);
      removeFloatingBtn();
      window.getSelection().removeAllRanges();
      if (mark) openNotePopover(mark, id);
      renderPanelList();
    });
    document.body.appendChild(btn);
  }

  function bindSelectionWatcher() {
    document.addEventListener("mouseup", function (e) {
      if (isInsideExcluded(e.target)) return;
      // Let the click that might be dismissing the button process first.
      setTimeout(function () {
        var sel = window.getSelection();
        if (!sel || sel.isCollapsed || !sel.toString().trim()) {
          removeFloatingBtn();
          return;
        }
        var range = sel.getRangeAt(0);
        if (isInsideExcluded(range.startContainer) || isInsideExcluded(range.endContainer)) {
          removeFloatingBtn();
          return;
        }
        showFloatingBtn(range);
      }, 0);
    });
    document.addEventListener("mousedown", function (e) {
      if (e.target.closest(".rf-highlight-btn")) return;
      removeFloatingBtn();
    });
  }

  // ---- note popover on an existing highlight ----

  function closePopover() {
    var p = $(".rf-note-popover");
    if (p) p.remove();
  }

  function openNotePopover(mark, id) {
    closePopover();
    var all = loadAll();
    var entry = all.filter(function (h) { return h.id === id; })[0];
    if (!entry) return;

    var rect = mark.getBoundingClientRect();
    var pop = document.createElement("div");
    pop.className = "rf-note-popover";
    pop.style.position = "absolute";
    pop.style.top = window.scrollY + rect.bottom + 6 + "px";
    pop.style.left = window.scrollX + rect.left + "px";

    var textarea = document.createElement("textarea");
    textarea.placeholder = "Add a note (optional)";
    textarea.value = entry.note || "";

    var saveBtn = document.createElement("button");
    saveBtn.type = "button";
    saveBtn.textContent = "Save";
    saveBtn.addEventListener("click", function () {
      var list = loadAll();
      var e2 = list.filter(function (h) { return h.id === id; })[0];
      if (e2) e2.note = textarea.value;
      saveAll(list);
      closePopover();
      renderPanelList();
    });

    var deleteBtn = document.createElement("button");
    deleteBtn.type = "button";
    deleteBtn.className = "rf-note-delete";
    deleteBtn.textContent = "Remove highlight";
    deleteBtn.addEventListener("click", function () {
      var list = loadAll().filter(function (h) { return h.id !== id; });
      saveAll(list);
      var parent = mark.parentNode;
      while (mark.firstChild) parent.insertBefore(mark.firstChild, mark);
      parent.removeChild(mark);
      parent.normalize();
      closePopover();
      renderPanelList();
    });

    pop.appendChild(textarea);
    var row = document.createElement("div");
    row.className = "rf-note-popover-row";
    row.appendChild(saveBtn);
    row.appendChild(deleteBtn);
    pop.appendChild(row);
    document.body.appendChild(pop);
    textarea.focus();
  }

  function bindHighlightClicks() {
    document.addEventListener("click", function (e) {
      var mark = e.target.closest(".rf-highlight");
      if (mark) {
        openNotePopover(mark, mark.dataset.highlightId);
        return;
      }
      if (!e.target.closest(".rf-note-popover")) closePopover();
    });
  }

  // ---- floating panel: this page's highlights + export-all ----

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function renderPanelList() {
    var list = $(".rf-notes-panel-list");
    if (!list) return;
    var mine = loadAll().filter(function (h) { return h.pageUrl === location.pathname; });
    var countEl = $(".rf-notes-fab-count");
    if (countEl) countEl.textContent = mine.length ? String(mine.length) : "";

    if (!mine.length) {
      list.innerHTML = '<p class="rf-notes-empty">No highlights on this page yet. Select any text to start.</p>';
      return;
    }
    list.innerHTML = mine
      .map(function (h) {
        return (
          '<div class="rf-notes-item">' +
          '<blockquote>' + escapeHtml(h.text) + "</blockquote>" +
          (h.note ? '<p class="rf-notes-item-note">' + escapeHtml(h.note) + "</p>" : "") +
          "</div>"
        );
      })
      .join("");
  }

  function exportAll() {
    var all = loadAll();
    if (!all.length) {
      window.alert("No highlights saved yet.");
      return;
    }
    var byPage = {};
    all.forEach(function (h) {
      var key = h.pageUrl + "|" + h.pageTitle;
      (byPage[key] = byPage[key] || []).push(h);
    });
    var lines = ["# My Highlights & Notes", "", "Exported " + new Date().toLocaleString(), ""];
    Object.keys(byPage).forEach(function (key) {
      var parts = key.split("|");
      var url = parts[0];
      var title = parts.slice(1).join("|");
      lines.push("## " + title, "", "_" + location.origin + url + "_", "");
      byPage[key].forEach(function (h) {
        lines.push("> " + h.text.replace(/\n/g, "\n> "), "");
        if (h.note) lines.push("Note: " + h.note, "");
        lines.push("---", "");
      });
    });
    var blob = new Blob([lines.join("\n")], { type: "text/markdown" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = "my-highlights-and-notes.md";
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  function buildPanel() {
    var fab = document.createElement("button");
    fab.type = "button";
    fab.className = "rf-notes-fab";
    fab.setAttribute("aria-label", "My highlights and notes");
    fab.innerHTML = '<span class="rf-notes-fab-glyph" aria-hidden="true">&#9998;</span><span class="rf-notes-fab-count"></span>';

    var panel = document.createElement("div");
    panel.className = "rf-notes-panel";
    panel.innerHTML =
      '<div class="rf-notes-panel-header">' +
      "<span>Highlights on this page</span>" +
      '<button type="button" class="rf-notes-panel-close" aria-label="Close">&times;</button>' +
      "</div>" +
      '<div class="rf-notes-panel-list"></div>' +
      '<button type="button" class="rf-notes-export">Export all notes</button>';

    fab.addEventListener("click", function () {
      panel.classList.toggle("rf-notes-panel-open");
      if (panel.classList.contains("rf-notes-panel-open")) renderPanelList();
    });
    $(".rf-notes-panel-close", panel).addEventListener("click", function () {
      panel.classList.remove("rf-notes-panel-open");
    });
    $(".rf-notes-export", panel).addEventListener("click", exportAll);

    document.body.appendChild(fab);
    document.body.appendChild(panel);
  }

  function init() {
    if (!document.body) return;
    buildPanel();
    relocateAllForThisPage();
    renderPanelList();
    bindSelectionWatcher();
    bindHighlightClicks();
  }

  init();
})();
