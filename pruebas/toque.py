#!/usr/bin/env python3
"""Prueba de interacción: tocar una pizza en el viaje, agregarla y ver el pedido; luego la llegada."""
import sys, asyncio, os, subprocess, time
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.environ.get('OUT', '/tmp')
async def main():
    w, h = int(sys.argv[1]), int(sys.argv[2]); touch = '--touch' in sys.argv
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', '8773', '-d', os.path.join(ROOT, 'dist')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
            ctx = await b.new_context(viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch)
            pg = await ctx.new_page(); errs = []
            pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None); pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
            await pg.goto('http://localhost:8773/3d/?snap&q=mid'); await pg.wait_for_selector('html.sky-on', timeout=25000); await pg.wait_for_timeout(2500)
            y = await pg.evaluate("(document.getElementById('top').offsetHeight - innerHeight) * 0.6"); await pg.evaluate(f"scrollTo(0,{y})"); await pg.wait_for_timeout(1500)
            pt = await pg.evaluate("(()=>{const S=window.__sky();for(let y=0.2;y<0.8;y+=0.04)for(let x=0.08;x<0.95;x+=0.04){const i=S.pick(innerWidth*x,innerHeight*y);if(i)return [innerWidth*x,innerHeight*y,i.title];}return null;})()")
            print('pizza encontrada:', pt)
            if pt:
                await pg.mouse.click(pt[0], pt[1]); await pg.wait_for_timeout(2600); await pg.screenshot(path=f'{OUT}/t{w}_1foco.png')
                await pg.click('#piece-go'); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{OUT}/t{w}_2pedido.png')
                print('enlace whatsapp:', (await pg.get_attribute('#cajon-ir', 'href'))[:150])
                await pg.click('#cajon .cerrar'); await pg.wait_for_timeout(500)
            await pg.evaluate("document.querySelector('#llegada').scrollIntoView()"); await pg.wait_for_timeout(1300); await pg.screenshot(path=f'{OUT}/t{w}_3llegada.png')
            await pg.evaluate("document.querySelector('#actos').scrollIntoView()"); await pg.wait_for_timeout(1300); await pg.screenshot(path=f'{OUT}/t{w}_4actos.png')
            print('eventos:', await pg.evaluate("(window.dataLayer||[]).map(e=>e.event).join(', ')")); print('errores:', errs[:5])
            # sin WebGL
            pg2 = await ctx.new_page(); await pg2.goto('http://localhost:8773/3d/?sin3d'); await pg2.wait_for_timeout(900); await pg2.screenshot(path=f'{OUT}/t{w}_5sin3d.png')
            print('sin 3D: alto del viaje =', await pg2.evaluate("document.getElementById('top').offsetHeight"))
            await b.close()
    finally: srv.terminate()
asyncio.run(main())
