/* CITINEL — the persistent rail. One navigation on every screen.
 *
 * Shell had a grouped left rail; the other fifteen screens each carried their
 * own inline horizontal strip. Same product, two different ways to move around
 * it, and nothing to tell an operator which screens belong together.
 *
 * This renders Shell's rail — the same four sections, the same order — on
 * every page that loads it, from one place. It is injected rather than pasted
 * into fifteen bespoke compositions on purpose: those layouts are built around
 * a full-width strip, and rewriting each one the day before a demo is how a
 * screen breaks in a way nobody notices until someone else is looking.
 *
 * It starts COLLAPSED. A page that has never seen it renders exactly as it did
 * before, and opening the rail is the operator's choice, remembered per
 * browser the way role.js remembers analyst/CISO depth. The existing top strip
 * is left alone; this sits beside it rather than replacing it.
 *
 * Vanilla ES5-safe, no build step, no dependencies — FastAPI serves this file
 * straight from disk.
 */
(function () {
  'use strict';

  // The DC runtime re-injects each page's <helmet> scripts after mount, so
  // this file executes twice per load. One rail per page; the second call is
  // a no-op rather than a duplicate rail stacked on the first.
  if (window.CITINEL_NAV) return;
  window.CITINEL_NAV = true;

  var KEY = 'citinel.railOpen';
  var SECTIONS = [
    { name: 'FLOOR', items: [
      ['Overview', 'Overview.dc.html'],
      ['Alert queue', 'Queue.dc.html'],
      ['Incident detail', 'Replay.dc.html'],
      ['Approvals', 'Approvals.dc.html']
    ]},
    { name: 'EVIDENCE', items: [
      ['Evidence viewer', 'Evidence.dc.html'],
      ['Confidence panel', 'Confidence.dc.html'],
      ['Audit log', 'Audit.dc.html'],
      ['Regulatory clocks', 'Compliance.dc.html']
    ]},
    { name: 'DETECTION', items: [
      ['Sigma corpus', 'Corpus.dc.html'],
      ['Policy & guardrails', 'Policy.dc.html'],
      ['Detection eval', 'Eval.dc.html'],
      ['Demo mode', 'Demo.dc.html']
    ]},
    { name: 'WATCH', items: [
      ['Shift handover', 'Handover.dc.html'],
      ['Connectors', 'Settings.dc.html'],
      ['Executive', 'Executive.dc.html'],
      ['Operations floor', 'Shell.dc.html']
    ]}
  ];

  function isOpen() {
    try { return localStorage.getItem(KEY) === '1'; } catch (e) { return false; }
  }
  function remember(open) {
    try { localStorage.setItem(KEY, open ? '1' : '0'); } catch (e) {}
  }

  var here = (location.pathname.split('/').pop() || 'Overview.dc.html');

  function build() {
    var rail = document.createElement('nav');
    rail.id = 'citinel-rail';
    rail.setAttribute('aria-label', 'CITINEL sections');

    var open = isOpen();
    rail.style.cssText = [
      'position:fixed', 'left:0', 'top:0', 'bottom:0', 'z-index:900',
      'width:' + (open ? '212px' : '38px'),
      'background:var(--ctn-color-surface-shell, #0b0f14)',
      'border-right:1px solid var(--ctn-color-border-strong, #2a3441)',
      'display:flex', 'flex-direction:column',
      'transition:width 140ms ease', 'overflow:hidden',
      'font-family:var(--ctn-font-display, ui-monospace, monospace)'
    ].join(';');

    var toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.id = 'citinel-rail-toggle';
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.title = 'Show or hide the section rail';
    toggle.style.cssText = [
      'flex:none', 'height:38px', 'width:100%', 'cursor:pointer',
      'background:none', 'border:none',
      'border-bottom:1px solid var(--ctn-color-border-hairline, #1b2330)',
      'color:var(--ctn-color-text-muted, #7c8ba1)',
      'font-family:inherit', 'font-size:11px', 'letter-spacing:0.14em',
      'display:flex', 'align-items:center', 'gap:10px',
      'padding:0 12px', 'text-align:left'
    ].join(';');
    toggle.innerHTML = '<span aria-hidden="true">' + (open ? '‹‹' : '››') + '</span>' +
                       '<span class="citinel-rail-label">SECTIONS</span>';

    var body = document.createElement('div');
    body.style.cssText = 'flex:1;min-height:0;overflow-y:auto;padding:6px 0';

    SECTIONS.forEach(function (sec) {
      var h = document.createElement('div');
      h.className = 'citinel-rail-label';
      h.textContent = sec.name;
      h.style.cssText = [
        'font-size:9px', 'letter-spacing:0.16em',
        'color:var(--ctn-color-text-disabled, #55627a)',
        'padding:11px 12px 5px'
      ].join(';');
      body.appendChild(h);

      sec.items.forEach(function (it) {
        var a = document.createElement('a');
        var current = it[1] === here;
        a.href = it[1];
        a.title = it[0];
        if (current) a.setAttribute('aria-current', 'page');
        a.style.cssText = [
          'display:flex', 'align-items:center', 'gap:10px',
          'padding:6px 12px', 'text-decoration:none', 'font-size:11px',
          'white-space:nowrap',
          'color:' + (current ? 'var(--ctn-color-text-primary, #e8eef7)'
                              : 'var(--ctn-color-text-secondary, #9fb0c7)'),
          'border-left:2px solid ' + (current ? 'var(--ctn-color-state-cited, #d98a2b)' : 'transparent')
        ].join(';');
        // A dot so the collapsed rail still shows which screen you are on.
        a.innerHTML = '<span aria-hidden="true" style="flex:none;width:5px;height:5px;border-radius:50%;background:' +
          (current ? 'var(--ctn-color-state-cited, #d98a2b)' : 'var(--ctn-color-text-disabled, #55627a)') +
          '"></span><span class="citinel-rail-label">' + it[0] + '</span>';
        body.appendChild(a);
      });
    });

    rail.appendChild(toggle);
    rail.appendChild(body);

    function paint(o) {
      rail.style.width = o ? '212px' : '38px';
      toggle.setAttribute('aria-expanded', o ? 'true' : 'false');
      toggle.firstChild.textContent = o ? '‹‹' : '››';
      var labels = rail.querySelectorAll('.citinel-rail-label');
      for (var i = 0; i < labels.length; i++) {
        labels[i].style.display = o ? '' : 'none';
      }
      // The page keeps its own layout; it is only pushed clear of the rail.
      document.body.style.paddingLeft = (o ? 212 : 38) + 'px';
    }

    toggle.addEventListener('click', function () {
      var next = !isOpen();
      remember(next);
      paint(next);
    });

    document.body.appendChild(rail);
    paint(open);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
