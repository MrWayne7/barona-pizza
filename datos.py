# -*- coding: utf-8 -*-
"""
DATOS DE BARONA PIZZA — este es el único archivo que hay que editar para cambiar
contenido del sitio. Después de editar:  python3 build.py

Lo marcado con  # CONFIRMAR  es dato de muestra o pendiente: hay que pedírselo a Barona.
Un campo vacío ("") no se publica: el sitio muestra un texto neutro en su lugar.
"""

SITIO = {
    "url": "https://barona-pizza.pages.dev",     # cambia al dominio propio cuando exista (sin / al final)
    "nombre": "Barona Pizza",
    "lema": "Más pizza, menos drama.",
    "ciudad": "Bogotá",
    "pais": "CO",
    "desde": 2006,
    "whatsapp": "573142953367",                  # código de país + número, sin + ni espacios
    "whatsapp_visible": "+57 314 2953367",
    "instagram": "https://www.instagram.com/baronapizza/",
    "instagram_usuario": "@baronapizza",
    "direccion": "",                             # CONFIRMAR  ej: "Cra 13 # 45-67"
    "barrio": "",                                # CONFIRMAR  ej: "Chapinero"
    "maps": "",                                  # CONFIRMAR  enlace de "Cómo llegar" del Perfil de Negocio de Google
    "lat": None, "lng": None,                    # CONFIRMAR  coordenadas del local
    "precio_rango": "$$",
}

# Horario — CONFIRMAR. 0 = domingo … 6 = sábado. Horas en formato 24 h, hora de Bogotá.
HORARIO = {d: ("15:00", "23:00") for d in range(7)}

# Medición. Vacío = no se instala. (Plan maestro: "todo lo que no se mide no se puede mejorar")
MEDICION = {
    "cloudflare_token": "",      # Cloudflare Web Analytics (gratis, sin cookies)
    "ga4": "",                   # ej: "G-XXXXXXX"
    "clarity": "",               # Microsoft Clarity: grabaciones de sesión
    "meta_pixel": "",            # Píxel de Meta
}

# Reels del plan audiovisual. Cuando existan, pega aquí el enlace de cada uno y aparecen solos en la portada.
# ej: {"titulo": "La nueva cara de Barona", "url": "https://www.instagram.com/reel/XXXX/", "poster": "img/reel-1.webp"}
REELS = []

# Reseñas REALES (nombre + texto + fuente). Vacío = la sección no aparece. Nunca inventar.
RESENAS = []

# ------------------------------------------------------------------ MENÚ  (CONFIRMAR nombres y precios)
P, M, G = "Personal", "Mediana", "Grande"
MENU = [
    {"id": "pizzas", "nombre": "Pizzas", "nota": "Horneadas al momento. Elige tamaño.", "items": [
        {"id": "la-de-siempre", "n": "La de Siempre", "d": "Mozzarella, salsa de tomate de la casa y albahaca fresca. La clásica.", "p": [(P, 18900), (M, 32900), (G, 45900)], "veg": True},
        {"id": "pepperoni-party", "n": "Pepperoni Party", "d": "Doble pepperoni y mozzarella derretida. Para los de siempre.", "p": [(P, 21900), (M, 36900), (G, 49900)]},
        {"id": "la-chimba", "n": "La Chimba", "d": "La especial de la casa: chorizo, maíz tierno y cebolla caramelizada.", "p": [(P, 25900), (M, 43900), (G, 57900)], "tag": "La favorita"},
        {"id": "barona-suprema", "n": "Barona Suprema", "d": "Pepperoni, jamón, champiñón, pimentón y cebolla. La más completa.", "p": [(P, 24900), (M, 41900), (G, 55900)]},
        {"id": "hawaiana-sin-drama", "n": "Hawaiana sin Drama", "d": "Jamón y piña. Sí, piña. Y no pasa nada.", "p": [(P, 21900), (M, 36900), (G, 49900)]},
        {"id": "cuatro-quesos", "n": "Cuatro Quesos", "d": "Mozzarella, parmesano, queso crema y un toque de queso azul.", "p": [(P, 23900), (M, 39900), (G, 53900)], "veg": True},
        {"id": "pollo-bbq", "n": "Pollo BBQ", "d": "Pollo, salsa BBQ, cebolla morada y cilantro.", "p": [(P, 23900), (M, 39900), (G, 53900)]},
        {"id": "vegetariana-del-barrio", "n": "Vegetariana del Barrio", "d": "Champiñón, pimentón, cebolla, maíz y aceitunas.", "p": [(P, 22900), (M, 37900), (G, 51900)], "veg": True},
    ]},
    {"id": "para-picar", "nombre": "Para picar", "nota": "Mientras llega la pizza.", "items": [
        {"id": "pan-de-ajo", "n": "Pan de ajo", "d": "Recién horneado, con mantequilla de ajo y orégano.", "p": [("Porción", 9900)], "veg": True},
        {"id": "palitos-de-queso", "n": "Palitos de queso", "d": "Masa de la casa rellena de mozzarella. Adictivos.", "p": [("x6", 12900)], "veg": True},
        {"id": "alitas-bbq", "n": "Alitas BBQ", "d": "Bañadas en salsa BBQ con un toque picante.", "p": [("x6", 18900), ("x12", 33900)]},
    ]},
    {"id": "combos", "nombre": "Combos", "nota": "Para el parche.", "items": [
        {"id": "combo-solo", "n": "Combo Solo", "d": "Pizza personal + bebida. Para el hambre express.", "p": [("Combo", 26900)]},
        {"id": "combo-parche", "n": "Combo Parche", "d": "Pizza grande + pan de ajo + 2 bebidas. Para compartir.", "p": [("Combo", 64900)], "tag": "Para compartir"},
        {"id": "combo-familiar", "n": "Combo Familiar", "d": "2 pizzas grandes + 4 bebidas. Para todos.", "p": [("Combo", 109900)]},
    ]},
    {"id": "adiciones", "nombre": "Adiciones", "nota": "Extra jamón, extra queso, extra amor.", "items": [
        {"id": "extra-queso", "n": "Extra queso", "d": "Más mozzarella. Siempre es buena idea.", "p": [("Adición", 4900)], "veg": True},
        {"id": "extra-jamon", "n": "Extra jamón", "d": "Para subirle el nivel.", "p": [("Adición", 5900)]},
        {"id": "extra-pepperoni", "n": "Extra pepperoni", "d": "Nunca es suficiente.", "p": [("Adición", 5900)]},
    ]},
    {"id": "bebidas", "nombre": "Bebidas", "nota": "Bien frías.", "items": [
        {"id": "gaseosa", "n": "Gaseosa personal", "d": "350 ml. Pregunta por los sabores.", "p": [("Unidad", 4900)]},
        {"id": "limonada", "n": "Limonada natural", "d": "Bien fría, como debe ser.", "p": [("Vaso", 6900)]},
        {"id": "cerveza", "n": "Cerveza nacional", "d": "330 ml. Para acompañar el parche.", "p": [("Unidad", 7900)]},
        {"id": "agua", "n": "Agua", "d": "600 ml, con o sin gas.", "p": [("Botella", 3900)]},
    ]},
]
FAVORITAS = ["la-chimba", "pepperoni-party", "la-de-siempre"]       # las tres de la portada
CARTA_3D = ["la-de-siempre", "pepperoni-party", "la-chimba", "barona-suprema", "hawaiana-sin-drama", "cuatro-quesos"]   # las que flotan en el viaje

# ------------------------------------------------------------------ PREGUNTAS
# Plan maestro: llenar con lo que la gente pregunta de verdad por WhatsApp, con sus palabras.
PREGUNTAS = [
    ("¿Hacen domicilios?", "Sí. Armas tu pedido en el menú, lo mandas por WhatsApp y ahí mismo te confirmamos el valor del domicilio y el tiempo de entrega según tu barrio."),
    ("¿Hasta dónde llegan en Bogotá?", "Depende de la zona. Escríbenos tu barrio o tu dirección por WhatsApp y te decimos al instante si llegamos y cuánto cuesta el envío."),
    ("¿Cómo pido?", "Entra al menú, agrega lo que quieras y toca «Pedir por WhatsApp». Se abre el chat con tu pedido ya escrito; solo pones tu nombre, la dirección y cómo vas a pagar."),
    ("¿Cuál es el horario?", "Atendemos {horario_texto}. Arriba en cada página ves si estamos abiertos en este momento."),
    ("¿Qué tamaños de pizza tienen?", "Personal, mediana y grande. En el menú eliges el tamaño de cada pizza y ves el precio de una vez."),
    ("¿Tienen opciones vegetarianas?", "Sí. En el menú están marcadas con la etiqueta «Vegetariana». Si quieres quitar o cambiar un ingrediente, dilo en el pedido."),
    ("¿Cómo puedo pagar?", "Lo confirmas por WhatsApp al hacer el pedido: ahí te decimos los medios de pago disponibles ese día."),
    ("¿Puedo pedir para un evento o para mucha gente?", "Claro. Para pedidos grandes escríbenos con anticipación por WhatsApp con la fecha, la hora y cuántas personas son, y lo dejamos listo."),
    ("¿Puedo recoger en el local?", "Sí. Haz el pedido por WhatsApp, te decimos en cuánto está listo y pasas por él."),
]
