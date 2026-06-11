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
- [ ] 11.1 Modelo `Presupuesto`
- [ ] 11.2 CRUD presupuestos con HTMX

## Fase 12 — Dashboard
- [ ] 12.1 Vista dashboard con resumen (ingresos, gastos, saldo)
- [ ] 12.2 Chart.js: gráfico ingresos vs gastos por mes
- [ ] 12.3 Últimas transacciones + alertas presupuestos
- [ ] 12.4 Template `dashboard.html`

## Fase 13 — Signals (restantes)
- [ ] 13.1 Signal `Presupuesto.monto_gastado` (al guardar/borrar Gasto)
- [ ] 13.2 Signal `MetaAhorro.monto_actual` (al guardar/borrar DepositoAhorro, Ingreso)

## Fase 14 — Celery
- [ ] 14.1 Config Celery en `config/celery.py`
- [ ] 14.2 Tarea: revisar transferencias recurrentes vencidas
- [ ] 14.3 Tarea: enviar recordatorios tarjeta crédito (T-7, T-5, T-2)
