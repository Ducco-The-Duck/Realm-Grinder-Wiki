// ---- runtime shims for transpiled ActionScript ------------------------------------------
var __initErr = [];
var __classes = [];
var __byQ = {};
var __byId = {};
function __reg(q, K, ids) {
  __classes.push({ q: q, K: K, ids: ids });
  if (!Object.prototype.hasOwnProperty.call(K, 'id'))
    Object.defineProperty(K, 'id', { value: undefined, writable: true, configurable: true, enumerable: true });
  __byQ[q] = K;
  for (var i = 0; i < ids.length; i++) __byId[ids[i]] = K;
}
function __vals(x) {
  if (x == null) return [];
  if (Array.isArray(x)) return x;
  return Object.keys(x).map(function (k) { return x[k]; });
}
function int(v) { return v | 0; }
function uint(v) { return v >>> 0; }
function trace() {}
function __fmt(s, rest) {
  for (var i = 0; i < rest.length; i++) s = String(s).replace('%' + i, rest[i]);
  return s;
}
function _(s) { return __fmt(s, Array.prototype.slice.call(arguments, 1)); }
function _n(a, b, n) { return __fmt(n !== 1 ? b : a, Array.prototype.slice.call(arguments, 3)); }
function getTimer() { return Date.now() - (typeof __t0 === 'undefined' ? 0 : __t0); }
var __t0 = Date.now();
function Vector(n) {
  if (typeof n === 'number') return new Array(n).fill(0);
  return n ? Array.prototype.slice.call(n) : [];
}
function Dictionary() { return {}; }
function Point(x, y) { this.x = x || 0; this.y = y || 0; }
function Rectangle(x, y, w, h) { this.x = x || 0; this.y = y || 0; this.width = w || 0; this.height = h || 0; }
function __def(ctor, test) {
  try { Object.defineProperty(ctor, Symbol.hasInstance, { value: test }); } catch (e) {}
}
__def(Number, function (v) { return typeof v === 'number'; });
__def(String, function (v) { return typeof v === 'string'; });
__def(Boolean, function (v) { return typeof v === 'boolean'; });
__def(Array, function (v) { return Array.isArray(v); });
__def(int, function (v) { return typeof v === 'number' && (v | 0) === v; });
__def(uint, function (v) { return typeof v === 'number' && (v >>> 0) === v; });
class __Base { constructor(...a) { this.__d(); this._ctor(...a); } __d() {} _ctor() {} }
// ---- generated classes follow ------------------------------------------------------------
var __bootErr = [];
function Translation() {}
Translation.locale = 0;
Translation._mn = function (a, b, n) { return _n.apply(null, arguments); };
// Platform/library stubs: any member access yields a callable no-op returning undefined.
function __stub() {
  var f = function () { return undefined; };
  return new Proxy(f, { get: function (t, k) { return k === Symbol.toPrimitive ? undefined : __stub(); },
                        apply: function () { return undefined; }, construct: function () { return {}; } });
}
var Kongregate = { isDesktop: function () { return true; }, isAndroid: function () { return false; },
                   isIOS: function () { return false; }, isWeb: function () { return false; }, adsAvailable: function () { return false; } };
var PlayFab = __stub(), SteamWorksAdapter = __stub(), Xsolla = __stub(), ArmorGames = __stub(),
    SupersonicWeb = __stub(), TimeServer = __stub(), ANE = __stub(), Capabilities = { os: 'Windows', version: 'WIN 32,0,0,0' },
    Matrix = function () {}, Vector3D = function () {}, Matrix3D = function () {}, Check = function () {},
    ToggleGroup = function () {}, ViewPortBounds = function () {}, PopUpManager = __stub(),
    Keyboard = {}, Mouse = __stub(), Starling = __stub(), Event = {}, TimerEvent = {}, Timer = function () {},
    Security = __stub(), ExternalInterface = __stub(), SharedObject = __stub(), Stage = __stub(), Math2 = Math;
