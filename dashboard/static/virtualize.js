// CITINEL — list virtualization. A small pool of DOM nodes, not one per row.
//
// A real-time list (the ledger reel, a large queue, a wide corpus table) keeps growing for as
// long as the session runs. One DOM node per row means the browser is holding thousands of
// nodes it never shows — most of a long list sits scrolled out of view at any given moment.
// This renders only the rows the viewport can actually show, reuses a small fixed pool of row
// elements for that window, and repaints them with fresh data as the operator scrolls. A
// 10,000-row feed then costs the same DOM weight as a 30-row one.
//
// ── Shared ARIA convention for dense/real-time tables (guidance, not code — apply this on the
//    screen that wires this helper in, wherever a table gets sortable columns or a virtualized
//    body) ──────────────────────────────────────────────────────────────────────────────────
//   - Sortable column: a <button> inside the <th>, with aria-sort ("ascending" | "descending" |
//     "none") set on the <th> itself. Only one column carries a sort at a time — reset the
//     others to "none" when a different column takes over.
//   - One role="status" aria-live="polite" element per screen announces sort/filter/live-update
//     changes in words ("Sorted by severity, descending" / "14 new events since last check").
//     Throttle it to roughly 1000–1500ms between announcements — a screen-reader queue fed one
//     message per row update is noise, not signal.
//   - When the table is virtualized (this file in use), set aria-rowcount on the table root to
//     the FULL list length, and aria-rowindex on each rendered row to its absolute position in
//     that full list — not its slot in the small rendered pool — so the accessibility tree still
//     describes the whole dataset even though only a slice of it is ever in the DOM.
(function () {
  'use strict';

  var DEFAULT_OVERSCAN = 4; // rows kept painted beyond each edge of the viewport, so a fast
                             // scroll or a screen reader's virtual cursor doesn't outrun the pool.

  function CitinelVirtualize(container, items, rowHeight, renderRow) {
    if (!(rowHeight > 0)) rowHeight = 1; // guard against a zero/undefined height wedging the math

    var list = items || [];
    var pool = [];
    var spacer = document.createElement('div');
    var renderedStart = -1; // last index painted into the pool; -1 forces the first paint

    spacer.style.position = 'relative';
    spacer.style.width = '100%';
    container.appendChild(spacer);

    function poolTarget() {
      var visible = Math.ceil((container.clientHeight || 0) / rowHeight);
      return Math.max(1, visible + DEFAULT_OVERSCAN * 2);
    }

    // Grows or shrinks the pool to match the current viewport. Cheap and rare: only the
    // container's own size changes this, never the length of the underlying list.
    function sizePool() {
      var target = poolTarget();
      while (pool.length < target) {
        var row = document.createElement('div');
        row.style.position = 'absolute';
        row.style.left = '0';
        row.style.right = '0';
        row.style.height = rowHeight + 'px';
        spacer.appendChild(row);
        pool.push(row);
      }
      while (pool.length > target) {
        var extra = pool.pop();
        extra.parentNode.removeChild(extra);
      }
      renderedStart = -1; // pool membership changed; every slot needs fresh data
    }

    function paint() {
      sizePool();
      spacer.style.height = (list.length * rowHeight) + 'px'; // full-list height keeps the
                                                                // scrollbar honest, not the
                                                                // pool's own size
      var maxStart = Math.max(0, list.length - pool.length);
      var start = Math.floor(container.scrollTop / rowHeight) - DEFAULT_OVERSCAN;
      if (start < 0) start = 0;
      if (start > maxStart) start = maxStart;
      if (start === renderedStart) return; // same window already painted; nothing to write
      renderedStart = start;

      for (var i = 0; i < pool.length; i++) {
        var idx = start + i;
        var row = pool[i];
        if (idx < list.length) {
          row.style.display = '';
          row.style.transform = 'translateY(' + (idx * rowHeight) + 'px)';
          renderRow(row, list[idx], idx);
        } else {
          row.style.display = 'none'; // pool is larger than the list itself (short list)
        }
      }
    }

    container.addEventListener('scroll', paint);
    window.addEventListener('resize', paint); // a panel resize changes how many rows fit

    paint();

    return {
      // Swaps in a new list (e.g. after a poll) without tearing down the pool — the same
      // nodes get repainted with the new data, so a refresh never re-creates DOM.
      refresh: function (newItems) {
        list = newItems || [];
        renderedStart = -1;
        paint();
      },
      // Not required by every caller, but a virtualizer that outlives its container (a screen
      // that tears down and rebuilds a panel) should stop listening rather than leak.
      destroy: function () {
        container.removeEventListener('scroll', paint);
        window.removeEventListener('resize', paint);
      }
    };
  }

  window.CitinelVirtualize = CitinelVirtualize;
})();
