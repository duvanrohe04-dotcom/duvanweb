const CACHE = 'dr-web-v1';
const PRECACHE_URLS = ['/', '/static/css/style.css', '/static/js/main.js'];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(PRECACHE_URLS))
  );
});

self.addEventListener('fetch', e => {
  const { request } = e;
  if (request.mode === 'navigate') {
    e.respondWith(
      fetch(request).catch(() => caches.match('/'))
    );
    return;
  }
  e.respondWith(
    caches.match(request).then(cached => cached || fetch(request).then(response =>
      caches.open(CACHE).then(cache => { cache.put(request, response.clone()); return response; })
    ))
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
  );
});
