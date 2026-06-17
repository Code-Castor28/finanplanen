# Guía de Integración: Web Push / PWA en Django

### Stack: HTML · CSS · JS · Django · MySQL · Redis · Celery · Nginx

> **Propósito:** Automatizar recordatorios de fechas de pago de tarjetas de crédito directamente en la pantalla de bloqueo del móvil del usuario, sin APIs externas ni costos de SMS.

-----

## Índice

1. [Prerequisitos del servidor](#1-prerequisitos-del-servidor)
1. [Fase 1 — Generar llaves VAPID](#2-fase-1--generar-llaves-vapid)
1. [Fase 2 — Modelos MySQL (Django ORM)](#3-fase-2--modelos-mysql-django-orm)
1. [Fase 3 — Service Worker (sw.js)](#4-fase-3--service-worker-swjs)
1. [Fase 4 — Flujo de suscripción Frontend → MySQL](#5-fase-4--flujo-de-suscripción-frontend--mysql)
1. [Fase 5 — Celery Beat + Workers (disparo automático)](#6-fase-5--celery-beat--workers-disparo-automático)
1. [Fase 6 — Nginx + HTTPS](#7-fase-6--nginx--https)
1. [Fase 7 — Caso especial iOS](#8-fase-7--caso-especial-ios)
1. [Fase 8 — Levantar servicios en producción](#9-fase-8--levantar-servicios-en-producción)
1. [Resumen del flujo completo](#10-resumen-del-flujo-completo)
1. [Checklist de verificación](#11-checklist-de-verificación)

-----

## 1. Prerequisitos del servidor

### 1.1 Paquetes del sistema (Ubuntu VPS)

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx mysql-server redis-server certbot python3-certbot-nginx
```

### 1.2 Librerías Python del proyecto

Dentro del entorno virtual del proyecto:

```bash
pip install django gunicorn mysqlclient celery redis pywebpush python-dotenv
```

Añadir al `requirements.txt`:

```
django>=4.2
gunicorn
mysqlclient
celery[redis]
pywebpush
python-dotenv
```

### 1.3 Verificar que Redis está activo

```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
redis-cli ping   # debe responder: PONG
```

-----

## 2. Fase 1 — Generar llaves VAPID

> Las llaves VAPID identifican tu servidor ante Google y Apple. Se generan **una sola vez** por proyecto.

### 2.1 Generar el par de llaves

```bash
# En la terminal del servidor, dentro del entorno virtual
python -c "
from pywebpush import Vapid
v = Vapid()
v.generate_keys()
print('VAPID_PRIVATE_KEY:', v.private_key.private_bytes(
    encoding=__import__('cryptography.hazmat.primitives.serialization', fromlist=['Encoding']).Encoding.PEM,
    format=__import__('cryptography.hazmat.primitives.serialization', fromlist=['PrivateFormat']).PrivateFormat.Raw,
    encryption_algorithm=__import__('cryptography.hazmat.primitives.serialization', fromlist=['NoEncryption']).NoEncryption()
).hex())
"
# Alternativa más simple con la CLI de pywebpush:
python -m pywebpush --gen-keys
```

Resultado esperado (valores ilustrativos):

```
Private Key: BNx8asd2...largacadena...xK29
Public Key:  BOq7zxc1...largacadena...P9sA
```

### 2.2 Guardar las llaves en el archivo `.env`

```bash
# /ruta/tu_proyecto/.env
VAPID_PUBLIC_KEY=BOq7zxc1...tu_llave_publica...P9sA
VAPID_PRIVATE_KEY=BNx8asd2...tu_llave_privada...xK29
VAPID_ADMIN_EMAIL=admin@tudominio.com

DATABASE_NAME=finanzas_db
DATABASE_USER=finanzas_user
DATABASE_PASSWORD=password_seguro
DATABASE_HOST=localhost
DATABASE_PORT=3306

REDIS_URL=redis://localhost:6379/0
```

### 2.3 Crear el archivo `.env.example` (para el repositorio)

```bash
# /ruta/tu_proyecto/.env.example
VAPID_PUBLIC_KEY=
VAPID_PRIVATE_KEY=
VAPID_ADMIN_EMAIL=

DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=localhost
DATABASE_PORT=3306

REDIS_URL=redis://localhost:6379/0
```

### 2.4 Añadir `.env` al `.gitignore`

```bash
# .gitignore
.env
*.pyc
__pycache__/
```

### 2.5 Cargar las variables en Django (`settings.py`)

```python
# settings.py
from dotenv import load_dotenv
import os

load_dotenv()

VAPID_PUBLIC_KEY  = os.getenv("VAPID_PUBLIC_KEY")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_ADMIN_EMAIL = os.getenv("VAPID_ADMIN_EMAIL")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME":     os.getenv("DATABASE_NAME"),
        "USER":     os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST":     os.getenv("DATABASE_HOST", "localhost"),
        "PORT":     os.getenv("DATABASE_PORT", "3306"),
    }
}
```

-----

## 3. Fase 2 — Modelos MySQL (Django ORM)

### 3.1 Estructura de tablas

Necesitas **dos tablas nuevas** que se vinculan al `User` de Django.

```python
# finanzas/models.py
from django.db import models
from django.contrib.auth.models import User


class TarjetaCredito(models.Model):
    """
    Almacena la información de cada tarjeta del usuario.
    """
    usuario             = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tarjetas")
    banco               = models.CharField(max_length=100)          # Ej: "BBVA", "Santander"
    nombre_tarjeta      = models.CharField(max_length=150)          # Ej: "Visa Oro"
    dia_corte           = models.PositiveSmallIntegerField()        # Día del mes: 1-31
    dia_pago            = models.PositiveSmallIntegerField()        # Día del mes: 1-31
    proxima_fecha_pago  = models.DateField()                        # Calculado: próximo vencimiento real
    activa              = models.BooleanField(default=True)

    class Meta:
        db_table = "tarjetas_credito"

    def __str__(self):
        return f"{self.banco} - {self.nombre_tarjeta} ({self.usuario.username})"


class SuscripcionPush(models.Model):
    """
    Almacena las credenciales criptográficas del navegador de cada dispositivo.
    Un usuario puede tener múltiples suscripciones (móvil + tablet + escritorio).
    """
    usuario    = models.ForeignKey(User, on_delete=models.CASCADE, related_name="suscripciones_push")
    endpoint   = models.TextField(unique=True)    # URL de Google/Apple (muy larga)
    p256dh     = models.TextField()               # Llave pública del navegador
    auth       = models.TextField()               # Token de autenticación del navegador
    creado_en  = models.DateTimeField(auto_now_add=True)
    activo     = models.BooleanField(default=True)

    class Meta:
        db_table = "suscripciones_push"

    def __str__(self):
        return f"Suscripción de {self.usuario.username} ({self.endpoint[:50]}...)"
```

### 3.2 Crear y aplicar las migraciones

```bash
python manage.py makemigrations finanzas
python manage.py migrate
```

### 3.3 Verificar en MySQL

```sql
-- Conectar a MySQL y verificar
SHOW TABLES;
-- Debe mostrar: tarjetas_credito, suscripciones_push

DESCRIBE tarjetas_credito;
DESCRIBE suscripciones_push;
```

-----

## 4. Fase 3 — Service Worker (sw.js)

> El Service Worker es el archivo JavaScript que “vive” en el navegador del usuario, incluso con la app cerrada. Es el receptor de todas las notificaciones push.

### 4.1 Ubicación del archivo

**CRÍTICO:** El archivo debe estar en la raíz del dominio, no en `/static/`.

```
# Estructura de archivos
tu_proyecto/
├── static/
│   ├── css/
│   └── js/
├── sw.js          ← AQUÍ, en la raíz del proyecto (al mismo nivel que manage.py)
└── manage.py
```

### 4.2 Contenido del sw.js

```javascript
// sw.js — Service Worker para notificaciones push
// Ubicación: raíz del dominio → https://tudominio.com/sw.js

const CACHE_NAME = "finanzas-v1";

// ─── Instalación silenciosa ───────────────────────────────────────────────────
self.addEventListener("install", function(event) {
    self.skipWaiting();  // Activar inmediatamente sin esperar recarga
});

self.addEventListener("activate", function(event) {
    event.waitUntil(self.clients.claim());
});

// ─── Recepción del Push (llega del servidor Django via Google/Apple) ──────────
self.addEventListener("push", function(event) {

    // Extraer los datos del mensaje enviado por Celery
    let datos = {
        title: "Recordatorio de pago",
        body:  "Tienes un pago próximo.",
        url:   "/finanzas/tarjetas/",
        icon:  "/static/img/icon-192.png",
        badge: "/static/img/badge-72.png"
    };

    if (event.data) {
        try {
            datos = event.data.json();
        } catch (e) {
            datos.body = event.data.text();
        }
    }

    const opciones = {
        body:    datos.body,
        icon:    datos.icon,
        badge:   datos.badge,
        vibrate: [200, 100, 200],           // Patrón de vibración
        data:    { url: datos.url },         // URL a abrir al tocar
        actions: [
            { action: "ver",     title: "Ver tarjetas" },
            { action: "cerrar",  title: "Cerrar"       }
        ],
        requireInteraction: true             // No desaparece solo en Android
    };

    event.waitUntil(
        self.registration.showNotification(datos.title, opciones)
    );
});

// ─── Clic en la notificación ──────────────────────────────────────────────────
self.addEventListener("notificationclick", function(event) {
    event.notification.close();

    if (event.action === "cerrar") return;

    const urlDestino = event.notification.data.url || "/";

    event.waitUntil(
        clients.matchAll({ type: "window", includeUncontrolled: true })
            .then(function(clientList) {
                // Si ya hay una pestaña abierta, enfocarla
                for (let client of clientList) {
                    if (client.url.includes(self.location.origin)) {
                        client.focus();
                        client.navigate(urlDestino);
                        return;
                    }
                }
                // Si no hay pestaña abierta, abrir una nueva
                return clients.openWindow(urlDestino);
            })
    );
});
```

### 4.3 Registrar la URL del sw.js en Django (`urls.py`)

```python
# tu_proyecto/urls.py
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    # ... otras rutas ...

    # Servir sw.js desde la raíz (NO desde /static/)
    path(
        "sw.js",
        TemplateView.as_view(
            template_name="sw.js",
            content_type="application/javascript"
        ),
        name="service-worker"
    ),
]
```

Alternativamente, servir el archivo directamente desde Nginx (ver Fase 6).

-----

## 5. Fase 4 — Flujo de suscripción Frontend → MySQL

### 5.1 El manifest.json (requerido para PWA)

Crear el archivo en `static/manifest.json`:

```json
{
    "name": "Mis Finanzas",
    "short_name": "Finanzas",
    "description": "Gestión de tarjetas y recordatorios de pago",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#1a73e8",
    "lang": "es",
    "icons": [
        {
            "src": "/static/img/icon-192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "maskable any"
        },
        {
            "src": "/static/img/icon-512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "maskable any"
        }
    ]
}
```

Referenciarlo en el template HTML base:

```html
<!-- templates/base.html -->
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#1a73e8">

    <!-- PWA -->
    <link rel="manifest" href="/static/manifest.json">
    <link rel="apple-touch-icon" href="/static/img/icon-192.png">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">

    <title>Mis Finanzas</title>
</head>
```

### 5.2 El botón en la interfaz HTML

```html
<!-- templates/finanzas/configuracion.html -->
{% extends "base.html" %}
{% block content %}

<div class="alertas-section">
    <h2>Notificaciones de Pago</h2>
    <p>Recibe alertas en tu teléfono 2 días antes de cada fecha de pago.</p>

    <!-- Contenedor dinámico — JavaScript lo controla -->
    <div id="push-container">
        <button id="btn-activar-push" class="btn btn-primary" style="display:none;">
            🔔 Activar alertas de pago
        </button>
        <button id="btn-desactivar-push" class="btn btn-secondary" style="display:none;">
            🔕 Desactivar alertas
        </button>
        <p id="push-no-soportado" style="display:none; color: #888;">
            Tu navegador no soporta notificaciones push.
        </p>
    </div>

    <!-- Banner educativo para iOS (oculto por defecto) -->
    <div id="ios-instrucciones" style="display:none;" class="alert alert-info">
        <strong>📱 iPhone detectado:</strong> Para recibir alertas nativas,
        toca el ícono <strong>Compartir ↑</strong> en Safari y selecciona
        <strong>"Agregar a pantalla de inicio"</strong>. Luego vuelve a activar las alertas.
    </div>
</div>

<!-- Pasar la llave pública VAPID al JavaScript desde Django -->
<script>
    const VAPID_PUBLIC_KEY = "{{ vapid_public_key }}";
</script>
<script src="/static/js/push-notifications.js"></script>
{% endblock %}
```

### 5.3 El JavaScript de suscripción (`static/js/push-notifications.js`)

```javascript
// static/js/push-notifications.js

// ─── Utilidades ───────────────────────────────────────────────────────────────

// Convierte la llave pública VAPID de base64 al formato que pide el navegador
function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - base64String.length % 4) % 4);
    const base64  = (base64String + padding)
        .replace(/-/g, "+")
        .replace(/_/g, "/");
    const rawData     = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Obtener el token CSRF de Django
function getCsrfToken() {
    return document.cookie
        .split(";")
        .find(c => c.trim().startsWith("csrftoken="))
        ?.split("=")[1];
}

// ─── Detección de soporte y estado inicial ────────────────────────────────────

document.addEventListener("DOMContentLoaded", async function() {

    const btnActivar     = document.getElementById("btn-activar-push");
    const btnDesactivar  = document.getElementById("btn-desactivar-push");
    const noSoportado    = document.getElementById("push-no-soportado");
    const iosInstruc     = document.getElementById("ios-instrucciones");

    // Detectar iOS no instalado como PWA
    const esIOS      = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const esPWA      = window.matchMedia("(display-mode: standalone)").matches;
    const esSafari   = /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent);

    if (esIOS && !esPWA) {
        iosInstruc.style.display = "block";
        return;  // En iOS sin PWA instalada, no continuar
    }

    // Verificar soporte de notificaciones push
    if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
        noSoportado.style.display = "block";
        return;
    }

    // Verificar si ya está suscrito
    const registro      = await navigator.serviceWorker.register("/sw.js");
    const suscripcion   = await registro.pushManager.getSubscription();

    if (suscripcion) {
        btnDesactivar.style.display = "inline-block";
    } else {
        btnActivar.style.display = "inline-block";
    }

    // ─── Activar suscripción ──────────────────────────────────────────────────
    btnActivar.addEventListener("click", async function() {

        btnActivar.disabled    = true;
        btnActivar.textContent = "Activando...";

        try {
            // 1. Pedir permiso al usuario (aparece el popup nativo del navegador)
            const permiso = await Notification.requestPermission();

            if (permiso !== "granted") {
                alert("Para recibir alertas, debes permitir las notificaciones.");
                btnActivar.disabled    = false;
                btnActivar.textContent = "🔔 Activar alertas de pago";
                return;
            }

            // 2. Suscribirse al Push Manager con la llave VAPID pública
            const nuevaSuscripcion = await registro.pushManager.subscribe({
                userVisibleOnly:      true,
                applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
            });

            // 3. El navegador genera este objeto con las credenciales del dispositivo:
            //    { endpoint: "https://fcm.googleapis.com/...", keys: { p256dh: "...", auth: "..." } }

            // 4. Enviar al servidor Django para guardarlo en MySQL
            const respuesta = await fetch("/api/suscripcion/guardar/", {
                method:  "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken":  getCsrfToken()
                },
                body: JSON.stringify(nuevaSuscripcion.toJSON())
            });

            if (respuesta.ok) {
                btnActivar.style.display    = "none";
                btnDesactivar.style.display = "inline-block";
                console.log("✅ Suscripción guardada correctamente.");
            } else {
                throw new Error("Error al guardar la suscripción en el servidor.");
            }

        } catch (error) {
            console.error("Error al suscribirse:", error);
            alert("No se pudo activar las alertas. Intenta de nuevo.");
            btnActivar.disabled    = false;
            btnActivar.textContent = "🔔 Activar alertas de pago";
        }
    });

    // ─── Desactivar suscripción ───────────────────────────────────────────────
    btnDesactivar.addEventListener("click", async function() {

        const suscripcionActual = await registro.pushManager.getSubscription();

        if (suscripcionActual) {
            // Cancelar en el navegador
            await suscripcionActual.unsubscribe();

            // Eliminar del servidor Django
            await fetch("/api/suscripcion/eliminar/", {
                method:  "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken":  getCsrfToken()
                },
                body: JSON.stringify({ endpoint: suscripcionActual.endpoint })
            });

            btnDesactivar.style.display = "none";
            btnActivar.style.display    = "inline-block";
            btnActivar.disabled         = false;
            btnActivar.textContent      = "🔔 Activar alertas de pago";
        }
    });
});
```

### 5.4 La vista Django que guarda en MySQL

```python
# finanzas/views.py
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from .models import SuscripcionPush
from django.conf import settings


@login_required
@csrf_protect
@require_POST
def guardar_suscripcion(request):
    """
    Recibe el objeto de suscripción del navegador y lo guarda en MySQL.
    Usa update_or_create para no duplicar si el mismo dispositivo se suscribe dos veces.
    """
    try:
        datos = json.loads(request.body)

        endpoint = datos.get("endpoint")
        p256dh   = datos.get("keys", {}).get("p256dh")
        auth     = datos.get("keys", {}).get("auth")

        if not all([endpoint, p256dh, auth]):
            return JsonResponse({"error": "Datos incompletos"}, status=400)

        suscripcion, creada = SuscripcionPush.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                "usuario": request.user,
                "p256dh":  p256dh,
                "auth":    auth,
                "activo":  True
            }
        )

        return JsonResponse({
            "status": "ok",
            "accion": "creada" if creada else "actualizada"
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_protect
@require_POST
def eliminar_suscripcion(request):
    """
    Elimina la suscripción del dispositivo cuando el usuario desactiva las alertas.
    """
    try:
        datos    = json.loads(request.body)
        endpoint = datos.get("endpoint")

        SuscripcionPush.objects.filter(
            usuario=request.user,
            endpoint=endpoint
        ).delete()

        return JsonResponse({"status": "ok"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def configuracion_alertas(request):
    """
    Vista que renderiza la página de configuración.
    Pasa la llave pública VAPID al template.
    """
    return render(request, "finanzas/configuracion.html", {
        "vapid_public_key": settings.VAPID_PUBLIC_KEY
    })
```

### 5.5 Registrar las URLs de la API

```python
# finanzas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("configuracion/",              views.configuracion_alertas, name="configuracion"),
    path("api/suscripcion/guardar/",    views.guardar_suscripcion,   name="guardar-suscripcion"),
    path("api/suscripcion/eliminar/",   views.eliminar_suscripcion,  name="eliminar-suscripcion"),
]
```

```python
# tu_proyecto/urls.py
from django.urls import path, include

urlpatterns = [
    path("finanzas/", include("finanzas.urls")),
    path("sw.js", TemplateView.as_view(
        template_name="sw.js",
        content_type="application/javascript"
    ), name="service-worker"),
]
```

-----

## 6. Fase 5 — Celery Beat + Workers (disparo automático)

### 6.1 Configurar Celery en el proyecto

```python
# tu_proyecto/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tu_proyecto.settings")

app = Celery("tu_proyecto")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```

```python
# tu_proyecto/__init__.py
from .celery import app as celery_app
__all__ = ("celery_app",)
```

### 6.2 Configurar Celery en settings.py

```python
# settings.py — añadir al final
from dotenv import load_dotenv
load_dotenv()

CELERY_BROKER_URL        = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND    = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_TIMEZONE          = "America/Mexico_City"    # Ajusta a tu zona horaria
CELERY_TASK_SERIALIZER   = "json"
CELERY_ACCEPT_CONTENT    = ["json"]

# Programar la tarea diaria
CELERY_BEAT_SCHEDULE = {
    "recordatorios-de-pago-diarios": {
        "task":     "finanzas.tasks.enviar_recordatorios_pago",
        "schedule": crontab(hour=8, minute=0),  # Todos los días a las 8:00 AM
    }
}
```

### 6.3 Las tareas Celery (`finanzas/tasks.py`)

```python
# finanzas/tasks.py
import json
import os
import logging
from datetime import date, timedelta

from celery import app
from pywebpush import webpush, WebPushException
from django.conf import settings

from .models import TarjetaCredito, SuscripcionPush

logger = logging.getLogger(__name__)


@app.task(name="finanzas.tasks.enviar_recordatorios_pago")
def enviar_recordatorios_pago():
    """
    Tarea principal disparada por Celery Beat cada mañana.
    Busca tarjetas que vencen en exactamente 2 días y delega el envío.
    """
    hoy        = date.today()
    en_dos_dias = hoy + timedelta(days=2)

    # Buscar tarjetas que vencen en 2 días (solo de usuarios activos)
    tarjetas = TarjetaCredito.objects.filter(
        proxima_fecha_pago=en_dos_dias,
        activa=True,
        usuario__is_active=True
    ).select_related("usuario")

    total = tarjetas.count()
    logger.info(f"[Recordatorios] Fecha objetivo: {en_dos_dias} | Tarjetas encontradas: {total}")

    for tarjeta in tarjetas:
        # Obtener todos los dispositivos suscritos de ese usuario
        suscripciones = SuscripcionPush.objects.filter(
            usuario=tarjeta.usuario,
            activo=True
        )

        for suscripcion in suscripciones:
            # Delegar a un worker paralelo con .delay()
            enviar_notificacion_push.delay(
                suscripcion_id=suscripcion.id,
                tarjeta_id=tarjeta.id
            )

    logger.info(f"[Recordatorios] {total} tareas de envío encoladas.")
    return f"Encoladas: {total} notificaciones"


@app.task(
    name="finanzas.tasks.enviar_notificacion_push",
    max_retries=2,
    default_retry_delay=60
)
def enviar_notificacion_push(suscripcion_id, tarjeta_id):
    """
    Worker individual: cifra y envía una notificación push a un dispositivo específico.
    Limpia automáticamente las suscripciones muertas (404/410).
    """
    try:
        suscripcion = SuscripcionPush.objects.get(id=suscripcion_id)
        tarjeta     = TarjetaCredito.objects.get(id=tarjeta_id)
    except (SuscripcionPush.DoesNotExist, TarjetaCredito.DoesNotExist):
        logger.warning(f"[Push] Registro no encontrado: suscripcion={suscripcion_id}, tarjeta={tarjeta_id}")
        return

    # Construir el mensaje que recibirá el sw.js
    mensaje = {
        "title": "⚠️ Pago próximo",
        "body":  f"Tu tarjeta {tarjeta.banco} ({tarjeta.nombre_tarjeta}) vence el {tarjeta.proxima_fecha_pago.strftime('%d/%m/%Y')}",
        "url":   f"/finanzas/tarjetas/{tarjeta.id}/",
        "icon":  "/static/img/icon-192.png",
        "badge": "/static/img/badge-72.png"
    }

    try:
        webpush(
            subscription_info={
                "endpoint": suscripcion.endpoint,
                "keys": {
                    "p256dh": suscripcion.p256dh,
                    "auth":   suscripcion.auth
                }
            },
            data=json.dumps(mensaje),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={
                "sub": f"mailto:{settings.VAPID_ADMIN_EMAIL}"
            }
        )
        logger.info(f"[Push] ✅ Enviado a {suscripcion.usuario.username} — {tarjeta.banco}")

    except WebPushException as error:
        codigo = error.response.status_code if error.response else None

        if codigo in [404, 410]:
            # Suscripción muerta: el usuario borró la app, revocó permisos o cambió de dispositivo
            logger.warning(f"[Push] 🗑️ Suscripción muerta (HTTP {codigo}), eliminando: {suscripcion.endpoint[:60]}...")
            suscripcion.delete()
        else:
            # Error temporal: reintentar
            logger.error(f"[Push] ❌ Error {codigo}: {str(error)}")
            raise enviar_notificacion_push.retry(exc=error)

    except Exception as error:
        logger.error(f"[Push] ❌ Error inesperado: {str(error)}")
        raise
```

### 6.4 Lógica para calcular `proxima_fecha_pago`

Este campo debe actualizarse cada vez que se crea o modifica una tarjeta.

```python
# finanzas/utils.py
from datetime import date
import calendar


def calcular_proxima_fecha_pago(dia_pago: int) -> date:
    """
    Calcula la próxima fecha de pago basándose en el día del mes configurado.
    Si el día ya pasó este mes, devuelve la fecha del siguiente mes.

    Ejemplo:
        dia_pago = 15, hoy = 20 de junio → devuelve 15 de julio
        dia_pago = 28, hoy = 5 de junio  → devuelve 28 de junio
    """
    hoy = date.today()

    # Intentar este mes primero
    ultimo_dia_mes = calendar.monthrange(hoy.year, hoy.month)[1]
    dia_ajustado   = min(dia_pago, ultimo_dia_mes)  # Evitar error en meses cortos

    fecha_este_mes = hoy.replace(day=dia_ajustado)

    if fecha_este_mes >= hoy:
        return fecha_este_mes

    # Calcular para el mes siguiente
    if hoy.month == 12:
        mes_sig = 1
        anio_sig = hoy.year + 1
    else:
        mes_sig = hoy.month + 1
        anio_sig = hoy.year

    ultimo_dia_mes_sig = calendar.monthrange(anio_sig, mes_sig)[1]
    dia_ajustado_sig   = min(dia_pago, ultimo_dia_mes_sig)

    return date(anio_sig, mes_sig, dia_ajustado_sig)
```

Usar en la vista al crear o editar una tarjeta:

```python
# En la vista de crear tarjeta
from .utils import calcular_proxima_fecha_pago

tarjeta = TarjetaCredito(
    usuario=request.user,
    banco=form.cleaned_data["banco"],
    dia_corte=form.cleaned_data["dia_corte"],
    dia_pago=form.cleaned_data["dia_pago"],
    proxima_fecha_pago=calcular_proxima_fecha_pago(form.cleaned_data["dia_pago"])
)
tarjeta.save()
```

-----

## 7. Fase 6 — Nginx + HTTPS

### 7.1 Obtener certificado SSL con Let’s Encrypt

```bash
sudo certbot --nginx -d tudominio.com -d www.tudominio.com
```

### 7.2 Configuración de Nginx

```nginx
# /etc/nginx/sites-available/finanzas
# Enlazar: sudo ln -s /etc/nginx/sites-available/finanzas /etc/nginx/sites-enabled/

# Redirigir HTTP → HTTPS
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;
    return 301 https://$host$request_uri;
}

# Servidor principal HTTPS
server {
    listen 443 ssl http2;
    server_name tudominio.com www.tudominio.com;

    # Certificados SSL (generados por Certbot)
    ssl_certificate     /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    # ─── CRÍTICO: Service Worker sin caché ────────────────────────────────────
    # El SW debe estar siempre actualizado. Nunca cachear este archivo.
    location = /sw.js {
        root  /ruta/a/tu_proyecto/;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        expires 0;
    }

    # ─── Archivos estáticos (CSS, JS, imágenes) ───────────────────────────────
    location /static/ {
        alias /ruta/a/tu_proyecto/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # ─── Todo lo demás → Django via Gunicorn ──────────────────────────────────
    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host             $host;
        proxy_set_header   X-Real-IP        $remote_addr;
        proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto https;
        proxy_read_timeout 60s;
    }
}
```

### 7.3 Verificar y recargar Nginx

```bash
sudo nginx -t          # Verificar sintaxis
sudo systemctl reload nginx
```

-----

## 8. Fase 7 — Caso especial iOS

### 8.1 Restricciones de Apple

En iPhones/iPads, el Web Push **solo funciona** si:

1. El usuario usa **Safari** (no Chrome para iOS)
1. El sitio está agregado a la **pantalla de inicio como PWA**
1. La versión de iOS es **16.4 o superior**

### 8.2 Detección y banner educativo (JavaScript)

El código de detección ya está incluido en `push-notifications.js` (Fase 4.3). El banner HTML ya está en el template (Fase 5.2).

### 8.3 Meta tags requeridas para iOS en el `<head>`

```html
<!-- En templates/base.html -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Mis Finanzas">

<!-- Ícono para la pantalla de inicio en iOS -->
<link rel="apple-touch-icon" sizes="180x180" href="/static/img/apple-touch-icon.png">

<!-- Pantalla de splash (opcional pero mejora UX) -->
<link rel="apple-touch-startup-image" href="/static/img/splash-2048x2732.png"
      media="(device-width: 1024px) and (device-height: 1366px) and (-webkit-device-pixel-ratio: 2)">
```

### 8.4 Iconos mínimos requeridos

```
static/img/
├── icon-192.png         # Android / Chrome (192x192 px)
├── icon-512.png         # Android / Chrome (512x512 px)
├── badge-72.png         # Ícono monocromático para la barra de estado (72x72 px)
└── apple-touch-icon.png # iOS pantalla de inicio (180x180 px)
```

-----

## 9. Fase 8 — Levantar servicios en producción

### 9.1 Archivos de configuración con Supervisor

Usar Supervisor para que todos los servicios se reinicien automáticamente si caen.

```bash
sudo apt install -y supervisor
```

**Gunicorn** (`/etc/supervisor/conf.d/gunicorn.conf`):

```ini
[program:gunicorn]
command=/ruta/venv/bin/gunicorn tu_proyecto.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 60
directory=/ruta/tu_proyecto
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/gunicorn/error.log
stdout_logfile=/var/log/gunicorn/access.log
```

**Celery Worker** (`/etc/supervisor/conf.d/celery-worker.conf`):

```ini
[program:celery-worker]
command=/ruta/venv/bin/celery -A tu_proyecto worker --loglevel=info --concurrency=4
directory=/ruta/tu_proyecto
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/celery/worker-error.log
stdout_logfile=/var/log/celery/worker.log
environment=DJANGO_SETTINGS_MODULE="tu_proyecto.settings"
```

**Celery Beat** (`/etc/supervisor/conf.d/celery-beat.conf`):

```ini
[program:celery-beat]
command=/ruta/venv/bin/celery -A tu_proyecto beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/ruta/tu_proyecto
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/celery/beat-error.log
stdout_logfile=/var/log/celery/beat.log
environment=DJANGO_SETTINGS_MODULE="tu_proyecto.settings"
```

### 9.2 Crear directorios de logs

```bash
sudo mkdir -p /var/log/gunicorn /var/log/celery
sudo chown -R www-data:www-data /var/log/gunicorn /var/log/celery
```

### 9.3 Arrancar todo

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all

# Verificar estado
sudo supervisorctl status
```

Resultado esperado:

```
celery-beat      RUNNING   pid 1234, uptime 0:00:05
celery-worker    RUNNING   pid 1235, uptime 0:00:05
gunicorn         RUNNING   pid 1236, uptime 0:00:05
```

### 9.4 Comandos útiles de mantenimiento

```bash
# Ver logs en tiempo real
sudo tail -f /var/log/celery/worker.log
sudo tail -f /var/log/celery/beat.log
sudo tail -f /var/log/gunicorn/error.log

# Reiniciar un servicio específico
sudo supervisorctl restart celery-worker

# Probar que Celery puede ejecutar tareas manualmente
python manage.py shell -c "from finanzas.tasks import enviar_recordatorios_pago; enviar_recordatorios_pago.delay()"

# Ver tareas en Redis (cola)
redis-cli llen celery
```

-----

## 10. Resumen del flujo completo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      REGISTRO (una sola vez por dispositivo)                │
│                                                                             │
│  Usuario toca "Activar alertas"                                             │
│       ↓                                                                     │
│  JS → navigator.serviceWorker.register("/sw.js")                            │
│       ↓                                                                     │
│  JS → pushManager.subscribe({ applicationServerKey: VAPID_PUBLIC_KEY })     │
│       ↓                                                                     │
│  Navegador muestra popup: "¿Permitir notificaciones?"                       │
│       ↓ (usuario acepta)                                                    │
│  Navegador genera: { endpoint, keys: { p256dh, auth } }                     │
│       ↓                                                                     │
│  JS → fetch("/api/suscripcion/guardar/", { body: datos_dispositivo })       │
│       ↓                                                                     │
│  Django → SuscripcionPush.objects.update_or_create(...)  →  MySQL           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                      DISPARO DIARIO AUTOMATIZADO                            │
│                                                                             │
│  8:00 AM → Celery Beat despierta                                            │
│       ↓                                                                     │
│  Consulta MySQL: tarjetas con proxima_fecha_pago = hoy + 2 días             │
│       ↓                                                                     │
│  Encuentra: Tarjeta BBVA Visa Oro → usuario@email.com                       │
│       ↓                                                                     │
│  Consulta SuscripcionPush del usuario → 2 dispositivos encontrados          │
│       ↓                                                                     │
│  Celery Worker 1: webpush(endpoint_movil, mensaje cifrado con VAPID)        │
│  Celery Worker 2: webpush(endpoint_tablet, mensaje cifrado con VAPID)       │
│       ↓                                                                     │
│  Google FCM / Apple APNs → valida llaves VAPID → empuja al dispositivo     │
│       ↓                                                                     │
│  sw.js se despierta → showNotification("⚠️ Tu BBVA vence en 2 días")       │
│       ↓                                                                     │
│  Usuario toca la notificación → abre /finanzas/tarjetas/ID/                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                      LIMPIEZA AUTOMÁTICA (anti-basura)                      │
│                                                                             │
│  Google/Apple responde 404 o 410 (dispositivo inválido)                     │
│       ↓                                                                     │
│  Celery Worker captura WebPushException                                     │
│       ↓                                                                     │
│  suscripcion.delete()  → MySQL elimina el registro muerto                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

-----

## 11. Checklist de verificación

Usar esta lista antes de considerar la integración completa:

### Seguridad

- [ ] El archivo `.env` está en `.gitignore` y **nunca** ha sido subido al repositorio
- [ ] El archivo `.env.example` está en el repositorio con las claves vacías
- [ ] HTTPS está activo y el certificado SSL es válido (`https://tudominio.com`)
- [ ] Todas las vistas de API tienen el decorador `@login_required` y `@csrf_protect`
- [ ] La llave VAPID privada **nunca** aparece en el código fuente ni en templates

### Infraestructura

- [ ] Redis responde `PONG` al ejecutar `redis-cli ping`
- [ ] Gunicorn está corriendo y Django responde en `http://127.0.0.1:8000`
- [ ] Nginx sirve correctamente `https://tudominio.com/sw.js` sin caché
- [ ] Supervisor tiene los tres procesos en estado `RUNNING`

### Base de datos

- [ ] Las tablas `tarjetas_credito` y `suscripciones_push` existen en MySQL
- [ ] Las migraciones están aplicadas (`python manage.py showmigrations`)

### Frontend

- [ ] El archivo `/sw.js` responde con `Content-Type: application/javascript`
- [ ] El archivo `/static/manifest.json` responde correctamente
- [ ] Los iconos `icon-192.png`, `icon-512.png` y `apple-touch-icon.png` existen
- [ ] El botón de suscripción aparece y funciona en Chrome Android
- [ ] El banner educativo aparece en Safari iOS sin PWA instalada

### Celery

- [ ] La tarea se puede disparar manualmente sin errores desde `manage.py shell`
- [ ] El log de Celery Beat muestra la tarea programada al iniciar
- [ ] Al enviar una notificación de prueba, llega al dispositivo en menos de 30 segundos
- [ ] Las suscripciones con código 404/410 se eliminan automáticamente de MySQL

-----

*Guía generada para stack: Django · MySQL · Redis · Celery · Nginx · HTML/CSS/JS nativo · pywebpush*