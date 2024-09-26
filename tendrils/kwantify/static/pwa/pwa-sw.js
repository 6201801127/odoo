const cacheName = "v2";

// Service worker installing
self.addEventListener('install', e => {
    console.log('service worker installing');
})

// Service worker activating
self.addEventListener('activate', e => {
    console.log('service worker activate');
    // Remove old caches
    e.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cache => {
                    if(cache !== cacheName) {
                        console.log('clearing old cache files...');
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});

// Service worker fetching
self.addEventListener('fetch', e => {
    console.log('service worker Fetching start');
    e.respondWith(
        fetch(e.request)
        .then(res => {
            //   Make clone of response
            const resClone = res.clone();
            // Open cache
            caches.open(cacheName).then(cache => {
                // Add response to cache
                cache.put(e.request, resClone);
            })
            return res;            
        })
        .catch(err => caches.match(e.request).then(res => res))
    );
});

/*
self.addEventListener('fetch', event => {
    // We only want to call event.respondWith() if this is a navigation request
    // for an HTML page.
    // request.mode of 'navigate' is unfortunately not supported in Chrome
    // versions older than 49, so we need to include a less precise fallback,
    // which checks for a GET request with an Accept: text/html header.
    if (event.request.mode === 'navigate' ||
        (event.request.method === 'GET' &&
         event.request.headers.get('accept').includes('text/html'))) {
      console.log('Handling fetch event for', event.request.url);
      event.respondWith(
        fetch(event.request).catch(error => {
          // The catch is only triggered if fetch() throws an exception, which will most likely
          // happen due to the server being unreachable.
          // If fetch() returns a valid HTTP response with an response code in the 4xx or 5xx
          // range, the catch() will NOT be called. If you need custom handling for 4xx or 5xx
          // errors, see https://github.com/GoogleChrome/samples/tree/gh-pages/service-worker/fallback-response
          console.log('Fetch failed; returning offline page instead.', error);
          return caches.match(OFFLINE_URL);
        })
      );
    }
  
    // If our if() condition is false, then this fetch handler won't intercept the request.
    // If there are any other fetch handlers registered, they will get a chance to call
    // event.respondWith(). If no fetch handlers call event.respondWith(), the request will be
    // handled by the browser as if there were no service worker involvement.
  });*/