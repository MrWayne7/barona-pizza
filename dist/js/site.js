/* BARONA PIZZA — interfaz común a todas las páginas (menú, pedido, medición, estado, movimiento) */
(function(){
'use strict';
var B = window.BARONA || {};
var d = document, root = d.documentElement;
var $ = function(s, r){ return (r || d).querySelector(s); };
var $$ = function(s, r){ return Array.prototype.slice.call((r || d).querySelectorAll(s)); };
var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
var plata = function(n){ return '$' + Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.'); };
function guardado(k, v){ try { if (v === undefined) return JSON.parse(localStorage.getItem(k)); localStorage.setItem(k, JSON.stringify(v)); } catch (e) { return null; } }

/* ---------- medición: cada contacto queda registrado (GA4, Clarity, Meta o dataLayer, lo que esté instalado) ---------- */
function ev(nombre, datos){
  datos = datos || {}; datos.pagina = location.pathname;
  try {
    (window.dataLayer = window.dataLayer || []).push(Object.assign({ event: nombre }, datos));
    if (window.gtag) window.gtag('event', nombre, datos);
    if (window.clarity) window.clarity('event', nombre);
    if (window.fbq && nombre === 'clic_whatsapp') window.fbq('track', 'Contact');
  } catch (e) {}
}
window.baronaEv = ev;

/* ---------- de dónde viene la visita (UTM de un reel, un QR, la biografía…) ---------- */
var origen = (function(){
  var q = new URLSearchParams(location.search), s = q.get('utm_source');
  if (s){ var o = [s, q.get('utm_medium'), q.get('utm_campaign')].filter(Boolean).join(' / '); try { sessionStorage.setItem('barona_origen', o); } catch (e) {} return o; }
  try { return sessionStorage.getItem('barona_origen') || ''; } catch (e) { return ''; }
})();
function wa(texto){ return 'https://wa.me/' + B.wa + '?text=' + encodeURIComponent(texto + (origen ? '\n\n(Llegué por: ' + origen + ')' : '')); }
$$('a[data-wa]').forEach(function(a){ a.href = wa(a.getAttribute('data-wa')); });
d.addEventListener('click', function(e){
  var a = e.target.closest && e.target.closest('a[href],button[data-ev]'); if (!a) return;
  var h = a.getAttribute('href') || '', n = a.getAttribute('data-ev');
  if (n) ev(n, { desde: a.getAttribute('data-desde') || '' });
  else if (h.indexOf('wa.me') > -1) ev('clic_whatsapp', { desde: a.getAttribute('data-desde') || 'enlace' });
  else if (h.indexOf('tel:') === 0) ev('clic_llamada');
  else if (h.indexOf('instagram.com') > -1) ev('clic_instagram');
});

/* ---------- menú del celular ---------- */
(function(){
  var b = $('#burger'), m = $('#movil'); if (!b || !m) return;
  function set(o){
    m.classList.toggle('open', o); m.setAttribute('aria-hidden', o ? 'false' : 'true'); if (o) m.removeAttribute('inert'); else m.setAttribute('inert', '');
    b.setAttribute('aria-expanded', o ? 'true' : 'false'); b.setAttribute('aria-label', o ? 'Cerrar menú' : 'Abrir menú');
    root.classList.toggle('lock', o); root.classList.toggle('menu-abierto', o);
  }
  b.addEventListener('click', function(){ set(!m.classList.contains('open')); });
  d.addEventListener('keydown', function(e){ if (e.key === 'Escape') set(false); });
  matchMedia('(min-width:981px)').addEventListener('change', function(){ set(false); });
})();

/* ---------- abierto / cerrado, siempre con la hora de Bogotá ---------- */
(function(){
  var H = B.horario; if (!H) return;
  function ahora(){
    var p = new Intl.DateTimeFormat('en-GB', { weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'America/Bogota' }).formatToParts(new Date()), o = {};
    p.forEach(function(x){ o[x.type] = x.value; });
    return { d: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(o.weekday), m: (+o.hour % 24) * 60 + (+o.minute) };
  }
  function min(s){ var a = s.split(':'); return +a[0] * 60 + (+a[1]); }
  function h12(s){ var a = s.split(':'), h = +a[0]; return ((h + 11) % 12 + 1) + ':' + a[1] + (h < 12 ? ' a. m.' : ' p. m.'); }
  function pinta(){
    var n; try { n = ahora(); } catch (e) { return; }
    var hoy = H[n.d], abre = hoy ? min(hoy[0]) : 0, cierra = hoy ? min(hoy[1]) : 0, on = !!hoy && n.m >= abre && n.m < cierra, txt;
    if (on) txt = 'Abierto ahora · hasta las ' + h12(hoy[1]);
    else if (hoy && n.m < abre) txt = 'Abrimos hoy a las ' + h12(hoy[0]);
    else { var k = 1, sig = null; while (k < 8 && !(sig = H[(n.d + k) % 7])) k++; txt = sig ? 'Cerrado · abrimos ' + (k === 1 ? 'mañana' : 'pronto') + ' a las ' + h12(sig[0]) : 'Cerrado'; }
    $$('[data-estado]').forEach(function(el){ el.classList.toggle('cerrado', !on); var t = $('span', el); if (t) t.textContent = txt; el.hidden = false; });
    $$('[data-dia]').forEach(function(li){ li.classList.toggle('hoy', +li.getAttribute('data-dia') === n.d); });
  }
  pinta(); setInterval(pinta, 60000);
})();

/* ---------- el pedido: se guarda en el teléfono y sale armado por WhatsApp ---------- */
(function(){
  var cajon = $('#cajon'), velo = $('#velo'), cuerpo = $('#cajon-cuerpo'), totalEl = $('#cajon-total'), ir = $('#cajon-ir'), aviso = $('#aviso');
  var cuentas = $$('[data-cuenta]');
  var C = guardado('barona_pedido') || [];
  if (!Array.isArray(C)) C = [];
  var antes = null, tAviso = 0;
  function total(){ return C.reduce(function(a, x){ return a + x.p * x.q; }, 0); }
  function cuantos(){ return C.reduce(function(a, x){ return a + x.q; }, 0); }
  function mensaje(){
    var t = '¡Hola Barona! Quiero pedir:\n\n';
    C.forEach(function(x){ t += '• ' + x.q + ' × ' + x.n + (x.t ? ' (' + x.t + ')' : '') + ' — ' + plata(x.p * x.q) + '\n'; });
    return t + '\nTotal: ' + plata(total()) + ' (sin domicilio)\n\nNombre: \nDirección o barrio: \nForma de pago: ';
  }
  function pinta(pop){
    guardado('barona_pedido', C);
    var n = cuantos();
    cuentas.forEach(function(b){ b.textContent = n; if (pop && !reduce){ b.classList.remove('pop'); void b.offsetWidth; b.classList.add('pop'); } });
    if (!cuerpo) return;
    if (!C.length){
      cuerpo.innerHTML = '<div class="vacio"><img src="' + B.base + 'img/ilus-mano.webp" alt="" width="481" height="678" loading="lazy"><p><b>Tu pedido está vacío.</b><br>Agrega algo rico del menú.</p><p style="margin-top:16px"><a class="btn btn-rojo btn-s" href="' + B.base + 'menu/">Ver el menú</a></p></div>';
    } else {
      cuerpo.innerHTML = C.map(function(x, i){
        return '<div class="lin"><div><b>' + x.n + '</b>' + (x.t ? '<small>' + x.t + '</small>' : '') +
          '<div class="cant"><button type="button" data-q="-1" data-i="' + i + '" aria-label="Quitar uno de ' + x.n + '">−</button><span>' + x.q + '</span><button type="button" data-q="1" data-i="' + i + '" aria-label="Agregar uno de ' + x.n + '">+</button></div></div><span class="pl">' + plata(x.p * x.q) + '</span></div>';
      }).join('');
    }
    totalEl.textContent = plata(total());
    if (C.length){ ir.href = wa(mensaje()); ir.removeAttribute('aria-disabled'); ir.classList.remove('off'); }
    else { ir.href = B.base + 'menu/'; ir.setAttribute('aria-disabled', 'true'); }
    ir.innerHTML = C.length ? ICONO_WA + 'Pedir por WhatsApp' : 'Ver el menú';
  }
  var ICONO_WA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.5 8.5 0 0 1-12.6 7.4L3 20.5l1.7-5A8.5 8.5 0 1 1 21 11.5Z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5"/></svg>';
  function abrir(){ if (!cajon) return; antes = d.activeElement; cajon.classList.add('open'); velo.classList.add('open'); cajon.removeAttribute('inert'); cajon.setAttribute('aria-hidden', 'false'); root.classList.add('lock'); var c = $('.cerrar', cajon); if (c) c.focus(); ev('abrir_pedido'); }
  function cerrar(){ if (!cajon) return; cajon.classList.remove('open'); velo.classList.remove('open'); cajon.setAttribute('inert', ''); cajon.setAttribute('aria-hidden', 'true'); root.classList.remove('lock'); if (antes && antes.focus) antes.focus(); }
  function avisar(t){ if (!aviso) return; aviso.textContent = t; aviso.classList.add('ver'); clearTimeout(tAviso); tAviso = setTimeout(function(){ aviso.classList.remove('ver'); }, 1900); }
  function agregar(n, t, p){
    var x = C.filter(function(y){ return y.n === n && y.t === t; })[0];
    if (x) x.q++; else C.push({ n: n, t: t, p: p, q: 1 });
    pinta(true); avisar(n + ' en tu pedido'); ev('agregar_al_pedido', { producto: n, valor: p });
  }
  window.baronaAgregar = function(n, t, p){ agregar(n, t, p); abrir(); };
  $$('[data-abrir-pedido]').forEach(function(b){ b.addEventListener('click', abrir); });
  $$('[data-cerrar-pedido]').forEach(function(b){ b.addEventListener('click', cerrar); });
  d.addEventListener('keydown', function(e){ if (e.key === 'Escape') cerrar(); });
  if (cuerpo) cuerpo.addEventListener('click', function(e){
    var b = e.target.closest('[data-q]'); if (!b) return;
    var x = C[+b.getAttribute('data-i')]; if (!x) return;
    x.q += +b.getAttribute('data-q'); if (x.q <= 0) C.splice(C.indexOf(x), 1); pinta();
  });
  if (ir) ir.addEventListener('click', function(){ if (C.length) ev('clic_whatsapp', { desde: 'pedido', valor: total(), productos: cuantos() }); });
  /* tarjetas del menú: tamaño → precio, y botón de agregar */
  $$('.item').forEach(function(it){
    var precio = $('.precio', it), mas = $('.mas', it), nombre = it.getAttribute('data-n');
    function sel(){ var r = $('.tam input:checked', it); return r ? { t: r.getAttribute('data-t'), p: +r.value } : { t: it.getAttribute('data-t') || '', p: +it.getAttribute('data-p') }; }
    $$('.tam input', it).forEach(function(r){ r.addEventListener('change', function(){ precio.textContent = plata(sel().p); }); });
    if (mas){
      mas.hidden = false; var alt = $('.pedir-directo', it); if (alt) alt.hidden = true;
      mas.addEventListener('click', function(){
        var s = sel(); agregar(nombre, s.t, s.p);
        mas.textContent = '¡Listo!'; mas.classList.add('ok'); setTimeout(function(){ mas.textContent = 'Agregar'; mas.classList.remove('ok'); }, 1100);
      });
    }
  });
  pinta();
})();

/* ---------- pestañas del menú: marcan la categoría que estás viendo ---------- */
(function(){
  var enl = $$('.cats a'); if (!enl.length || !('IntersectionObserver' in window)) return;
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){ if (!e.isIntersecting) return;
      enl.forEach(function(a){ var on = a.getAttribute('href') === '#' + e.target.id; a.classList.toggle('act', on); if (on && a.scrollIntoView && !reduce) a.parentNode.parentNode.scrollTo({ left: a.offsetLeft - 60, behavior: 'smooth' }); });
    });
  }, { rootMargin: '-30% 0px -60% 0px' });
  $$('.grupo').forEach(function(g){ io.observe(g); });
})();

/* ---------- movimiento: entradas al hacer scroll, botón fijo, inercia en escritorio ---------- */
(function(){
  requestAnimationFrame(function(){ requestAnimationFrame(function(){ root.classList.add('listo'); }); });
  var els = $$('[data-m]');
  if (!('IntersectionObserver' in window) || reduce){ els.forEach(function(e){ e.classList.add('in'); }); }
  else {
    var io = new IntersectionObserver(function(es){ es.forEach(function(e){ if (e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
    els.forEach(function(e){ io.observe(e); });
    setTimeout(function(){ els.forEach(function(e){ var r = e.getBoundingClientRect(); if (r.top < innerHeight) e.classList.add('in'); }); }, 1500);
  }
  var fijo = $('#fijo');
  if (fijo){
    var pie = $('.pie'), ult = -1;
    var f = function(){ var on = scrollY > 420 && (!pie || pie.getBoundingClientRect().top > innerHeight - 40); if (on !== ult){ fijo.classList.toggle('ver', on); ult = on; } };
    addEventListener('scroll', f, { passive: true }); f();
  }
  /* la B gigante y las pegatinas se mueven un poco con el scroll */
  var par = $$('[data-par]');
  if (par.length && !reduce){
    var tick = false;
    addEventListener('scroll', function(){ if (tick) return; tick = true; requestAnimationFrame(function(){ tick = false;
      par.forEach(function(el){ var r = el.parentNode.getBoundingClientRect(); if (r.bottom < 0 || r.top > innerHeight) return; el.style.transform = 'translate3d(0,' + ((r.top + r.height / 2 - innerHeight / 2) * -(+el.getAttribute('data-par'))).toFixed(1) + 'px,0)'; });
    }); }, { passive: true });
  }
  if (!reduce && B.lenis && matchMedia('(hover:hover) and (pointer:fine)').matches && !$('#top.viaje3d')){
    var s = d.createElement('script'); s.src = B.lenis; s.async = true;
    s.onload = function(){ if (!window.Lenis) return; var l = new window.Lenis({ lerp: 0.1, wheelMultiplier: 0.95 }); window.baronaLenis = l;
      (function raf(t){ l.raf(t); requestAnimationFrame(raf); })(performance.now());
      new MutationObserver(function(){ if (root.classList.contains('lock')) l.stop(); else l.start(); }).observe(root, { attributes: true, attributeFilter: ['class'] });
    };
    d.head.appendChild(s);
  }
})();
})();
