# -*- coding: utf-8 -*-
"""Página /3d/: el viaje de una Barona. Usa src/viaje.js (mundo 3D) y src/viaje.css."""
import os, json, shutil

TOPS = {   # qué lleva encima cada pizza del viaje (solo para dibujarla)
    'la-de-siempre': ['albahaca'], 'pepperoni-party': ['pepperoni'], 'la-chimba': ['chorizo', 'maiz', 'cebolla'],
    'barona-suprema': ['pepperoni', 'jamon', 'champinon', 'pimenton'], 'hawaiana-sin-drama': ['jamon', 'pina'], 'cuatro-quesos': ['queso', 'azul'],
    'pollo-bbq': ['jamon', 'cebolla', 'albahaca'], 'vegetariana-del-barrio': ['champinon', 'pimenton', 'maiz', 'aceituna'],
}
ACTOS = [
    ('La masa', 'Todo empieza en el aire. Una bola de masa se abre girando entre harina, hasta volverse el disco donde va a pasar todo lo demás.'),
    ('Los extras', 'Extra jamón, extra queso, extra amor. Una lluvia de pepperoni, mozzarella y albahaca cruza la cocina; si la tocas, se espanta.'),
    ('El horno', 'Cruzas la boca de ladrillo y entras al fuego. Aquí adentro pasa lo importante, y pasa rápido: la pizza sale al momento.'),
    ('La carta', 'Seis pizzas de la casa flotan en la sala. Tocas una, la cámara se acerca, ves qué lleva y cuánto cuesta, y la agregas a tu pedido.'),
    ('Llegó', 'Los ingredientes arman la B de Barona frente al letrero encendido. Más pizza, menos drama: lo único que falta es que pidas la tuya.'),
]

def construir(c):
    ROOT, DIST, URL, S, D = c['ROOT'], c['DIST'], c['URL'], c['S'], c['D']
    img, I, wa_url, plata, e = c['img'], c['I'], c['wa_url'], c['plata'], c['e']
    base = '../'
    p = dict(ruta='3d/', slug='3d', prio='0.7',
             titulo='El viaje de una Barona: del horno a tu puerta en 3D | Barona Pizza',
             desc=f'Recorre en 3D el viaje de una pizza de Barona: la masa en el aire, la lluvia de extras, el horno por dentro y la carta flotando. Toca una pizza y pídela a domicilio en {S["ciudad"]}.',
             og='El viaje de una Barona — del horno a tu puerta', wa='¡Hola Barona! Vengo del viaje 3D y quiero pedir.')
    p['ld'] = [c['migas_ld']('Viaje 3D', '3d/'),
               {"@context": "https://schema.org", "@type": "WebPage", "name": "El viaje de una Barona", "url": URL + "/3d/", "inLanguage": "es-CO", "about": {"@id": URL + "/#restaurante"},
                "description": p['desc'], "hasPart": [{"@type": "WebPageElement", "name": n, "description": t} for n, t in ACTOS]}]
    c['og_image']('3d', 'El viaje de una Barona', 'Del horno a tu puerta · experiencia 3D')

    sz = json.load(open(os.path.join(ROOT, 'static', 'img', 'sizes.json')))
    tex = {k: {"u": f"{base}img/{f}.webp", "a": round(sz[f][0] / sz[f][1], 4)} for k, f in
           dict(masa='ilus-masa-sticker', mano='ilus-mano-sticker', gaseosa='ilus-gaseosa-sticker', cajas='ilus-cajas-sticker', fiesta='ilus-fiesta-sticker').items()}
    carta = []
    for i in D.CARTA_3D:
        it = c['por_id'](i); t, pr = it['p'][0]
        carta.append({"n": it['n'], "d": it['d'], "t": t, "p": pr, "precio": plata(pr), "varios": len(it['p']) > 1, "tops": TOPS.get(i, ['pepperoni'])})
    cfg = {"libs": {"three": base + "js/three.min.js", "lenis": base + "js/lenis.min.js"}, "tex": tex, "carta": carta}
    js = open(os.path.join(ROOT, 'src', 'viaje.js'), encoding='utf-8').read().replace('__CFG__', json.dumps(cfg, ensure_ascii=False, separators=(',', ':')))
    open(os.path.join(DIST, 'js', 'viaje.js'), 'w', encoding='utf-8').write(js)
    shutil.copy(os.path.join(ROOT, 'src', 'viaje.css'), os.path.join(DIST, 'css', 'viaje.css'))

    extra = f'<link rel="stylesheet" href="{base}css/viaje.css">\n<link rel="preload" as="script" href="{base}js/three.min.js">\n'
    actos = ''.join(f'<li data-m><h3>{e(n)}</h3><p>{e(t)}</p></li>' for n, t in ACTOS)
    cartas = ''.join(c['tarjeta'](c['por_id'](i), base, k) for k, i in enumerate(D.CARTA_3D))
    cuerpo = f'''<body class="p3d">
<div id="mundo-bg" aria-hidden="true"></div>
<canvas id="mundo" aria-hidden="true"></canvas>
<div id="loader" role="status" aria-live="polite"><div class="loader-in">{img("mascota-blanca", "", base, lazy=False)}<div class="loader-wm">Barona<br>Pizza</div><div class="loader-row"><span>Precalentando el horno</span><span id="load-n">0°</span></div></div></div>
<div class="cur" id="cur" aria-hidden="true"></div>
{c["nav"](p, base, " nav-viaje")}
<header class="viaje3d" id="top" aria-label="El viaje de una Barona, recorrido en 3D">
  <div class="hero-ui" id="hero-ui">
    <div class="gyro-row"><button id="gyro" class="gyro" type="button" hidden>Mover con el teléfono</button></div>
    <div class="hero-core"><div class="hero-title" id="hero-title">
      <p class="pre">Barona Pizza · {S["ciudad"]} · desde {S["desde"]}</p>
      <h1><span style="--i:0"><i>El viaje</i></span><span style="--i:1"><i>de una</i></span><span style="--i:2"><i>Barona</i></span></h1>
      <p class="sub">Del horno a tu puerta, en un minuto.</p>
    </div></div>
    <div class="hero-foot">
      <div class="cap" id="cap" aria-live="polite"><div class="cap-n" id="cap-n">01</div><div><div class="cap-t" id="cap-t">La masa</div><div class="cap-s" id="cap-s">Todo empieza en el aire.</div></div></div>
      <div class="piece" id="piece" aria-live="polite">
        <div class="piece-n" id="piece-n">01</div>
        <div><div class="piece-t" id="piece-t"></div><p id="piece-d"></p><b class="piece-p" id="piece-p"></b>
          <div class="piece-act"><button class="btn btn-rojo btn-s" id="piece-go" type="button">Agregar al pedido</button><button class="btn btn-linea btn-s" id="piece-close" type="button">Seguir el viaje</button></div></div>
      </div>
      <div class="hero-bar"><span id="bar-idx">01 / 05</span><div class="bar-line"><i id="bar-fill"></i></div><a href="#llegada" class="skip" id="saltar">Saltar el viaje</a></div>
      <div class="hint" id="hint" aria-hidden="true"><span></span>Desliza para empezar</div>
    </div>
  </div>
</header>
<main id="contenido">
<section class="sec cierre" id="llegada">
  <div class="wrap">
    {img("ilus-cajas-sticker", "El pizzero de Barona cargando una torre de cajas de pizza", base, cls="pegatina", extra='data-m="zoom"')}
    <span class="ante">Llegó</span><h2 data-m>Ahora pide la tuya</h2>
    <p class="bajada" data-m>Ese fue el viaje. El de verdad empieza cuando mandas el pedido: sale del horno a tu caja y de ahí a tu puerta, en {S["ciudad"]}.</p>
    <div class="acciones" data-m><a class="btn btn-rojo" href="{base}menu/" data-ev="clic_pedir" data-desde="viaje-llegada">Ver el menú completo</a><a class="btn btn-wa" data-wa="{e(p["wa"])}" data-desde="viaje-llegada" href="{wa_url(p["wa"])}">{I["wa"]}Pedir por WhatsApp</a></div>
  </div>
</section>
<div class="cuadros" aria-hidden="true"></div>
<section class="sec crema" id="carta">
  <div class="wrap">
    <div class="cab"><div><span class="ante">Las del viaje</span><h2 data-m>La carta que viste flotando</h2></div><a class="btn btn-linea" href="{base}menu/" data-m>Menú completo</a></div>
    <div class="rej">{cartas}</div>
  </div>
</section>
<section class="sec" id="actos">
  <div class="wrap">
    <span class="ante">El mismo viaje, contado</span><h2 data-m>Cinco actos, de la masa a tu puerta</h2>
    <p class="bajada" data-m>¿Saltaste el recorrido o prefieres leerlo? Esto es lo que pasa en él. Y si quieres saber de dónde viene todo, está <a class="enl" href="{base}historia/">la historia de Barona desde {S["desde"]}</a>.</p>
    <ol class="actos">{actos}</ol>
    <div class="acciones"><a class="btn btn-linea" href="#top">Volver a empezar el viaje</a></div>
  </div>
</section>
''' + c['cierre'](base, 'Más pizza, menos drama', 'Arma tu pedido y mándalo por WhatsApp. Así de fácil.', p['wa'],
                  [('menu/', 'Menú y precios', 'Todo lo que hay para pedir.'), ('domicilios/', 'Domicilios', 'Cómo pedir y a dónde llegamos.'), ('historia/', 'Historia', 'Pizza con calle desde 2006.')], desde='viaje-cierre') + f'''
</main>
{c["pie"](p, base)}<script src="{base}js/viaje.js" defer></script>
</body>
</html>
'''
    c['escribir']('3d/index.html', c['cabeza'](p, base, extra) + cuerpo)
    return p
