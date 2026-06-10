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
- [ ] 2.1 Modelo `Tenant` + señal auto-crear al registrar
- [ ] 2.2 Modelo `Usuario(AbstractUser)` con FK a Tenant
- [ ] 2.3 Forms: registro, login, perfil
- [ ] 2.4 Vistas + URLs: registro, login, logout, perfil
- [ ] 2.5 Templates: `login.html`, `register.html`, `profile.html`

## Fase 3 — Tema (Colores + Iconos)
- [ ] 3.1 Modelo `Color`
- [ ] 3.2 Modelo `Icono`
- [ ] 3.3 CRUD colores con HTMX (vistas, URLs, templates)
- [ ] 3.4 CRUD iconos con HTMX (vistas, URLs, templates)
- [ ] 3.5 Template tag `{% theme_css_variables %}` en `templatetags/theme_tags.py`
- [ ] 3.6 Integrar template tag en `<head>` de `base.html`

## Fase 4 — Categorías + Etiquetas
- [ ] 4.1 Modelo `Categoria` con FK a Color e Icono
- [ ] 4.2 Modelo `Etiqueta` con FK a Color y M2M a Categoria
- [ ] 4.3 CRUD categorías con HTMX
- [ ] 4.4 CRUD etiquetas con HTMX

## Fase 5 — Cuentas
- [ ] 5.1 Modelo `Cuenta` con FK a Color e Icono
- [ ] 5.2 CRUD cuentas con HTMX

## Fase 6 — Transacciones
- [ ] 6.1 Modelo `Transaccion`
- [ ] 6.2 CRUD transacciones con filtros (fecha, cuenta, categoría) + paginación
- [ ] 6.3 Subida de comprobante

## Fase 7 — Transferencias
- [ ] 7.1 Modelo `Transferencia`
- [ ] 7.2 Modelo `TransferenciaRecurrente`
- [ ] 7.3 CRUD transferencias (crear → 2 Transaccion débito/crédito)
- [ ] 7.4 CRUD recurrentes + toggle activa

## Fase 8 — Ahorros
- [ ] 8.1 Modelo `MetaAhorro` con FK a Color e Icono
- [ ] 8.2 Modelo `DepositoAhorro`
- [ ] 8.3 CRUD metas + formulario de depósito

## Fase 9 — Presupuestos
- [ ] 9.1 Modelo `Presupuesto`
- [ ] 9.2 CRUD presupuestos con HTMX

## Fase 10 — Dashboard
- [ ] 10.1 Vista dashboard con resumen (ingresos, gastos, saldo)
- [ ] 10.2 Chart.js: gráfico ingresos vs gastos por mes
- [ ] 10.3 Últimas transacciones + alertas presupuestos
- [ ] 10.4 Template `dashboard.html`

## Fase 11 — Signals
- [ ] 11.1 Signal `Cuenta.saldo` (al guardar/borrar Transaccion o Transferencia)
- [ ] 11.2 Signal `Presupuesto.monto_gastado` (al guardar/borrar Transaccion)
- [ ] 11.3 Signal `MetaAhorro.monto_actual` (al guardar/borrar DepositoAhorro)

## Fase 12 — Celery
- [ ] 12.1 Config Celery en `config/celery.py`
- [ ] 12.2 Tarea: revisar transferencias recurrentes vencidas
- [ ] 12.3 Tarea: enviar recordatorios tarjeta crédito (T-7, T-5, T-2)
