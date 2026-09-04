// CITINEL — left navigation rail. Shared across every screen; the top nav stays.
//
// Icon-only by default. Every icon carries its label on demand: hover or keyboard
// focus shows a translucent label beside that icon and nothing else moves; the
// control at the top expands the rail persistently for anyone who wants the
// labels to stay, and that choice is remembered on the device. This is the
// established shape for a persistent rail (a navigation rail with hover labels,
// an activity bar): icons alone are rarely understood, and a rail that expands
// itself on hover jumps the whole page sideways every time the pointer crosses
// the edge. Neither problem exists here.
//
// The glyphs are the instruments the screens already borrow (Direction A on the
// "CITINEL Rail Icons" canvas): the countdown gauge, the strip board, the key
// switch turned to ARMED, the clock with its six-hour sector, chain links for
// the ledger, the boom gate for policy, the completed ring for Exec. Stroke-based
// on a 16px grid, currentColor, so they take the row's own colour.
//
// Built from a static list rather than cloned from each page's own <nav>, on
// purpose: Demo and Shell have no header nav, the DC runtime announces no
// "rendered" event to wait for, and six links are incident-scoped and must be
// rebuilt through api.js's incidentLink() so the incident a reader selected
// keeps propagating screen to screen. Mounted beside #dc-root, outside the
// runtime's territory, so no hole, sc-for or dc-import is involved and a
// re-render can never wipe it.
(function () {
  var KEY = 'citinel.rail';                    // 'open' | 'closed'; absent = closed
  var W_OPEN = 168, W_CLOSED = 44;
  var S = 'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"';
  var F = 'fill="currentColor" stroke="none"';
  function svg(inner) { return '<svg viewBox="0 0 16 16" width="16" height="16" ' + S + ' aria-hidden="true">' + inner + '</svg>'; }

  // [file, label, incident-scoped, glyph]
  var PAGES = [
    ['Overview.dc.html',   'OVERVIEW',   false, '<path d="M3.5 11.5A5.5 5.5 0 1 1 12.5 11.5"/><path d="M8 8l2.6-2.6"/><circle cx="8" cy="8" r="0.9" ' + F + '/>'],
    ['Queue.dc.html',      'QUEUE',      false, '<rect x="2" y="3" width="12" height="2.6" rx=".6"/><rect x="2" y="6.7" width="12" height="2.6" rx=".6"/><rect x="2" y="10.4" width="12" height="2.6" rx=".6"/><rect x="3" y="3.8" width="1.6" height="1" ' + F + '/>'],
    ['Replay.dc.html',     'REPLAY',     true,  '<path d="M2 11.5h12"/><path d="M4.5 11.5v-2M8 11.5v-4M11.5 11.5v-2"/><path d="M8 3l-1.6 2.2h3.2z" ' + F + '/>'],
    ['Confidence.dc.html', 'CONFIDENCE', true,  '<path d="M2.5 12A6 6 0 0 1 13.5 12"/><path d="M3.9 9.4l1 .6M12.1 9.4l-1 .6"/><path d="M8 12l3-5.4"/><circle cx="8" cy="12" r="1.1" ' + F + '/>'],
    ['Evidence.dc.html',   'EVIDENCE',   true,  '<circle cx="6.5" cy="6.5" r="3.6"/><path d="M9.2 9.2l4 4"/><path d="M5 6.5h3"/>'],
    ['Approvals.dc.html',  'APPROVALS',  true,  '<circle cx="8" cy="8" r="5.6"/><path d="M8 4.4v3.6"/><path d="M8 8l2.6 2.6"/>'],
    ['Compliance.dc.html', 'COMPLIANCE', true,  '<circle cx="8" cy="8" r="5.6"/><path d="M8 8V2.4A5.6 5.6 0 0 1 13.6 8z" ' + F + ' opacity=".55"/><path d="M8 8l-2.6 2.2"/>'],
    ['Audit.dc.html',      'AUDIT',      true,  '<rect x="1.5" y="6" width="7" height="4" rx="2"/><rect x="7.5" y="6" width="7" height="4" rx="2"/>'],
    ['Corpus.dc.html',     'CORPUS',     false, '<rect x="4.5" y="2.5" width="9" height="11" rx="1"/><path d="M2.5 5v8.5H11"/><path d="M7 6h4M7 8.6h4"/>'],
    ['Eval.dc.html',       'EVAL',       false, '<path d="M2 5h12v6H2z"/><path d="M5 5v2.6M8 5v4M11 5v2.6"/>'],
    ['Policy.dc.html',     'POLICY',     false, '<path d="M3.5 13V6.5"/><path d="M3.5 7.2l10-3"/><circle cx="3.5" cy="6.5" r="1.1" ' + F + '/><path d="M2 13h3"/>'],
    ['Handover.dc.html',   'HANDOVER',   false, '<path d="M2 5.5h6"/><path d="M8 10.5h6"/><path d="M6.8 5.5l2.4 2.5-2.4 2.5"/>'],
    ['Executive.dc.html',  'EXEC',       false, '<circle cx="8" cy="8" r="5.6"/><circle cx="8" cy="8" r="1.6" ' + F + '/>'],
    ['Settings.dc.html',   'CONNECTORS', false, '<path d="M5.5 2.5v3M10.5 2.5v3"/><path d="M3.5 5.5h9v2a4.5 4.5 0 0 1-9 0z"/><path d="M8 12v2"/>'],
    ['Demo.dc.html',       'DEMO',       false, '<rect x="2" y="3" width="12" height="10" rx="1"/><path d="M6.6 6l4 2-4 2z" ' + F + '/>'],
    ['Shell.dc.html',      'SHELL',      false, '<rect x="2" y="2.5" width="12" height="11" rx="1"/><path d="M2 5.6h12"/><path d="M6 5.6v7.9"/>']
  ];

  function stored() {
    try { return localStorage.getItem(KEY) === 'open' ? 'open' : 'closed'; }
    catch (e) { return 'closed'; }
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
      '#citinel-rail a:hover,#citinel-rail a:focus-visible{color:var(--ctn-color-text-primary);outline:none}',
      '#citinel-rail a[aria-current=page]{color:var(--ctn-color-text-primary);background:var(--ctn-color-surface-well);',
      '  border-left-color:var(--ctn-color-text-primary)}',
      '#citinel-rail a i{flex:none;display:flex;align-items:center;justify-content:center;width:16px;height:16px;font-style:normal}',
      '#citinel-rail a i svg{display:block}',
      '#citinel-rail[data-state=closed] a span{display:none}',
      '#citinel-rail[data-state=closed] a{padding:0 12px}',
      // the brand row: the mark sits in the rail's own top row, on the screen header's
      // line, and the row is the expand control. Open shows the lockup with the chevron
      // at the right edge; closed shows the falcon alone, centred in 44px, because a
      // 90px lockup and a chevron do not both fit and the mark is the half worth keeping.
      '#citinel-rail button.brand{justify-content:space-between;gap:8px;padding:0 12px;box-sizing:border-box;width:100%}',
      '#citinel-rail button.brand picture{display:block;flex:none;line-height:0}',
      '#citinel-rail button.brand img{display:block}',
      '#citinel-rail .brand-lockup img{width:90px;height:34px}',
      '#citinel-rail .brand-falcon img{width:24px;height:24px}',
      '#citinel-rail button.brand .chev{flex:none;font-size:15px;line-height:1;color:var(--ctn-color-text-muted)}',
      '#citinel-rail button.brand:hover .chev,#citinel-rail button.brand:focus-visible .chev{color:var(--ctn-color-text-primary)}',
      '#citinel-rail[data-state=open] .brand-falcon{display:none}',
      '#citinel-rail[data-state=closed] .brand-lockup{display:none}',
      '#citinel-rail[data-state=closed] button.brand{justify-content:center;padding:0}',
      '#citinel-rail[data-state=closed] button.brand .chev{display:none}',
      // the footer: state word on one line, the operator's name on the next. Michroma is
      // wide; 'ARMED · DANISH' on one line needs ~200px in a 168px rail and was clipped
      // mid-glyph, so the two parts stack and a long name gets an ellipsis, never a cut.
      '#citinel-rail a.arm{margin-top:auto;border-left:0;border-top:1px solid var(--ctn-color-border-strong);height:auto;min-height:40px;padding:9px 14px;flex:none}',
      '#citinel-rail a.arm i{font-size:12px;line-height:1}',
      '#citinel-rail a.arm span{display:flex;flex-direction:column;gap:3px;min-width:0;overflow:hidden}',
      '#citinel-rail a.arm span b{font-weight:normal;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.2}',
      '#citinel-rail a.arm span b+b{font-size:8.5px;letter-spacing:0.1em;color:var(--ctn-color-text-muted)}',
      '#citinel-rail a.arm[data-armed=true] span b+b{color:var(--ctn-color-text-secondary)}',
      '#citinel-rail a.arm[data-armed=true]{color:var(--ctn-color-text-primary)}',
      '#citinel-rail a.arm[data-armed=true] i{color:var(--ctn-color-ok)}',
      '#citinel-rail a.arm[data-armed=false] i{color:var(--ctn-color-text-muted)}',
      // the label flyout: fixed beside the hovered icon, translucent, never in the layout
      '#citinel-rail-tip{position:fixed;z-index:1000;pointer-events:none;transform:translateY(-50%);',
      '  padding:7px 11px;border:1px solid var(--ctn-color-border-strong);border-radius:6px;',
      '  background:var(--ctn-color-surface-panel);background:color-mix(in oklch,var(--ctn-color-surface-panel) 88%,transparent);',
      '  backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);',
      '  font-family:var(--ctn-font-display);font-size:9.5px;letter-spacing:0.12em;color:var(--ctn-color-text-primary);',
      '  white-space:nowrap;opacity:0;transition:opacity 110ms ease}',
      '#citinel-rail-tip[data-show=true]{opacity:1}',
      '@media (prefers-reduced-motion:reduce){#citinel-rail,#citinel-rail-tip{transition:none}}',
      '@media print{#citinel-rail,#citinel-rail-tip{display:none}}'
    ].join('\n');
    document.head.appendChild(s);
  }

  // The DC runtime renders every page inside body > #dc-root > div > [data-citinel-page].
  // The rail mounts BESIDE #dc-root, as body's own child, outside the runtime's territory.
  function mountPoint() {
    return document.getElementById('dc-root')
        || document.querySelector('body>[data-citinel-page]')
        || document.querySelector('body>[data-screen-label]');
  }

  function build() {
    if (document.getElementById('citinel-rail')) return;
    var root = mountPoint();
    if (!root) {
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

    // -- the label flyout ---------------------------------------------------
    var tip = document.createElement('div');
    tip.id = 'citinel-rail-tip'; tip.setAttribute('role', 'tooltip');
    document.body.appendChild(tip);
    var tipTimer = null;
    function showTip(anchor, text, immediate, always) {
      // labels are already visible when the rail is open, except the footer's: its
      // flyout carries the expiry time, which the two-line label does not
      if (!always && rail.getAttribute('data-state') === 'open') return;
      clearTimeout(tipTimer);
      tipTimer = setTimeout(function () {
        tip.textContent = text;
        var r = anchor.getBoundingClientRect();
        tip.style.top = (r.top + r.height / 2) + 'px';
        tip.style.left = (r.right + 8) + 'px';
        tip.setAttribute('data-show', 'true');
      }, immediate ? 0 : 120);                                       // a short intent delay, no flicker
    }
    function hideTip() { clearTimeout(tipTimer); tip.removeAttribute('data-show'); }
    function labelled(el, text, always) {
      el.addEventListener('mouseenter', function () { showTip(el, typeof text === 'function' ? text() : text, false, always); });
      el.addEventListener('focus',      function () { showTip(el, typeof text === 'function' ? text() : text, true, always); });
      el.addEventListener('mouseleave', hideTip);
      el.addEventListener('blur', hideTip);
    }
    window.addEventListener('scroll', hideTip, true);
    window.addEventListener('keydown', function (e) { if (e.key === 'Escape') hideTip(); });

    // -- the brand, and expand / collapse -----------------------------------
    // The top row carried a lone chevron in 168px of empty panel, and the mark
    // appeared only in the screen's own header, so the rail read as an unlabelled
    // strip of glyphs. It now opens with the mark, on the same line as the header's.
    function mark(cls, webp, png) {
      var pic = document.createElement('picture');
      pic.className = cls;
      var src = document.createElement('source');
      src.type = 'image/webp'; src.srcset = webp;
      var img = document.createElement('img');
      img.src = png; img.alt = ''; img.decoding = 'async';   // decorative: the button is labelled
      pic.appendChild(src); pic.appendChild(img);
      return pic;
    }
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'brand';
    btn.appendChild(mark('brand-lockup', 'assets/mark-white-254.webp', 'assets/mark-white-254.png'));
    btn.appendChild(mark('brand-falcon', 'assets/falcon-white-96.webp', 'assets/falcon-white-96.png'));
    var chev = document.createElement('span');
    chev.className = 'chev'; chev.setAttribute('aria-hidden', 'true');
    btn.appendChild(chev);
    function paint() {
      var open = rail.getAttribute('data-state') === 'open';
      chev.textContent = open ? '‹' : '›';                  // ‹  ›
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Collapse navigation' : 'Expand navigation');
      btn.title = open ? 'Collapse to icons (remembered on this device)' : 'Expand to show labels (remembered on this device)';
      if (open) hideTip();
    }

    // Two alignments, and they are not the same one. The rail's divider belongs on the
    // screen header's own rule, so the two columns share a line: every header here is
    // min-height:52px and wraps TALLER when its row runs out of width (a11y.css), so the
    // height is measured, never assumed. But a header that wrapped to 119px would then
    // centre the rail's mark against the middle of a two-row block, sitting it well below
    // the header's own logo. So the mark is centred on that logo's line instead, and the
    // rest of the block is padding. Executive has no header and keeps the 52px default.
    var ro = null;
    function alignBrand() {
      var page = document.querySelector('[data-citinel-page]');
      var hdr = page && page.querySelector(':scope > header');
      if (!hdr) { btn.style.height = '52px'; btn.style.paddingBottom = ''; return false; }
      var hr = hdr.getBoundingClientRect();
      var h = Math.round(hr.height);
      if (h < 44) { btn.style.height = '52px'; btn.style.paddingBottom = ''; return true; }
      btn.style.height = h + 'px';
      var logo = hdr.querySelector('a picture, a img, a svg');
      var lr = logo && logo.getBoundingClientRect();
      // the band the header's own logo is centred in, measured from the header's top edge
      var band = lr && lr.height ? Math.round((lr.top - hr.top) * 2 + lr.height) : 52;
      // floor is the rail mark's own height, not the row height: on a header that
      // wrapped, the logo is top-aligned in a 34px line, and a 44px floor pushed the
      // rail's mark 5px below it -- visible, and the whole point of this measurement.
      btn.style.paddingBottom = Math.max(0, h - Math.max(24, band)) + 'px';
      return true;
    }
    function watchHeader() {
      var page = document.querySelector('[data-citinel-page]');
      var hdr = page && page.querySelector(':scope > header');
      if (!hdr) return false;
      if (window.ResizeObserver) {
        if (ro) ro.disconnect();
        ro = new ResizeObserver(alignBrand);
        ro.observe(hdr);
      }
      alignBrand();
      return true;
    }
    // the DC runtime mounts the screen after this script runs, so keep looking briefly
    if (!watchHeader()) {
      var tries = 0;
      var iv = setInterval(function () {
        if (watchHeader() || ++tries > 40) clearInterval(iv);
      }, 150);
    }
    window.addEventListener('resize', alignBrand);
    btn.addEventListener('click', function () {
      var next = rail.getAttribute('data-state') === 'open' ? 'closed' : 'open';
      rail.setAttribute('data-state', next); store(next); paint();
    });
    labelled(btn, 'EXPAND');
    paint();
    rail.appendChild(btn);

    // -- the screens --------------------------------------------------------
    var nav = document.createElement('nav');
    var cur = here();
    PAGES.forEach(function (p) {
      var a = document.createElement('a');
      a.href = href(p[0], p[2]);
      var i = document.createElement('i'); i.innerHTML = svg(p[3]);
      var s = document.createElement('span'); s.textContent = p[1];
      a.appendChild(i); a.appendChild(s);
      a.setAttribute('aria-label', p[1]);
      if (p[0].toLowerCase() === cur) a.setAttribute('aria-current', 'page');
      labelled(a, p[1]);
      nav.appendChild(a);
    });
    rail.appendChild(nav);

    // -- the arming indicator -----------------------------------------------
    var arm = document.createElement('a');
    arm.className = 'arm'; arm.href = 'Settings.dc.html';
    var dot = document.createElement('i'); var lab = document.createElement('span');
    arm.appendChild(dot); arm.appendChild(lab); rail.appendChild(arm);
    function armText() {
      var API = window.CITINEL_API;
      var st = (API && API.armState) ? API.armState() : { armed: false };
      var when = '';
      if (st.armed && st.expiresAt) {
        try { when = ' · EXPIRES ' + new Intl.DateTimeFormat('en-IN', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'Asia/Kolkata' }).format(new Date(st.expiresAt)) + ' IST'; } catch (e) {}
      }
      return st.armed ? ('ARMED · ' + (st.name || 'UNNAMED').toUpperCase() + when) : 'READ-ONLY · CLICK TO ARM';
    }
    function paintArm() {
      var API = window.CITINEL_API;
      var st = (API && API.armState) ? API.armState() : { armed: false };
      arm.setAttribute('data-armed', st.armed ? 'true' : 'false');
      dot.textContent = st.armed ? '●' : '○';
      var line1 = document.createElement('b'), line2 = document.createElement('b');
      line1.textContent = st.armed ? 'ARMED' : 'READ-ONLY';
      line2.textContent = st.armed ? (st.name || 'UNNAMED').toUpperCase() : 'TAP TO ARM';
      lab.textContent = ''; lab.appendChild(line1); lab.appendChild(line2);
      arm.setAttribute('aria-label', armText());
    }
    labelled(arm, armText, true);
    paintArm();
    window.addEventListener('citinel:arm', paintArm);
    window.addEventListener('storage', function (e) { if (e.key === 'citinel.operator') paintArm(); });
    setInterval(paintArm, 60000);

    root.parentNode.insertBefore(rail, root);

    window.addEventListener('storage', function (e) {
      if (e.key === KEY) { rail.setAttribute('data-state', stored()); paint(); }
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build);
  else build();
})();
