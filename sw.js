// Service worker : garde l'application et ses bibliothèques en cache pour l'ouvrir sans réseau.
// Changer VERSION à chaque mise à jour des données pour forcer le rechargement.
const VERSION = 'stages-auto-v4';
const SHELL = [
  './', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './icon-180.png',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'
];

self.addEventListener('install', e => {
  // Fichier par fichier : un fichier manquant ou un CDN indisponible ne doit pas bloquer l'installation
  e.waitUntil(caches.open(VERSION)
    .then(c => Promise.all(SHELL.map(u => c.add(u).catch(() => {}))))
    .then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  // Géocodage et fonds de carte : toujours le réseau (pas de mise en cache)
  if (/geopf\.fr|data\.gouv\.fr|openstreetmap\.org/.test(url.hostname)) return;
  // Page : réseau d'abord pour avoir les dernières données, cache si hors connexion
  if (e.request.mode === 'navigate') {
    e.respondWith(fetch(e.request)
      .then(r => { const copy = r.clone(); caches.open(VERSION).then(c => c.put('./index.html', copy)); return r; })
      .catch(() => caches.match('./index.html')));
    return;
  }
  // Bibliothèques, icônes : cache d'abord
  e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request)));
});
