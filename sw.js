// App shell cache. Network first so updates land; cache is the offline fallback.
// The page itself is always fetched past the CDN cache (unique query) so a new GitHub version shows on the next load.
const CACHE = "day-v72";
const SHELL = ["./", "./index.html", "./manifest.webmanifest", "./icons/icon-192.png", "./icons/icon-180.png", "./icons/sun.svg", "./icons/moon.svg"];
self.addEventListener("install", (e) => { e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).catch(() => {})); self.skipWaiting(); });
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return;
  const page = e.request.mode === "navigate" || /\/(index\.html)?$/.test(u.pathname);
  const key = page ? u.origin + u.pathname : e.request;
  const net = page ? fetch(u.origin + u.pathname + "?fresh=" + Date.now(), {cache:"no-store"}) : fetch(e.request, {cache:"no-cache"});
  e.respondWith(net.then((r) => {
    if (r.ok){ const copy = r.clone(); caches.open(CACHE).then((c) => c.put(key, copy)); }
    return r;
  }).catch(() => caches.match(key).then((m) => m || caches.match("./index.html"))));
});
