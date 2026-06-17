function urlBase64ToUint8Array(b64) {
    const padding = '='.repeat((4 - b64.length % 4) % 4);
    const base64 = (b64 + padding).replace(/-/g, '+').replace(/_/g, '/');
    const raw = window.atob(base64);
    const arr = new Uint8Array(raw.length);
    for (let i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i);
    return arr;
}

function getCsrfToken() {
    return document.cookie
        .split(';')
        .find(c => c.trim().startsWith('csrftoken='))
        ?.split('=')[1];
}

document.addEventListener('DOMContentLoaded', async function() {
    const btnActivar = document.getElementById('btn-activar-push');
    const btnDesactivar = document.getElementById('btn-desactivar-push');
    const noSoportado = document.getElementById('push-no-soportado');
    const iosInstruc = document.getElementById('ios-instrucciones');

    if (!btnActivar) return;

    if (!window.VAPID_PUBLIC_KEY) {
        if (noSoportado) {
            noSoportado.style.display = 'block';
            noSoportado.textContent = 'Notificaciones push no configuradas. Contacta al administrador.';
        }
        return;
    }

    const esIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const esPWA = window.matchMedia('(display-mode: standalone)').matches;

    if (esIOS && !esPWA) {
        if (iosInstruc) iosInstruc.style.display = 'block';
        return;
    }

    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        if (noSoportado) noSoportado.style.display = 'block';
        return;
    }

    let registro;
    try {
        registro = await navigator.serviceWorker.register('/sw.js');
    } catch (err) {
        console.warn('Service Worker no disponible:', err);
        if (noSoportado) {
            noSoportado.style.display = 'block';
            noSoportado.textContent = 'El Service Worker no está disponible. Recarga la página o contacta al administrador.';
        }
        return;
    }

    const suscripcion = await registro.pushManager.getSubscription();

    if (suscripcion) {
        btnDesactivar.style.display = 'inline-block';
    } else {
        btnActivar.style.display = 'inline-block';
    }

    btnActivar.addEventListener('click', async function() {
        btnActivar.disabled = true;
        btnActivar.textContent = 'Activando...';

        try {
            const permiso = await Notification.requestPermission();
            if (permiso !== 'granted') {
                alert('Debes permitir las notificaciones.');
                btnActivar.disabled = false;
                btnActivar.textContent = '🔔 Activar alertas';
                return;
            }

            const nueva = await registro.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(window.VAPID_PUBLIC_KEY),
            });

            const resp = await fetch('/notificaciones/api/guardar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify(nueva.toJSON()),
            });

            if (resp.ok) {
                btnActivar.style.display = 'none';
                btnDesactivar.style.display = 'inline-block';
            } else {
                throw new Error('Error al guardar');
            }
        } catch (err) {
            console.error(err);
            alert('No se pudo activar. Intenta de nuevo.');
            btnActivar.disabled = false;
            btnActivar.textContent = '🔔 Activar alertas';
        }
    });

    btnDesactivar.addEventListener('click', async function() {
        const actual = await registro.pushManager.getSubscription();
        if (actual) {
            await actual.unsubscribe();
            await fetch('/notificaciones/api/eliminar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ endpoint: actual.endpoint }),
            });
            btnDesactivar.style.display = 'none';
            btnActivar.style.display = 'inline-block';
            btnActivar.disabled = false;
            btnActivar.textContent = '🔔 Activar alertas';
        }
    });
});
