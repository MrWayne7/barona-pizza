#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arma el sitio de Barona Pizza en  dist/  (HTML estático, listo para Cloudflare Pages).
    python3 build.py                 -> sitio para publicar
    LOCAL=1 python3 build.py         -> igual, pero sin etiquetas de medición (para probar)
El contenido se edita en datos.py; el diseño en src/site.css; el viaje 3D en src/viaje-*.js.
"""
import os, sys, json, shutil, html, re, datetime, urllib.parse
from PIL import Image, ImageDraw, ImageFont
import datos as D

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist')
S = D.SITIO
URL = os.environ.get('SITE_URL', S['url']).rstrip('/')
LOCAL = bool(os.environ.get('LOCAL'))
HOY = datetime.date.today().isoformat()
SZ = json.load(open(os.path.join(ROOT, 'static', 'img', 'sizes.json')))
e = html.escape
DIAS = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']

def plata(n): return '$' + f'{n:,.0f}'.replace(',', '.')
def h12(s):
    h, m = map(int, s.split(':'))
    return f"{(h + 11) % 12 + 1}:{m:02d} {'a. m.' if h < 12 else 'p. m.'}"
def horario_texto():
    vals = {D.HORARIO.get(d) for d in range(7)}
    if len(vals) == 1 and None not in vals:
        a, b = vals.pop(); return f'todos los días de {h12(a)} a {h12(b)}'
    return 'en el horario que ves en la página de ubicación'
def wa_url(texto): return f"https://wa.me/{S['whatsapp']}?text=" + urllib.parse.quote(texto)

def img(name, alt, base, cls='', lazy=True, sizes=None, extra=''):
    w, h = SZ[name]
    src = f'{base}img/{name}.webp'
    ss = ''
    if name + '-s' in SZ:
        ss = f' srcset="{base}img/{name}-s.webp {SZ[name + "-s"][0]}w, {src} {w}w" sizes="{sizes or "(max-width:820px) 92vw, 46vw"}"'
    return (f'<img src="{src}"{ss} alt="{e(alt)}" width="{w}" height="{h}"' + (f' class="{cls}"' if cls else '') +
            (' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high" decoding="async"') + (' ' + extra if extra else '') + '>')

I = {
 'wa': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.5 8.5 0 0 1-12.6 7.4L3 20.5l1.7-5A8.500 8.500 0 1 1 21 11.500Z"/><path d="M9 9.500c0 3 2.500 5.500 5.500 5.500"/></svg>',
 'carro': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="20.500" r="1.200"/><circle cx="18.500" cy="20.500" r="1.200"/><path d="M2 2.500h3.200l2.600 12.200a1.800 1.800 0 0 0 1.800 1.400h8.300a1.800 1.800 0 0 0 1.800-1.400L21.500 7H6.200"/></svg>',
 'x': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>',
 'pin': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 6.500-8 12-8 12s-8-5.500-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="2.800"/></svg>',
 'tel': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 3h4l2 5-2.500 1.500a11 11 0 0 0 5 5L15 12l5 2v4a2 2 0 0 1-2 2A15 15 0 0 1 3 5a2 2 0 0 1 2-2Z"/></svg>',
 'ig': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.500 6.500h.01"/></svg>',
 'reloj': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
 'cubo': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.200" stroke-linecap="round" stroke-linejoin="round" width="16" height="16" aria-hidden="true"><path d="m12 2 9 5v10l-9 5-9-5V7l9-5Z"/><path d="m3 7 9 5 9-5M12 12v10"/></svg>',
}
I = {k: re.sub(r'(\d)\.(\d)00(?=\D)', r'\1.\2', v) for k, v in I.items()}

NAV = [('menu/', 'Menú'), ('domicilios/', 'Domicilios'), ('historia/', 'Historia'), ('ubicacion/', 'Ubicación'), ('preguntas/', 'Preguntas')]

def og_image(slug, titulo, sub):
    """imagen para compartir (WhatsApp, Instagram): una distinta por página"""
    W, H = 1200, 630
    im = Image.new('RGB', (W, H), (173, 41, 29))
    d = ImageDraw.Draw(im)
    f = os.path.join(ROOT, 'static', 'fonts', 'Archivo.ttf')
    def font(size, wght, wdth):
        t = ImageFont.truetype(f, size)
        try: t.set_variation_by_axes([wght, wdth])
        except Exception as ex: print('fuente:', ex)
        return t
    d.text((W - 430, -150), 'B', font=font(900, 900, 125), fill=(191, 63, 52))
    lg = Image.open(os.path.join(ROOT, 'static', 'img', 'lockup-blanco.webp')).convert('RGBA'); lg.thumbnail((300, 300))
    im.paste(lg, (W - 60 - lg.width, (H - lg.height) // 2), lg)
    words, lines, cur = titulo.upper().split(), [], ''
    F = font(78, 900, 125)
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=F) > 760 and cur: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur)
    y = 90 + max(0, (3 - len(lines))) * 40
    for l in lines[:4]: d.text((64, y), l, font=F, fill=(244, 235, 233)); y += 78
    d.text((66, y + 22), sub, font=font(30, 600, 100), fill=(244, 235, 233))
    for i in range(0, W, 30):
        d.rectangle((i, H - 30, i + 30, H), fill=(244, 235, 233) if (i // 30) % 2 else (173, 41, 29))
        d.rectangle((i, H - 60, i + 30, H - 30), fill=(173, 41, 29) if (i // 30) % 2 else (244, 235, 233))
    im.save(os.path.join(DIST, 'img', f'og-{slug}.jpg'), 'JPEG', quality=84, optimize=True, progressive=True)

def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '</script>'

def restaurante():
    r = {"@context": "https://schema.org", "@type": "Restaurant", "@id": URL + "/#restaurante", "name": S['nombre'], "url": URL + "/",
         "image": [URL + "/img/og-inicio.jpg", URL + "/img/foto-pizza.webp"], "logo": URL + "/img/icono-180.png",
         "description": "Pizzería en Bogotá desde 2006. Pizza horneada al momento, para comer en el local, recoger o pedir a domicilio por WhatsApp.",
         "telephone": "+" + S['whatsapp'], "servesCuisine": ["Pizza", "Italiana"], "priceRange": S['precio_rango'], "foundingDate": str(S['desde']),
         "slogan": S['lema'], "hasMenu": URL + "/menu/", "sameAs": [S['instagram']], "acceptsReservations": False,
         "address": {"@type": "PostalAddress", "addressLocality": S['ciudad'], "addressRegion": "Bogotá D.C.", "addressCountry": S['pais']},
         "areaServed": {"@type": "City", "name": "Bogotá"},
         "potentialAction": {"@type": "OrderAction", "target": {"@type": "EntryPoint", "urlTemplate": URL + "/menu/", "actionPlatform": ["https://schema.org/DesktopWebPlatform", "https://schema.org/MobileWebPlatform"]}, "deliveryMethod": ["http://purl.org/goodrelations/v1#DeliveryModeOwnFleet", "http://purl.org/goodrelations/v1#DeliveryModePickUp"]}}
    if S['direccion']: r['address']['streetAddress'] = S['direccion']
    if S['lat'] and S['lng']: r['geo'] = {"@type": "GeoCoordinates", "latitude": S['lat'], "longitude": S['lng']}
    if S['maps']: r['hasMap'] = S['maps']
    en = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    r['openingHoursSpecification'] = [{"@type": "OpeningHoursSpecification", "dayOfWeek": en[d], "opens": D.HORARIO[d][0], "closes": D.HORARIO[d][1]} for d in range(7) if D.HORARIO.get(d)]
    return r

def migas_ld(nombre, ruta):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Inicio", "item": URL + "/"}, {"@type": "ListItem", "position": 2, "name": nombre, "item": URL + "/" + ruta}]}

def medicion():
    if LOCAL: return ''
    M, o = D.MEDICION, ''
    if M['ga4']:
        o += f'<script async src="https://www.googletagmanager.com/gtag/js?id={M["ga4"]}"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());gtag("config","{M["ga4"]}");</script>'
    if M['clarity']:
        o += '<script>(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);})(window,document,"clarity","script","%s");</script>' % M['clarity']
    if M['meta_pixel']:
        o += '<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version="2.0";n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,"script","https://connect.facebook.net/en_US/fbevents.js");fbq("init","%s");fbq("track","PageView");</script>' % M['meta_pixel']
    if M['cloudflare_token']:
        o += f'<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{{"token":"{M["cloudflare_token"]}"}}\'></script>'
    return o

def cabeza(p, base, extra_head=''):
    canon = URL + '/' + p['ruta']
    cfg = {"wa": S['whatsapp'], "base": base, "horario": {str(k): v for k, v in D.HORARIO.items()}, "lenis": base + 'js/lenis.min.js'}
    robots = '<meta name="robots" content="noindex">' if p.get('noindex') else ''
    return f'''<!DOCTYPE html>
<html lang="es-CO">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(p["titulo"])}</title>
<meta name="description" content="{e(p["desc"])}">
{robots}<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#ad291d">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Barona Pizza">
<meta property="og:locale" content="es_CO">
<meta property="og:title" content="{e(p.get("og", p["titulo"]))}">
<meta property="og:description" content="{e(p["desc"])}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{URL}/img/og-{p["slug"]}.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="{base}img/favicon.png">
<link rel="apple-touch-icon" href="{base}img/icono-180.png">
<link rel="preload" href="{base}fonts/archivo.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{base}css/site.css">
{extra_head}<script>document.documentElement.className+=" js";window.BARONA={json.dumps(cfg, separators=(",", ":"))};</script>
{"".join(ld(x) for x in p.get("ld", []))}
{medicion()}</head>
'''

def nav(p, base, clase=''):
    def li(r, t):
        cur = ' aria-current="page"' if p['ruta'] == r else ''
        return f'<a href="{base}{r}"{cur}>{t}</a>'
    enl = ''.join(li(r, t) for r, t in NAV)
    cur3 = ' aria-current="page"' if p['ruta'] == '3d/' else ''
    return f'''<a class="salto" href="#contenido">Saltar al contenido</a>
<header class="nav{clase}" id="nav">
  <div class="wrap nav-in">
    <a class="marca" href="{base}" aria-label="Barona Pizza, inicio">{img("logo-horizontal", "Barona Pizza", base, lazy=False)}</a>
    <nav class="nav-enl" aria-label="Principal">{enl}<a class="n3d" href="{base}3d/"{cur3}>{I["cubo"]}Viaje 3D</a></nav>
    <div class="nav-der">
      <button class="carro" type="button" data-abrir-pedido aria-label="Ver tu pedido">{I["carro"]}<span>Pedido</span><b data-cuenta>0</b></button>
      <button class="burger" id="burger" type="button" aria-label="Abrir menú" aria-expanded="false" aria-controls="movil"><i></i><i></i></button>
    </div>
  </div>
</header>
<div class="movil" id="movil" aria-hidden="true" inert>
  <nav aria-label="Menú del celular"><a href="{base}">Inicio</a>{enl}<a href="{base}3d/">Viaje 3D</a></nav>
  <div class="movil-pie"><a class="btn btn-lino" data-wa="¡Hola Barona! Quiero hacer un pedido." data-desde="menu-celular" href="{wa_url("¡Hola Barona! Quiero hacer un pedido.")}">{I["wa"]}Pedir por WhatsApp</a><span>{S["ciudad"]} · desde {S["desde"]} · {S["instagram_usuario"]}</span></div>
</div>
'''

def pie(p, base):
    dire = e(S['direccion']) + (', ' + e(S['barrio']) if S['barrio'] else '') if S['direccion'] else 'Escríbenos y te mandamos la ubicación'
    return f'''<footer class="pie">
  <div class="wrap">
    <div class="pie-rej">
      <div>{img("lockup-blanco", "Barona Pizza, establecida en 2006", base, cls="logo")}<p class="lema">Más pizza,<br>menos drama.</p><p style="margin-top:14px;max-width:32ch">Pizzería en {S["ciudad"]} desde {S["desde"]}. La misma pizza de siempre, con nueva imagen.</p></div>
      <div><h3>El sitio</h3><ul><li><a href="{base}menu/">Menú y precios</a></li><li><a href="{base}domicilios/">Domicilios</a></li><li><a href="{base}historia/">Nuestra historia</a></li><li><a href="{base}ubicacion/">Ubicación y horario</a></li><li><a href="{base}preguntas/">Preguntas frecuentes</a></li><li><a href="{base}3d/">El viaje de una Barona (3D)</a></li></ul></div>
      <div><h3>Dónde y cuándo</h3><p>{dire}<br>{S["ciudad"]}, Colombia</p><p>{horario_texto().capitalize()}</p><p><a class="enl" href="{base}ubicacion/">Cómo llegar</a></p></div>
      <div><h3>Contacto</h3><ul><li><a data-wa="¡Hola Barona! Quiero hacer un pedido." data-desde="pie" href="{wa_url("¡Hola Barona! Quiero hacer un pedido.")}">WhatsApp {S["whatsapp_visible"]}</a></li><li><a href="{S["instagram"]}" target="_blank" rel="noopener">Instagram {S["instagram_usuario"]}</a></li></ul></div>
    </div>
    <div class="pie-base"><span>© {datetime.date.today().year} Barona Pizza · {S["ciudad"]}, Colombia · ESTD {S["desde"]}</span><span><a href="{base}privacidad/">Privacidad</a> · <a href="{base}creditos/">Créditos</a> · Sitio por <a href="https://studiobashi.com" target="_blank" rel="noopener">BASHI</a></span></div>
  </div>
</footer>
<div class="fijo" id="fijo"><a class="btn btn-wa" data-wa="{e(p.get("wa", "¡Hola Barona! Quiero hacer un pedido."))}" data-desde="boton-fijo" href="{wa_url(p.get("wa", "¡Hola Barona! Quiero hacer un pedido."))}">{I["wa"]}Pedir por WhatsApp</a></div>
<div class="velo" id="velo" data-cerrar-pedido></div>
<aside class="cajon" id="cajon" aria-label="Tu pedido" aria-hidden="true" inert>
  <div class="cajon-cab"><h2>Tu pedido</h2><button class="cerrar" type="button" data-cerrar-pedido aria-label="Cerrar el pedido">{I["x"]}</button></div>
  <div class="cajon-cuerpo" id="cajon-cuerpo"></div>
  <div class="cajon-pie"><div class="total"><span>Total sin domicilio</span><b id="cajon-total">$0</b></div><a class="btn btn-wa" id="cajon-ir" href="{base}menu/" target="_blank" rel="noopener">Ver el menú</a><small>Se abre WhatsApp con tu pedido escrito. Ahí confirmas dirección, pago y valor del domicilio.</small></div>
</aside>
<div class="aviso" id="aviso" role="status" aria-live="polite"></div>
<script src="{base}js/site.js" defer></script>
'''

def tarjeta(it, base, i=0):
    etq = (f'<span class="etq">{e(it["tag"])}</span>' if it.get('tag') else '') + ('<span class="etq v">Vegetariana</span>' if it.get('veg') else '')
    multi = len(it['p']) > 1
    if multi:
        tams = f'<fieldset class="tams"><legend>Tamaño de {e(it["n"])}</legend>' + ''.join(
            f'<label class="tam"><input type="radio" name="t-{it["id"]}" value="{pr}" data-t="{e(t)}"{" checked" if k == 0 else ""}><span><b>{e(t)}</b>{plata(pr)}</span></label>'
            for k, (t, pr) in enumerate(it['p'])) + '</fieldset>'
        attrs = ''
    else:
        t, pr = it['p'][0]; tams = ''; attrs = f' data-t="{e(t)}" data-p="{pr}"'
    t0, p0 = it['p'][0]
    directo = wa_url(f'¡Hola Barona! Quiero pedir: {it["n"]} ({t0}).')
    return f'''<article class="item" id="{it["id"]}" data-n="{e(it["n"])}"{attrs} data-m style="--d:{(i % 3) * .07:.2f}s">
  <div class="etqs">{etq}</div><h3>{e(it["n"])}</h3><p>{e(it["d"])}</p>{tams}
  <div class="item-pie"><span class="precio">{plata(p0)}</span><button class="mas" type="button" hidden>Agregar</button><a class="mas pedir-directo" href="{directo}" data-desde="tarjeta" rel="noopener">Pedir</a></div>
</article>'''

def por_id(i):
    for g in D.MENU:
        for it in g['items']:
            if it['id'] == i: return it

def cierre(base, titulo, texto, wa, sigue, pegatina='ilus-fiesta-sticker', desde='cierre'):
    cards = ''.join(f'<a href="{base}{r}"><b>{t}</b><span>{s}</span></a>' for r, t, s in sigue)
    return f'''<section class="sec rojo cierre">
  <div class="wrap">
    {img(pegatina, "", base, cls="pegatina", extra='data-m="zoom"')}
    <h2 data-m>{titulo}</h2><p class="bajada" data-m>{texto}</p>
    <div class="acciones" data-m><a class="btn btn-lino" data-wa="{e(wa)}" data-desde="{desde}" href="{wa_url(wa)}">{I["wa"]}Pedir por WhatsApp</a><a class="btn btn-linea" href="{base}menu/">Ver el menú</a></div>
    <nav class="sigue" aria-label="Sigue por aquí" data-m>{cards}</nav>
  </div>
</section>'''

def portadilla(base, nombre, h1, bajada, pegatina):
    return f'''<section class="portadilla">
  <div class="wrap">
    <ol class="migas" aria-label="Estás en"><li><a href="{base}">Inicio</a></li><li aria-current="page">{nombre}</li></ol>
    <h1>{h1}</h1><p class="bajada">{bajada}</p>
  </div>
  {img(pegatina, "", base, cls="pegatina", lazy=False)}
</section>
<div class="cuadros" aria-hidden="true"></div>'''

ESTADO = '<span class="estado" data-estado hidden><i></i><span>Abierto</span></span>'
CINTA1 = ''.join('<span>Más pizza, menos drama</span><span>Extra queso</span><span>Extra jamón</span><span>Extra amor</span>' for _ in range(2))
CINTA2 = ''.join('<span>Llegaron las pizzas</span><span>Desde 2006</span><span>Horneada al momento</span><span>Qué chimba de pizza</span>' for _ in range(2))

# ================================================================== PÁGINAS
def p_inicio(base):
    favs = ''.join(tarjeta(por_id(i), base, k) for k, i in enumerate(D.FAVORITAS))
    faq = ''.join(f'<details><summary>{e(q)}</summary><p>{e(a.format(horario_texto=horario_texto()))}</p></details>' for q, a in D.PREGUNTAS[:4])
    reels = ''
    if D.REELS:
        reels = '<section class="sec crema"><div class="wrap"><div class="cab"><div><span class="ante">En video</span><h2>Así se vive una Barona</h2></div></div><div class="reels">' + ''.join(
            f'<a class="reel" href="{e(r["url"])}" target="_blank" rel="noopener">' + (f'<img src="{base}{e(r["poster"])}" alt="" loading="lazy">' if r.get('poster') else '') + f'<b>{e(r["titulo"])}</b></a>' for r in D.REELS) + '</div></div></section>'
    resenas = ''
    if D.RESENAS:
        resenas = '<section class="sec"><div class="wrap"><span class="ante">Lo que dice la gente</span><h2>Reseñas</h2><div class="rej" style="margin-top:30px">' + ''.join(
            f'<blockquote class="item"><p>“{e(r["texto"])}”</p><footer><b>{e(r["nombre"])}</b> · {e(r.get("fuente", ""))}</footer></blockquote>' for r in D.RESENAS) + '</div></div></section>'
    return f'''<section class="hero">
  <div class="hero-b" aria-hidden="true" data-par="0.12">B</div>
  <div class="wrap hero-in">
    <div>
      <h1><small>Pizzería en {S["ciudad"]} · a domicilio y para recoger · desde {S["desde"]}</small><span class="l" style="--i:0"><span>Más pizza,</span></span><span class="l" style="--i:1"><span>menos drama.</span></span></h1>
      <p class="bajada">La misma pizza de siempre, horneada al momento y con todo el sabor. Armas tu pedido aquí y lo mandas directo a nuestro WhatsApp.</p>
      <div class="acciones"><a class="btn btn-lino" href="{base}menu/" data-ev="clic_pedir" data-desde="portada">Pedir ahora</a><a class="btn btn-linea" data-wa="¡Hola Barona! Quiero hacer un pedido." data-desde="portada" href="{wa_url("¡Hola Barona! Quiero hacer un pedido.")}">{I["wa"]}WhatsApp</a></div>
      <div class="hero-meta">{ESTADO}<span>{S["instagram_usuario"]}</span></div>
    </div>
    <div class="hero-fig">{img("mascota-sticker", "El personaje de Barona Pizza: un pizzero sonriente de gorra, dibujado como una caricatura de los años 30", base, lazy=False)}<div class="sello"><span>Desde<b>{S["desde"]}</b>{S["ciudad"]}</span></div></div>
  </div>
  <div class="wrap"><ul class="datos">
    <li><b>Desde {S["desde"]}</b>La misma pizza de siempre.</li><li><b>Al momento</b>Sale del horno a tu caja.</li><li><b>Sin intermediarios</b>Pides directo por WhatsApp.</li><li><b>{S["ciudad"]}</b>Domicilio o recoges en el local.</li>
  </ul></div>
</section>
<div class="cinta" aria-hidden="true"><div class="cinta-t">{CINTA1}</div></div>

<section class="sec crema" id="favoritas">
  <div class="wrap">
    <div class="cab"><div><span class="ante">Las que más salen</span><h2 data-m>Empieza por aquí</h2></div><a class="btn btn-linea" href="{base}menu/" data-m>Ver el menú completo</a></div>
    <div class="rej">{favs}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="viaje" data-m>
      <div><span class="ante">Experiencia 3D</span><h2>Sigue una Barona del horno a tu puerta</h2>
        <p>Un viaje de un minuto: la masa en el aire, la lluvia de extras, el horno por dentro y la carta flotando. Toca una pizza para pedirla.</p>
        <ol><li>La masa</li><li>Los extras</li><li>El horno</li><li>La carta</li><li>Llegó</li></ol>
        <div class="acciones"><a class="btn btn-lino" href="{base}3d/" data-ev="clic_viaje_3d" data-desde="portada">{I["cubo"]}Empezar el viaje</a></div></div>
      <div class="viaje-fig">{img("ilus-masa-sticker", "El pizzero de Barona lanzando la masa al aire", base)}</div>
    </div>
  </div>
</section>

<section class="sec crema">
  <div class="wrap duo">
    <div data-m="izq"><span class="ante">Nuestra historia</span><h2>Pizza con calle desde {S["desde"]}</h2>
      <div class="prosa bajada"><p>Barona lleva lo urbano a todos los públicos: una pizzería cercana, cotidiana y sin pretensiones. En 2025 estrenamos imagen, con un personaje inspirado en las caricaturas de los años 30. La receta no la tocamos.</p></div>
      <div class="cifras"><div class="cifra"><b>{S["desde"]}</b><span>Año en que empezó todo</span></div><div class="cifra"><b>{datetime.date.today().year - S["desde"]}</b><span>años haciendo pizza</span></div><div class="cifra"><b>1</b><span>sola regla: menos drama</span></div></div>
      <div class="acciones"><a class="btn btn-rojo" href="{base}historia/">Conoce la historia</a></div></div>
    <div class="marco" data-m="der">{img("foto-masa", "Manos estirando una bola de masa de pizza sobre una mesa enharinada", base)}{img("ilus-mano-sticker", "", base, cls="pegado")}</div>
  </div>
</section>
<div class="cinta r" aria-hidden="true"><div class="cinta-t" style="animation-direction:reverse">{CINTA2}</div></div>

<section class="sec rojo">
  <div class="wrap duo inv">
    <div class="marco h" data-m="izq">{img("foto-cajas", "Cajas de Barona Pizza con el personaje cargando una torre de cajas y el texto Llegaron las pizzas", base)}</div>
    <div data-m="der"><span class="ante">Domicilios en {S["ciudad"]}</span><h2>Llegaron las pizzas</h2>
      <p class="bajada">Pides por WhatsApp, sin aplicaciones de por medio. Te confirmamos al instante si llegamos a tu barrio, cuánto cuesta el envío y en cuánto está en tu puerta.</p>
      <div class="acciones"><a class="btn btn-lino" href="{base}domicilios/">Cómo funcionan los domicilios</a><a class="btn btn-linea" href="{base}ubicacion/">Ubicación y horario</a></div></div>
  </div>
</section>
{reels}{resenas}
<section class="sec">
  <div class="wrap">
    <div class="cab"><div><span class="ante">Antes de pedir</span><h2 data-m>Lo que más nos preguntan</h2></div><a class="btn btn-linea" href="{base}preguntas/" data-m>Todas las preguntas</a></div>
    <div class="faq" data-m>{faq}</div>
  </div>
</section>
''' + cierre(base, '¿Con hambre? Pide la tuya', 'Abre el menú, arma tu pedido y mándalo. Así de fácil, sin drama.', '¡Hola Barona! Quiero hacer un pedido.',
             [('menu/', 'Menú y precios', 'Pizzas, combos, adiciones y bebidas.'), ('domicilios/', 'Domicilios', 'Cómo pedir y a dónde llegamos.'), ('3d/', 'Viaje 3D', 'Del horno a tu puerta, en un minuto.')])

def p_menu(base):
    cats = ''.join(f'<li><a href="#{g["id"]}">{e(g["nombre"])}</a></li>' for g in D.MENU)
    grupos = ''.join(f'<section class="grupo" id="{g["id"]}" aria-labelledby="t-{g["id"]}"><header><h2 id="t-{g["id"]}">{e(g["nombre"])}</h2><p>{e(g["nota"])}</p></header><div class="rej">' +
                     ''.join(tarjeta(it, base, k) for k, it in enumerate(g['items'])) + '</div></section>' for g in D.MENU)
    return portadilla(base, 'Menú', 'Menú y precios', f'Pizzas horneadas al momento, combos, adiciones y bebidas. Agrega lo que quieras y manda el pedido por WhatsApp: llega a domicilio en {S["ciudad"]} o lo recoges en el local.', 'ilus-fiesta-sticker') + f'''
<nav class="cats" aria-label="Categorías del menú"><ul>{cats}</ul></nav>
<section class="sec crema" style="padding-top:0">
  <div class="wrap">{grupos}
    <p style="margin-top:34px;color:var(--tinta-2);font-size:.92rem">Precios en pesos colombianos. El valor del domicilio se confirma por WhatsApp según tu barrio. ¿Quieres quitar o cambiar un ingrediente? Dilo en el mensaje del pedido. <a class="enl" href="{base}preguntas/">Más preguntas frecuentes</a>.</p>
  </div>
</section>
''' + cierre(base, '¿Ya armaste tu pedido?', 'Revísalo y mándalo. Te respondemos por WhatsApp con el tiempo de entrega.', '¡Hola Barona! Quiero hacer un pedido.',
             [('domicilios/', 'Domicilios', 'Cobertura, tiempos y cómo pagar.'), ('ubicacion/', 'Ubicación y horario', 'Para recoger o comer en el local.'), ('preguntas/', 'Preguntas', 'Lo que la gente quiere saber antes de pedir.')], pegatina='ilus-cajas-sticker', desde='menu-cierre')

def p_domicilios(base):
    return portadilla(base, 'Domicilios', f'Pizza a domicilio en {S["ciudad"]}', 'Sin aplicaciones ni intermediarios: pides directo por WhatsApp y te atiende alguien de Barona. Tú solo dices a dónde.', 'ilus-cajas-sticker') + f'''
<section class="sec">
  <div class="wrap">
    <span class="ante">Así se pide</span><h2 data-m>Tres pasos y ya</h2>
    <ol class="pasos claro">
      <li data-m><h3>Arma tu pedido</h3><p>En el <a class="enl" href="{base}menu/">menú</a> eliges pizzas, tamaños, combos y adiciones. Se va guardando en «Pedido».</p></li>
      <li data-m style="--d:.08s"><h3>Mándalo por WhatsApp</h3><p>Tocas «Pedir por WhatsApp» y se abre el chat con todo escrito. Agregas tu nombre, la dirección y cómo pagas.</p></li>
      <li data-m style="--d:.16s"><h3>Recibe y disfruta</h3><p>Te confirmamos el valor del envío y el tiempo. Sale del horno a tu caja, y de ahí a tu puerta.</p></li>
    </ol>
  </div>
</section>
<section class="sec rojo">
  <div class="wrap duo">
    <div data-m="izq"><span class="ante">Cobertura y tiempos</span><h2>¿Llegamos a tu barrio?</h2>
      <div class="prosa bajada"><p>La cobertura y el costo del domicilio dependen de la zona de {S["ciudad"]}. Mándanos tu barrio o tu dirección y te respondemos al instante con el valor y el tiempo estimado.</p><p>¿Estás cerca? También puedes pedir para recoger: te avisamos cuando esté lista. Mira la <a class="enl" href="{base}ubicacion/">ubicación y el horario</a>.</p></div>
      <div class="acciones"><a class="btn btn-lino" data-wa="¡Hola Barona! ¿Llegan a domicilio a este barrio?: " data-desde="domicilios-cobertura" href="{wa_url("¡Hola Barona! ¿Llegan a domicilio a este barrio?: ")}">{I["wa"]}Preguntar por mi barrio</a></div></div>
    <div data-m="der"><div class="horas"><h3 style="margin-bottom:6px">Horario de domicilios</h3><p style="margin-bottom:14px">{ESTADO}</p><ul>{horas_li()}</ul></div></div>
  </div>
</section>
<section class="sec crema">
  <div class="wrap duo inv">
    <div class="marco h" data-m="izq">{img("foto-vasos", "Vasos de Barona Pizza con el personaje, sobre el capó de un carro rojo", base)}</div>
    <div data-m="der"><span class="ante">Para el parche</span><h2>Pedidos grandes y eventos</h2>
      <div class="prosa bajada"><p>Cumpleaños, oficina, reunión del combo: si son muchos, escríbenos con anticipación con la fecha, la hora y cuántas personas son. Lo dejamos listo para que solo te preocupes por repartir.</p><p>Los <a class="enl" href="{base}menu/#combos">combos</a> son un buen punto de partida.</p></div>
      <div class="acciones"><a class="btn btn-rojo" data-wa="¡Hola Barona! Quiero cotizar un pedido grande. Fecha: · Personas: " data-desde="domicilios-eventos" href="{wa_url("¡Hola Barona! Quiero cotizar un pedido grande. Fecha: · Personas: ")}">{I["wa"]}Cotizar pedido grande</a></div></div>
  </div>
</section>
''' + cierre(base, 'Llegaron las pizzas', 'Bueno, casi. Falta que las pidas.', '¡Hola Barona! Quiero pedir a domicilio.',
             [('menu/', 'Menú y precios', 'Arma tu pedido aquí.'), ('preguntas/', 'Preguntas', 'Pagos, tamaños y más.'), ('ubicacion/', 'Ubicación', 'Si prefieres pasar por ella.')], pegatina='ilus-gaseosa-sticker', desde='domicilios-cierre')

def horas_li():
    return ''.join(f'<li data-dia="{d}"><span>{DIAS[d]}</span><span>{h12(D.HORARIO[d][0]) + " – " + h12(D.HORARIO[d][1]) if D.HORARIO.get(d) else "Cerrado"}</span></li>' for d in [1, 2, 3, 4, 5, 6, 0])

def p_historia(base):
    return portadilla(base, 'Historia', f'Pizza con calle desde {S["desde"]}', 'La misma pizza de siempre. Nueva imagen.', 'mascota-sticker') + f'''
<section class="sec">
  <div class="wrap duo">
    <div data-m="izq"><span class="ante">De dónde venimos</span><h2>Empezó en {S["desde"]}</h2>
      <div class="prosa bajada"><p>Barona Pizza nació en {S["ciudad"]} en {S["desde"]} con una idea que no ha cambiado: una pizza rica, hecha al momento y sin poses. Una pizzería para todos los públicos, de esas a las que uno vuelve.</p>
      <p>Casi veinte años después seguimos igual de tercos con el sabor. Lo que cambió fue la cara.</p></div></div>
    <div class="marco" data-m="der">{img("foto-miga", "Corte de una masa horneada: se ve la miga aireada y la corteza dorada", base)}</div>
  </div>
</section>
<section class="sec rojo">
  <div class="wrap duo inv">
    <div class="lam" data-m="zoom">{img("lockup-blanco", "Logo de Barona Pizza: el personaje con gorra, ESTD 2006 y el nombre", base)}</div>
    <div data-m="der"><span class="ante">La nueva imagen</span><h2>Un personaje con calle</h2>
      <div class="prosa bajada"><p>En 2025 estrenamos marca. El protagonista es un pizzero carismático, inspirado en las caricaturas de los años 30 y dibujado con trazo moderno: amigable, cotidiano y sin pretensiones. Igualito a como se come una Barona.</p>
      <p>Los colores son tres y no más: rojo ladrillo, rojo carmín y lino. Calidez, apetito y tradición, con aire para respirar.</p></div></div>
  </div>
</section>
<section class="sec crema">
  <div class="wrap">
    <span class="ante">Cómo hablamos</span><h2 data-m>Más pizza, menos drama</h2>
    <ol class="pasos claro">
      <li data-m><h3>Extra jamón</h3><p>Si vas a pedir, pide bien. Las <a class="enl" href="{base}menu/#adiciones">adiciones</a> existen por algo.</p></li>
      <li data-m style="--d:.08s"><h3>Extra queso</h3><p>Nadie se ha quejado nunca de que una pizza tenga demasiado queso.</p></li>
      <li data-m style="--d:.16s"><h3>Extra amor</h3><p>La hacemos como nos gusta comerla. Ese es todo el secreto.</p></li>
    </ol>
  </div>
</section>
<section class="sec">
  <div class="wrap duo">
    <div class="marco h" data-m="izq">{img("foto-letrero", "Letrero redondo e iluminado con la cara del personaje de Barona Pizza en la fachada de un local", base)}</div>
    <div data-m="der"><span class="ante">Míralo en movimiento</span><h2>El viaje de una Barona</h2>
      <p class="bajada">Hicimos un recorrido en 3D para contarlo sin palabras: de la masa en el aire al horno, y del horno a tu puerta.</p>
      <div class="acciones"><a class="btn btn-rojo" href="{base}3d/" data-ev="clic_viaje_3d" data-desde="historia">{I["cubo"]}Empezar el viaje</a></div></div>
  </div>
</section>
''' + cierre(base, 'La historia sigue en tu mesa', 'Pide la tuya y haz parte.', '¡Hola Barona! Quiero hacer un pedido.',
             [('menu/', 'Menú y precios', 'Lo que hay para pedir hoy.'), ('ubicacion/', 'Ubicación', 'Ven a conocernos.'), ('3d/', 'Viaje 3D', 'La historia en un minuto.')], desde='historia-cierre')

def p_ubicacion(base):
    if S['direccion']:
        dire = e(S['direccion']) + (', ' + e(S['barrio']) if S['barrio'] else '') + f'<br>{S["ciudad"]}, Colombia'
    else:
        dire = f'{S["ciudad"]}, Colombia<br><span style="font-size:.95rem;opacity:.85">Escríbenos por WhatsApp y te mandamos la ubicación exacta.</span>'
    mapa = S['maps'] or ('https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote(f'Barona Pizza {S["direccion"]} {S["ciudad"]}'.replace('  ', ' ')))
    return portadilla(base, 'Ubicación', f'Ubicación y horario en {S["ciudad"]}', 'Pasa por tu pizza, cómetela aquí o pídela a domicilio.', 'ilus-gaseosa-sticker') + f'''
<section class="sec rojo">
  <div class="wrap duo">
    <div data-m="izq">
      <dl class="filas">
        <div>{I["pin"]}<div><dt>Dirección</dt><dd>{dire}</dd></div></div>
        <div>{I["reloj"]}<div><dt>Horario</dt><dd>{horario_texto().capitalize()}</dd></div></div>
        <div>{I["tel"]}<div><dt>Pedidos por WhatsApp</dt><dd><a class="enl" data-wa="¡Hola Barona! Quiero hacer un pedido." data-desde="ubicacion" href="{wa_url("¡Hola Barona! Quiero hacer un pedido.")}">{S["whatsapp_visible"]}</a></dd></div></div>
        <div>{I["ig"]}<div><dt>Instagram</dt><dd><a class="enl" href="{S["instagram"]}" target="_blank" rel="noopener">{S["instagram_usuario"]}</a></dd></div></div>
      </dl>
      <div class="acciones"><a class="btn btn-lino" href="{mapa}" target="_blank" rel="noopener" data-ev="clic_como_llegar" data-desde="ubicacion">{I["pin"]}Cómo llegar</a><a class="btn btn-linea" data-wa="¡Hola Barona! ¿Me comparten la ubicación del local?" data-desde="ubicacion-pedir-ubicacion" href="{wa_url("¡Hola Barona! ¿Me comparten la ubicación del local?")}">{I["wa"]}Pedir la ubicación</a></div>
    </div>
    <div data-m="der"><div class="horas"><h3 style="margin-bottom:6px">Horario</h3><p style="margin-bottom:14px">{ESTADO}</p><ul>{horas_li()}</ul></div></div>
  </div>
</section>
<section class="sec crema">
  <div class="wrap duo inv">
    <div class="marco h" data-m="izq">{img("foto-letrero", "Letrero redondo e iluminado con la cara del personaje de Barona Pizza", base)}</div>
    <div data-m="der"><span class="ante">Busca la cara</span><h2>Donde veas al de la gorra, es ahí</h2>
      <div class="prosa bajada"><p>¿No quieres salir? También llegamos: mira cómo funcionan los <a class="enl" href="{base}domicilios/">domicilios</a> o arma tu pedido en el <a class="enl" href="{base}menu/">menú</a>.</p></div></div>
  </div>
</section>
''' + cierre(base, '¿Vienes o te la llevamos?', 'De las dos formas llega caliente.', '¡Hola Barona! Quiero hacer un pedido.',
             [('menu/', 'Menú y precios', 'Mira qué vas a pedir.'), ('domicilios/', 'Domicilios', 'Si prefieres quedarte en casa.'), ('preguntas/', 'Preguntas', 'Pagos, tamaños y horarios.')], pegatina='ilus-cajas-sticker', desde='ubicacion-cierre')

def p_preguntas(base):
    faq = ''.join(f'<details{" open" if i == 0 else ""}><summary>{e(q)}</summary><p>{e(a.format(horario_texto=horario_texto()))}</p></details>' for i, (q, a) in enumerate(D.PREGUNTAS))
    return portadilla(base, 'Preguntas', 'Preguntas frecuentes', 'Domicilios, horarios, tamaños y pagos: lo que la gente quiere saber antes de pedir.', 'ilus-sonrisa-sticker') + f'''
<section class="sec crema">
  <div class="wrap">
    <div class="faq">{faq}</div>
    <p class="bajada" style="margin-top:34px">¿No está tu pregunta? Escríbela tal cual por WhatsApp y te respondemos.</p>
    <div class="acciones"><a class="btn btn-rojo" data-wa="¡Hola Barona! Tengo una pregunta: " data-desde="preguntas" href="{wa_url("¡Hola Barona! Tengo una pregunta: ")}">{I["wa"]}Hacer mi pregunta</a></div>
  </div>
</section>
''' + cierre(base, 'Resuelto. ¿Pedimos?', 'El menú está a un toque.', '¡Hola Barona! Quiero hacer un pedido.',
             [('menu/', 'Menú y precios', 'Arma tu pedido.'), ('domicilios/', 'Domicilios', 'Cómo y a dónde llegamos.'), ('ubicacion/', 'Ubicación y horario', 'Para pasar por ella.')], pegatina='ilus-masa-sticker', desde='preguntas-cierre')

def p_privacidad(base):
    return portadilla(base, 'Privacidad', 'Privacidad', 'Qué datos usa este sitio y qué no. En corto y sin letra pequeña.', 'ilus-sonrisa-sticker') + f'''
<section class="sec crema"><div class="wrap prosa">
  <h2 style="font-size:1.6rem">Tu pedido se queda en tu teléfono</h2>
  <p>Lo que agregas a «Pedido» se guarda únicamente en tu navegador para que no se pierda si cambias de página. No llega a ningún servidor nuestro. Si borras los datos del navegador, se borra.</p>
  <h2 style="font-size:1.6rem;margin-top:1.4em">WhatsApp</h2>
  <p>Cuando tocas «Pedir por WhatsApp» se abre esa aplicación con el mensaje escrito. Desde ese momento la conversación se rige por las condiciones de WhatsApp. Los datos que nos des ahí (nombre, dirección, teléfono) los usamos solo para preparar y entregar tu pedido.</p>
  <h2 style="font-size:1.6rem;margin-top:1.4em">Estadísticas de visitas</h2>
  <p>Medimos de forma agregada cuánta gente entra y qué botones se usan, para mejorar el sitio. No vendemos ni compartimos datos personales. Si en algún momento activamos herramientas de publicidad que usen cookies, lo avisaremos aquí y con un aviso en pantalla.</p>
  <h2 style="font-size:1.6rem;margin-top:1.4em">Tus derechos</h2>
  <p>Puedes pedirnos en cualquier momento que consultemos, corrijamos o eliminemos los datos que nos hayas dado por WhatsApp, escribiendo al mismo número: {S["whatsapp_visible"]}.</p>
  <p style="font-size:.9rem;color:var(--tinta-2)">Última actualización: {HOY}. Barona Pizza, {S["ciudad"]}, Colombia.</p>
  <div class="acciones"><a class="btn btn-rojo" href="{base}menu/">Ir al menú</a><a class="btn btn-linea" href="{base}">Volver al inicio</a></div>
</div></section>'''

def p_creditos(base):
    return portadilla(base, 'Créditos', 'Cómo está hecho este sitio', 'Quién lo hizo y con qué.', 'ilus-mano-sticker') + f'''
<section class="sec crema"><div class="wrap prosa">
  <p><b>Diseño, desarrollo y contenido audiovisual:</b> <a href="https://studiobashi.com" target="_blank" rel="noopener">BASHI</a>.</p>
  <p><b>Identidad de marca:</b> manual de marca Barona Pizza (2025). Colores rojo ladrillo, rojo carmín y lino; personaje y recursos gráficos del manual.</p>
  <p><b>Tipografía:</b> Archivo, variable (Omnibus-Type, licencia SIL Open Font). El manual usa PC Merchis y Antipol; cuando la marca entregue las licencias web se cambian en una línea.</p>
  <p><b>Tecnología:</b> HTML, CSS y JavaScript sin framework. El <a href="{base}3d/">viaje 3D</a> usa three.js, GSAP y Lenis sobre un motor propio de BASHI. Alojado en Cloudflare Pages.</p>
  <p><b>Accesibilidad y rendimiento:</b> todo el contenido está en HTML, el sitio se puede recorrer con teclado, respeta la preferencia de movimiento reducido y el 3D tiene versión en texto.</p>
  <div class="acciones"><a class="btn btn-rojo" href="{base}menu/">Ir al menú</a><a class="btn btn-linea" href="{base}3d/">Ver el viaje 3D</a></div>
</div></section>'''

def p_404(base):
    return f'''<section class="sec rojo cierre" style="min-height:76vh;display:grid;align-items:center">
  <div class="wrap">
    {img("ilus-sonrisa-sticker", "", base, cls="pegatina", lazy=False)}
    <p class="ante">Error 404</p><h1 style="max-width:14ch;margin:0 auto">Esta página se la comieron</h1>
    <p class="bajada">La dirección no existe o cambió. Lo que sí existe es la pizza.</p>
    <div class="acciones"><a class="btn btn-lino" href="/menu/">Ver el menú</a><a class="btn btn-linea" href="/">Ir al inicio</a></div>
    <nav class="sigue" aria-label="Otras páginas"><a href="/domicilios/"><b>Domicilios</b><span>Cómo pedir y a dónde llegamos.</span></a><a href="/ubicacion/"><b>Ubicación y horario</b><span>Para pasar por ella.</span></a><a href="/3d/"><b>Viaje 3D</b><span>Del horno a tu puerta.</span></a></nav>
  </div>
</section>'''

def menu_ld():
    return {"@context": "https://schema.org", "@type": "Menu", "@id": URL + "/menu/#menu", "name": "Menú de Barona Pizza", "url": URL + "/menu/", "inLanguage": "es-CO",
            "hasMenuSection": [{"@type": "MenuSection", "name": g['nombre'], "hasMenuItem": [
                {"@type": "MenuItem", "name": it['n'], "description": it['d'], **({"suitableForDiet": "https://schema.org/VegetarianDiet"} if it.get('veg') else {}),
                 "offers": [{"@type": "Offer", "name": t, "price": pr, "priceCurrency": "COP"} for t, pr in it['p']]} for it in g['items']]} for g in D.MENU]}

PAGINAS = [
    dict(ruta='', slug='inicio', f=p_inicio, titulo=f'Pizzería en {S["ciudad"]} a domicilio desde {S["desde"]} | Barona Pizza',
         desc=f'Barona Pizza: pizzería en {S["ciudad"]} desde {S["desde"]}. Pizza horneada al momento, a domicilio o para recoger. Arma tu pedido y mándalo por WhatsApp. Más pizza, menos drama.',
         og='Barona Pizza — Más pizza, menos drama', ogt='Más pizza, menos drama', ogs=f'Pizzería en {S["ciudad"]} · desde {S["desde"]}', prio='1.0',
         ld=[restaurante(), {"@context": "https://schema.org", "@type": "WebSite", "name": "Barona Pizza", "url": URL + "/", "inLanguage": "es-CO"}]),
    dict(ruta='menu/', slug='menu', f=p_menu, titulo=f'Menú y precios: pizzas, combos y adiciones en {S["ciudad"]} | Barona Pizza',
         desc=f'Menú de Barona Pizza con precios: pizzas personales, medianas y grandes, combos, adiciones y bebidas. Pide por WhatsApp a domicilio en {S["ciudad"]} o para recoger.',
         ogt='Menú y precios', ogs='Pizzas, combos, adiciones y bebidas', prio='0.9', wa='¡Hola Barona! Vengo del menú y quiero pedir.', ld=[menu_ld(), migas_ld('Menú', 'menu/')]),
    dict(ruta='domicilios/', slug='domicilios', f=p_domicilios, titulo=f'Pizza a domicilio en {S["ciudad"]}: pide por WhatsApp | Barona Pizza',
         desc=f'Pide pizza a domicilio en {S["ciudad"]} directo por WhatsApp, sin aplicaciones. Te confirmamos cobertura, valor del envío y tiempo de entrega al instante. También para recoger.',
         ogt='Pizza a domicilio', ogs=f'{S["ciudad"]} · pides por WhatsApp', prio='0.9', wa='¡Hola Barona! Quiero pedir a domicilio.', ld=[migas_ld('Domicilios', 'domicilios/')]),
    dict(ruta='historia/', slug='historia', f=p_historia, titulo=f'Nuestra historia: pizzería bogotana desde {S["desde"]} | Barona Pizza',
         desc=f'Barona Pizza hace pizza en {S["ciudad"]} desde {S["desde"]}. La misma receta de siempre y una nueva imagen con un personaje inspirado en las caricaturas de los años 30.',
         ogt=f'Pizza con calle desde {S["desde"]}', ogs='La misma pizza de siempre. Nueva imagen.', prio='0.6', ld=[migas_ld('Historia', 'historia/')]),
    dict(ruta='ubicacion/', slug='ubicacion', f=p_ubicacion, titulo=f'Ubicación y horario de la pizzería en {S["ciudad"]} | Barona Pizza',
         desc=f'Dónde queda Barona Pizza en {S["ciudad"]}, horario de atención y cómo llegar. Pide para recoger o a domicilio por WhatsApp.',
         ogt='Ubicación y horario', ogs=f'{S["ciudad"]}, Colombia', prio='0.8', wa='¡Hola Barona! Vi la ubicación y quiero pedir.', ld=[restaurante(), migas_ld('Ubicación', 'ubicacion/')]),
    dict(ruta='preguntas/', slug='preguntas', f=p_preguntas, titulo='Preguntas frecuentes: domicilios, pagos y horarios | Barona Pizza',
         desc=f'Respuestas rápidas sobre Barona Pizza en {S["ciudad"]}: cómo pedir, cobertura de domicilios, horarios, tamaños, opciones vegetarianas, pagos y pedidos para eventos.',
         ogt='Preguntas frecuentes', ogs='Domicilios, pagos y horarios', prio='0.7',
         ld=[{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a.format(horario_texto=horario_texto())}} for q, a in D.PREGUNTAS]}, migas_ld('Preguntas', 'preguntas/')]),
    dict(ruta='privacidad/', slug='privacidad', f=p_privacidad, titulo='Privacidad | Barona Pizza', desc='Qué datos usa el sitio de Barona Pizza: el pedido se guarda en tu teléfono y sale por WhatsApp. Sin letra pequeña.', ogt='Privacidad', ogs='Barona Pizza', prio='0.2'),
    dict(ruta='creditos/', slug='creditos', f=p_creditos, titulo='Créditos: cómo está hecho este sitio | Barona Pizza', desc='Sitio de Barona Pizza diseñado y desarrollado por BASHI. Tipografía, tecnología y créditos de marca.', ogt='Créditos', ogs='Sitio por BASHI', prio='0.2'),
]
P404 = dict(ruta='404.html', slug='inicio', f=p_404, titulo='Página no encontrada | Barona Pizza', desc='Esta página no existe. Mira el menú de Barona Pizza o vuelve al inicio.', noindex=True)

def escribir(ruta, contenido):
    p = os.path.join(DIST, ruta); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(contenido)

def main():
    if os.path.exists(DIST): shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, 'css'))
    shutil.copytree(os.path.join(ROOT, 'static', 'img'), os.path.join(DIST, 'img'), ignore=shutil.ignore_patterns('sizes.json'))
    os.makedirs(os.path.join(DIST, 'fonts')); shutil.copy(os.path.join(ROOT, 'static', 'fonts', 'archivo.woff2'), os.path.join(DIST, 'fonts'))
    os.makedirs(os.path.join(DIST, 'js'))
    for f in ('lenis.min.js', 'gsap.min.js', 'ScrollTrigger.min.js', 'three.min.js'): shutil.copy(os.path.join(ROOT, 'static', 'js', f), os.path.join(DIST, 'js'))
    shutil.copy(os.path.join(ROOT, 'src', 'site.css'), os.path.join(DIST, 'css', 'site.css'))
    shutil.copy(os.path.join(ROOT, 'src', 'site.js'), os.path.join(DIST, 'js', 'site.js'))

    for p in PAGINAS + [P404]:
        base = '/' if p is P404 else ('../' if p['ruta'] else '')
        if p is not P404: og_image(p['slug'], p['ogt'], p['ogs'])
        out = cabeza(p, base) + '<body>\n' + nav(p, base) + '<main id="contenido">\n' + p['f'](base) + '\n</main>\n' + pie(p, base) + '</body>\n</html>\n'
        escribir(p['ruta'] + ('index.html' if not p['ruta'].endswith('.html') else ''), out)

    import viaje
    v = viaje.construir(dict(ROOT=ROOT, DIST=DIST, URL=URL, S=S, D=D, cabeza=cabeza, nav=nav, pie=pie, img=img, I=I, wa_url=wa_url, plata=plata, por_id=por_id, tarjeta=tarjeta,
                             cierre=cierre, ld=ld, migas_ld=migas_ld, og_image=og_image, e=e, escribir=escribir))
    todas = PAGINAS + [v]

    # la propuesta comercial vive aparte y fuera del índice
    prop = os.path.join(ROOT, 'static', 'propuesta.html')
    if os.path.exists(prop): shutil.copy(prop, os.path.join(DIST, 'propuesta.html'))

    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        f'  <url><loc>{URL}/{p["ruta"]}</loc><lastmod>{HOY}</lastmod><priority>{p["prio"]}</priority></url>\n' for p in todas) + '</urlset>\n'
    escribir('sitemap.xml', sm)
    escribir('robots.txt', f'User-agent: *\nAllow: /\nDisallow: /propuesta\n\nSitemap: {URL}/sitemap.xml\n')
    escribir('_headers', '''/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), interest-cohort=()
  Strict-Transport-Security: max-age=31536000; includeSubDomains

/img/*
  Cache-Control: public, max-age=2592000, stale-while-revalidate=86400
/fonts/*
  Cache-Control: public, max-age=31536000, immutable
/js/three.min.js
  Cache-Control: public, max-age=31536000, immutable
/js/gsap.min.js
  Cache-Control: public, max-age=31536000, immutable
/js/ScrollTrigger.min.js
  Cache-Control: public, max-age=31536000, immutable
/js/lenis.min.js
  Cache-Control: public, max-age=31536000, immutable
/css/*
  Cache-Control: public, max-age=3600, stale-while-revalidate=86400
/js/*
  Cache-Control: public, max-age=3600, stale-while-revalidate=86400
/propuesta*
  X-Robots-Tag: noindex, nofollow
''')
    escribir('_redirects', '/menu.html /menu/ 301\n/carta /menu/ 301\n/pedir /menu/ 301\n/domicilio /domicilios/ 301\n/nosotros /historia/ 301\n/contacto /ubicacion/ 301\n/faq /preguntas/ 301\n/viaje /3d/ 301\n')

    # solo se publican las imágenes que alguna página usa
    texto = ''
    for dp, _, fs in os.walk(DIST):
        for f in fs:
            if f.endswith(('.html', '.js', '.css')) and not f.endswith('.min.js'): texto += open(os.path.join(dp, f), encoding='utf-8').read()
    for f in os.listdir(os.path.join(DIST, 'img')):
        if f not in texto and not f.startswith(('og-', 'favicon', 'icono')): os.remove(os.path.join(DIST, 'img', f))

    tot = 0
    for dp, _, fs in os.walk(DIST):
        for f in fs: tot += os.path.getsize(os.path.join(dp, f))
    print(f'listo: {len(todas)} páginas + 404 · {tot // 1024} KB en dist/ · URL {URL}')
    pend = [k for k in ('direccion', 'barrio', 'maps') if not S[k]] + [k for k, v in D.MEDICION.items() if not v] + (['reels'] if not D.REELS else []) + (['reseñas'] if not D.RESENAS else [])
    if pend: print('pendiente en datos.py:', ', '.join(pend))

if __name__ == '__main__':
    main()
