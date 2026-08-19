/* Service worker: Limpieza total de caché y prevención de respuestas vacías */
const CACHE = 'dr-web-v10.0';

self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const { request } = e;
  const url = new URL(request.url);

  if (request.method !== 'GET') return;

  if (request.mode === 'navigate') {
    e.respondWith(
      fetch(request).catch(() => caches.match('/'))
    );
    return;
  }

  /* JS, CSS y API: red siempre primero */
  if (url.pathname.startsWith('/static/') || url.pathname.startsWith('/api/')) {
    e.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.ok && response.status === 200) {
            const contentLength = response.headers.get('content-length');
            if (contentLength && parseInt(contentLength, 10) > 0) {
              const copy = response.clone();
              caches.open(CACHE).then((cache) => cache.put(request, copy));
            }
          }
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  e.respondWith(
    fetch(request).catch(() => caches.match(request))
  );
});
