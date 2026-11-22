# Barona Pizza — sitio web + viaje 3D

Sitio estático de varias páginas, hecho por BASHI. Aplica el "Plan maestro" (texto real en HTML, SEO local, medición, páginas por intención) y el motor de viaje 3D con un recorrido propio de Barona.

## Qué hay

| Ruta | Qué es |
|---|---|
| `dist/` | **El sitio listo para publicar.** Esto es lo que sube Wrangler |
| `datos.py` | **Lo único que se edita para cambiar contenido**: WhatsApp, dirección, horario, menú, precios, preguntas, reels, reseñas, medición |
| `build.py` | Arma `dist/` (páginas, datos estructurados, sitemap, robots, `_headers`, imágenes para compartir) |
| `viaje.py`, `src/viaje.js`, `src/viaje.css` | El viaje 3D (`/3d/`) |
| `src/site.css`, `src/site.js` | Diseño e interfaz de todo el sitio (pedido, medición, movimiento) |
| `static/` | Logos e ilustraciones sacados del manual, fuente, librerías, `propuesta.html` |
| `assets.py` | Vuelve a sacar los recursos del manual (solo si cambia el manual) |
| `pruebas/` | Capturas automáticas con Playwright |

## Cambiar algo y publicar

```
python3 build.py
npx wrangler@latest pages deploy dist --project-name=barona-pizza --commit-dirty=true
```

`build.py` necesita Pillow una sola vez: `pip3 install pillow`.
Para ver el sitio en tu Mac antes de subir: `python3 -m http.server 8000 -d dist` y abre `http://localhost:8000`.

## Páginas

`/` · `/menu/` · `/domicilios/` · `/historia/` · `/ubicacion/` · `/preguntas/` · `/3d/` · `/privacidad/` · `/creditos/` · `404` · `/propuesta` (fuera del índice).

## El viaje 3D

Concepto: **sigues a una pizza desde la masa en el aire hasta tu puerta.** Cinco actos: La masa, Los extras, El horno, La carta, Llegó.
No se parece al de PIYION: no hay cielo ni fotos; todo es masa, ingredientes, ladrillo y pizzas hechas por código, en los tres colores del manual, más las calcomanías del personaje.

- Las pizzas de la carta se pueden tocar: la cámara se acerca y aparece el botón para agregarla al pedido. Salen de `CARTA_3D` en `datos.py`.
- El enjambre de ingredientes se espanta con el cursor o el dedo y al final dibuja la B.
- Ritmo y cámara: `RM` y `KEYS` en `src/viaje.js`. Actos y textos: `CH`.
- Debajo del viaje está el mismo contenido en texto. Sin WebGL (o con `?sin3d`) la página arranca directo ahí.
- Parámetros de prueba: `?q=low|mid|high`, `?snap`, `?sin3d`.

## Pendiente de Barona (todo en `datos.py`)

- Dirección, barrio, enlace de "Cómo llegar" y coordenadas.
- Confirmar horario, nombres y precios del menú (hoy son de muestra).
- Medios de pago y zonas de domicilio, para responderlos en `/preguntas/`.
- Reseñas reales y los reels del plan audiovisual: al pegarlos aparecen solos en la portada.
- Códigos de medición (Cloudflare Web Analytics, GA4, Clarity, Meta).
- Licencias web de PC Merchis y Antipol; mientras tanto se usa Archivo variable.

## Probado y sin probar

Probado en Chromium sin tarjeta gráfica: todas las páginas a 390 y 1280 px sin desborde ni errores de consola, enlaces internos, pedido y enlace de WhatsApp, el viaje completo en escritorio y celular, tocar una pizza y agregarla, y la versión sin WebGL.
Sin probar: Safari en iPhone, un Android real, giroscopio y rendimiento con tarjeta gráfica real.
