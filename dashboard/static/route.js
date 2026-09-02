// CITINEL — width routing.
//
// The console reflows natively from 720px up: rails stack under the work area and every
// radial instrument sizes from its own column, so no width in 720–1920 needs a separate page.
// Routing therefore only applies below 720, where Narrow is a genuinely different designed
// composition (five stations, 44px targets, 2D-scroll exception panels) rather than a fallback.
//
// Below 720 the switch is live, not load-only: crossing the boundary mid-session hands off
// immediately, because at that width the dense layout has no working state to stay in.
(function () {
  var FLOOR = 720;
  var qs = new URLSearchParams(location.search);
  if (qs.get('force') === 'console') { mark(); return; }

  // A page name that doesn't look like one of ours (missing, a bare
  // "undefined" from some future caller's unset variable, a directory,
  // an API path) must never reach the handoff URL: Narrow's "OPEN ... ANYWAY"
  // link is built directly from this value, and a bad one there is a dead
  // link with no page behind it.
  var here = location.pathname.split('/').pop() || '';
  if (!/^[A-Za-z][\w-]*\.dc\.html$/.test(here)) here = 'Overview.dc.html';
  if (/^(Narrow|Entry)\.dc\.html$/.test(here)) return;

  if (window.innerWidth < FLOOR) {
    location.replace('Narrow.dc.html?from=' + encodeURIComponent(here) + '&w=' + window.innerWidth);
    return;
  }
  mark();

  function mark() {
    var shown = false;
    function check() {
      if (shown || window.innerWidth >= FLOOR) return;
      shown = true;
      // below 720 there is no working dense state — hand off live rather than pan
      location.replace('Narrow.dc.html?from=' + encodeURIComponent(here) + '&w=' + window.innerWidth);
      return;
    }
    window.addEventListener('resize', check, { passive: true });
    check();
  }
})();
