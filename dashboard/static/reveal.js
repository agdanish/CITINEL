// CITINEL — truncation reveal.
//
// The bar is "zero clipping without an affordance". An opt-in list cannot meet that bar:
// it only covers the elements an author remembered to mark, and it misses container-level
// clipping entirely — a block whose inner flex row is wider than it is measures clipped
// while none of its text elements do.
//
// So the sweep is over MEASURED clipping, not over authored intent. Any element that is
// actually cut gets a tab stop and a title; anything untruncated gets neither, so no dead
// tab stops appear. Re-evaluated on resize, on font load, and after the DOM settles.
(function () {
  var MIN = 2;          // px of loss worth an affordance
  var MAX_TAGS = 240;   // a dense screen should not grow hundreds of tab stops

  function textOf(el) {
    return (el.textContent || '').replace(/\s+/g, ' ').trim();
  }

  function qualifies(el) {
    if (el.hasAttribute('data-source-badge')) return false;
    if (el.ownerSVGElement || el.tagName === 'svg') return false;
    var lost = el.scrollWidth - el.clientWidth;
    if (lost <= MIN || el.clientWidth <= 0) return false;
    var cs = getComputedStyle(el);
    // already reachable: the user can scroll to the rest
    if (cs.overflowX === 'auto' || cs.overflowX === 'scroll') return false;
    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    if (!textOf(el)) return false;
    // a focusable element handles its own reveal
    if (/^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName)) return false;
    return true;
  }

  function sync() {
    var root = document.querySelector('[data-screen-label]') || document.body;
    if (!root) return;

    var all = root.querySelectorAll('*');
    var hit = [];
    for (var i = 0; i < all.length; i++) {
      if (qualifies(all[i])) hit.push(all[i]);
    }

    // Innermost wins. A clipped block that contains a clipped span should not also become a
    // tab stop — the operator wants the specific value, not its container.
    var keep = [];
    for (var j = 0; j < hit.length; j++) {
      var inner = false;
      for (var k = 0; k < hit.length; k++) {
        if (k !== j && hit[j].contains(hit[k])) { inner = true; break; }
      }
      if (!inner) keep.push(hit[j]);
    }
    keep = keep.slice(0, MAX_TAGS);

    // clear anything previously tagged that now fits
    var was = root.querySelectorAll('[data-clipped]');
    for (var w = 0; w < was.length; w++) {
      if (keep.indexOf(was[w]) === -1) {
        if (was[w].getAttribute('tabindex') === '0' && !was[w].hasAttribute('data-keep-tabindex')) {
          was[w].removeAttribute('tabindex');
        }
        if (was[w].getAttribute('data-reveal-title') === '1') {
          was[w].removeAttribute('title');
          was[w].removeAttribute('data-reveal-title');
        }
        was[w].removeAttribute('data-clipped');
      }
    }

    for (var m = 0; m < keep.length; m++) {
      var el = keep[m];
      if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '0');
      if (!el.hasAttribute('title')) {
        el.setAttribute('title', textOf(el));
        el.setAttribute('data-reveal-title', '1');
      }
      el.setAttribute('data-clipped', '');
    }
  }

  var t, running = false, lastRun = 0;
  function run() {
    if (running) return;
    running = true;
    lastRun = Date.now();
    try { sync(); } finally { setTimeout(function () { running = false; }, 0); }
  }
  // A 180ms debounce is starved on screens whose clocks tick faster than that: every tick
  // resets the timer and sync never fires. Replay measured 3 unreachable clipped strings and
  // 0 tagged for exactly that reason. So the debounce has a ceiling — 1.2s since the last
  // successful pass forces one through regardless of how busy the DOM is.
  function schedule() {
    if (Date.now() - lastRun > 1200) { run(); return; }
    clearTimeout(t);
    t = setTimeout(run, 180);
  }

  if (document.readyState !== 'loading') schedule();
  else document.addEventListener('DOMContentLoaded', schedule);
  window.addEventListener('resize', schedule);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(schedule);
  new MutationObserver(function (recs) {
    for (var i = 0; i < recs.length; i++) {
      // ignore the attributes this script writes, or it loops
      if (recs[i].type === 'attributes') return;
    }
    schedule();
  }).observe(document.documentElement, { childList: true, subtree: true, characterData: true });

  window.CitinelReveal = { sync: sync, count: function () {
    var r = document.querySelector('[data-screen-label]') || document.body;
    return r.querySelectorAll('[data-clipped]').length;
  } };
})();
