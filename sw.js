// Кэш приложения: работает офлайн, обновляется при смене VERSION
const VERSION = 'fullbody-v50';
const ASSETS = ['.', 'index.html', 'data.js?v=12', 'manifest.json', 'icon-180.png?v=2', 'icon-192.png?v=2', 'icon-512.png?v=2', 'icon-512-maskable.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Сеть в приоритете, кэш — запасной вариант: в зале без связи всё равно откроется
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then(res => {
        const copy = res.clone();
        caches.open(VERSION).then(c => c.put(e.request, copy)).catch(() => {});
        return res;
      })
      .catch(() => caches.match(e.request).then(r => r || caches.match('index.html')))
  );
});
