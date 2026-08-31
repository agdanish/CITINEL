/* CITINEL — backend seam.
 *
 * One file stands between every screen and the API. Switching a page from scripted demo
 * data to the real service is a `live: false → true` flip on one ENDPOINTS entry, plus
 * pointing BASE at the service if it is not same-origin. No markup moves, no framework.
 *
 * Vanilla ES5-safe: FastAPI serves these files directly, no build step.
 *
 * ── For the backend session ────────────────────────────────────────────────────
 *  1. Same-origin (FastAPI serves this directory): leave BASE as ''.
 *     Cross-origin: set BASE to the service root, e.g. 'http://localhost:8000'.
 *  2. INCIDENT_PRIMARY / INCIDENT_SECONDARY are the only incident ids the UI names.
 *     PRIMARY is INC-0417 — the Cerber chain, 2,487 findings, the id on the deck.
 *     SECONDARY is a placeholder: set it to the second real corpus id.
 *  3. Endpoints marked `live: false` have no route yet. The seam is wired and the call
 *     site exists; flipping the flag is the whole integration for that surface.
 *  4. Every page carries a data-source badge derived from this registry. It is honest by
 *     construction: a page whose endpoints are all `live: false`, or any page when
 *     /healthz does not answer, reads DEMO DATA. Do not hand-edit the badge.
 */
(function () {
  'use strict';

  var API = {
    BASE: '',
    INCIDENT_PRIMARY: 'INC-0417',
    INCIDENT_SECONDARY: 'INC-0416',
    TIMEOUT_MS: 6000,
    reachable: null,          // null = not probed, true/false after probe()
    service: null
  };

  /* ── The contract ─────────────────────────────────────────────────────────────
     Verified against the running service. `live: true` means the route exists today. */
  API.ENDPOINTS = {
    health:       { path: function () { return '/healthz'; },
                    live: true,  note: 'service liveness' },
    incidents:    { path: function () { return '/api/incidents'; },
                    live: true,  note: 'Incident[]' },
    incident:     { path: function (id) { return '/api/incidents/' + id; },
                    live: true,  note: 'Incident, 404 if unknown' },
    audit:        { path: function (id) { return '/api/incidents/' + id + '/audit'; },
                    live: true,  note: 'AuditEntry[], 404 if none' },
    draft:        { path: function (id, kind) { return '/api/incidents/' + id + '/draft?kind=' + (kind || 'certin'); },
                    live: true,  note: '{draft, rendered} · kind=certin|dpdp' },
    policy:       { path: function () { return '/api/policy'; },
                    live: true,  note: '{name, version, policy_sha256, clauses[]}' },
    ledgerVerify: { path: function () { return '/api/ledger/verify'; },
                    live: true,  note: '{intact, message}' },

    /* Not built yet. The agent swarm (step 7), action execution and the eval harness have
       no routes. Paths below are the intended shape, not a promise the service keeps. */
    verdict:      { path: function (id) { return '/api/incidents/' + id + '/verdict'; },
                    live: false, note: 'swarm verdict + citations · agent swarm not running' },
    proposals:    { path: function (id) { return '/api/incidents/' + id + '/proposals'; },
                    live: false, note: 'Response Marshal proposals · not running' },
    execute:      { path: function () { return '/api/actions/execute'; },
                    live: false, note: 'action execution · mocks only, no route' },
    rollback:     { path: function (token) { return '/api/actions/rollback/' + token; },
                    live: false, note: 'rollback by token · no route' },
    evalRuns:     { path: function () { return '/api/eval/runs'; },
                    live: false, note: 'harness runs + denominators · no route' },
    corpusRules:  { path: function () { return '/api/corpus/rules'; },
                    live: false, note: 'sigma corpus + review bench · no route' }
  };

  /* ── Page registry ────────────────────────────────────────────────────────────
     Which endpoints each screen consumes, and what stays scripted regardless.
     HANDOFF.md is the human-readable form of this table; keep them in step. */
  API.PAGES = {
    entry:      { uses: [],                                  scripted: ['statutory clock', 'first-run vs returning session'] },
    shell:      { uses: ['incidents'],                        scripted: ['nav counts', 'annunciator strip'] },
    overview:   { uses: ['incidents', 'policy'],              scripted: ['agent fleet traces', 'autonomy mandate', 'disposition feed'] },
    queue:      { uses: ['incidents'],                        scripted: ['lane A/B split reasoning'] },
    replay:     { uses: ['incident', 'audit', 'verdict'],     scripted: ['citation chips', 'agent timeline', 'kill-chain narrative'] },
    confidence: { uses: ['verdict'],                          scripted: ['supporting/counter ledger', 'retired-evidence trail'] },
    evidence:   { uses: ['incident'],                         scripted: ['external-source provenance', 'quarantine well'] },
    approvals:  { uses: ['policy', 'proposals', 'execute', 'rollback'], scripted: ['blast rings', 'intent preview', 'rollback tokens'] },
    corpus:     { uses: ['corpusRules'],                      scripted: ['accession bench', 'export packet'] },
    eval:       { uses: ['evalRuns'],                         scripted: ['FP rate + denominators', 'inferred cost'] },
    policy:     { uses: ['policy'],                           scripted: ['autonomy dials', 'change history'] },
    compliance: { uses: ['draft', 'incident'],                scripted: ['press mechanics', 'DPDP artifacts'] },
    audit:      { uses: ['audit', 'ledgerVerify'],            scripted: ['detect→sign ribbon geometry'] },
    handover:   { uses: ['incidents', 'audit'],               scripted: ['watch register', 'exceptions'] },
    executive:  { uses: ['incidents', 'policy', 'ledgerVerify'], scripted: ['board narrative', 'quarter figures'] },
    settings:   { uses: ['health'],                           scripted: ['connector roster', 'enrichment quota', 'mock endpoints'] },
    demo:       { uses: [],                                   scripted: ['entire walkthrough, by design'] },
    narrow:     { uses: ['incidents', 'audit'],               scripted: ['same as the console it mirrors'] }
  };

  /* ── One call path ────────────────────────────────────────────────────────────
     Always resolves. Never throws into a render. `source` says where the data came
     from, and callers must surface that rather than silently blending the two. */
  API.get = function (name, a, b) {
    var ep = API.ENDPOINTS[name];
    if (!ep) return Promise.resolve({ ok: false, source: 'scripted', error: 'unknown endpoint ' + name });
    if (!ep.live) return Promise.resolve({ ok: false, source: 'scripted', error: 'endpoint not built: ' + ep.note });

    var url = API.BASE + ep.path(a, b);
    var ctl = typeof AbortController !== 'undefined' ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) ctl.abort(); }, API.TIMEOUT_MS);

    return fetch(url, {
      headers: { accept: 'application/json' },
      signal: ctl ? ctl.signal : undefined
    }).then(function (r) {
      clearTimeout(timer);
      if (!r.ok) return { ok: false, source: 'scripted', status: r.status, error: r.status + ' from ' + url };
      return r.json().then(function (d) { return { ok: true, source: 'live', data: d, url: url }; });
    }).catch(function (e) {
      clearTimeout(timer);
      return { ok: false, source: 'scripted', error: String(e && e.message || e) + ' · ' + url };
    });
  };

  /* Probe once per page load; every badge reads the cached answer. */
  API.probe = function () {
    if (API._probe) return API._probe;
    API._probe = API.get('health').then(function (r) {
      API.reachable = !!r.ok;
      API.service = r.ok && r.data ? r.data.service : null;
      return API.reachable;
    });
    return API._probe;
  };

  /* Convenience wrappers — the shapes screens actually want. */
  API.incidents = function () { return API.get('incidents'); };
  API.incident = function (id) { return API.get('incident', id || API.INCIDENT_PRIMARY); };
  API.auditFor = function (id) { return API.get('audit', id || API.INCIDENT_PRIMARY); };
  API.draftFor = function (id, kind) { return API.get('draft', id || API.INCIDENT_PRIMARY, kind || 'certin'); };
  API.policy = function () { return API.get('policy'); };
  API.verifyLedger = function () { return API.get('ledgerVerify'); };

  /* ── Data-source badge ────────────────────────────────────────────────────────
     Once some pages are wired and others are not, an unmarked mix misrepresents which
     numbers are real. The badge is derived, never authored: it counts live endpoints in
     the page's registry entry and folds in the /healthz result. */
  function verdictFor(key) {
    var p = API.PAGES[key];
    if (!p) return { tag: 'DEMO DATA', detail: 'page not in the API registry' };
    var live = 0, pending = 0, names = [];
    for (var i = 0; i < p.uses.length; i++) {
      var ep = API.ENDPOINTS[p.uses[i]];
      if (!ep) continue;
      if (ep.live) { live++; names.push(p.uses[i]); } else { pending++; }
    }
    if (!live) {
      return { tag: 'DEMO DATA', detail: p.uses.length
        ? 'no route yet for: ' + p.uses.join(', ')
        : 'scripted by design: ' + p.scripted.join('; ') };
    }
    if (!API.reachable) {
      return { tag: 'DEMO DATA', detail: 'backend not reached · would use ' + names.join(', ') };
    }
    if (pending) {
      return { tag: 'MIXED · ' + live + ' LIVE / ' + pending + ' SCRIPTED',
               detail: 'live: ' + names.join(', ') + ' · still scripted: ' + p.scripted.join('; ') };
    }
    return { tag: 'LIVE · ' + names.join(' '), detail: 'served by ' + (API.service || 'citinel-web') };
  }

  function paint() {
    var root = document.querySelector('[data-citinel-page]');
    if (!root) return;
    var key = root.getAttribute('data-citinel-page');
    var v = verdictFor(key);
    var host = root.querySelector(':scope > header') || root;
    var el = host.querySelector('[data-source-badge]');
    if (!el) {
      el = document.createElement('span');
      el.setAttribute('data-source-badge', '');
      el.style.cssText = 'flex:none;font-family:var(--ctn-font-display);font-size:7.5px;' +
        'letter-spacing:0.1em;padding:4px 8px;border-radius:3px;white-space:nowrap;' +
        'color:var(--ctn-color-text-muted);cursor:help';
      host.appendChild(el);
    }
    var isLive = v.tag.indexOf('LIVE') === 0;
    el.style.border = '1px ' + (isLive ? 'solid' : 'dashed') + ' var(--ctn-color-border-strong)';
    el.style.color = isLive ? 'var(--ctn-color-text-primary)' : 'var(--ctn-color-text-muted)';
    el.textContent = v.tag;
    el.title = v.detail;
  }

  API.badge = paint;

  function boot() {
    paint();                                   // honest immediately: DEMO until proven live
    API.probe().then(paint);                   // upgrade only if /healthz answers
    // the DC runtime mounts after DOMContentLoaded, so re-paint once the root appears
    var tries = 0;
    var iv = setInterval(function () {
      if (document.querySelector('[data-citinel-page] [data-source-badge]') || ++tries > 40) {
        clearInterval(iv);
      } else { paint(); }
    }, 150);
  }

  window.CITINEL_API = API;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
