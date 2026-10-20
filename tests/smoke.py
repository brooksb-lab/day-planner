import asyncio, json, os, subprocess, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from playwright.async_api import async_playwright
srv = subprocess.Popen(["python3","-m","http.server","8765","--directory",ROOT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
seed = {"data":{"cols":{"todos":{
 "a":{"title":"Pick up trims","pri":1,"cal":"Personal","est":45,"status":"open","top":True,"order":1,"createdAt":1,"_u":1},
 "b":{"title":"Book dinner for Saturday","pri":2,"cal":"Meal","est":15,"status":"open","order":2,"createdAt":2,"_u":1},
 "c":{"title":"Sketch three jacket ideas","pri":2,"cal":"Personal","est":90,"status":"done","order":3,"createdAt":3,"doneAt":1,"_u":1}}},"tomb":{}},"fileId":None}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, vp, tab in [("desk",{"width":1280,"height":820},"day"),("phone",{"width":390,"height":844},"day")]:
            ctx = await b.new_context(viewport=vp, device_scale_factor=2)
            page = await ctx.new_page()
            errs = []
            page.on("pageerror", lambda e: errs.append(str(e)))
            page.on("console", lambda m: errs.append("console:"+m.text) if m.type=="error" else None)
            await page.route("https://accounts.google.com/**", lambda r: r.abort())
            await page.route("https://fonts.googleapis.com/**", lambda r: r.abort())
            await page.goto("http://localhost:8765/")
            await page.evaluate("""s => { localStorage.setItem('gClientId','x.apps.googleusercontent.com'); localStorage.setItem('plannerStore', s); }""", json.dumps(seed))
            await page.goto(f"http://localhost:8765/?t=1#{tab}")
            await page.wait_for_timeout(900)
            await page.screenshot(path=os.path.join(ROOT, "tests", f"shot-{name}.png"))
            print(name, "errors:", [e for e in errs if "Failed to load resource" not in e])
            await ctx.close()
        await b.close()
asyncio.run(main())
srv.terminate()
