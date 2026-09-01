/* CITINEL — backend seam.
 *
 * One file stands between every screen and the API. A screen goes live in two moves, and
 * both are required: its own <script data-dc-script> reads the endpoint through API.get (or
 * one of the wrappers below), AND the ENDPOINTS entry it reads is `live: true`. Pointing BASE
 * at the service covers the cross-origin case. No markup moves, no framework.
 *
 * The data-source badge every page carries is derived from what the page ACTUALLY read on
 * this load (API.consumed), never from the registry alone. The 1 Sep 2026 wiring audit found
 * every page declared endpoints in API.PAGES that no page script ever called -- the moment
 * /healthz answered, the badge would have painted LIVE over scripted fiction. Declaring an
 * endpoint is intent; reading it is the fact the badge reports.
 *
 * Vanilla ES5-safe: FastAPI serves these files directly, no build step.
 *
 * ── For the backend session ────────────────────────────────────────────────────
 *  1. Same-origin (FastAPI serves this directory): leave BASE as ''.
 *     Cross-origin: set BASE to the service root, e.g. 'http://localhost:8000'.
 *  2. INCIDENT_PRIMARY / INCIDENT_SECONDARY are the only incident ids the UI names.
 *     PRIMARY is INC-0417 — the Cerber chain, 2,487 findings, the id on the deck.
 *     SECONDARY is INC-0416 — the second real corpus id, 337 findings.
 *  3. Endpoints marked `live: false` have no route yet. API.get short-circuits them with
 *     source:'scripted' and makes no network call. Once the route exists, flip the flag AND
 *     make the page read it -- the badge will not move until the page does.
 *  4. Every page carries a data-source badge derived from this registry plus API.consumed.
 *     It is honest by construction: a page reads DEMO DATA until its own script has read at
 *     least one live endpoint on this load, and MIXED until it has read all it declares.
 *     Do not hand-edit the badge.
 *  5. Incident bodies carry every finding's raw log line (INC-0417 alone is ~3.8 MB) and the
 *     ledger-verify route waits on the external Lyzr witness, so the wrappers for those use
 *     BULK_TIMEOUT_MS rather than the probe timeout.
 */
(function () {
  'use strict';
  // The DC runtime re-injects each page's <helmet> scripts into <head> after mount, so this
  // file executes twice per load. A second instance would replace window.CITINEL_API with an
  // empty `consumed` registry and repaint the badge DEMO over a page that had already read
  // live data. One instance per page, the first one wins, the second is a no-op.
  if (window.CITINEL_API) return;

  var API = {
    BASE: '',
    INCIDENT_PRIMARY: 'INC-0417',
    INCIDENT_SECONDARY: 'INC-0416',
    TIMEOUT_MS: 6000,          // probes and small reads
    BULK_TIMEOUT_MS: 20000,    // incident bodies, audit chains, drafts, ledger verify
    reachable: null,           // null = not probed, true/false after probe()
    service: null,             // /healthz's service name once probed
    corpus: null,              // /api/source's answer: 'live' pipeline output or the committed 'seed'
    consumed: {}               // endpoint name -> 'live' | 'failed', written by API.get as pages read
  };

  /* ── The contract ─────────────────────────────────────────────────────────────
     Verified against the running service. `live: true` means the route exists today. */
  API.ENDPOINTS = {
    health:       { path: function () { return '/healthz'; },
                    live: true,  note: 'service liveness' },
    source:       { path: function () { return '/api/source'; },
                    live: true,  note: '{source: live|seed, incident_count, ...} · which corpus answers' },
    incidents:    { path: function () { return '/api/incidents'; },
                    live: true,  note: 'Incident[] · full bodies, every finding' },
    incident:     { path: function (id) { return '/api/incidents/' + id; },
                    live: true,  note: 'Incident, 404 if unknown · X-Citinel-Role adapts depth' },
    audit:        { path: function (id) { return '/api/incidents/' + id + '/audit'; },
                    live: true,  note: 'AuditEntry[], 404 if none · includes the swarm trail' },
    draft:        { path: function (id, kind) { return '/api/incidents/' + id + '/draft?kind=' + (kind || 'certin'); },
                    live: true,  note: '{draft, rendered, guard} · kind=certin|dpdp' },
    policy:       { path: function () { return '/api/policy'; },
                    live: true,  note: '{name, version, policy_sha256, clauses[]}' },
    ledgerVerify: { path: function () { return '/api/ledger/verify'; },
                    live: true,  note: '{intact, message, witness}' },
    evalRuns:     { path: function () { return '/api/eval'; },
                    live: true,  note: '{measured[], unmeasured[], ...} · harness report, denominators included' },

    /* Not built yet. The swarm runs (step 7 is live) but its verdict and proposals are printed
       by the CLI and not persisted or served; action execution and the corpus have no routes.
       Paths below are the intended shape, not a promise the service keeps. */
    verdict:      { path: function (id) { return '/api/incidents/' + id + '/verdict'; },
                    live: false, note: 'swarm verdict + citations · produced live, not persisted or served yet' },
    proposals:    { path: function (id) { return '/api/incidents/' + id + '/proposals'; },
                    live: false, note: 'Response Marshal proposals · produced live, not persisted or served yet' },
    execute:      { path: function () { return '/api/actions/execute'; },
                    live: false, note: 'action execution · mocks only, no route' },
    rollback:     { path: function (token) { return '/api/actions/rollback/' + token; },
                    live: false, note: 'rollback by token · no route' },
    corpusRules:  { path: function () { return '/api/corpus/rules'; },
                    live: false, note: 'sigma corpus + review bench · no route' }
  };

  /* ── Page registry ────────────────────────────────────────────────────────────
     Which endpoints each screen declares, and what stays scripted regardless. Declaring is
     not reading: the badge only counts an endpoint once the page's script has read it.
     HANDOFF.md is the human-readable form of this table; keep them in step. */
  API.PAGES = {
    entry:      { uses: [],                                  scripted: ['statutory clock', 'first-run vs returning session'] },
    shell:      { uses: ['incidents'],                        scripted: ['nav counts', 'annunciator strip'] },
    overview:   { uses: ['incidents', 'policy'],              scripted: ['agent fleet traces', 'autonomy mandate', 'disposition feed'] },
    queue:      { uses: ['incidents', 'audit'],               scripted: ['belt-dot decoration', '?state=quiet|firstrun demo panels'] },
    replay:     { uses: ['incident', 'audit', 'verdict'],     scripted: ['citation chips', 'agent timeline', 'kill-chain narrative'] },
    confidence: { uses: ['verdict'],                          scripted: ['supporting/counter ledger', 'retired-evidence trail'] },
    evidence:   { uses: ['incident', 'audit'],                scripted: [] },
    approvals:  { uses: ['policy', 'proposals', 'execute', 'rollback'], scripted: ['blast rings', 'intent preview', 'rollback tokens'] },
    corpus:     { uses: ['corpusRules'],                      scripted: ['accession bench', 'export packet'] },
    eval:       { uses: ['evalRuns'],                         scripted: ['FP rate + denominators', 'inferred cost'] },
    policy:     { uses: ['policy'],                           scripted: ['autonomy dials', 'change history'] },
    compliance: { uses: ['draft', 'incident'],                scripted: ['press mechanics', 'DPDP artifacts'] },
    audit:      { uses: ['audit', 'ledgerVerify'],            scripted: [] },
    handover:   { uses: ['incidents', 'audit'],               scripted: ['watch register', 'exceptions'] },
    executive:  { uses: ['incidents', 'policy', 'ledgerVerify'], scripted: ['board narrative', 'quarter figures'] },
    settings:   { uses: ['health'],                           scripted: ['connector roster', 'enrichment quota', 'mock endpoints'] },
    demo:       { uses: [],                                   scripted: ['entire walkthrough, by design'] },
    narrow:     { uses: ['incidents', 'audit'],               scripted: ['same as the console it mirrors'] }
  };

  /* ── One call path ────────────────────────────────────────────────────────────
     Always resolves. Never throws into a render. `source` says where the data came
     from, and callers must surface that rather than silently blending the two.
     opts.timeoutMs overrides the probe timeout; opts.probe keeps the call out of
     API.consumed (the health/source probes are the seam's, not the page's). */
  API.get = function (name, a, b, opts) {
    opts = opts || {};
    var ep = API.ENDPOINTS[name];
    if (!ep) return Promise.resolve({ ok: false, source: 'scripted', error: 'unknown endpoint ' + name });
    if (!ep.live) return Promise.resolve({ ok: false, source: 'scripted', error: 'endpoint not built: ' + ep.note });

    var url = API.BASE + ep.path(a, b);
    var ctl = typeof AbortController !== 'undefined' ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) ctl.abort(); }, opts.timeoutMs || API.TIMEOUT_MS);

    function record(res) {
      if (!opts.probe) {
        API.consumed[name] = res.ok ? 'live' : 'failed';
        paint();                                   // the badge follows the read, not the registry
      }
      return res;
    }

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
    }).then(record);
  };

  /* Probe once per page load; every badge reads the cached answer. /api/source is asked
     alongside /healthz because "the service is up" and "it is serving the live corpus rather
     than the committed seed slice" are different facts, and the badge states both. */
  API.probe = function () {
    if (API._probe) return API._probe;
    API._probe = API.get('health', null, null, { probe: true }).then(function (r) {
      API.reachable = !!r.ok;
      API.service = r.ok && r.data ? r.data.service : null;
      if (!r.ok) return false;
      return API.get('source', null, null, { probe: true }).then(function (s) {
        API.corpus = s.ok && s.data ? s.data.source : null;
        return true;
      });
    });
    return API._probe;
  };

  /* Convenience wrappers — the shapes screens actually want. */
  var BULK = { timeoutMs: API.BULK_TIMEOUT_MS };
  API.incidents = function () { return API.get('incidents', null, null, BULK); };
  API.incident = function (id) { return API.get('incident', id || API.INCIDENT_PRIMARY, null, BULK); };
  API.auditFor = function (id) { return API.get('audit', id || API.INCIDENT_PRIMARY, null, BULK); };
  API.draftFor = function (id, kind) { return API.get('draft', id || API.INCIDENT_PRIMARY, kind || 'certin', BULK); };
  API.policy = function () { return API.get('policy'); };
  API.verifyLedger = function () { return API.get('ledgerVerify', null, null, BULK); };
  API.evalReport = function () { return API.get('evalRuns'); };

  /* ── Data-source badge ────────────────────────────────────────────────────────
     Once some pages are wired and others are not, an unmarked mix misrepresents which
     numbers are real. The badge is derived, never authored: it counts the page's declared
     endpoints that its own script has read live on this load, and folds in the probe. */
  function verdictFor(key) {
    var p = API.PAGES[key];
    if (!p) return { tag: 'DEMO DATA', detail: 'page not in the API registry' };
    if (!p.uses.length) return { tag: 'DEMO DATA', detail: 'scripted by design: ' + p.scripted.join('; ') };

    var read = [], unread = [], failed = [], unbuilt = [];
    for (var i = 0; i < p.uses.length; i++) {
      var name = p.uses[i], ep = API.ENDPOINTS[name];
      if (!ep) continue;
      if (!ep.live) unbuilt.push(name);
      else if (API.consumed[name] === 'live') read.push(name);
      else if (API.consumed[name] === 'failed') failed.push(name);
      else unread.push(name);
    }
    var corpus = API.corpus ? ' · ' + API.corpus + ' corpus' : '';
    var still = p.scripted.length ? ' · still scripted: ' + p.scripted.join('; ') : '';

    if (!read.length) {
      if (API.reachable === false) {
        return { tag: 'DEMO DATA', detail: 'backend not reached · would read ' + p.uses.join(', ') };
      }
      var why = [];
      if (unbuilt.length) why.push('no route yet for: ' + unbuilt.join(', '));
      if (failed.length) why.push('read failed: ' + failed.join(', '));
      if (unread.length) why.push('not read by this page yet: ' + unread.join(', '));
      return { tag: 'DEMO DATA', detail: why.join(' · ') };
    }
    var scripted = unread.length + failed.length + unbuilt.length;
    if (scripted) {
      var parts = ['read live: ' + read.join(', ')];
      if (failed.length) parts.push('read failed: ' + failed.join(', '));
      if (unread.length) parts.push('not read: ' + unread.join(', '));
      if (unbuilt.length) parts.push('no route: ' + unbuilt.join(', '));
      return { tag: 'MIXED · ' + read.length + ' LIVE / ' + scripted + ' SCRIPTED',
               detail: parts.join(' · ') + still + corpus };
    }
    return { tag: 'LIVE · ' + read.join(' '),
             detail: 'served by ' + (API.service || 'citinel-web') + corpus + still };
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
  API.verdictFor = verdictFor;

  function boot() {
    paint();                                   // honest immediately: DEMO until proven live
    API.probe().then(paint);                   // fold in /healthz and /api/source once they answer
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
