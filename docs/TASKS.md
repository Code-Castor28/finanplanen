# FinanPlanen — Lista de Tareas

## Fase 1 — Proyecto base
- [x] 1.1 `django-admin startproject config .`
- [x] 1.2 Renombrar `config/settings.py` → `config/settings/base.py` + crear `dev.py`, `prod.py`, `__init__.py`
- [x] 1.2b Configurar `manage.py` → `config.settings.dev`, `wsgi.py`/`asgi.py` → `config.settings.prod`
- [x] 1.3 `startapp` para las 9 apps en `apps/` (accounts, budgets, categories, core, savings, theme, transactions, transfers, users)
- [x] 1.4 Crear `apps/__init__.py`
- [x] 1.5 Crear `requirements.txt`
- [x] 1.6 Configurar `base.py` (MySQL, apps registradas, templates dir, static, media)
- [x] 1.7 Configurar `config/urls.py` raíz + `apps/core/urls.py` + vista `inicio`
- [x] 1.8 Crear `static/css/style.css`, `static/js/main.js`, `media/.gitkeep`, `templates/base.html` + dashboard.html

## Fase 2 — Inquilino + Usuarios
- [x] 2.1 Modelo `Tenant` + señal auto-crear al registrar
- [x] 2.2 Modelo `Usuario(AbstractUser)` con FK a Tenant
- [x] 2.3 Forms: registro, login, perfil
- [x] 2.4 Vistas + URLs: registro, login, logout, perfil
- [x] 2.4b Proteger dashboard con `@login_required` + configurar `LOGIN_URL`
- [x] 2.5 Templates: `login.html`, `register.html`, `profile.html`

## Fase 3 — Tema (Colores + Iconos)
- [x] 3.1 Modelo `Color`
- [x] 3.2 Modelo `Icono`
- [x] 3.3 CRUD colores con HTMX (vistas, URLs, templates)
- [x] 3.4 CRUD iconos con HTMX (vistas, URLs, templates)
- [x] 3.5 Template tag `{% theme_css_variables %}` en `templatetags/theme_tags.py`
- [x] 3.6 Integrar template tag en `<head>` de `base.html`

## Fase 4 — Categorías + Etiquetas
- [x] 4.1 Modelo `Categoria` con FK a Color e Icono
- [x] 4.2 Modelo `Etiqueta` con FK a Color y M2M a Categoria
- [x] 4.3 CRUD categorías con HTMX
- [x] 4.4 CRUD etiquetas con HTMX

## Fase 5 — Cuentas
- [x] 5.1 Modelo `Cuenta` con FK a Color e Icono
- [x] 5.2 CRUD cuentas con HTMX

## Fase 6 — Gastos
- [x] 6.1 Modelo `Gasto` (cuenta FK, categoría FK, monto, fecha, nota, comprobante)
- [x] 6.2 Signal: al crear/borrar Gasto → actualiza `Cuenta.balance`
- [x] 6.3 CRUD gastos con HTMX + filtros (fecha, categoría, cuenta) + paginación
- [x] 6.4 Templates: `gastos.html`, `_lista_gastos.html`, `_form_gasto.html`

## Fase 7 — Ingresos
- [x] 7.1 Modelo `Ingreso` (cuenta FK, categoría FK, monto, fecha, nota, comprobante)
- [x] 7.2 Signal: al crear/borrar Ingreso → actualiza `Cuenta.balance` (suma)
- [x] 7.3 CRUD ingresos con HTMX + filtros + paginación
- [x] 7.4 Templates: `ingresos.html`, `_lista_ingresos.html`, `_form_ingreso.html`

## Fase 8 — Transacciones (solo lectura)
- [x] 8.1 Vista unificada que consulta `Ingreso` + `Gasto` + `Transferencia`
- [x] 8.2 Filtros: fecha, cuenta, tipo (ingreso/gasto/transferencia)
- [x] 8.3 Paginación
- [x] 8.4 Template `transacciones.html` (solo lectura, sin formulario)

## Fase 9 — Transferencias
- [x] 9.1 Modelo `Transferencia` (origen FK cuenta, destino FK cuenta, monto)
- [x] 9.2 Signal: al crear/borrar → ajusta balances origen/destino
- [x] 9.3 CRUD transferencias con HTMX
- [x] 9.4 Templates: `transferencias.html`, `_lista_transferencias.html`, `_form_transferencia.html`

## Fase 10 — Ahorros
- [x] 10.1 Modelo `MetaAhorro` con FK a Color e Icono
- [x] 10.2 Modelo `DepositoAhorro`
- [x] 10.3 CRUD metas + formulario de depósito

## Fase 11 — Presupuestos
- [x] 11.1 Modelo `Presupuesto` (monto_limite, monto_gastado, mes, año, progreso_pct, restante, excedido)
- [x] 11.2 CRUD presupuestos con HTMX (lista, crear, editar, eliminar)
- [x] 11.3 Signal: `Presupuesto.monto_gastado` se actualiza al crear/borrar `Gasto`

## Fase 12 — Dashboard
- [x] 12.1 Vista `PanelPrincipal` con resumen (ingresos, gastos, saldo, cambios % vs mes anterior)
- [x] 12.2 Chart.js: 4 gráficos (barras ingreso/gasto, dona categorías, línea ahorro, barras apiladas evolución)
- [x] 12.3 Últimas 10 transacciones + tabla ahorro mensual con superávit/déficit
- [x] 12.4 Template `dashboard.html` (397 líneas, extiende base.html)

## Fase 19 — Notificaciones toast + Login feedback
- [ ] 19.1 App `users`: login non_field_errors + registro success message
- [ ] 19.2 App `accounts`: messages en CuentaCrear, Editar, Eliminar
- [ ] 19.3 App `transactions`: messages en Ingreso/Gasto Crear, Editar, Eliminar
- [ ] 19.4 App `transfers`: messages en Transferencia Crear, Editar, Eliminar
- [ ] 19.5 App `budgets`: messages en Presupuesto Crear, Editar, Eliminar
- [ ] 19.6 App `savings`: messages en MetaAhorro + Deposito Crear, Editar, Eliminar
- [ ] 19.7 App `categories`: messages en Categoria/Etiqueta Crear, Editar, Eliminar
- [ ] 19.8 App `theme`: messages en Color/Icono Crear, Editar, Eliminar
- [ ] 19.9 `templates/base.html`: render Django messages como toast

## Fase 13 — Signals
- [x] 13.1 Signal `Presupuesto.monto_gastado` (al guardar/borrar Gasto) — `apps/budgets/signals.py`
- [x] 13.2 Signal `MetaAhorro.monto_actual` (al guardar/borrar DepositoAhorro) — `apps/savings/signals.py`
- [x] 13.3 Signals `Cuenta.balance` para Ingreso, Gasto, Transferencia — `apps/transactions/signals.py`, `apps/transfers/signals.py`
- [x] 13.4 Signal auto-crear Tenant al registrar Usuario — `apps/users/signals.py`

## Fase 14 — Celery
- [x] 14.1 Config Celery en `config/celery.py` + `config/__init__.py`
- [x] 14.2 Tarea `ejecutar_recurrencias`: transferencias recurrentes vencidas (06:00 diario)
- [x] 14.3 Tarea `recordatorio_tarjetas_credito`: recordatorios tarjeta crédito (09:00 diario)
- [x] 14.4 Config: Redis broker/backend, beat schedule, JSON serializer, zona horaria

## Fase 15 — Web Push / PWA (Notificaciones Push)
- [x] 15.1 Crear app `apps/notifications/` + modelo `SuscripcionPush` (endpoint, p256dh, auth, usuario FK)
- [x] 15.2 Configurar VAPID keys en `.env` + `settings.py` + `requirements.txt` (pywebpush ya estaba)
- [x] 15.3 Crear Service Worker `templates/sw.js` + ruta `/sw.js` en `urls.py`
- [x] 15.4 Crear `static/manifest.json` + PWA meta tags en `base.html`
- [x] 15.5 Crear iconos PWA placeholder (`icon-192`, `icon-512`, `badge-72`, `apple-touch-icon`)
- [x] 15.6 API backend: `guardar_suscripcion` / `eliminar_suscripcion` (views + urls)
- [x] 15.7 Frontend: `static/js/push-notifications.js` (suscripción/desuscripción push)
- [x] 15.8 Template partial `_push_config.html` incluido en página de perfil
- [x] 15.9 Tarea Celery movida a `apps/notifications/tasks.py`: pushes reales con pywebpush (T-7, T-5, T-2, T-0)
- [x] 15.10 Agregar enlace "Notificaciones" en sidebar de `base.html`
- [x] 15.11 Migrations + `python manage.py check` 0 issues

## Fase 16 — Sesión por Inactividad (Idle Timeout)
- [x] 16.1 JS idle detection en `static/js/main.js` (15 min sin actividad)
- [x] 16.2 Modal countdown 60s en `templates/base.html`
- [x] 16.3 Banner "sesión expirada" en `login.html` vía sessionStorage
- [x] 16.4 Redirección a `/acceso/salir/` al llegar a 0
- [x] 16.5 Fix móvil: sessionStorage persistente, eventos `touchend`/`focusin`/`pageshow`/`webkitvisibilitychange`, tiempo restante en vez de reinicio completo

## Fase 17 — Correcciones de Auditoría (Hallazgos y Soluciones)

### Batch 1 — Críticos
- [x] P19 Capturar ProtectedError en CuentaEliminar y MetaAhorroEliminar
- [x] P23 Proteger acceso a categoria.nombre en budgets/ (views, models, template)
- [x] C5 on_delete=CASCADE → PROTECT/SET_NULL en modelos financieros + migraciones
- [x] C1+C2 transaction.atomic() + select_for_update + .create() individual en transfers/tasks.py
- [x] C3 F('balance') + transaction.atomic() + logger en signals.py
- [x] C4 timeout=10 + ignore_result + .only() en notifications/tasks.py

### Batch 2 — Altos
- [x] P6 MinValueValidator en campos de monto
- [x] P7 Dashboard: select_related + TruncMonth + fix import random
- [x] P8 Añadir categoria__color a select_related en budgets/views.py
- [x] P9 db_index en campos críticos + migrate
- [ ] P10 ignore_result en transfers/tasks.py (ya hecho en C1+C2)
- [x] P11 Separar Redis backend a DB 1 + CELERY_RESULT_EXPIRES

### Batch 3 — Medios
- [x] P12 annotate en IngresoLista/GastoLista + budget_limit real
- [x] P13 Validar endpoint en eliminar_suscripcion
- [x] P17 Filtro fecha default en TransaccionLista

### Batch 4 — Bajos
- [x] P18 except→ (ValueError, InvalidOperation) en forms.py
- [x] P20 LOGGING config en base.py
- [x] P21 HSTS + X_FRAME en prod.py
- [x] P22 ALLOWED_HOSTS requerido en prod.py
- [x] P25 budget_limit con query real en GastoLista (hecho en P12)

## Fase 18 — Próximos Pagos + Límite Crédito
- [x] 18.1 Agregar campo `limite_credito` a `Cuenta` (+ migration)
- [x] 18.2 Formulario: input `limite_credito` en `#credito-fields` + validación
- [x] 18.3 JS auto-complete: balance = limite_credito al tipear
- [x] 18.4 Template Cuenta.html: mostrar límite en tarjetas crédito
- [x] 18.5 Extraer `calcular_prox_pago()` a `apps/core/utils.py`
- [x] 18.6 Refactor `notifications/tasks.py` y `test_push.py` (importar desde utils)
- [x] 18.7 Dashboard: contexto `proximos_pagos` en `PanelPrincipal`
- [x] 18.8 Dashboard template: loop de próximos pagos
- [x] 18.9 Opción A vs B: se probó Opción B (balance=deuda) y se revirtió a Opción A (balance=disponible)
