// ═══════════════════════════════════════════════════════════
// SMARTSPORTS - SERVICE WORKER
// Version: 1.0 - Advanced PWA Features
// ═══════════════════════════════════════════════════════════

const CACHE_NAME = 'smartsports-v1.0.0';
const RUNTIME_CACHE = 'smartsports-runtime-v1.0.0';
const API_CACHE = 'smartsports-api-v1.0.0';

// קבצים לאחסון במטמון
const STATIC_CACHE_URLS = [
  '/frontend/',
  '/frontend/index.html',
  '/frontend/predictions.html',
  '/frontend/arena.html',
  '/frontend/chat.html',
  '/frontend/community.html',
  '/frontend/news.html',
  '/frontend/stats.html',
  '/frontend/halp_center.html',
  '/frontend/game_arena.html',
  '/frontend/differentiation.html',
  '/frontend/start_up.html',
  '/frontend/about.html',
  '/frontend/profile.html',
  '/frontend/global-styles.css',
  '/frontend/manifest.json',
  'https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css',
  'https://cdn.jsdelivr.net/npm/chart.js'
];

// התקנת Service Worker
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Caching static assets');
        return cache.addAll(STATIC_CACHE_URLS.map(url => new Request(url, { cache: 'reload' })));
      })
      .then(() => self.skipWaiting())
      .catch(error => console.error('[Service Worker] Installation failed:', error))
  );
});

// הפעלת Service Worker
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name !== RUNTIME_CACHE && name !== API_CACHE)
          .map((name) => {
            console.log('[Service Worker] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    })
    .then(() => self.clients.claim())
  );
});

// טיפול בבקשות - אסטרטגיית Cache First עם Fallback
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // התעלם מבקשות שאינן HTTP/HTTPS
  if (!url.protocol.startsWith('http')) {
    return;
  }

  // אסטרטגיה שונה לבקשות API
  if (url.pathname.startsWith('/api/') || url.hostname.includes('api-sports')) {
    event.respondWith(networkFirstStrategy(request));
    return;
  }

  // Cache First עבור משאבים סטטיים
  event.respondWith(cacheFirstStrategy(request));
});

// אסטרטגיית Cache First
async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);

  if (cachedResponse) {
    // מצא במטמון - החזר מיד ועדכן ברקע
    updateCache(request);
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.error('[Service Worker] Fetch failed:', error);

    // החזר דף אופליין אם קיים
    const offlinePage = await caches.match('/frontend/offline.html');
    if (offlinePage) {
      return offlinePage;
    }

    return new Response('אתה במצב אופליין. אנא בדוק את החיבור לאינטרנט.', {
      status: 503,
      statusText: 'Service Unavailable',
      headers: new Headers({
        'Content-Type': 'text/plain; charset=utf-8'
      })
    });
  }
}

// אסטרטגיית Network First (לנתוני API)
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
      const cache = await caches.open(API_CACHE);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.error('[Service Worker] API fetch failed, trying cache:', error);

    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    return new Response(JSON.stringify({ error: 'אופליין - לא ניתן לטעון נתונים' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// עדכון מטמון ברקע
async function updateCache(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, networkResponse);
    }
  } catch (error) {
    // שקט - רק עדכון ברקע
  }
}

// טיפול בהתראות Push
self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push notification received');

  let data = { title: 'SMARTSPORTS', body: 'עדכון חדש זמין!' };

  if (event.data) {
    try {
      data = event.data.json();
    } catch (error) {
      data.body = event.data.text();
    }
  }

  const options = {
    body: data.body,
    icon: '/frontend/icons/icon-192x192.png',
    badge: '/frontend/icons/badge-72x72.png',
    vibrate: [200, 100, 200],
    tag: data.tag || 'smartsports-notification',
    requireInteraction: false,
    actions: data.actions || [
      { action: 'open', title: 'פתח', icon: '/frontend/icons/icon-96x96.png' },
      { action: 'close', title: 'סגור', icon: '/frontend/icons/icon-96x96.png' }
    ],
    data: data.url || '/frontend/index.html'
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// טיפול בלחיצה על התראה
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Notification clicked');
  event.notification.close();

  const urlToOpen = event.notification.data || '/frontend/index.html';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // אם יש טאב פתוח - עבור אליו
        for (const client of clientList) {
          if (client.url === urlToOpen && 'focus' in client) {
            return client.focus();
          }
        }
        // אחרת פתח טאב חדש
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
  );
});

// סנכרון ברקע
self.addEventListener('sync', (event) => {
  console.log('[Service Worker] Background sync:', event.tag);

  if (event.tag === 'sync-predictions') {
    event.waitUntil(syncPredictions());
  } else if (event.tag === 'sync-live-scores') {
    event.waitUntil(syncLiveScores());
  }
});

// פונקציות עזר לסנכרון
async function syncPredictions() {
  try {
    const response = await fetch('/api/predictions/latest');
    if (response.ok) {
      const data = await response.json();
      // שלח הודעה לכל הלקוחות
      const clients = await self.clients.matchAll();
      clients.forEach(client => {
        client.postMessage({
          type: 'PREDICTIONS_UPDATED',
          data: data
        });
      });
    }
  } catch (error) {
    console.error('[Service Worker] Sync predictions failed:', error);
  }
}

async function syncLiveScores() {
  try {
    const response = await fetch('/api/live/scores');
    if (response.ok) {
      const data = await response.json();
      const clients = await self.clients.matchAll();
      clients.forEach(client => {
        client.postMessage({
          type: 'LIVE_SCORES_UPDATED',
          data: data
        });
      });
    }
  } catch (error) {
    console.error('[Service Worker] Sync live scores failed:', error);
  }
}

// שליחת הודעות ללקוחות
self.addEventListener('message', (event) => {
  console.log('[Service Worker] Message received:', event.data);

  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data && event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => caches.delete(cacheName))
        );
      })
    );
  }
});

console.log('[Service Worker] Script loaded successfully');
