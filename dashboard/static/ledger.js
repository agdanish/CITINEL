// CITINEL — session ledger. Append-only, shared across screens.
// Decisions taken in one screen must be findable in the audit log. Nothing here is ever removed.
(function () {
  var KEY = 'citinel.session.ledger';
  var subs = new Set();
  function all() {
    try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return []; }
  }
  function append(entry) {
    var list = all();
    var seq = 88427 + list.length + 1;
    var e = Object.assign({ seq: String(seq), at: Date.now() }, entry);
    list.push(e);
    try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (err) {}
    subs.forEach(function (f) { try { f(list); } catch (err) {} });
    return e;
  }
  function has(tag) { return all().some(function (e) { return e.tag === tag; }); }
  function subscribe(f) { subs.add(f); return function () { subs.delete(f); }; }
  window.addEventListener('storage', function (ev) {
    if (ev.key === KEY) { var l = all(); subs.forEach(function (f) { try { f(l); } catch (e) {} }); }
  });
  window.CitinelLedger = { all: all, append: append, has: has, subscribe: subscribe };
})();

// Never let a ledger write break a decision handler.
window.__ledgerSafe = function (e) {
  try { if (window.CitinelLedger) return window.CitinelLedger.append(e); } catch (err) { try { console.warn('ledger append failed', err); } catch (e2) {} }
  return null;
};
