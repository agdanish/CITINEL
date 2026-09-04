// CITINEL — left navigation rail. Shared across every screen; the top nav stays.
//
// Built from a static list rather than cloned from the page's own <nav>, on
// purpose: Demo and Shell have no header nav, the DC runtime announces no
// "rendered" event to wait for, and six links are incident-scoped and must be
// rebuilt through api.js's incidentLink() so the incident a reader selected
// keeps propagating screen to screen (the same rule the top nav follows).
// Mounted as a sibling of the page root, outside the runtime's template, so
// no hole, sc-for or dc-import is involved and nothing here can render blank.
(function () {
  var KEY = 'citinel.rail';                    // 'open' | 'closed'
  var W_OPEN = 168, W_CLOSED = 44;
  var PAGES = [
    ['Overview.dc.html',   'OVERVIEW',   false],
    ['Queue.dc.html',      'QUEUE',      false],
    ['Replay.dc.html',     'REPLAY',     true],
    ['Confidence.dc.html', 'CONFIDENCE', true],
    ['Evidence.dc.html',   'EVIDENCE',   true],
    ['Approvals.dc.html',  'APPROVALS',  true],
    ['Compliance.dc.html', 'COMPLIANCE', true],
    ['Audit.dc.html',      'AUDIT',      true],
    ['Corpus.dc.html',     'CORPUS',     false],
    ['Eval.dc.html',       'EVAL',       false],
    ['Policy.dc.html',     'POLICY',     false],
    ['Handover.dc.html',   'HANDOVER',   false],
    ['Executive.dc.html',  'EXEC',       false],
    ['Settings.dc.html',   'CONNECTORS', false],
    ['Demo.dc.html',       'DEMO',       false],
    ['Shell.dc.html',      'SHELL',      false]
  ];

  function stored() {
    try { return localStorage.getItem(KEY) === 'closed' ? 'closed' : 'open'; }
    catch (e) { return 'open'; }
  }
  function store(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  function here() {
    var p = location.pathname.split('/').pop() || 'Overview.dc.html';
    return p.toLowerCase();
  }
  function href(page, scoped) {
    var API = window.CITINEL_API;
    return (scoped && API && API.incidentLink) ? API.incidentLink(page) : page;
  }

  function css() {
    var s = document.createElement('style');
    s.setAttribute('data-citinel-rail', '');
    s.textContent = [
      'body{display:flex;margin:0}',
      'body>#dc-root,body>[data-citinel-page],body>[data-screen-label]{flex:1 1 auto;min-width:0}',
      '#citinel-rail{flex:none;box-sizing:border-box;display:flex;flex-direction:column;',
      '  border-right:1px solid var(--ctn-color-border-strong);background:var(--ctn-color-surface-panel);',
      '  height:100vh;position:sticky;top:0;overflow:hidden;transition:width 160ms ease}',
      '#citinel-rail[data-state=open]{width:' + W_OPEN + 'px}',
      '#citinel-rail[data-state=closed]{width:' + W_CLOSED + 'px}',
      '#citinel-rail button{all:unset;cursor:pointer;display:flex;align-items:center;justify-content:center;',
      '  height:52px;flex:none;border-bottom:1px solid var(--ctn-color-border-strong);',
      '  font-family:var(--ctn-font-display);font-size:13px;color:var(--ctn-color-text-primary)}',
      '#citinel-rail button:focus-visible{outline:2px solid var(--ctn-color-text-primary);outline-offset:-2px}',
      '#citinel-rail nav{display:flex;flex-direction:column;overflow-y:auto;overflow-x:hidden;flex:1;padding:6px 0;scrollbar-width:thin}',
      '#citinel-rail a{display:flex;align-items:center;gap:10px;height:34px;padding:0 14px;box-sizing:border-box;',
      '  text-decoration:none;white-space:nowrap;font-family:var(--ctn-font-display);font-size:9.5px;',
      '  letter-spacing:0.12em;color:var(--ctn-color-text-muted);border-left:2px solid transparent}',
      '#citinel-rail a:hover{color:var(--ctn-color-text-primary)}',
      '#citinel-rail a[aria-current=page]{color:var(--ctn-color-text-primary);background:var(--ctn-color-surface-well);',
      '  border-left-color:var(--ctn-color-text-primary)}',
      '#citinel-rail a i{flex:none;width:16px;text-align:center;font-style:normal;font-size:10px}',
      '#citinel-rail[data-state=closed] a span{display:none}',
      '#citinel-rail[data-state=closed] a{padding:0 12px}',
      '@media print{#citinel-rail{display:none}}'
    ].join('\n');
    document.head.appendChild(s);
  }

  // The DC runtime renders every page inside body > #dc-root > div > [data-citinel-page].
  // The rail mounts BESIDE #dc-root, as body's own child, so it lives outside the
  // runtime's territory: a re-render inside #dc-root can never wipe it, and it
  // never has to know how deep the page root sits. Confirmed live 4 Sep 2026 --
  // a body>[data-citinel-page] selector matched nothing and the rail never appeared.
  function mountPoint() {
    return document.getElementById('dc-root')
        || document.querySelector('body>[data-citinel-page]')
        || document.querySelector('body>[data-screen-label]');
  }

  function build() {
    if (document.getElementById('citinel-rail')) return;
    var root = mountPoint();
    if (!root) {
      // The runtime may not have created #dc-root yet; mount the moment it does.
      var mo = new MutationObserver(function () {
        if (mountPoint()) { mo.disconnect(); build(); }
      });
      mo.observe(document.documentElement, { childList: true, subtree: true });
      return;
    }
    css();
    var rail = document.createElement('aside');
    rail.id = 'citinel-rail';
    rail.setAttribute('aria-label', 'CITINEL screens');
    rail.setAttribute('data-state', stored());

    var btn = document.createElement('button');
    btn.type = 'button';
    function paint() {
      var open = rail.getAttribute('data-state') === 'open';
      btn.textContent = open ? '‹' : '›';          // ‹  ›
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Collapse navigation' : 'Expand navigation');
      btn.title = open ? 'Collapse (rail stays collapsed on every screen)' : 'Expand navigation';
    }
    btn.addEventListener('click', function () {
      var next = rail.getAttribute('data-state') === 'open' ? 'closed' : 'open';
      rail.setAttribute('data-state', next); store(next); paint();
    });
    paint();
    rail.appendChild(btn);

    var nav = document.createElement('nav');
    var cur = here();
    PAGES.forEach(function (p) {
      var a = document.createElement('a');
      a.href = href(p[0], p[2]);
      var i = document.createElement('i'); i.textContent = p[1].charAt(0);
      var s = document.createElement('span'); s.textContent = p[1];
      a.appendChild(i); a.appendChild(s);
      a.title = p[1];
      if (p[0].toLowerCase() === cur) a.setAttribute('aria-current', 'page');
      nav.appendChild(a);
    });
    rail.appendChild(nav);
    root.parentNode.insertBefore(rail, root);

    // Another tab collapsing the rail collapses this one too; same pattern as role.js.
    window.addEventListener('storage', function (e) {
      if (e.key === KEY) { rail.setAttribute('data-state', stored()); paint(); }
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build);
  else build();
})();
