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
    WRITE_TIMEOUT_MS: 45000,   // writes append ledger frames and may wait on connectors; never retried
    reachable: null,           // null = not probed, true/false after probe()
    service: null,             // /healthz's service name once probed
    corpus: null,              // /api/source's answer: 'live' pipeline output or the committed 'seed'
    consumed: {},              // endpoint name -> 'live' | 'failed', written by API.get as pages read
    demoServed: {},            // endpoint name -> true when that specific read came back with X-Citinel-Demo
    DEMO_MODE: false,          // Step 14: replay a captured run instead of live for GETs that support it
    WRITE_TOKEN: null          // operator token sent as X-Citinel-Write-Token on every write; unset -> writes 503
  };

  /* Arming a device.

     The operator token and the operator's NAME are remembered together on this
     device, for ARM_TTL_MS, then forgotten by themselves. This replaced a per-tab
     sessionStorage design: on a demo laptop the token vanished the moment a tab
     closed, a second tab was never armed, and nothing on any screen said so --
     the first sign was a 401 on a click. Per-device with a lifetime is what a
     privileged-action credential is expected to look like: required, expiring,
     attributable to a named person, and revocable centrally in one move by
     rotating CITINEL_WRITE_TOKEN on the server. CLEAR forgets it at once.

     The server gate is untouched: reads never need this, writes fail closed
     without it, and the token travels only as a header to this API. Never
     throws if storage is unavailable (a private window, a locked-down embed). */
  var ARM_KEY = 'citinel.operator';
  var ARM_TTL_MS = 12 * 60 * 60 * 1000;
  API.OPERATOR = null;           // the name every write is attributed to
  API.ARMED_AT = null;
  API.ARM_TTL_MS = ARM_TTL_MS;

  function loadArm() {
    var rec = null;
    try { rec = JSON.parse(localStorage.getItem(ARM_KEY) || 'null'); } catch (e) { rec = null; }
    if (!rec) {
      // one-time migration from the per-tab design, so a token pasted today is not lost
      try { var legacy = sessionStorage.getItem('citinel.writeToken'); if (legacy) rec = { token: legacy, name: '', at: Date.now() }; } catch (e) {}
    }
    if (!rec || !rec.token || !rec.at || (Date.now() - rec.at) > ARM_TTL_MS) {
      API.WRITE_TOKEN = null; API.OPERATOR = null; API.ARMED_AT = null;
      if (rec) { try { localStorage.removeItem(ARM_KEY); } catch (e) {} }   // expired: forget it
      return;
    }
    API.WRITE_TOKEN = rec.token; API.OPERATOR = rec.name || null; API.ARMED_AT = rec.at;
  }
  loadArm();

  function announceArm() {
    try { window.dispatchEvent(new CustomEvent('citinel:arm', { detail: API.armState() })); } catch (e) {}
  }

  API.setWriteToken = function (token, name) {
    if (!token) return API.clearWriteToken();
    var rec = { token: token, name: String(name || '').trim().slice(0, 80), at: Date.now() };
    API.WRITE_TOKEN = rec.token; API.OPERATOR = rec.name || null; API.ARMED_AT = rec.at;
    try { localStorage.setItem(ARM_KEY, JSON.stringify(rec)); sessionStorage.removeItem('citinel.writeToken'); } catch (e) {}
    announceArm();
  };
  API.clearWriteToken = function () {
    API.WRITE_TOKEN = null; API.OPERATOR = null; API.ARMED_AT = null;
    try { localStorage.removeItem(ARM_KEY); sessionStorage.removeItem('citinel.writeToken'); } catch (e) {}
    announceArm();
  };
  /* {armed, name, expiresAt} -- what the rail's indicator and Settings both read. */
  API.armState = function () {
    loadArm();   // re-check the lifetime on every read, so expiry is honoured mid-session
    return { armed: !!API.WRITE_TOKEN, name: API.OPERATOR, expiresAt: API.ARMED_AT ? API.ARMED_AT + ARM_TTL_MS : null };
  };
  // another tab arming or clearing this device is reflected here too
  try { window.addEventListener('storage', function (e) { if (e.key === ARM_KEY) { loadArm(); announceArm(); } }); } catch (e) {}

  // Sticky across navigation, not just this page: a presenter flips it on once (Settings, or
  // ?demo=1 on any URL) and every screen they click through afterward stays in capture mode.
  // Never throws if storage is unavailable (a private window, a locked-down embed).
  (function () {
    try {
      if (new URLSearchParams(location.search).get('demo') === '1') {
        API.DEMO_MODE = true;
        localStorage.setItem('citinel.demoMode', '1');
      } else {
        API.DEMO_MODE = localStorage.getItem('citinel.demoMode') === '1';
      }
    } catch (e) { API.DEMO_MODE = false; }
  })();

  API.setDemoMode = function (on) {
    API.DEMO_MODE = !!on;
    try { localStorage.setItem('citinel.demoMode', on ? '1' : '0'); } catch (e) {}
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
                    live: true,  note: '{measured[], unmeasured[], served_from} · harness report, denominators included' },
    incidentsSummary: { path: function () { return '/api/incidents?summary=true'; },
                    live: true,  note: 'Incident[] without findings · state derived from the ledger · swarm summary' },
    verdict:      { path: function (id) { return '/api/incidents/' + id + '/verdict'; },
                    live: true,  note: 'persisted SwarmResult: triage, correlation, cited verdict, proposals, runs · 404 until a run is saved' },
    swarmRun:     { path: function (id) { return '/api/incidents/' + id + '/swarm'; },
                    live: true,  note: 'POST {confirm:true} · starts a live swarm run (real model spend) · 202, then poll status', method: 'POST' },
    swarmStatus:  { path: function (id) { return '/api/incidents/' + id + '/swarm/status'; },
                    live: true,  note: '{running, mode, error, summary, has_result}' },
    execute:      { path: function () { return '/api/actions/execute'; },
                    live: true,  note: 'POST {incident_id, action_class, target, assets_affected, approver?} · gate + simulated endpoints · 403 when denied', method: 'POST' },
    deny:         { path: function () { return '/api/actions/deny'; },
                    live: true,  note: 'POST {incident_id, action_class, target, by, reason} · a human refusal as a ledger frame', method: 'POST' },
    rollback:     { path: function (token) { return '/api/actions/rollback/' + token; },
                    live: true,  note: 'POST {incident_id, actor} · reverses a simulated action by token · 404 unknown', method: 'POST' },
    reopen:       { path: function (id) { return '/api/incidents/' + id + '/reopen'; },
                    live: true,  note: 'POST {by, reason} · a named reopen frame, closed → caught · 409 unless closed', method: 'POST' },
    signoff:      { path: function (id) { return '/api/incidents/' + id + '/signoff'; },
                    live: true,  note: 'POST {signed_by} · human sign-off frame + n8n dispatch (degrades to not_configured)', method: 'POST' },
    context:      { path: function (id) { return '/api/incidents/' + id + '/context'; },
                    live: true,  note: 'public context gathered via Tavily: per technique/rule, query, URLs, fetch time · 404 until gathered' },
    contextGather:{ path: function (id) { return '/api/incidents/' + id + '/context'; },
                    live: true,  note: 'POST {confirm:true} · gathers public context (one Tavily credit per uncached query)', method: 'POST' },
    sweep:        { path: function (id) { return '/api/incidents/' + id + '/sweep'; },
                    live: true,  note: 'Gemini wide-lens sweep: what the long context found past the swarm evidence window · 404 until swept · context, never evidence' },
    sweepRun:     { path: function (id) { return '/api/incidents/' + id + '/sweep'; },
                    live: true,  note: 'POST {confirm:true} · one Gemini call reading every finding, including the unexamined region', method: 'POST' },
    brief:        { path: function (id) { return '/api/incidents/' + id + '/brief'; },
                    live: true,  note: 'Tavily Research brief: {status, question, content, sources[]} · a pending run advances by being read · 404 until requested · context, never evidence' },
    briefStart:   { path: function (id) { return '/api/incidents/' + id + '/brief'; },
                    live: true,  note: 'POST {confirm:true} · starts a multi-search Tavily Research run · 503 without a Tavily key', method: 'POST' },
    visual:       { path: function (id) { return '/api/incidents/' + id + '/visual'; },
                    live: true,  note: '{readings[]} · per image: the model\'s reading, plus corroborated[]/unseen[] indicators checked against this record\'s own findings · 404 until one is read' },
    visualRead:   { path: function (id) { return '/api/incidents/' + id + '/visual'; },
                    live: true,  note: 'POST {image_base64, mime_type, note?} · one Gemini vision read, then in-code corroboration · 503 without a Gemini key', method: 'POST' },
    handover:     { path: function (id) { return '/api/incidents/' + id + '/handover'; },
                    live: true,  note: 'a Lyzr-written handover note from the ledger frames · 404 until written · not_configured without its agent id' },
    handoverWrite:{ path: function (id) { return '/api/incidents/' + id + '/handover'; },
                    live: true,  note: 'POST {confirm:true} · asks the Lyzr handover agent to write the note; cached on disk', method: 'POST' },
    corpusRules:  { path: function () { return '/api/corpus'; },
                    live: true,  note: '{release, rules_total|null, by_dir, fired[], techniques_observed, anomaly_kinds}' },
    corpusReview: { path: function () { return '/api/corpus/review'; },
                    live: true,  note: 'the standing Lyzr coverage advisory · 404 until generated · not_configured without its agent id' },
    corpusReviewWrite: { path: function () { return '/api/corpus/review'; },
                    live: true,  note: 'POST {confirm:true} · asks the Lyzr corpus advisor to review coverage; cached on disk', method: 'POST' },
    connectors:   { path: function () { return '/api/connectors'; },
                    live: true,  note: '{rails, connectors[] (presence only), mock_endpoints, policy}' },
    n8nExecutions:{ path: function (limit, status) { return '/api/n8n/executions?limit=' + (limit || 20) + (status ? '&status=' + encodeURIComponent(status) : ''); },
                    live: true,  note: '{status, fetched_at, executions[] (id, workflow_id, state, mode, started_at, waiting_until, finished)} · what the automation layer actually did, read back from n8n · status:not_configured without its API url + key' },
    startupedSignals: { path: function () { return '/api/startuped/signals'; },
                    live: true,  note: '{provider, configured, signals[], what_is_never_sent} · the whole of what CITINEL reports to its GTM platform: aggregate counters, no incident content' },

    /* The Response Marshal's proposals ride inside the persisted verdict; there is no separate
       route and none is planned. */
    proposals:    { path: function (id) { return '/api/incidents/' + id + '/verdict'; },
                    live: true,  note: 'alias of verdict · proposals[] is a field of it' }
  };

  /* ── Page registry ────────────────────────────────────────────────────────────
     Which endpoints each screen declares, and what stays scripted regardless. Declaring is
     not reading: the badge only counts an endpoint once the page's script has read it.
     HANDOFF.md is the human-readable form of this table; keep them in step. */
  API.PAGES = {
    entry:      { uses: ['incidentsSummary'],                 scripted: ['first-run vs returning session'] },
    shell:      { uses: ['incidentsSummary', 'policy', 'ledgerVerify'], scripted: [] },
    overview:   { uses: ['incidentsSummary', 'policy', 'connectors'], scripted: [] },
    queue:      { uses: ['incidents', 'audit'],               scripted: ['belt-dot decoration', '?state=quiet|firstrun demo panels'] },
    replay:     { uses: ['incident', 'audit', 'verdict', 'context', 'sweep', 'brief', 'visual'], scripted: [] },
    confidence: { uses: ['incident', 'verdict'],              scripted: [] },
    evidence:   { uses: ['incident', 'audit'],                scripted: [] },
    approvals:  { uses: ['policy', 'verdict', 'audit', 'execute'], scripted: [] },
    corpus:     { uses: ['corpusRules', 'corpusReview'],       scripted: [] },
    eval:       { uses: ['evalRuns'],                         scripted: [] },
    policy:     { uses: ['policy', 'connectors'],             scripted: [] },
    compliance: { uses: ['draft', 'incident', 'context'],      scripted: [] },
    audit:      { uses: ['audit', 'ledgerVerify', 'n8nExecutions'], scripted: [] },
    handover:   { uses: ['incidentsSummary', 'audit', 'handover'],        scripted: [] },
    executive:  { uses: ['incidentsSummary', 'policy', 'ledgerVerify'], scripted: [] },
    settings:   { uses: ['connectors', 'source', 'startupedSignals'], scripted: [] },
    demo:       { uses: ['incidentsSummary'],                                   scripted: ['guided walkthrough of the live screens'] }
  };

  /* ── Errors a reader can act on ───────────────────────────────────────────────
     Confirmed 3 Sep 2026: a failed read surfaced as "503 from http://…/api/actions/deny"
     and pages rendered that string straight into the note a reader sees. The service
     always sends a one-sentence `detail` (the write guard: "write operations are disabled
     on this deployment (CITINEL_WRITE_TOKEN is not configured)"); the gate's 403 sends
     {refused, decision}. Use that sentence verbatim, else a plain phrase for the status.
     The raw status and url stay on the envelope for devtools -- they never reach the note. */
  API.NOT_ARMED = 'This device is not armed. Open Settings and paste the operator token.';
  API.WRITES_OFF = 'Writes are switched off on this deployment: no operator token is configured on the server.';
  function humanError(status, d) {
    var detail = d && d.detail;
    // The two token failures get one plain sentence each, everywhere, before the
    // server's own wording is considered: on stage, "401" explains nothing.
    if (status === 401) return API.NOT_ARMED;
    if (status === 503 && typeof detail === 'string' && /WRITE_TOKEN/i.test(detail)) return API.WRITES_OFF;
    if (detail && typeof detail === 'object' && typeof detail.refused === 'string' && detail.refused) return detail.refused;
    if (typeof detail === 'string' && detail) return detail;
    if (status === 401) return 'not authorised for this action';
    if (status === 403) return 'the gate refused this action';
    if (status === 404) return 'that record was not found';
    if (status >= 500) return 'the service could not complete this request';
    return 'the service rejected this request';
  }
  API.humanError = humanError;   // exposed so the two token sentences can be asserted from a test page
  function transportError(e) {
    return 'could not reach the service · check the connection';
  }

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
    if (API.DEMO_MODE) url += (url.indexOf('?') === -1 ? '?' : '&') + 'demo=1';
    var ctl = typeof AbortController !== 'undefined' ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) ctl.abort(); }, opts.timeoutMs || API.TIMEOUT_MS);

    function record(res) {
      if (!opts.probe) {
        API.consumed[name] = res.ok ? 'live' : 'failed';
        if (res.demo) API.demoServed[name] = true;
        paint();                                   // the badge follows the read, not the registry
      }
      return res;
    }

    return fetch(url, {
      headers: { accept: 'application/json' },
      signal: ctl ? ctl.signal : undefined
    }).then(function (r) {
      clearTimeout(timer);
      var demo = r.headers.get('X-Citinel-Demo') === '1';
      if (!r.ok) {
        return r.json().catch(function () { return null; }).then(function (d) {
          return { ok: false, source: 'scripted', status: r.status, error: humanError(r.status, d), url: url, demo: demo };
        });
      }
      return r.json().then(function (d) { return { ok: true, source: 'live', data: d, url: url, demo: demo }; });
    }).catch(function (e) {
      clearTimeout(timer);
      return { ok: false, source: 'scripted', error: transportError(e), url: url };
    }).then(record);
  };

  /* The write path. Same envelope as API.get, same consumption record, JSON body in, JSON out.
     Never retried: every one of these is a ledger frame or real model spend. */
  API.post = function (name, a, body, opts) {
    opts = opts || {};
    var ep = API.ENDPOINTS[name];
    if (!ep) return Promise.resolve({ ok: false, source: 'scripted', error: 'unknown endpoint ' + name });
    if (!ep.live) return Promise.resolve({ ok: false, source: 'scripted', error: 'endpoint not built: ' + ep.note });
    var url = API.BASE + ep.path(a);
    var ctl = typeof AbortController !== 'undefined' ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) ctl.abort(); }, opts.timeoutMs || API.WRITE_TIMEOUT_MS);
    var writeHeaders = { accept: 'application/json', 'content-type': 'application/json' };
    if (API.WRITE_TOKEN) writeHeaders['X-Citinel-Write-Token'] = API.WRITE_TOKEN;
    // Every write names the operator this device is armed as, unless the screen
    // already named someone. The ledger then never carries an anonymous action.
    var payload = (body && typeof body === 'object' && !Array.isArray(body)) ? Object.assign({}, body) : (body || {});
    if (API.OPERATOR && typeof payload === 'object') {
      if (!payload.by) payload.by = API.OPERATOR;
      if (name === 'signoff' && !payload.signed_by) payload.signed_by = API.OPERATOR;
    }
    return fetch(url, {
      method: 'POST',
      headers: writeHeaders,
      body: JSON.stringify(payload),
      signal: ctl ? ctl.signal : undefined
    }).then(function (r) {
      clearTimeout(timer);
      return r.json().catch(function () { return null; }).then(function (d) {
        if (!r.ok) return { ok: false, source: 'live', status: r.status, data: d, error: humanError(r.status, d), url: url };
        return { ok: true, source: 'live', status: r.status, data: d, url: url };
      });
    }).catch(function (e) {
      clearTimeout(timer);
      return { ok: false, source: 'scripted', error: transportError(e), url: url };
    }).then(function (res) {
      // a refused action (403) is still a live answer from the gate; only transport failure is 'scripted'
      API.consumed[name] = res.source === 'live' ? 'live' : 'failed';
      paint();
      return res;
    });
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

  /* ── Drill-down context (MAT-F01) ─────────────────────────────────────────────
     Confirmed live, 3 Sep 2026: no page read ?id= from the URL -- every incident-
     scoped screen always showed API.INCIDENT_PRIMARY regardless of what a reader
     clicked on Overview or Queue, so "drill into this incident" silently dropped
     which incident you meant. currentIncidentId() is the one place that decides
     which incident a page is looking at; incidentLink() is the one place that
     builds a link to another screen carrying it forward. Every incident-scoped
     page should read the former instead of touching API.INCIDENT_PRIMARY
     directly, and should build its OWN outgoing nav links (both the top nav bar
     and any per-row "open" link) through the latter -- so the id a reader
     actually selected keeps propagating, screen to screen, instead of resetting. */
  API.currentIncidentId = function () {
    try {
      var id = new URLSearchParams(location.search).get('id');
      return id || API.INCIDENT_PRIMARY;
    } catch (e) { return API.INCIDENT_PRIMARY; }
  };
  API.incidentLink = function (page, id) {
    id = id || API.currentIncidentId();
    return page + '?id=' + encodeURIComponent(id);
  };

  /* Convenience wrappers — the shapes screens actually want. */
  var BULK = { timeoutMs: API.BULK_TIMEOUT_MS };
  API.incidents = function () { return API.get('incidents', null, null, BULK); };
  API.incident = function (id) { return API.get('incident', id || API.currentIncidentId(), null, BULK); };
  API.auditFor = function (id) { return API.get('audit', id || API.currentIncidentId(), null, BULK); };
  // The draft route runs two blocking Lyzr calls (screen 20s + field review 25s)
  // before it answers. BULK's 20s abort fired first, so a slow Lyzr left the
  // compliance desk with no draft at all -- while both calls were still billed.
  API.draftFor = function (id, kind) { return API.get('draft', id || API.currentIncidentId(), kind || 'certin', { timeoutMs: API.WRITE_TIMEOUT_MS }); };
  API.policy = function () { return API.get('policy'); };
  API.verifyLedger = function () { return API.get('ledgerVerify', null, null, BULK); };
  API.evalReport = function () { return API.get('evalRuns'); };
  API.incidentsSummary = function () { return API.get('incidentsSummary'); };
  API.verdictFor = function (id) { return API.get('verdict', id || API.currentIncidentId(), null, BULK); };
  API.swarmStatus = function (id) { return API.get('swarmStatus', id || API.currentIncidentId()); };
  API.runSwarm = function (id) { return API.post('swarmRun', id || API.currentIncidentId(), { confirm: true }); };
  API.execute = function (body) { return API.post('execute', null, body); };
  API.rollback = function (token, body) { return API.post('rollback', token, body); };
  API.deny = function (body) { return API.post('deny', null, body); };
  API.signOff = function (id, signedBy, extra) { return API.post('signoff', id || API.currentIncidentId(), Object.assign({ signed_by: signedBy }, extra || {})); };
  API.corpusRules = function () { return API.get('corpusRules'); };  // not API.corpus: the badge helper below stores the corpus *source name* there
  API.corpusReview = function () { return API.get('corpusReview'); };
  API.writeCorpusReview = function () { return API.post('corpusReviewWrite', undefined, { confirm: true }); };
  API.sweepFor = function (id) { return API.get('sweep', id || API.currentIncidentId()); };
  API.runSweep = function (id) { return API.post('sweepRun', id || API.currentIncidentId(), { confirm: true }, { timeoutMs: API.WRITE_TIMEOUT_MS }); };
  // Reading a pending brief is what advances it: the route polls Tavily once per
  // ask rather than holding a worker open, so this GET makes an outbound call and
  // will not always answer inside the probe timeout.
  API.briefFor = function (id) { return API.get('brief', id || API.currentIncidentId(), null, BULK); };
  API.requestBrief = function (id) { return API.post('briefStart', id || API.currentIncidentId(), { confirm: true }, { timeoutMs: API.WRITE_TIMEOUT_MS }); };
  API.visualsFor = function (id) { return API.get('visual', id || API.currentIncidentId()); };
  API.readVisual = function (id, imageBase64, mimeType, note) {
    return API.post('visualRead', id || API.currentIncidentId(),
      { image_base64: imageBase64, mime_type: mimeType, note: note || '' },
      { timeoutMs: API.WRITE_TIMEOUT_MS });
  };
  API.contextFor = function (id) { return API.get('context', id || API.currentIncidentId()); };
  API.gatherContext = function (id) { return API.post('contextGather', id || API.currentIncidentId(), { confirm: true }); };
  API.handoverFor = function (id) { return API.get('handover', id || API.currentIncidentId()); };
  API.writeHandover = function (id) { return API.post('handoverWrite', id || API.currentIncidentId(), { confirm: true }); };
  API.connectors = function () { return API.get('connectors'); };
  API.source = function () { return API.get('source'); };
  // n8n is asked over the network on every read (its own client waits up to 20s),
  // so the probe timeout would abort a run list that was on its way.
  API.n8nExecutions = function (limit, status) { return API.get('n8nExecutions', limit, status, BULK); };
  API.startupedSignals = function () { return API.get('startupedSignals'); };

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
    var allDemo = read.length > 0 && read.every(function (n) { return API.demoServed[n]; });
    if (allDemo) {
      return { tag: 'CAPTURED · ' + read.join(' '),
               detail: 'replayed from a captured run, not the live service, at this reader\'s own request'
                 + corpus + still };
    }
    return { tag: 'LIVE · ' + read.join(' '),
             detail: 'served by ' + (API.service || 'citinel-web') + corpus + still };
  }

  function paint() {
    var root = document.querySelector('[data-citinel-page]');
    if (!root) return;
    var key = root.getAttribute('data-citinel-page');
    var v = verdictFor(key);
    // Most screens carry the badge in their own top bar. Entry and Executive
    // have no <header> (a two-column sign-in, and a printable board copy), so
    // appending into the root's flow dropped the badge wherever the layout
    // ended -- clipped against the bottom edge on Executive, confirmed live
    // 2 Sep 2026. With no header to sit in, it floats in a fixed corner
    // instead, which is legible on any layout and clipped by none.
    var header = root.querySelector(':scope > header');
    var host = header || root;
    var el = host.querySelector('[data-source-badge]');
    if (!el) {
      el = document.createElement('span');
      el.setAttribute('data-source-badge', '');
      el.style.cssText = 'flex:none;font-family:var(--ctn-font-display);font-size:7.5px;' +
        'letter-spacing:0.1em;padding:4px 8px;border-radius:3px;white-space:nowrap;' +
        'color:var(--ctn-color-text-muted);cursor:help;' +
        'background:var(--ctn-color-surface-panel)' +
        (header ? '' : ';position:fixed;right:12px;bottom:12px;z-index:40');
      host.appendChild(el);
    }
    var isLive = v.tag.indexOf('LIVE') === 0;
    el.style.border = '1px ' + (isLive ? 'solid' : 'dashed') + ' var(--ctn-color-border-strong)';
    el.style.color = isLive ? 'var(--ctn-color-text-primary)' : 'var(--ctn-color-text-muted)';
    el.textContent = v.tag;
    el.title = v.detail;
  }

  API.badge = paint;
  API.badgeVerdict = verdictFor;   // the badge's own verdict; API.verdictFor (above) is the swarm verdict read

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
