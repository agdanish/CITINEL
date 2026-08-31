// CITINEL — instrument motion driver. Binds animation to data, never to a timer.
//
// Every effect here fires because a value in the DOM actually changed. There is no
// ambient animation loop: if the data is still, the screen is still.
(function () {
  var reduce = false;
  try { reduce = matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}

  var NUM = /^[\s₹+\-]*[\d.,:%\/]+[\s a-z%\/]*$/i;

  // ── Tick flash on changed values ─────────────────────────────────────────────
  // Watches leaf text nodes that read as numeric. A changed figure flashes once;
  // the direction decides the colour, and a severity/critical context flashes red.
  function flash(el, oldText, newText) {
    if (reduce && !el.isConnected) return;
    // A value on a fixed cadence announces itself by changing. Flashing a 1Hz countdown
    // means 460ms of highlight every second on the hero readout — flicker, not signal.
    // The flash is for values that change unpredictably: counts, rates, dispositions.
    if (/^[+\-]?\d{1,3}:\d{2}(:\d{2})?$/.test(String(newText).trim())) return;
    var cls = 'ctn-ticked';
    var a = parseFloat(String(oldText).replace(/[^\d.\-]/g, ''));
    var b = parseFloat(String(newText).replace(/[^\d.\-]/g, ''));
    var ctx = (el.className || '') + ' ' + (el.getAttribute('style') || '');
    if (/severity-critical|severity-high/.test(ctx)) cls = 'ctn-ticked-alarm';
    else if (!isNaN(a) && !isNaN(b) && b > a) cls = 'ctn-ticked-up';
    el.classList.remove('ctn-ticked', 'ctn-ticked-up', 'ctn-ticked-alarm');
    void el.offsetWidth;
    el.classList.add(cls);
    setTimeout(function () { el.classList.remove(cls); }, 700);
  }

  var last = new WeakMap();

  function watchValues(root) {
    var obs = new MutationObserver(function (muts) {
      for (var i = 0; i < muts.length; i++) {
        var m = muts[i];
        var el = m.target.nodeType === 3 ? m.target.parentElement : m.target;
        if (!el || el.children.length) continue;
        var txt = (el.textContent || '').trim();
        if (!txt || txt.length > 22 || !NUM.test(txt)) continue;
        var prev = last.get(el);
        if (prev !== undefined && prev !== txt) flash(el, prev, txt);
        last.set(el, txt);
      }
    });
    obs.observe(root, { subtree: true, characterData: true, childList: true });
  }

  // ── Arc draw on the state device ─────────────────────────────────────────────
  // Any gold arc that represents a reached state draws itself once, so the ring
  // visibly completes instead of arriving pre-closed.
  function drawArcs(root) {
    if (reduce) return;
    var paths = root.querySelectorAll('path[stroke*="state-cited"], path[stroke*="color-clock"]');
    for (var i = 0; i < paths.length; i++) {
      var p = paths[i];
      if (p.__ctnDrawn) continue;
      var len = 0;
      try { len = p.getTotalLength(); } catch (e) { continue; }
      if (!len || len > 3000) continue;
      p.__ctnDrawn = true;
      p.style.setProperty('--ctn-arc-len', len.toFixed(1));
      p.classList.add('ctn-arc');
      setTimeout(function (el) {
        return function () { el.classList.remove('ctn-arc'); el.style.strokeDasharray = ''; };
      }(p), 1000);
    }
  }

  // ── Strip advance on appended rows ───────────────────────────────────────────
  // Marks nodes added to a scrolling list so an append reads as an append.
  function watchAppends(root) {
    if (reduce) return;
    var obs = new MutationObserver(function (muts) {
      for (var i = 0; i < muts.length; i++) {
        var added = muts[i].addedNodes;
        for (var j = 0; j < added.length; j++) {
          var n = added[j];
          if (n.nodeType !== 1) continue;
          // Walk up to the nearest scroll ancestor rather than demanding the direct
          // parent be one — feed and ledger rows sit several levels inside their
          // scroller, so a direct-parent test never matched and this never fired.
          var sc = null;
          for (var p = n.parentElement, d = 0; p && d < 5; p = p.parentElement, d++) {
            var ov = getComputedStyle(p).overflowY;
            if (ov === 'auto' || ov === 'scroll') { sc = p; break; }
          }
          if (!sc || !n.parentElement || n.parentElement.children.length < 3) continue;
          n.classList.add('ctn-advanced');
          setTimeout(function (el) {
            return function () { el.classList.remove('ctn-advanced'); };
          }(n), 400);
        }
      }
    });
    obs.observe(root, { subtree: true, childList: true });
  }

  // ── Deadline breath ─────────────────────────────────────────────────────────
  // Marks a live statutory countdown inside its final hour. A met or breached
  // window is a fact, not a deadline, so it never pulses.
  function markDeadlines(root) {
    var els = root.querySelectorAll('[style*="color-clock"]');
    for (var i = 0; i < els.length; i++) {
      var t = (els[i].textContent || '').trim();
      var m = /^\+?(\d{2}):(\d{2}):(\d{2})$/.exec(t);
      if (!m) { els[i].removeAttribute('data-deadline'); continue; }
      var breached = t.charAt(0) === '+';
      var hrs = parseInt(m[1], 10);
      if (!breached && hrs === 0) els[i].setAttribute('data-deadline', 'closing');
      else els[i].removeAttribute('data-deadline');
    }
  }

  function start() {
    var root = document.querySelector('[data-screen-label]') || document.body;
    if (!root) return;
    watchValues(root);
    watchAppends(root);
    drawArcs(root);
    markDeadlines(root);
    setInterval(function () { markDeadlines(root); }, 5000);
    // Newly mounted arcs (a state advancing, a screen switching record) draw too.
    new MutationObserver(function () { drawArcs(root); })
      .observe(root, { subtree: true, childList: true });
  }

  function boot() {
    if (document.querySelector('[data-screen-label]')) return start();
    var tries = 0;
    var iv = setInterval(function () {
      if (document.querySelector('[data-screen-label]') || ++tries > 60) {
        clearInterval(iv);
        start();
      }
    }, 200);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
