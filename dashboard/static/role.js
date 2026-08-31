// CITINEL — role depth. One record, two depths. Shared across every screen.
(function () {
  var KEY = 'citinel.role';
  var subs = new Set();
  function get() {
    try { var r = localStorage.getItem(KEY); return r === 'ciso' ? 'ciso' : 'analyst'; }
    catch (e) { return 'analyst'; }
  }
  function set(r) {
    var v = r === 'ciso' ? 'ciso' : 'analyst';
    try { localStorage.setItem(KEY, v); } catch (e) {}
    subs.forEach(function (f) { try { f(v); } catch (e) {} });
  }
  function subscribe(f) { subs.add(f); return function () { subs.delete(f); }; }
  window.addEventListener('storage', function (e) {
    if (e.key === KEY) { var v = get(); subs.forEach(function (f) { try { f(v); } catch (e2) {} }); }
  });
  window.CitinelRole = { get: get, set: set, subscribe: subscribe };
})();
