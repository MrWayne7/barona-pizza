#!/usr/bin/env python3
"""Capturas del viaje 3D. uso: python3 pruebas/viaje.py <nombre> <ancho> <alto> h0,h10,… [--touch] [--cols N]   (hNN = NN % del scroll del viaje)
QS="&q=mid" para forzar calidad."""
import sys, asyncio, math, os, subprocess, time
from playwright.async_api import async_playwright
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get('OUT', '/tmp')
async def main():
    name, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); poss = sys.argv[4].split(','); touch = '--touch' in sys.argv
    cols = int(sys.argv[sys.argv.index('--cols') + 1]) if '--cols' in sys.argv else 4
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', '8772', '-d', os.path.join(ROOT, 'dist')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, has_touch=touch, is_mobile=touch)
            page = await ctx.new_page(); errs = []
            page.on('console', lambda m: errs.append(m.text) if m.type in ('error', 'warning') else None)
            page.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
            await page.goto('http://localhost:8772/3d/?snap' + os.environ.get('QS', ''))
            for cls in ('ready', 'sky-on'):
                try: await page.wait_for_selector('html.' + cls, timeout=20000)
                except Exception: errs.append(cls + ' timeout')
            await page.wait_for_timeout(3500); shots = []
            for pos in poss:
                if pos.startswith('h'):
                    y = await page.evaluate(f"(document.getElementById('top').offsetHeight - innerHeight) * {float(pos[1:]) / 100}")
                else:
                    sel, off = (pos.split('+') + ['0'])[:2]
                    y = await page.evaluate(f"document.querySelector('{sel}').getBoundingClientRect().top + scrollY + {int(off)}")
                await page.evaluate(f"window.scrollTo({{top:{y},behavior:'instant'}})"); await page.wait_for_timeout(1600)
                fn = f"{OUT}/{name}_{pos.replace('#', '').replace('+', '_')}.png"; await page.screenshot(path=fn); shots.append(fn)
            info = await page.evaluate("({sw:document.documentElement.scrollWidth, iw:innerWidth, tier: window.__sky && window.__sky() ? window.__sky().tier() : -1})")
            print('pagina', info, '| desborde:', info['sw'] > info['iw'])
            for e in errs[:12]: print('  consola:', e[:300])
            await b.close()
    finally: srv.terminate()
    ims = [Image.open(s).convert('RGB') for s in shots]
    scale = min(1.0, 640 / w) if w > h else min(1.0, 330 / w)
    ims = [im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS) for im in ims]
    rows = math.ceil(len(ims) / cols); cw, ch = ims[0].size
    sheet = Image.new('RGB', (cols * cw + (cols - 1) * 6, rows * ch + (rows - 1) * 6), (255, 0, 255))
    for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * (cw + 6), (i // cols) * (ch + 6)))
    out = f"{OUT}/{name}_hoja.jpg"; sheet.save(out, quality=84); print('hoja', out, sheet.size)
asyncio.run(main())
