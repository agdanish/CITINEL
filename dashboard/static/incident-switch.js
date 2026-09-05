// CITINEL — incident switcher. A dropdown on every incident-scoped screen so a
// reader can jump between incidents from any page, instead of walking back to the
// Queue. The chosen id rides on ?id= and propagates screen to screen exactly the
// way a Queue click already does (see api.js currentIncidentId / incidentLink).
//
// Loaded only on the incident-scoped pages (Replay, Confidence, Evidence,
// Compliance, Audit, Approvals), after api.js and nav.js.
//
// Design note: the DC runtime re-renders the page content (a settling mount, an
// ANALYST/CISO toggle, a live tick), which wipes anything injected into its
// header. So this fetches the incident list ONCE, caches it, and only ever
// injects an ALREADY-POPULATED switcher; a MutationObserver re-adds it the
// instant a re-render removes it. There is no async "loading" state to strand on
// a detached node, and it fails closed: any error leaves the page as it was.
(function () {
  var SCOPED = { replay: 1, confidence: 1, evidence: 1, compliance: 1, audit: 1, approvals: 1 };
  var incidents = null;   // cached [{incident_id, state}, ...]

  function currentId() {
    try {
      var id = new URLSearchParams(location.search).get('id');
      if (id) return id;
      var A = window.CITINEL_API;
      return (A && A.currentIncidentId) ? A.currentIncidentId() : null;
    } catch (e) { return null; }
  }
  function base() { try { return (window.CITINEL_API && window.CITINEL_API.BASE) || ''; } catch (e) { return ''; } }
  function root() { return document.querySelector('[data-citinel-page]'); }
  function scoped(r) { try { return !!(r && SCOPED[r.getAttribute('data-citinel-page')]); } catch (e) { return false; } }

  function buildSwitcher() {
    var cur = currentId();
    var wrap = document.createElement('label');
    wrap.setAttribute('data-incident-switch', '');
    wrap.style.cssText = 'flex:none;display:inline-flex;align-items:center;gap:7px;' +
      'font-family:var(--ctn-font-display);font-size:8.5px;letter-spacing:0.12em;' +
      'color:var(--ctn-color-text-muted);white-space:nowrap;margin:0 4px';
    wrap.appendChild(document.createTextNode('INCIDENT'));
    var sel = document.createElement('select');
    sel.setAttribute('aria-label', 'Switch incident');
    sel.style.cssText = 'font-family:var(--ctn-font-mono);font-size:11px;padding:5px 8px;' +
      'border-radius:6px;border:1px solid var(--ctn-color-border-strong);' +
      'background:var(--ctn-color-surface-raised);color:var(--ctn-color-text-primary);cursor:pointer';
    incidents.forEach(function (inc) {
      var o = document.createElement('option');
      o.value = inc.incident_id;
      o.textContent = inc.incident_id + ' · ' + String(inc.state || '').replace(/_/g, ' ').toUpperCase();
      if (inc.incident_id === cur) o.selected = true;
      sel.appendChild(o);
    });
    sel.addEventListener('change', function () {
      if (!sel.value || sel.value === cur) return;
      try { var u = new URL(location.href); u.searchParams.set('id', sel.value); location.href = u.toString(); }
      catch (e) { location.href = location.pathname + '?id=' + encodeURIComponent(sel.value); }
    });
    wrap.appendChild(sel);
    return wrap;
  }

  // The incident screens carry a second bar under the top nav (the ANALYST/CISO
  // depth toggle, the incident id, a RETURN link). That bar has room; the top-nav
  // row does not -- inserting there wraps the header to three lines. So the
  // switcher sits right after the depth toggle, in the incident-context bar.
  function place(r, header, wrap) {
    try {
      var btns = r.querySelectorAll('button');
      for (var i = 0; i < btns.length; i++) {
        if (btns[i].textContent.trim() === 'ANALYST') {
          var box = btns[i].parentElement;                 // the div holding ANALYST + CISO
          if (box && box.parentElement) { box.parentElement.insertBefore(wrap, box.nextSibling); return; }
        }
      }
    } catch (e) {}
    var logo = header.querySelector(':scope > a');          // fallback: header, after the wordmark
    if (logo && logo.nextSibling) header.insertBefore(wrap, logo.nextSibling);
    else header.appendChild(wrap);
  }

  function ensure() {
    try {
      if (!incidents) return;
      var r = root();
      if (!scoped(r)) return;
      if (r.querySelector('[data-incident-switch]')) return;   // already present
      var header = r.querySelector(':scope > header');
      if (!header) return;
      place(r, header, buildSwitcher());
    } catch (e) {}
  }

  function watch() {
    ensure();
    try {
      var mo = new MutationObserver(function () { ensure(); });   // re-add after any re-render
      mo.observe(document.body, { childList: true, subtree: true });
    } catch (e) {}
  }

  function init() {
    // Confirm this is an incident-scoped page (poll briefly; the DC root mounts
    // after DOMContentLoaded), then fetch the list once and start watching.
    var tries = 0;
    (function waitForRoot() {
      var r = root();
      if (r) { if (!scoped(r)) return; }                    // mounted, not incident-scoped: done
      else if (++tries <= 40) { setTimeout(waitForRoot, 150); return; }
      fetch(base() + '/api/incidents?summary=true', { headers: { accept: 'application/json' } })
        .then(function (res) { return res.json(); })
        .then(function (list) { if (Array.isArray(list) && list.length) { incidents = list; watch(); } })
        .catch(function () {});
    })();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
