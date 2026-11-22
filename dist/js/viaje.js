/* ============================================================
   EL VIAJE DE UNA BARONA — del horno a tu puerta
   Concepto: sigues a una pizza desde la masa en el aire hasta la caja en tu puerta.
   Cinco actos: La masa · Los extras · El horno · La carta · Llegó.
   Mundo en los tres colores del manual (ladrillo, carmín, lino). Sin cielo, sin fotos:
   masa, ingredientes, ladrillo, pizzas hechas por código y las calcomanías del personaje.
   Base: motor de viaje 3D de BASHI (carga diferida, calidad adaptativa, cámara por puntos, foco al tocar).
   ============================================================ */
(function(){
'use strict';
var CFG = {"libs":{"three":"../js/three.min.js","lenis":"../js/lenis.min.js"},"tex":{"masa":{"u":"../img/ilus-masa-sticker.webp","a":1.2826},"mano":{"u":"../img/ilus-mano-sticker.webp","a":0.7453},"gaseosa":{"u":"../img/ilus-gaseosa-sticker.webp","a":0.8422},"cajas":{"u":"../img/ilus-cajas-sticker.webp","a":0.8125},"fiesta":{"u":"../img/ilus-fiesta-sticker.webp","a":0.7734}},"carta":[{"n":"La de Siempre","d":"Mozzarella, salsa de tomate de la casa y albahaca fresca. La clásica.","t":"Personal","p":18900,"precio":"$18.900","varios":true,"tops":["albahaca"]},{"n":"Pepperoni Party","d":"Doble pepperoni y mozzarella derretida. Para los de siempre.","t":"Personal","p":21900,"precio":"$21.900","varios":true,"tops":["pepperoni"]},{"n":"La Chimba","d":"La especial de la casa: chorizo, maíz tierno y cebolla caramelizada.","t":"Personal","p":25900,"precio":"$25.900","varios":true,"tops":["chorizo","maiz","cebolla"]},{"n":"Barona Suprema","d":"Pepperoni, jamón, champiñón, pimentón y cebolla. La más completa.","t":"Personal","p":24900,"precio":"$24.900","varios":true,"tops":["pepperoni","jamon","champinon","pimenton"]},{"n":"Hawaiana sin Drama","d":"Jamón y piña. Sí, piña. Y no pasa nada.","t":"Personal","p":21900,"precio":"$21.900","varios":true,"tops":["jamon","pina"]},{"n":"Cuatro Quesos","d":"Mozzarella, parmesano, queso crema y un toque de queso azul.","t":"Personal","p":23900,"precio":"$23.900","varios":true,"tops":["queso","azul"]}]};
var LIBS = CFG.libs, TEX = CFG.tex, CARTA = CFG.carta;

function loadScript(src){ return new Promise(function(ok, fail){ var s = document.createElement('script'); s.src = src; s.async = true; s.onload = ok; s.onerror = fail; document.head.appendChild(s); }); }
var $ = function(s, r){ return (r || document).querySelector(s); };
var $$ = function(s, r){ return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
var clamp = function(x, a, b){ a = a === undefined ? 0 : a; b = b === undefined ? 1 : b; return Math.min(b, Math.max(a, x)); };
var sstep = function(a, b, x){ var t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
var lerp = function(a, b, t){ return a + (b - a) * t; };
var ev = function(n, d){ if (window.baronaEv) window.baronaEv(n, d); };

var root = document.documentElement;
var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
var finePointer = matchMedia('(hover:hover) and (pointer:fine)').matches;
var SNAP = /[?&]snap/.test(location.search);          // solo para pruebas
var hero = $('#top');
if (!hero) return;

/* sin WebGL no hay viaje: se queda la versión en texto y la página no pide scroll de más */
var glOK = (function(){ try { var c = document.createElement('canvas'); return !!(window.WebGLRenderingContext && (c.getContext('webgl') || c.getContext('experimental-webgl'))); } catch (e) { return false; } })();
if (!glOK || /[?&]sin3d/.test(location.search)){ root.classList.add('gl-off', 'ready'); var L0 = $('#loader'); if (L0) L0.classList.add('done'); return; }

var threeReady = loadScript(LIBS.three);
var S = { p: 0, u: 0, mx: 0, my: 0, pt: -9999 };
var lenis = null, tickers = [], heroMax = 1;

/* ---------- calidad: se ajusta sola al equipo ---------- */
var Q = (function(){
  var m = /[?&]q=(high|mid|low)/.exec(location.search);
  var coarse = matchMedia('(pointer:coarse)').matches;
  var mem = navigator.deviceMemory || 8, cores = navigator.hardwareConcurrency || 8;
  var tier = coarse ? 1 : 2;
  if (mem <= 4 || cores <= 4) tier = Math.max(0, tier - 1);
  if (m) tier = { high: 2, mid: 1, low: 0 }[m[1]];
  return { tier: tier, forced: !!m, coarse: coarse };
})();

/* ---------- puntero y giroscopio ---------- */
function setPointer(x, y){ S.mx = x / innerWidth - 0.5; S.my = y / innerHeight - 0.5; S.cx = x; S.cy = y; S.moved = true; S.pt = performance.now(); }
addEventListener('pointermove', function(e){ setPointer(e.clientX, e.clientY); }, { passive: true });
['touchstart', 'touchmove'].forEach(function(n){ addEventListener(n, function(e){ var t = e.touches && e.touches[0]; if (t) setPointer(t.clientX, t.clientY); }, { passive: true }); });
(function(){
  if (!Q.coarse || reduce || !window.DeviceOrientationEvent) return;
  var base = null, btn = $('#gyro');
  function onOri(e){
    if (e.gamma == null || e.beta == null) return;
    var land = Math.abs(window.orientation || 0) === 90, gx = land ? e.beta : e.gamma, gy = land ? e.gamma : e.beta;
    if (!base) base = { x: gx, y: gy };
    S.gx = clamp((gx - base.x) / 28, -1, 1) * 0.5; S.gy = clamp((gy - base.y) / 28, -1, 1) * 0.5; S.gyro = true;
  }
  function start(){ addEventListener('deviceorientation', onOri, { passive: true }); }
  addEventListener('orientationchange', function(){ base = null; });
  if (typeof DeviceOrientationEvent.requestPermission === 'function'){
    if (!btn) return; btn.hidden = false;
    btn.addEventListener('click', function(){ DeviceOrientationEvent.requestPermission().then(function(r){ if (r === 'granted') start(); btn.hidden = true; }).catch(function(){ btn.hidden = true; }); });
  } else start();
})();

/* ---------- progreso: el scroll no avanza parejo. Corre dentro del horno y frena frente a la carta ---------- */
var TRAVEL = 150;
var RM = [[0, 0], [0.17, 0.2], [0.37, 0.4], [0.5, 0.615], [0.85, 0.88], [1, 1]];
function remap(p){ for (var i = 0; i < RM.length - 1; i++){ if (p <= RM[i + 1][0]) return RM[i][1] + (RM[i + 1][1] - RM[i][1]) * (p - RM[i][0]) / (RM[i + 1][0] - RM[i][0]); } return 1; }
function unmap(u){ for (var i = 0; i < RM.length - 1; i++){ if (u <= RM[i + 1][1]) return RM[i][0] + (RM[i + 1][0] - RM[i][0]) * (u - RM[i][1]) / (RM[i + 1][1] - RM[i][1]); } return 1; }
function measure(){ heroMax = Math.max(1, hero.offsetHeight - innerHeight); }
function onScroll(){ S.p = clamp(scrollY / heroMax); S.u = remap(S.p); }
measure(); onScroll();
addEventListener('scroll', onScroll, { passive: true });
addEventListener('resize', function(){ measure(); onScroll(); });
function irA(y, dur){ if (lenis) lenis.scrollTo(y, { duration: dur || 1.4 }); else scrollTo({ top: y, behavior: reduce ? 'auto' : 'smooth' }); }

/* ---------- cargador: el horno se precalienta mientras llegan las fuentes; el 3D entra después con un fundido ---------- */
var loaderEl = $('#loader'), loadN = $('#load-n'), loadShown = 0, loadTarget = 0.35, loaderDone = false;
function finishLoader(){
  if (loaderDone) return; loaderDone = true; loadTarget = 1;
  setTimeout(function(){ if (loaderEl) loaderEl.classList.add('done'); root.classList.add('ready'); }, 320);
}
tickers.push(function(){
  if (!loadN || loadShown > 0.999) return;
  loadShown += (loadTarget - loadShown) * 0.16; if (loadTarget === 1 && loadShown > 0.985) loadShown = 1;
  loadN.textContent = Math.round(loadShown * 250) + '°';
});
setTimeout(finishLoader, 3200);
var fontsReady = (document.fonts && document.fonts.load)
  ? Promise.race([Promise.all([document.fonts.load('900 80px Archivo'), document.fonts.load('600 40px Archivo')]), new Promise(function(r){ setTimeout(r, 2600); })]).catch(function(){})
  : Promise.resolve();
fontsReady.then(finishLoader);

if (!reduce && !Q.coarse && !SNAP) loadScript(LIBS.lenis).then(function(){
  if (!window.Lenis) return;
  lenis = new window.Lenis({ lerp: 0.085, wheelMultiplier: 0.9, smoothWheel: true });
  tickers.push(function(now){ lenis.raf(now); });
  new MutationObserver(function(){ if (root.classList.contains('lock')) lenis.stop(); else lenis.start(); }).observe(root, { attributes: true, attributeFilter: ['class'] });
  document.addEventListener('click', function(e){
    var a = e.target.closest && e.target.closest('a[href^="#"]'); if (!a) return;
    var el = document.querySelector(a.getAttribute('href')); if (!el) return;
    e.preventDefault(); lenis.scrollTo(el, { duration: 1.5 });
  });
}).catch(function(){});

/* ============================================================
   EL MUNDO
   ============================================================ */
var SKY = null;
function skyOff(){ root.classList.add('gl-off'); }
function initWorld(){
  if (!window.THREE){ skyOff(); return; }
  var THREE = window.THREE, canvas = $('#mundo'), renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, powerPreference: 'high-performance' }); } catch (e) { skyOff(); return; }
  var gl2 = renderer.capabilities.isWebGL2;
  var lost = false, shown = false;
  canvas.addEventListener('webglcontextlost', function(e){ e.preventDefault(); lost = true; root.classList.add('gl-lost'); });
  canvas.addEventListener('webglcontextrestored', function(){ lost = false; root.classList.remove('gl-lost'); post.forget(); resize(); });

  var tier = Q.tier, small = innerWidth < 900;
  /* ---- los tres colores del manual y sus sombras ---- */
  var C = { lino: 0xf4ebe9, lad: 0xbf3f34, car: 0xad291d, car2: 0x8f1f15, horno: 0x1f0a08, tinta: 0x3a1a16, borde: 0xe6cdc5 };
  var K = {}; Object.keys(C).forEach(function(k){ K[k] = new THREE.Color(C[k]); });
  /* color del lugar en cada tramo: cocina carmín → lluvia ladrillo → horno oscuro → sala carmín → calle ladrillo → lino */
  var STOPS = [[0, K.car], [0.17, K.car], [0.215, K.lad], [0.365, K.lad], [0.4, K.horno], [0.6, K.horno], [0.63, K.car], [0.84, K.car], [0.885, K.lad], [0.945, K.lad], [0.99, K.lino], [1, K.lino]];
  function zoneColor(p, out){
    for (var i = 0; i < STOPS.length - 1; i++){ if (p <= STOPS[i + 1][0]){ var f = (p - STOPS[i][0]) / Math.max(1e-5, STOPS[i + 1][0] - STOPS[i][0]); return out.copy(STOPS[i][1]).lerp(STOPS[i + 1][1], clamp(f)); } }
    return out.copy(K.lino);
  }
  var scene = new THREE.Scene(), bg = new THREE.Color().copy(K.car);
  scene.background = bg; scene.fog = new THREE.Fog(C.car, 7, 38);
  var U = { time: { value: 0 } };
  var camera = new THREE.PerspectiveCamera(52, 1, 0.1, 150);
  scene.add(new THREE.HemisphereLight(0xfff1ea, 0x8f1f15, 0.7));
  var key = new THREE.DirectionalLight(0xffffff, 0.42); key.position.set(-4, 8, 6); scene.add(key);
  var tl = new THREE.TextureLoader();
  function noMip(t){ t.minFilter = THREE.LinearFilter; t.generateMipmaps = false; return t; }
  function canvasTex(c){ return noMip(new THREE.CanvasTexture(c)); }

  var aspect = 1, kR = 1, spread = 1, sizeK = 1, AMP = 2.4, baseFov = 52;
  var placed = [];
  function place(o, bx, s){ o.userData.bx = bx; o.userData.bs = s || 0; placed.push(o); return o; }
  function applySpread(){ placed.forEach(function(o){ o.position.x = o.userData.bx * spread; if (o.userData.bs) o.scale.setScalar(o.userData.bs * sizeK); }); }

  var world = new THREE.Group(); scene.add(world);
  var fx = new THREE.Group(); world.add(fx);
  var rnd = (function(){ var s = 20060; return function(){ s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; }; })();   // siempre el mismo azar: 2006
  function lam(c, o){ return new THREE.MeshLambertMaterial(Object.assign({ color: c }, o || {})); }
  function radialTex(stops){
    var c = document.createElement('canvas'); c.width = c.height = 128; var x = c.getContext('2d'), g = x.createRadialGradient(64, 64, 0, 64, 64, 64);
    stops.forEach(function(s){ g.addColorStop(s[0], s[1]); }); x.fillStyle = g; x.fillRect(0, 0, 128, 128); return canvasTex(c);
  }
  var softT = radialTex([[0, 'rgba(255,255,255,1)'], [0.35, 'rgba(255,255,255,.7)'], [1, 'rgba(255,255,255,0)']]);

  /* ---- piso: el ajedrezado de las cajas, en dos rojos ---- */
  (function(){
    var c = document.createElement('canvas'); c.width = c.height = 64; var x = c.getContext('2d');
    x.fillStyle = '#a3261b'; x.fillRect(0, 0, 64, 64); x.fillStyle = '#b8382d'; x.fillRect(0, 0, 32, 32); x.fillRect(32, 32, 32, 32);
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(30, 110); t.magFilter = THREE.NearestFilter;
    var m = new THREE.Mesh(new THREE.PlaneGeometry(60, 220), new THREE.MeshBasicMaterial({ map: t }));
    m.rotation.x = -Math.PI / 2; m.position.set(0, -2.6, -80); world.add(m);
  })();

  /* ---- calcomanías del personaje (recursos gráficos del manual): siempre miran a la cámara ---- */
  var stickers = [];
  function sticker(keyName, h, x, y, z, sway){
    var t = TEX[keyName]; if (!t) return null;
    var m = new THREE.Mesh(new THREE.PlaneGeometry(h * t.a, h), new THREE.MeshBasicMaterial({ transparent: true, opacity: 0, depthWrite: false }));
    m.position.set(0, y, z); m.userData = { key: keyName, st: 0, by: y, sway: sway || 0.06, ph: rnd() * 6 };
    place(m, x, 1); world.add(m); stickers.push(m); return m;
  }
  function ensureSticker(m){
    var u = m.userData; if (u.st) return; u.st = 1;
    tl.load(TEX[u.key].u, function(t){ noMip(t); m.material.map = t; m.material.needsUpdate = true; u.st = 2; }, undefined, function(){ u.st = 0; });
  }

  /* ============ ACTO 1 — LA MASA: discos de masa girando en el aire, harina ============ */
  var doughs = [];
  (function(){
    var mDough = lam(0xf1e3dc), mEdge = lam(0xe2c6bc);
    function dough(r, x, y, z, tilt, speed, wob){
      var g = new THREE.Group(), spin = new THREE.Group();
      var disc = new THREE.Mesh(new THREE.CylinderGeometry(r, r, r * 0.05, 40), mDough); spin.add(disc);
      var rim = new THREE.Mesh(new THREE.TorusGeometry(r, r * 0.085, 8, 44), mEdge); rim.rotation.x = Math.PI / 2; spin.add(rim);
      for (var i = 0; i < 5; i++){ var b = new THREE.Mesh(new THREE.SphereGeometry(r * (0.05 + rnd() * 0.05), 8, 6), mEdge), a = rnd() * 6.28, d = rnd() * r * 0.7; b.position.set(Math.cos(a) * d, r * 0.02, Math.sin(a) * d); b.scale.y = 0.4; spin.add(b); }
      g.add(spin); g.position.set(0, y, z); g.userData = { spin: spin, tilt: tilt, speed: speed, wob: wob, by: y, ph: rnd() * 6 };
      place(g, x, 1); world.add(g); doughs.push(g);
    }
    var ball = new THREE.Mesh(new THREE.SphereGeometry(0.75, 20, 14), mDough); ball.scale.y = 0.72; ball.position.set(0, -1.25, -2.5); ball.userData = { by: -1.25 }; place(ball, -3.6, 1); world.add(ball); doughs.ball = ball;
    dough(1.15, 3.6, 1.5, -7.5, 1.15, 2.4, 0.22);
    dough(1.7, -2.7, 1.3, -12, 0.95, -1.9, 0.3);
    dough(2.5, -1.4, 2.6, -19.5, 0.62, 1.5, 0.2);
  })();
  var flour = (function(){
    var n = [120, 260, 420][tier], pos = new Float32Array(n * 3), i;
    for (i = 0; i < n; i++){ pos[i * 3] = (rnd() - 0.5) * 16; pos[i * 3 + 1] = -2.2 + rnd() * 6.5; pos[i * 3 + 2] = 6 - rnd() * 32; }
    var g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    var m = new THREE.Points(g, new THREE.PointsMaterial({ color: C.lino, size: 0.09, map: softT, transparent: true, opacity: 0.8, depthWrite: false }));
    fx.add(m); return m;
  })();
  sticker('masa', 3.7, 3.6, 0.3, -16.5, 0.05);
  sticker('mano', 2.3, -3.5, 0.1, -10.5, 0.09);

  /* ============ ACTO 2 — LOS EXTRAS: palabras del manual y un enjambre de ingredientes ============ */
  function textTex(lines, o){
    o = o || {};
    var fs = o.size || 150, font = '900 ' + fs + 'px Archivo, "Arial Black", sans-serif';
    var mc = document.createElement('canvas').getContext('2d'); mc.font = font; try { mc.fontStretch = 'extra-expanded'; } catch (e) {}
    var w = 0; lines.forEach(function(l){ w = Math.max(w, mc.measureText(l).width); });
    w = Math.ceil(w + fs * 0.5); var lh = fs * 1.0, h = Math.ceil(lh * lines.length + fs * 0.4), k = Math.min(1, 2048 / w);
    var c = document.createElement('canvas'); c.width = Math.ceil(w * k); c.height = Math.ceil(h * k);
    var x = c.getContext('2d'); x.scale(k, k); x.font = font; try { x.fontStretch = 'extra-expanded'; } catch (e) {}
    x.textBaseline = 'middle'; x.textAlign = 'center';
    lines.forEach(function(l, i){
      var ty = fs * 0.22 + lh * (i + 0.5);
      if (o.outline){ x.lineWidth = fs * 0.035; x.strokeStyle = o.color || '#f4ebe9'; x.lineJoin = 'round'; x.strokeText(l, w / 2, ty); }
      else { x.fillStyle = o.color || '#f4ebe9'; x.fillText(l, w / 2, ty); }
    });
    return { tex: canvasTex(c), a: w / h };
  }
  function textPlane(lines, height, o){
    var t = textTex(lines, o); if (o && o.maxW) height = Math.min(height, o.maxW / t.a);
    var m = new THREE.Mesh(new THREE.PlaneGeometry(height * t.a, height), new THREE.MeshBasicMaterial({ map: t.tex, transparent: true, depthWrite: false }));
    m.userData.w = height * t.a; return m;
  }
  var words = [];
  var WORDS = [['EXTRA', 1, -27, -1], ['JAMÓN', 0, -31.5, 1], ['EXTRA', 1, -36, -1], ['QUESO', 0, -40.5, 1], ['EXTRA', 1, -45, -1], ['AMOR', 0, -49.5, 1],
               ['LLEGARON', 1, -117, 1], ['LAS PIZZAS', 0, -120.5, -1], ['MÁS PIZZA,', 0, -127.5, -1, 2.0], ['MENOS DRAMA.', 1, -131.5, 1, 2.3]];
  function buildText(){
    WORDS.forEach(function(wd, n){
      var m = textPlane([wd[0]], 1.35, { outline: !!wd[1], maxW: 5.6 });
      m.position.set(0, wd[4] !== undefined ? wd[4] : (wd[3] > 0 ? 1.55 : -0.55) + ((n % 3) - 1) * 0.22, wd[2]);
      m.userData.by = m.position.y; m.userData.ph = n * 1.7;
      place(m, wd[3] * (1.7 + (n % 2) * 0.5), 1); world.add(m); words.push(m);
    });
    pizzas.forEach(function(g){
      var lab = textPlane([g.userData.label], 0.46, { size: 90, maxW: 4.4 });
      lab.position.set(0, -2.2, 0.3); g.add(lab); g.userData.lab = lab;
    });
    buildForm();
    applySpread();
  }

  /* enjambre de ingredientes: rodajas (pepperoni, mozzarella, aceituna) y hojas de albahaca, con comportamiento de bandada */
  var NB_MAX = 150, NB_TIER = [44, 84, small ? 104 : 150];
  var swarmA, swarmB, B, FORM = null, formK = 0;
  (function(){
    var gA = new THREE.CylinderGeometry(0.3, 0.3, 0.07, 14);
    var leaf = new THREE.Shape(); leaf.moveTo(0, -0.42); leaf.quadraticCurveTo(0.34, -0.1, 0, 0.46); leaf.quadraticCurveTo(-0.34, -0.1, 0, -0.42);
    var gB = new THREE.ShapeGeometry(leaf, 6); gB.rotateX(-Math.PI / 2);
    swarmA = new THREE.InstancedMesh(gA, lam(0xffffff), NB_MAX); swarmB = new THREE.InstancedMesh(gB, lam(0xffffff, { side: THREE.DoubleSide }), NB_MAX);
    [swarmA, swarmB].forEach(function(m){ m.frustumCulled = false; world.add(m); });
    B = { p: new Float32Array(NB_MAX * 3), v: new Float32Array(NB_MAX * 3), s: new Float32Array(NB_MAX), ax: new Float32Array(NB_MAX * 3), sp: new Float32Array(NB_MAX), kind: new Uint8Array(NB_MAX) };
    var pal = [K.lino, K.lino, K.car2, K.tinta, K.lino, K.car2], iA = 0, iB = 0;
    for (var i = 0; i < NB_MAX; i++){
      var a = rnd() * 6.28, r = 0.3 + rnd() * 0.7;
      B.p[i * 3] = Math.cos(a) * r * 7; B.p[i * 3 + 1] = (rnd() - 0.5) * 4; B.p[i * 3 + 2] = Math.sin(a) * r * 7;
      var va = rnd() * 6.28; B.v[i * 3] = Math.cos(va) * 2.2; B.v[i * 3 + 1] = (rnd() - 0.5) * 0.6; B.v[i * 3 + 2] = Math.sin(va) * 2.2;
      B.s[i] = 0.7 + rnd() * 0.7; B.sp[i] = 0.8 + rnd() * 2.2;
      var v = new THREE.Vector3(rnd() - 0.5, rnd() - 0.5, rnd() - 0.5).normalize(); B.ax[i * 3] = v.x; B.ax[i * 3 + 1] = v.y; B.ax[i * 3 + 2] = v.z;
      B.kind[i] = (i % 4 === 3) ? 1 : 0;
      if (B.kind[i]){ swarmB.setColorAt(iB++, K.tinta); } else { swarmA.setColorAt(iA++, pal[i % pal.length]); }
    }
    swarmA.instanceColor.needsUpdate = true; swarmB.instanceColor.needsUpdate = true;
  })();
  /* al final el enjambre dibuja la B de Barona */
  function buildForm(){
    try {
      var c = document.createElement('canvas'); c.width = c.height = 128; var x = c.getContext('2d');
      x.font = '800 132px Archivo, Arial, sans-serif'; try { x.fontStretch = 'normal'; } catch (e) {} x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('B', 64, 70);
      var d = x.getImageData(0, 0, 128, 128).data, cand = [], yy, xx;
      for (yy = 1; yy < 128; yy += 2) for (xx = 1; xx < 128; xx += 2) if (d[(yy * 128 + xx) * 4 + 3] > 128) cand.push([xx, yy]);
      if (cand.length < NB_MAX) return;
      var out = new Float32Array(NB_MAX * 2), dist = new Float32Array(cand.length), pick = 0, i, j;
      for (j = 0; j < cand.length; j++) dist[j] = 1e9;
      for (i = 0; i < NB_MAX; i++){
        var pc = cand[pick]; out[i * 2] = (pc[0] - 64) / 100; out[i * 2 + 1] = (66 - pc[1]) / 100;
        var best = -1, bi = 0;
        for (j = 0; j < cand.length; j++){ var dx = cand[j][0] - pc[0], dy = cand[j][1] - pc[1], dd = dx * dx + dy * dy; if (dd < dist[j]) dist[j] = dd; if (dist[j] > best){ best = dist[j]; bi = j; } }
        pick = bi;
      }
      FORM = out;
    } catch (e) { FORM = null; }
  }
  var flockC = new THREE.Vector3(), dummy = new THREE.Object3D(), qT = new THREE.Quaternion(), qF = new THREE.Quaternion(), axV = new THREE.Vector3();
  var camR = new THREE.Vector3(), camU = new THREE.Vector3(), prj = new THREE.Vector3(), swarmOn = 0;
  var colForm = new THREE.Color(C.car), white = new THREE.Color(0xffffff);
  function updateSwarm(dt, p, t){
    formK = (FORM && !reduce) ? sstep(0.885, 0.915, p) : (FORM ? sstep(0.9, 0.905, p) : 0);
    /* aparece al salir de la masa, se esconde dentro del horno y vuelve para el final */
    swarmOn = Math.max(sstep(0.1, 0.17, p) * (1 - sstep(0.37, 0.41, p)), sstep(0.845, 0.88, p));
    var nBase = NB_TIER[tier], n = formK > 0.01 ? Math.max(nBase, [90, 130, NB_MAX][tier]) : nBase;
    var vis = swarmOn > 0.01; swarmA.visible = swarmB.visible = vis; if (!vis) return;
    swarmA.material.color.copy(white).lerp(colForm, formK); swarmB.material.color.copy(white).lerp(colForm, formK * 0.5);
    var dA = 12 - 2 * sstep(0.2, 0.3, p);
    var pc = p + dA / TRAVEL;
    flockC.set(pathX(pc) * 0.5, pathY(pc) + 0.5, pathZ(p) - dA);
    var FH = lerp(4.4, 7.6, kR);
    if (formK > 0){ flockC.x = lerp(flockC.x, 0, formK); flockC.y = lerp(flockC.y, 1.2, formK); flockC.z = lerp(flockC.z, pathZ(p) - 12, formK); }
    var Rx = lerp(3.0, 9.5, kR), Ry = 2.8, Rz = 7.5, free = 1 - formK;
    var scatter = !reduce && (performance.now() - S.pt) < 450, px = S.mx * 2, py = -S.my * 2;
    camR.setFromMatrixColumn(camera.matrixWorld, 0); camU.setFromMatrixColumn(camera.matrixWorld, 1);
    var cx = camera.position.x, cy = camera.position.y, cz = camera.position.z, P = B.p, V = B.v, i, j, ix, jx, iA = 0, iB = 0;
    qF.setFromEuler(new THREE.Euler(Math.PI / 2, 0, 0));
    for (i = 0; i < n; i++){
      ix = i * 3;
      var x = P[ix], y = P[ix + 1], z = P[ix + 2], vx = V[ix], vy = V[ix + 1], vz = V[ix + 2];
      var ax = 0, ay = 0, az = 0, cnt = 0, mx = 0, my = 0, mz = 0, avx = 0, avy = 0, avz = 0;
      for (j = 0; j < n; j++){
        if (j === i) continue; jx = j * 3;
        var dx = P[jx] - x, dy = P[jx + 1] - y, dz = P[jx + 2] - z, d2 = dx * dx + dy * dy + dz * dz;
        if (d2 > 7) continue;
        cnt++; mx += dx; my += dy; mz += dz; avx += V[jx]; avy += V[jx + 1]; avz += V[jx + 2];
        if (d2 < 2.2){ var inv = 1 / (d2 + 0.05); ax -= dx * inv * 2.6; ay -= dy * inv * 2.6; az -= dz * inv * 2.6; }
      }
      if (cnt){ ax += mx / cnt * 0.25 + (avx / cnt - vx) * 0.7; ay += my / cnt * 0.25 + (avy / cnt - vy) * 0.7; az += mz / cnt * 0.25 + (avz / cnt - vz) * 0.7; }
      var e = (x * x) / (Rx * Rx) + (y * y) / (Ry * Ry) + (z * z) / (Rz * Rz);
      if (e > 1){ var k = (e - 1) * 1.4 + 0.4; ax -= x / Rx * k; ay -= y / Ry * k * 1.6; az -= z / Rz * k; }
      var wx = flockC.x + x, wy = flockC.y + y, wz = flockC.z + z;
      var rr = Math.sqrt(x * x + (wy - cy) * (wy - cy)); if (rr < 1.8) ax += (x < 0 ? -1 : 1) * (1.8 - rr) * 2.2;      // no tapan el centro
      var qx = wx - cx, qy = wy - cy, qz = wz - cz, qd = Math.sqrt(qx * qx + qy * qy + qz * qz);
      if (qd < 3.6){ var f = (3.6 - qd) * 3 / (qd + 0.01); ax += qx * f; ay += qy * f; az += qz * f * 0.3; }            // la cámara los abre al pasar
      if (scatter){                                                                                                 // el cursor o el dedo los espanta
        prj.set(wx, wy, wz).project(camera);
        if (prj.z < 1){ var sx = (prj.x - px) * aspect, sy = prj.y - py, sd = Math.sqrt(sx * sx + sy * sy);
          if (sd < 0.34){ var sf = (0.34 - sd) * 46 / (sd + 0.02); ax += (camR.x * sx + camU.x * sy) * sf; ay += (camR.y * sx + camU.y * sy) * sf; az += (camR.z * sx + camU.z * sy) * sf; } }
      }
      if (formK > 0){
        ax = ax * free + ((FORM[i * 2] * FH - x) * 7 - vx * 3.4) * formK;
        ay = ay * free + ((FORM[i * 2 + 1] * FH - y) * 7 - vy * 3.4) * formK;
        az = az * free + ((Math.sin(i * 1.7) * 0.2 - z) * 7 - vz * 3.4) * formK;
      }
      vx += ax * dt; vy += ay * dt; vz += az * dt; vy *= (1 - 0.6 * dt);
      var sp = Math.sqrt(vx * vx + vy * vy + vz * vz), smin = 1.2 * free, smax = 4.2;
      if (sp > smax){ var s1 = smax / sp; vx *= s1; vy *= s1; vz *= s1; } else if (sp < smin && sp > 1e-4){ var s2 = smin / sp; vx *= s2; vy *= s2; vz *= s2; }
      x += vx * dt; y += vy * dt; z += vz * dt;
      P[ix] = x; P[ix + 1] = y; P[ix + 2] = z; V[ix] = vx; V[ix + 1] = vy; V[ix + 2] = vz;
      dummy.position.set(flockC.x + x, flockC.y + y, flockC.z + z);
      axV.set(B.ax[ix], B.ax[ix + 1], B.ax[ix + 2]); qT.setFromAxisAngle(axV, t * B.sp[i] + i);
      if (formK > 0) qT.slerp(qF, formK * 0.92);                       // al formar la B se ponen de frente
      dummy.quaternion.copy(qT);
      dummy.scale.setScalar(lerp(B.s[i] * lerp(0.62, 1, kR), 0.98 * lerp(0.62, 1, kR), formK) * swarmOn);
      dummy.updateMatrix();
      if (B.kind[i]) swarmB.setMatrixAt(iB++, dummy.matrix); else swarmA.setMatrixAt(iA++, dummy.matrix);
    }
    swarmA.count = iA; swarmB.count = iB; swarmA.instanceMatrix.needsUpdate = true; swarmB.instanceMatrix.needsUpdate = true;
  }
  sticker('gaseosa', 3.0, 3.6, -0.3, -43, 0.07);

  /* ============ ACTO 3 — EL HORNO: fachada de ladrillo, bóveda, brasas y fuego ============ */
  var OV0 = -54, OV1 = -86, ovenFx = new THREE.Group(); fx.add(ovenFx);
  var embers, flames = [], glow;
  (function(){
    function brickTex(base, dark, lite, rx, ry){
      var c = document.createElement('canvas'); c.width = 256; c.height = 256; var x = c.getContext('2d');
      x.fillStyle = dark; x.fillRect(0, 0, 256, 256);
      for (var r = 0; r < 8; r++) for (var q = -1; q < 4; q++){
        var v = rnd(); x.fillStyle = v > 0.82 ? lite : (v < 0.16 ? dark : base); x.globalAlpha = v < 0.16 ? 0.55 : 1;
        x.fillRect(q * 64 + (r % 2 ? 32 : 0) + 3, r * 32 + 3, 58, 26);
      }
      x.globalAlpha = 1;
      var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rx, ry); return t;
    }
    /* fachada: un muro con la boca del horno. Hace de telón entre la cocina y el fuego */
    var W = 44, H = 26, hole = new THREE.Path(), s = new THREE.Shape();
    s.moveTo(-W / 2, -2.6); s.lineTo(W / 2, -2.6); s.lineTo(W / 2, H - 2.6); s.lineTo(-W / 2, H - 2.6); s.closePath();
    hole.moveTo(-2.7, -2.6); hole.lineTo(-2.7, 0.5); hole.absarc(0, 0.5, 2.7, Math.PI, 0, true); hole.lineTo(2.7, -2.6); hole.closePath();
    s.holes.push(hole);
    var g = new THREE.ShapeGeometry(s, 24), uv = g.attributes.uv; for (var i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) / 4, uv.getY(i) / 4);
    var wall = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ map: brickTex('#b8382d', '#8f1f15', '#c94a3e', 1, 1) })); wall.position.z = OV0; world.add(wall);
    var arcS = new THREE.Shape(); arcS.absarc(0, 0.5, 3.25, 0, Math.PI, false); arcS.absarc(0, 0.5, 2.7, Math.PI, 0, true);
    var arc = new THREE.Mesh(new THREE.ShapeGeometry(arcS, 24), new THREE.MeshBasicMaterial({ color: C.lino })); arc.position.z = OV0 + 0.02; world.add(arc);
    [-1, 1].forEach(function(sd){ var j = new THREE.Mesh(new THREE.PlaneGeometry(0.55, 3.1), new THREE.MeshBasicMaterial({ color: C.lino })); j.position.set(sd * 2.975, -1.05, OV0 + 0.02); world.add(j); });
    /* bóveda */
    var L = OV0 - OV1, vault = new THREE.Mesh(new THREE.CylinderGeometry(3.3, 3.3, L, 28, 1, true), new THREE.MeshBasicMaterial({ map: brickTex('#6e1c14', '#2a0f0c', '#8f2a1e', 10, 14), side: THREE.BackSide }));
    vault.rotation.x = Math.PI / 2; vault.position.set(0, 0.3, (OV0 + OV1) / 2); world.add(vault);
    var floor = new THREE.Mesh(new THREE.PlaneGeometry(6.8, L), new THREE.MeshBasicMaterial({ map: brickTex('#3d130e', '#1f0a08', '#57190f', 4, 18) }));
    floor.rotation.x = -Math.PI / 2; floor.position.set(0, -1.75, (OV0 + OV1) / 2); world.add(floor);
    var ribG = new THREE.TorusGeometry(3.22, 0.16, 6, 28), ribM = new THREE.MeshBasicMaterial({ color: C.car2 });
    for (var z = OV0 - 3; z > OV1; z -= 4){ var rb = new THREE.Mesh(ribG, ribM); rb.position.set(0, 0.3, z); world.add(rb); }
    var back = new THREE.Mesh(new THREE.RingGeometry(3.25, 26, 28), new THREE.MeshBasicMaterial({ color: C.car2, side: THREE.DoubleSide })); back.position.set(0, 0.3, OV1); world.add(back);
    /* fuego a los lados y brasas subiendo */
    var fT = radialTex([[0, 'rgba(255,236,224,1)'], [0.25, 'rgba(255,150,110,.85)'], [0.6, 'rgba(191,63,52,.45)'], [1, 'rgba(173,41,29,0)']]);
    var nF = [8, 14, 20][tier];
    for (i = 0; i < nF; i++){
      var f = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: fT, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false }));
      var sd = i % 2 ? 1 : -1; f.position.set(sd * (2.2 + rnd() * 0.5), -1.3, OV0 - 2 - (i / nF) * (L - 3)); f.userData = { ph: rnd() * 6, s: 1.5 + rnd() * 1.3 };
      ovenFx.add(f); flames.push(f);
    }
    glow = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: fT, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false, opacity: 0.9 }));
    glow.scale.set(7.5, 7.5, 1); glow.position.set(0, 0.2, OV1 + 0.6); ovenFx.add(glow);
    var n = [70, 150, 240][tier], pos = new Float32Array(n * 3);
    for (i = 0; i < n; i++){ pos[i * 3] = (rnd() - 0.5) * 5.4; pos[i * 3 + 1] = -1.7 + rnd() * 4.2; pos[i * 3 + 2] = OV0 - rnd() * L; }
    var eg = new THREE.BufferGeometry(); eg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    embers = new THREE.Points(eg, new THREE.PointsMaterial({ color: 0xffd9c8, size: 0.08, map: softT, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false }));
    ovenFx.add(embers);
    /* la pizza que va dentro del horno, sobre la pala */
    var peel = new THREE.Group();
    var pala = new THREE.Mesh(new THREE.CylinderGeometry(1.25, 1.25, 0.06, 28), new THREE.MeshBasicMaterial({ color: 0x57190f })); peel.add(pala);
    var mango = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.06, 5), new THREE.MeshBasicMaterial({ color: 0x57190f })); mango.position.z = 3.4; peel.add(mango);
    peel.position.set(0, -1.0, OV0 - 17); peel.rotation.x = 0.42; world.add(peel); doughs.peel = peel;
  })();

  /* ============ ACTO 4 — LA CARTA: seis pizzas flotando. Se pueden tocar ============ */
  var pizzas = [], pickables = [];
  var PM = { crust: lam(0xe7cdc1), sauce: lam(0xc9483c), cheese: lam(0xf3e4da), pep: lam(C.car2), dark: lam(C.tinta), lad: lam(0xd0584c), lite: lam(0xfbefe8) };
  var PG = { blob: new THREE.CylinderGeometry(1, 1, 1, 9), disc: new THREE.CylinderGeometry(1, 1, 1, 36), top: new THREE.CylinderGeometry(1, 1, 1, 14), ring: new THREE.TorusGeometry(1, 0.22, 6, 14), box: new THREE.BoxGeometry(1, 1, 1), ball: new THREE.SphereGeometry(1, 8, 6),
             rim: new THREE.TorusGeometry(1.5, 0.14, 8, 40) };
  function buildPizza(spec){
    var g = new THREE.Group();
    function add(geo, mat, x, y, z, sx, sy, sz, ry){ var m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.scale.set(sx, sy, sz); if (ry) m.rotation.y = ry; g.add(m); return m; }
    var base = add(PG.disc, PM.crust, 0, 0, 0, 1.5, 0.12, 1.5);
    var rim = new THREE.Mesh(PG.rim, PM.crust); rim.rotation.x = Math.PI / 2; rim.position.y = 0.05; g.add(rim);
    add(PG.disc, PM.sauce, 0, 0.07, 0, 1.36, 0.03, 1.36);
    add(PG.blob, PM.cheese, 0, 0.092, 0, 1.2, 0.02, 1.2, rnd() * 3);
    for (var i = 0; i < 6; i++){ var a = i * 1.05 + rnd() * 0.4, d = 0.95 + rnd() * 0.2; add(PG.top, PM.cheese, Math.cos(a) * d, 0.094, Math.sin(a) * d, 0.3 + rnd() * 0.14, 0.02, 0.3 + rnd() * 0.14); }
    function scatterTop(n, fn){ for (var k = 0; k < n; k++){ var a2 = (k / n) * 6.28 + rnd() * 0.5, d2 = (k % 3 === 0 ? 0.25 : 0.62 + (k % 2) * 0.42) + rnd() * 0.12; fn(Math.cos(a2) * d2, Math.sin(a2) * d2, rnd() * 3); } }
    (spec || []).forEach(function(tp){
      if (tp === 'pepperoni') scatterTop(12, function(x, z){ add(PG.top, PM.pep, x, 0.125, z, 0.25, 0.035, 0.25); });
      else if (tp === 'albahaca') scatterTop(6, function(x, z, r){ add(PG.top, PM.dark, x, 0.135, z, 0.27, 0.014, 0.13, r); });
      else if (tp === 'jamon') scatterTop(8, function(x, z, r){ add(PG.box, PM.pep, x, 0.125, z, 0.3, 0.035, 0.24, r); });
      else if (tp === 'pina' || tp === 'maiz') scatterTop(tp === 'maiz' ? 16 : 9, function(x, z, r){ var s = tp === 'maiz' ? 0.085 : 0.19; add(PG.box, PM.lite, x, 0.14, z, s, 0.06, s, r); });
      else if (tp === 'aceituna') scatterTop(8, function(x, z){ var m = add(PG.ring, PM.dark, x, 0.14, z, 0.11, 0.11, 0.11); m.rotation.x = Math.PI / 2; });
      else if (tp === 'cebolla') scatterTop(6, function(x, z){ var m = add(PG.ring, PM.sauce, x, 0.135, z, 0.2, 0.2, 0.06); m.rotation.x = Math.PI / 2; });
      else if (tp === 'champinon') scatterTop(7, function(x, z, r){ add(PG.ball, PM.crust, x, 0.13, z, 0.2, 0.06, 0.14, r); });
      else if (tp === 'chorizo') scatterTop(9, function(x, z){ add(PG.top, PM.pep, x, 0.13, z, 0.17, 0.06, 0.17); });
      else if (tp === 'pimenton') scatterTop(7, function(x, z, r){ add(PG.box, PM.dark, x, 0.13, z, 0.36, 0.025, 0.08, r); });
      else if (tp === 'queso') scatterTop(6, function(x, z){ add(PG.ball, PM.lite, x, 0.11, z, 0.26, 0.06, 0.26); });
      else if (tp === 'azul') scatterTop(5, function(x, z){ add(PG.ball, PM.dark, x, 0.15, z, 0.08, 0.04, 0.08); });
    });
    return { g: g, hit: base };
  }
  CARTA.forEach(function(it, n){
    var G = new THREE.Group(), T = new THREE.Group(), pz = buildPizza(it.tops), side = (n % 2 ? 1 : -1);
    T.rotation.x = 1.08; T.add(pz.g); G.add(T);
    G.position.set(0, 0.55 + ((n % 3) - 1) * 0.22, -92 - n * 4.9); G.rotation.y = -side * 0.42;
    G.userData = { i: n, spin: pz.g, by: G.position.y, w: 3.3, h: 3.3, near: 3.0, label: ('0' + (n + 1)).slice(-2) + '  ' + it.n.toUpperCase(),
                   info: { n: ('0' + (n + 1)).slice(-2), title: it.n, desc: it.d, t: it.t, p: it.p, precio: it.precio, varios: it.varios } };
    pz.hit.userData.frame = G; place(G, side * 3.3, 1); world.add(G); pizzas.push(G); pickables.push(pz.hit);
  });
  (function(){ var pp = buildPizza(['pepperoni', 'albahaca']); pp.g.scale.setScalar(0.78); pp.g.position.y = 0.08; doughs.peel.add(pp.g); doughs.peel.userData.pz = pp.g; })();
  sticker('cajas', 3.9, 3.8, 0.3, -123.5, 0.05);

  /* ============ ACTO 5 — LLEGÓ: el letrero redondo encendido, y la B que arman los ingredientes ============ */
  var sign = new THREE.Group();
  (function(){
    var d = new THREE.Mesh(new THREE.CircleGeometry(1, 56), new THREE.MeshBasicMaterial({ color: C.lino, fog: false }));
    var h = new THREE.Mesh(new THREE.PlaneGeometry(3.4, 3.4), new THREE.MeshBasicMaterial({ map: softT, transparent: true, depthWrite: false, fog: false, opacity: 0.55, color: C.lino }));
    h.position.z = -0.1; sign.add(h); sign.add(d);
    sign.scale.setScalar(8); sign.position.set(0, 1.2, -166); fx.add(sign);
  })();
  sticker('fiesta', 3.4, 4.2, 0.1, -135.5, 0.08);

  fontsReady.then(buildText);

  /* ---- recorrido de cámara: [z, x, y]. Cada acto tiene su gesto ----
     masa: esquiva los discos · extras: eslalon entre palabras · horno: recta y rápida a ras de piso
     carta: pasillo suave · llegó: sube y entra al letrero */
  var KEYS = [[14, 0, 0.35], [8, 0, 0.35], [1, 0, 0.3], [-5, 1.0, 0.0], [-11, -0.9, -0.3], [-18, 0.5, 0.5],
              [-25, -1.0, 0.5], [-30, 1.1, 0.8], [-34.5, -1.1, 0.2], [-39, 1.1, 0.7], [-43.5, -0.9, 0.2], [-48, 0.5, 0.5],
              [-53, 0, -0.1], [-60, 0, -0.75], [-68, 0, -0.55], [-76, 0, -0.8], [-84, 0, -0.3],
              [-89, 0.3, 0.6], [-96, -0.35, 0.5], [-103, 0.35, 0.6], [-110, -0.3, 0.5], [-117, 0.2, 0.6], [-124, 0, 0.7],
              [-131, 0, 1.0], [-138, 0, 1.2], [-146, 0, 1.2], [-156, 0, 1.2], [-166, 0, 1.2]];
  function spl(z, c){
    var n = KEYS.length, i = 1; while (i < n - 3 && KEYS[i + 1][0] > z) i++;
    var a = KEYS[i - 1][c], b = KEYS[i][c], d = KEYS[i + 1][c], e = KEYS[i + 2][c], f = clamp((KEYS[i][0] - z) / (KEYS[i][0] - KEYS[i + 1][0]));
    return 0.5 * ((2 * b) + (-a + d) * f + (2 * a - 5 * b + 4 * d - e) * f * f + (-a + 3 * b - 3 * d + e) * f * f * f);
  }
  function pathZ(p){ return 8 - p * TRAVEL; }
  function pathX(p){ return spl(pathZ(p), 1) * (AMP / 2.4); }
  function pathY(p){ return spl(pathZ(p), 2); }

  /* ============ POSTPROCESADO: resplandor del fuego, grano de imprenta, viñeta ============ */
  var post = (function(){
    var tri = new THREE.BufferGeometry();
    tri.setAttribute('position', new THREE.BufferAttribute(new Float32Array([-1, -1, 0, 3, -1, 0, -1, 3, 0]), 3));
    tri.setAttribute('uv', new THREE.BufferAttribute(new Float32Array([0, 0, 2, 0, 0, 2]), 2));
    var VS = 'varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.0,1.0); }';
    var blur = new THREE.ShaderMaterial({ uniforms: { t: { value: null }, d: { value: new THREE.Vector2() } }, vertexShader: VS, depthTest: false, depthWrite: false,
      fragmentShader: 'uniform sampler2D t; uniform vec2 d; varying vec2 vUv; void main(){ vec3 c=texture2D(t,vUv).rgb*0.227; c+=(texture2D(t,vUv+d*1.385).rgb+texture2D(t,vUv-d*1.385).rgb)*0.316; c+=(texture2D(t,vUv+d*3.231).rgb+texture2D(t,vUv-d*3.231).rgb)*0.0703; gl_FragColor=vec4(c,1.0); }' });
    var comp = new THREE.ShaderMaterial({
      uniforms: { tS: { value: null }, tB: { value: null }, uBloom: { value: 0.3 }, uCA: { value: 0.001 }, uGrain: { value: 0.04 }, uTime: U.time, uVig: { value: 0.5 }, uRes: { value: new THREE.Vector2(1, 1) } },
      vertexShader: VS, depthTest: false, depthWrite: false,
      fragmentShader: [
        'uniform sampler2D tS,tB; uniform float uBloom,uCA,uGrain,uTime,uVig; uniform vec2 uRes; varying vec2 vUv;',
        'float hs(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453); }',
        'void main(){',
        '  vec2 c=vUv-0.5; float r2=dot(c,c); vec2 o=c*uCA*(0.35+r2*2.6);',
        '  vec3 col=vec3(texture2D(tS,vUv+o).r, texture2D(tS,vUv).g, texture2D(tS,vUv-o).b);',
        '  vec3 bl=texture2D(tB,vUv).rgb; float lum=dot(bl,vec3(0.3,0.59,0.11));',
        '  col+=bl*smoothstep(0.55,1.0,lum)*uBloom;',
        '  col*=1.0-uVig*r2*1.7;',
        '  col+=(hs(floor(vUv*uRes/1.5)+fract(uTime)*61.0)-0.5)*uGrain;',
        '  gl_FragColor=vec4(col,1.0);',
        '}'].join('\n') });
    var qs = new THREE.Scene(), qc = new THREE.Camera(), qm = new THREE.Mesh(tri, blur); qm.frustumCulled = false; qs.add(qm);
    var rtS = null, rtA = null, rtB = null, W = 1, H = 1;
    function pass(mat, target){ qm.material = mat; renderer.setRenderTarget(target); renderer.render(qs, qc); }
    return {
      comp: comp, forget: function(){ rtS = rtA = rtB = null; },
      size: function(w, h, pr){
        W = Math.max(2, Math.floor(w * pr)); H = Math.max(2, Math.floor(h * pr));
        [rtS, rtA, rtB].forEach(function(r){ if (r) r.dispose(); });
        if (gl2 && THREE.WebGLMultisampleRenderTarget){ rtS = new THREE.WebGLMultisampleRenderTarget(W, H); rtS.samples = 4; } else rtS = new THREE.WebGLRenderTarget(W, H);
        rtS.texture.minFilter = rtS.texture.magFilter = THREE.LinearFilter;
        var w4 = Math.max(2, W >> 2), h4 = Math.max(2, H >> 2);
        rtA = new THREE.WebGLRenderTarget(w4, h4, { depthBuffer: false }); rtB = new THREE.WebGLRenderTarget(w4, h4, { depthBuffer: false });
        comp.uniforms.uRes.value.set(W, H);
      },
      render: function(sc, cam){
        renderer.setRenderTarget(rtS); renderer.render(sc, cam);
        var w4 = rtA.width, h4 = rtA.height;
        blur.uniforms.t.value = rtS.texture; blur.uniforms.d.value.set(1 / w4, 0); pass(blur, rtA);
        blur.uniforms.t.value = rtA.texture; blur.uniforms.d.value.set(0, 1 / h4); pass(blur, rtB);
        blur.uniforms.t.value = rtB.texture; blur.uniforms.d.value.set(2 / w4, 0); pass(blur, rtA);
        blur.uniforms.t.value = rtA.texture; blur.uniforms.d.value.set(0, 2 / h4); pass(blur, rtB);
        comp.uniforms.tS.value = rtS.texture; comp.uniforms.tB.value = rtB.texture; pass(comp, null);
      }
    };
  })();

  /* ---- calidad adaptativa ---- */
  var PR_TIER = [1, 1.5, 2];
  var acc = 0, accN = 0, warm = 0, skipFrame = false;
  document.addEventListener('visibilitychange', function(){ skipFrame = true; });
  function watchFps(dt){
    if (Q.forced || tier === 0) return;
    if (skipFrame){ skipFrame = false; return; }
    warm += dt; if (warm < 1.5) return;
    acc += dt; accN++;
    if (acc >= 2.5){ if (acc / accN > 0.03){ tier--; warm = 0; resize(); ev('viaje_3d_calidad', { nivel: tier }); } acc = 0; accN = 0; }
  }
  function resize(){
    var w = innerWidth, h = innerHeight, pr = Math.min(devicePixelRatio || 1, PR_TIER[tier], w < 900 ? 1.5 : 2);
    renderer.setPixelRatio(pr); renderer.setSize(w, h, false);
    if (tier > 0) post.size(w, h, pr);
    aspect = w / h; camera.aspect = aspect;
    kR = clamp((aspect - 0.46) / (1.6 - 0.46));
    spread = lerp(0.42, 1, kR); sizeK = lerp(0.6, 1, kR); AMP = lerp(0.5, 2.4, kR); baseFov = lerp(70, 52, kR);
    camera.fov = baseFov; camera.updateProjectionMatrix();
    applySpread();
  }
  resize(); addEventListener('resize', resize);

  /* ---- tocar una pizza: la cámara vuela hasta ella ---- */
  var focus = { g: null, k: 0, pos: new THREE.Vector3(), look: new THREE.Vector3() };
  var ray = new THREE.Raycaster(), ndc = new THREE.Vector2(), journeyOn = false;
  function pick(cx, cy){
    if (!journeyOn) return null;
    ndc.set(cx / innerWidth * 2 - 1, -(cy / innerHeight) * 2 + 1); ray.setFromCamera(ndc, camera); ray.far = 26;
    var hit = ray.intersectObjects(pickables, false)[0]; return hit ? hit.object.userData.frame : null;
  }
  function setFocus(g){
    focus.g = g; if (!g) return;
    var u = g.userData, s = g.scale.x, ry = g.rotation.y, hh = (u.h * s) / 2 + 0.7, hw = (u.w * s) / 2 + 0.4, tf = Math.tan(baseFov * Math.PI / 360), wide = aspect > 1.15;
    var dist = Math.max(hh / (tf * (wide ? 1 : 0.6)), hw / (tf * aspect * (wide ? 0.5 : 1)));
    var sx = wide ? tf * dist * aspect * 0.42 : 0, sy = wide ? 0 : tf * dist * 0.38;
    focus.look.set(g.position.x - Math.cos(ry) * sx, u.by - 0.1 * s - sy, g.position.z + Math.sin(ry) * sx);
    focus.pos.set(focus.look.x + Math.sin(ry) * dist, focus.look.y + 0.5, focus.look.z + Math.cos(ry) * dist);
  }
  SKY = {
    pick: function(x, y){ var g = pick(x, y); return g ? g.userData.info : null; },
    focus: function(x, y){ var g = pick(x, y); if (!g) return null; setFocus(g); return g.userData.info; },
    unfocus: function(){ focus.g = null; }, tier: function(){ return tier; }
  };

  var pS = 0, pPrev = 0, vel = 0, tx = 0, ty = 0, t = 0, last = performance.now(), kick = 0, tick = 0;
  var tmp = new THREE.Vector3(), tgt = new THREE.Vector3(), pA = new THREE.Vector3(), qA = new THREE.Quaternion(), qB = new THREE.Quaternion();
  var fP = flour.geometry.attributes.position, eP = embers.geometry.attributes.position;

  function frame(now){
    var rawDt = (now - last) / 1000, dt = Math.min(0.05, rawDt); last = now;
    var hr = hero.getBoundingClientRect(), showJ = hr.bottom > 0;
    journeyOn = showJ;
    if (lost || !showJ) return;
    if (!shown){ shown = true; root.classList.add('sky-on'); }
    if (!reduce) t += dt;
    U.time.value = t;
    var gmx = S.gyro ? S.gx : S.mx, gmy = S.gyro ? S.gy : S.my;
    tx += (gmx - tx) * 0.05; ty += (gmy - ty) * 0.05;
    var ptx = reduce ? 0 : tx, pty = reduce ? 0 : ty;

    pS += (S.p - pS) * ((reduce || SNAP) ? 1 : 0.075);
    vel += (((pS - pPrev) / Math.max(dt, 0.001)) - vel) * 0.1; pPrev = pS; if (SNAP) vel = 0;
    var p = remap(pS);
    zoneColor(p, bg); scene.fog.color.copy(bg);
    var wo = sstep(0.95, 1, p), inOven = sstep(0.385, 0.41, p) * (1 - sstep(0.6, 0.625, p));
    scene.fog.near = lerp(lerp(7, 3, inOven), 0.5, wo); scene.fog.far = lerp(lerp(38, 30, inOven), 9, wo);

    var cz = pathZ(p), cx = pathX(p), cy = pathY(p);
    var shake = (!reduce && inOven > 0.2) ? inOven * Math.min(Math.abs(vel) * 9, 1) : 0;      // dentro del horno la cámara tiembla con la velocidad
    camera.position.set(cx + ptx * 0.6 + Math.sin(t * 31) * 0.03 * shake, cy - pty * 0.35 + Math.sin(t * 37) * 0.03 * shake, cz);
    var pa = p + 0.035;
    tgt.set(pathX(pa) * 0.92 + ptx * 1.3, pathY(pa) - 0.05 - pty * 0.8, cz - 6);
    /* frente a la carta la mirada se va hacia cada pizza al pasar */
    var lookX = 0, lw, ld2, li;
    for (li = 0; li < pizzas.length; li++){ ld2 = cz - pizzas[li].position.z; if (ld2 > 1 && ld2 < 14){ lw = sstep(14, 7, ld2) * sstep(1, 4, ld2); lookX += (pizzas[li].position.x - cx) * 0.4 * lw; } }
    tgt.x += clamp(lookX, -3.2, 3.2);
    if (formK > 0){ tmp.set(0, 1.2, cz - 12); tgt.lerp(tmp, formK * 0.8); }
    camera.lookAt(tgt);
    if (!reduce) camera.rotateZ(clamp(-(pathX(p + 0.006) - pathX(p - 0.006)) * 1.2, -0.2, 0.2));

    focus.k += ((focus.g ? 1 : 0) - focus.k) * (reduce ? 1 : 0.07);
    if (focus.k > 0.002){
      var e = focus.k * focus.k * (3 - 2 * focus.k);
      pA.copy(camera.position); qA.copy(camera.quaternion);
      if (focus.g){ focus._p = focus.pos; focus._l = focus.look; }
      var oa = reduce ? 0 : Math.sin(t * 0.45) * 0.13, oc = Math.cos(oa), os = Math.sin(oa), ox = focus._p.x - focus._l.x, oz = focus._p.z - focus._l.z;
      tmp.set(focus._l.x + ox * oc - oz * os, focus._p.y + (reduce ? 0 : Math.sin(t * 0.33) * 0.12), focus._l.z + ox * os + oz * oc);
      camera.position.copy(tmp); camera.lookAt(focus._l); qB.copy(camera.quaternion);
      camera.position.lerpVectors(pA, tmp, e); camera.quaternion.copy(qA).slerp(qB, e);
    }
    kick += ((reduce || focus.g ? 0 : Math.min(Math.abs(vel) * 60, 15) + inOven * 6) - kick) * 0.08;
    camera.fov = baseFov + kick; camera.updateProjectionMatrix(); camera.updateMatrixWorld();

    updateSwarm(reduce ? 0 : dt, p, t);

    /* masa: gira, se bambolea, y la bola del inicio respira */
    var n, g, dz, i;
    for (n = 0; n < doughs.length; n++){
      g = doughs[n]; var du = g.userData; du.spin.rotation.y = t * du.speed;
      g.rotation.set(du.tilt + Math.sin(t * 1.1 + du.ph) * du.wob, 0, Math.cos(t * 0.9 + du.ph) * du.wob);
      g.position.y = du.by + Math.sin(t * 0.8 + du.ph) * 0.35;
    }
    doughs.ball.scale.set(1 + Math.sin(t * 2) * 0.04, 0.72 - Math.sin(t * 2) * 0.04, 1 + Math.sin(t * 2) * 0.04);
    doughs.peel.position.z = OV0 - 17 - Math.sin(t * 0.7) * 0.6; doughs.peel.userData.pz.rotation.y = t * 0.4;
    if (!reduce && cz > -30){ for (i = 0; i < fP.count; i++){ var fy = fP.getY(i) - dt * (0.12 + (i % 5) * 0.03); if (fy < -2.4) fy = 4.3; fP.setY(i, fy); } fP.needsUpdate = true; }
    flour.visible = cz > -34;

    /* palabras: flotan, miran a la cámara y se deshacen al pasar */
    for (n = 0; n < words.length; n++){
      var wm = words[n]; dz = cz - wm.position.z; wm.visible = dz > 0.4 && dz < 17; if (!wm.visible) continue;
      wm.position.y = wm.userData.by + Math.sin(t * 0.5 + wm.userData.ph) * 0.14; wm.quaternion.copy(camera.quaternion);
      wm.material.opacity = sstep(0.8, 4.2, dz) * sstep(17, 11, dz);
    }
    /* calcomanías */
    if ((tick++ % 8) === 0){ for (n = 0; n < stickers.length; n++){ dz = cz - stickers[n].position.z; if (dz < 48 && dz > -6) ensureSticker(stickers[n]); } }
    for (n = 0; n < stickers.length; n++){
      var sk = stickers[n], su = sk.userData; dz = cz - sk.position.z; sk.visible = su.st === 2 && dz > 0.3 && dz < 44; if (!sk.visible) continue;
      sk.position.y = su.by + Math.sin(t * 0.9 + su.ph) * 0.1; sk.quaternion.copy(camera.quaternion); sk.rotateZ(Math.sin(t * 1.3 + su.ph) * su.sway);
      sk.material.opacity = sstep(0.6, 3.2, dz) * sstep(44, 30, dz);
    }
    /* horno */
    var ovenNear = cz < OV0 + 30 && cz > OV1 - 0.5; ovenFx.visible = ovenNear;
    if (ovenNear){
      for (n = 0; n < flames.length; n++){ var fl = flames[n], fu = fl.userData, fs = fu.s * (1 + Math.sin(t * 6 + fu.ph) * 0.18 + Math.sin(t * 13.7 + fu.ph * 2) * 0.1); fl.scale.set(fs * 0.9, fs * 1.5, 1); fl.quaternion.copy(camera.quaternion); fl.material.opacity = 0.75 + Math.sin(t * 9 + fu.ph) * 0.2; }
      glow.quaternion.copy(camera.quaternion); glow.material.opacity = 0.75 + Math.sin(t * 3) * 0.12;
      if (!reduce){ for (i = 0; i < eP.count; i++){ var ey = eP.getY(i) + dt * (0.5 + (i % 7) * 0.12); if (ey > 2.6) ey = -1.7; eP.setY(i, ey); eP.setX(i, eP.getX(i) + Math.sin(t * 2 + i) * dt * 0.15); } eP.needsUpdate = true; }
    }
    /* carta */
    for (n = 0; n < pizzas.length; n++){
      g = pizzas[n]; dz = cz - g.position.z; g.visible = dz > -4 && dz < 46; if (!g.visible) continue;
      g.position.y = g.userData.by + Math.sin(t * 0.7 + n * 1.3) * 0.09; g.userData.spin.rotation.y = t * 0.35 + n;
      if (g.userData.lab){ g.userData.lab.material.opacity = (focus.g === g ? 0 : 1) * sstep(1.2, 4, dz) * sstep(20, 13, dz); }
    }
    /* letrero final */
    sign.visible = p > 0.62; sign.quaternion.copy(camera.quaternion);

    if (tier === 0){ renderer.setRenderTarget(null); renderer.render(scene, camera); }
    else {
      var cu = post.comp.uniforms;
      cu.uBloom.value = 0.1 + inOven * 0.85 + wo * 0.25; cu.uVig.value = (0.5 + inOven * 0.5) * (1 - wo);
      cu.uCA.value = reduce ? 0 : 0.0008 + Math.min(Math.abs(vel) * 0.04, 0.008) + inOven * 0.0016;
      cu.uGrain.value = 0.045 * (1 - wo * 0.7);
      post.render(scene, camera);
    }
    watchFps(rawDt);
  }
  tickers.push(frame);
}
threeReady.then(function(){ try { initWorld(); } catch (e) { console.error(e); skyOff(); } }, skyOff);

/* ============================================================
   INTERFAZ DEL VIAJE: actos, barra, ficha de la pizza, medición
   ============================================================ */
(function(){
  var CH = [
    [0,     'La masa',    'Todo empieza en el aire. Harina, manos y cero afán.'],
    [0.2,   'Los extras', 'Extra jamón, extra queso, extra amor.'],
    [0.4,   'El horno',   'Aquí adentro pasa lo importante. Sale al momento.'],
    [0.615, 'La carta',   'Toca una pizza para verla de cerca y pedirla.'],
    [0.88,  'Llegó',      'Más pizza, menos drama. Ahora pide la tuya.']
  ];
  var nav = $('#nav'), ui = $('#hero-ui'), title = $('#hero-title'), hint = $('#hint');
  var cap = $('#cap'), capN = $('#cap-n'), capT = $('#cap-t'), capS = $('#cap-s'), idx = $('#bar-idx'), fill = $('#bar-fill'), line = $('.bar-line');
  var cur = -1, swapping = false, tm = 0, lastP = -1, lastSolid = null, vistos = {}, fin = false;
  var gy = $('.gyro-row');
  if (line) CH.forEach(function(c, i){
    if (!i) return;
    var b = document.createElement('button'); b.type = 'button'; b.className = 'bar-tick'; b.style.left = (unmap(c[0]) * 100).toFixed(2) + '%';
    b.setAttribute('aria-label', 'Ir al acto ' + (i + 1) + ': ' + c[1]);
    b.addEventListener('click', function(){ irA((unmap(c[0]) + 0.012) * heroMax); });
    line.appendChild(b);
  });
  document.addEventListener('keydown', function(e){
    if (scrollY > heroMax || (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') || root.classList.contains('lock')) return;
    var k = clamp(cur + (e.key === 'ArrowRight' ? 1 : -1), 0, CH.length - 1); irA(k ? (unmap(CH[k][0]) + 0.012) * heroMax : 0);
  });
  var skip = $('#saltar'); if (skip) skip.addEventListener('click', function(){ ev('viaje_3d_saltar', { en: Math.round(S.p * 100) }); });
  tickers.push(function(){
    var p = S.p, u = S.u, y = scrollY;
    var solid = u > 0.965 || y > heroMax + 4;
    if (solid !== lastSolid){ nav.classList.toggle('solida', solid); root.classList.toggle('en-viaje', !solid); lastSolid = solid; }
    if (y > heroMax + innerHeight) return;
    if (Math.abs(p - lastP) < 0.00005 && cur !== -1) return;
    lastP = p;
    var tOut = sstep(0.02, 0.07, u);
    title.style.opacity = (1 - tOut).toFixed(3);
    title.style.transform = 'translate3d(0,' + (-p * 900).toFixed(1) + 'px,0) scale(' + (1 + p * 5).toFixed(3) + ')';
    title.style.visibility = tOut > 0.999 ? 'hidden' : 'visible';
    hint.style.opacity = (1 - sstep(0.004, 0.03, p)).toFixed(3);
    if (gy){ var go = 1 - sstep(0.01, 0.04, p); gy.style.opacity = go.toFixed(3); gy.style.pointerEvents = go < 0.1 ? 'none' : ''; }
    ui.style.opacity = (1 - sstep(0.955, 0.99, u)).toFixed(3);
    ui.style.pointerEvents = u > 0.98 ? 'none' : '';
    fill.style.transform = 'scaleX(' + p.toFixed(4) + ')';
    var a = 0; for (var i = 0; i < CH.length; i++){ if (u >= CH[i][0]) a = i; }
    var want = u > 0.035 && u < 0.955;
    if (a !== cur){
      cur = a; swapping = true; cap.classList.remove('on'); clearTimeout(tm);
      if (!vistos[a]){ vistos[a] = 1; ev('viaje_3d_acto', { acto: a + 1, nombre: CH[a][1] }); }
      tm = setTimeout(function(){
        capN.textContent = ('0' + (cur + 1)).slice(-2); capT.textContent = CH[cur][1]; capS.textContent = CH[cur][2];
        idx.textContent = ('0' + (cur + 1)).slice(-2) + ' / 0' + CH.length; swapping = false; lastP = -1;
      }, 230);
    }
    if (!swapping) cap.classList.toggle('on', want);
    if (!fin && u > 0.97){ fin = true; ev('viaje_3d_fin'); }
  });
})();

/* ---------- ficha: al tocar una pizza aparece su nombre, precio y el botón para pedirla ---------- */
(function(){
  var ui = $('#hero-ui'), panel = $('#piece'); if (!panel || !ui) return;
  var pn = $('#piece-n'), pt = $('#piece-t'), pd = $('#piece-d'), pp = $('#piece-p'), go = $('#piece-go'), curEl = $('#cur');
  var open = false, y0 = 0, hov = false, fc = 0, info = null;
  function close(){ if (!open) return; open = false; panel.classList.remove('on'); ui.classList.remove('focus'); if (SKY) SKY.unfocus(); }
  function show(i){
    info = i; pn.textContent = i.n; pt.textContent = i.title; pd.textContent = i.desc; pp.textContent = (i.varios ? 'Desde ' : '') + i.precio;
    panel.classList.add('on'); ui.classList.add('focus'); open = true; y0 = scrollY; ev('viaje_3d_pizza', { producto: i.title });
  }
  hero.addEventListener('click', function(e){
    if (!SKY || (e.target.closest && e.target.closest('a,button'))) return;
    var i = SKY.focus(e.clientX, e.clientY); if (i) show(i); else close();
  });
  $('#piece-close').addEventListener('click', close);
  go.addEventListener('click', function(){ if (info && window.baronaAgregar) window.baronaAgregar(info.title, info.t, info.p); close(); });
  document.addEventListener('keydown', function(e){ if (e.key === 'Escape') close(); });
  addEventListener('scroll', function(){ if (open && Math.abs(scrollY - y0) > 70) close(); }, { passive: true });
  if (finePointer) tickers.push(function(){
    if (!SKY || !S.moved || (fc++) % 4) return;
    var h = scrollY < heroMax && !open && !!SKY.pick(S.cx, S.cy);
    if (h === hov) return; hov = h; ui.style.cursor = h ? 'pointer' : ''; if (curEl) curEl.classList.toggle('see', h);
  });
})();

/* ---------- cursor propio (solo ratón) ---------- */
(function(){
  if (!finePointer || reduce) return;
  var c = $('#cur'); if (!c) return; var x = 0, y = 0;
  tickers.push(function(){ if (!S.moved) return; c.classList.add('on'); x += (S.cx - x) * 0.22; y += (S.cy - y) * 0.22; c.style.transform = 'translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,0)'; });
  document.addEventListener('pointerover', function(e){ c.classList.toggle('big', !!(e.target.closest && e.target.closest('a,button,.item'))); });
  document.addEventListener('pointerleave', function(){ c.classList.remove('on'); });
})();

if (SNAP) window.__sky = function(){ return SKY; };
(function loop(now){ for (var i = 0; i < tickers.length; i++){ try { tickers[i](now); } catch (e) { console.error(e); } } requestAnimationFrame(loop); })(performance.now());
})();
