#!/usr/bin/env python3
"""Capturas de página completa + errores de consola + desborde horizontal.
uso: python3 pruebas/paginas.py <salida> <ancho> <alto> ruta[,ruta…] [--touch]"""
import sys, asyncio, os, subprocess, time
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
async def main():
    out, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); rutas = sys.argv[4].split(','); touch = '--touch' in sys.argv
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', '8771', '-d', os.path.join(ROOT, 'dist')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch()
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, has_touch=touch, is_mobile=touch)
            for r in rutas:
                pg = await ctx.new_page(); errs = []
                pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
                pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
                await pg.goto('http://localhost:8771/' + r); await pg.wait_for_timeout(900)
                H = await pg.evaluate('document.documentElement.scrollHeight')
                for y in range(0, H, h): 
                    await pg.evaluate(f'scrollTo(0,{y})'); await pg.wait_for_timeout(120)
                await pg.evaluate('scrollTo(0,0)'); await pg.wait_for_timeout(500)
                info = await pg.evaluate('({sw:document.documentElement.scrollWidth,iw:innerWidth})')
                fn = os.path.join(out, (r.strip('/').replace('/', '_') or 'inicio') + f'_{w}.jpg')
                await pg.screenshot(path=fn, full_page=True, type='jpeg', quality=70)
                print(r or '/', 'alto', H, '| desborde:', info['sw'] > info['iw'], '|', errs[:4])
                await pg.close()
            await b.close()
    finally: srv.terminate()
asyncio.run(main())
