const CACHE_NAME = 'finanplanen-v1';

self.addEventListener('install', function(event) {
    self.skipWaiting();
});

self.addEventListener('activate', function(event) {
    event.waitUntil(self.clients.claim());
});

self.addEventListener('push', function(event) {
    let datos = {
        title: 'Recordatorio de pago',
        body: 'Tienes un pago próximo.',
        url: '/cuentas/',
        icon: '/static/img/icon-192.png',
        badge: '/static/img/badge-72.png',
    };

    if (event.data) {
        try {
            datos = event.data.json();
        } catch (e) {
            datos.body = event.data.text();
        }
    }

    event.waitUntil(
        self.registration.showNotification(datos.title, {
            body: datos.body,
            icon: datos.icon,
            badge: datos.badge,
            vibrate: [200, 100, 200],
            data: { url: datos.url },
            actions: [
                { action: 'ver', title: 'Ver cuentas' },
                { action: 'cerrar', title: 'Cerrar' },
            ],
            requireInteraction: true,
        })
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    if (event.action === 'cerrar') return;

    const url = event.notification.data.url || '/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(function(list) {
                for (let client of list) {
                    if (client.url.includes(self.location.origin)) {
                        client.focus();
                        client.navigate(url);
                        return;
                    }
                }
                return clients.openWindow(url);
            })
    );
});
