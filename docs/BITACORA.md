# Bitácora de Cambios — FinanPlanen

Formato: `YYYY-MM-DD | Archivo | Línea(s) | Cambio | Motivo (ref. AUDITORIA.md)`

---

## 2026-06-23 — Correcciones de Auditoría (Fase 17)

| # | Archivo | Líneas | Cambio | Motivo |
|---|---------|--------|--------|--------|
| C1 | `apps/transfers/tasks.py` | 1-40 | `select_for_update(nowait=True)` + `transaction.atomic()` + `bulk_create()` + `bulk_update()` + `ignore_result=True` | Race condition duplicaba transferencias concurrentes; no había rollback en fallos; N queries individuales; resultado saturaba Redis |
| C2 | `apps/transfers/tasks.py` | 40-55 | Recalcular balances de cuentas afectadas con `F()` + `Sum` post-bulk_create | `bulk_create` no dispara señales; balances quedarían corruptos sin este recálculo explícito |
| C3a | `apps/transactions/signals.py` | 1-45 | `F('balance')` + `transaction.atomic()` + `IntegrityError` + `logger.info` | Race condition clásica: dos requests leían mismo balance en memoria y el último write ganaba, perdiendo dinero. `F()` delega a SQL, atómico. Savepoints anidados frágiles en MySQL → try/except IntegrityError |
| C3b | `apps/transfers/signals.py` | 1-43 | `F('balance')` + `transaction.atomic()` + `IntegrityError` + `logger.info` | Idem C3a. Transferencias actualizan 2 cuentas; sin atomicidad una podía fallar dejando dinero perdido |
| C3c | `apps/savings/signals.py` | 1-50 | `F()` + `transaction.atomic()` + try/except `logger.critical` + validar `updated` | Idem C3a + C3b. Adicional: si `meta_id` no existe al hacer post_delete, la excepción no se capturaba y silenciaba el error |
| C4 | `apps/notifications/tasks.py` | 29-91 | `timeout=10`, `ignore_result=True`, `bind=True`, `max_retries=3`, eliminar `self.retry()` del bucle, `.only()` en query | Sin timeout el worker se congelaba con push service lento; `self.retry()` dentro del bucle reintentaba toda la tarea duplicando notificaciones previas; `.only()` reduce RAM |
| C5a | `apps/transfers/models.py` | 16, 21 | `on_delete=CASCADE` → `PROTECT` en `Transferencia.origen` y `destino` | Eliminar una Cuenta borraba en cascada todo el historial de transferencias. `PROTECT` fuerza a limpiar transacciones primero |
| C5b | `apps/transactions/models.py` | 13, 51 | `on_delete=CASCADE` → `PROTECT` en `Ingreso.cuenta` y `Gasto.cuenta` | Idem C5a: borrar cuenta destruía ingresos y gastos asociados |
| C5c | `apps/budgets/models.py` | 13 | `on_delete=CASCADE` → `SET_NULL, null=True` en `Presupuesto.categoria` | Categoría es dato maestro; al eliminarla los presupuestos deben quedar huérfanos, no borrarse |
| C5d | `apps/savings/models.py` | 68 | `on_delete=CASCADE` → `PROTECT` en `DepositoAhorro.meta` | Eliminar una meta de ahorro no debe borrar el historial de depósitos |

## 2026-06-23 — Implementación efectiva (Hallazgos reales aplicados al código)

| # | Archivo | Líneas | Cambio | Motivo |
|---|---------|--------|--------|--------|
| P19a | `apps/accounts/views.py` | 1, 110-115 | Import `ProtectedError`; try/except en `CuentaEliminar.form_valid` | Sin captura, eliminar cuenta con movimientos daba Error 500 tras CASCADE→PROTECT |
| P19b | `apps/savings/views.py` | 4, 129-134 | Import `ProtectedError`; try/except en `MetaAhorroEliminar.form_valid` | Idem P19a para metas con depósitos |
| P23a | `apps/budgets/models.py` | 37 | `__str__` protegido: verifica `categoria_id` antes de acceder a `.nombre` | Tras C5 (SET_NULL), categoria=None crasheaba el __str__ |
| P23b | `apps/budgets/views.py` | 73-78 | Accesos a `p.categoria.*` protegidos con `if p.categoria_id` | Idem P23a: el loop de presupuestos_json crasheaba con categoria=None |
| P23c | `apps/budgets/templates/budgets/presupuesto.html` | 341-381 | Envuelto card en `{% if p.categoria_id %}` con `{% else %}` para categoría eliminada | Template crasheaba al acceder a `p.categoria.nombre` con categoria=None |
| C5a | `apps/transactions/models.py` | 13, 51 | `on_delete=CASCADE` → `PROTECT` en `Ingreso.cuenta` y `Gasto.cuenta` | Eliminar Cuenta ya no destruye historial de transacciones |
| C5b | `apps/transfers/models.py` | 16, 21, 58, 63 | `on_delete=CASCADE` → `PROTECT` en `Transferencia.origen/destino` y `RecurrenciaTransferencia.origen/destino` | Protege historial de transfers y recurrencias al borrar cuenta |
| C5c | `apps/budgets/models.py` | 13-15 | `on_delete=CASCADE` → `SET_NULL, null=True` en `Presupuesto.categoria` | Categoría eliminada deja presupuesto huérfano, no lo borra |
| C5d | `apps/savings/models.py` | 68 | `on_delete=CASCADE` → `PROTECT` en `DepositoAhorro.meta` | Eliminar meta no destruye historial de depósitos |
| C5e | Varios | — | `makemigrations` + `migrate` (4 migraciones aplicadas) | Cambios de on_delete requieren migración de esquema |

## 2026-06-23 — Batch 2: Críticos + Altos completados

| # | Archivo | Cambio | Motivo |
|---|---------|--------|--------|
| C3a | `apps/transactions/signals.py` | F('balance') + transaction.atomic() + logger en Ingreso/Gasto post_save + post_delete | Race condition en actualización de balances |
| C3b | `apps/transfers/signals.py` | F('balance') + transaction.atomic() + logger en Transferencia post_save + post_delete | Race condition en actualización de balances |
| C3c | `apps/savings/signals.py` | F('monto_actual') + F('balance') + transaction.atomic() + logger + try/except crítico en DepositoAhorro | Race condition + fallo silencioso en post_delete |
| C1+C2 | `apps/transfers/tasks.py` | @shared_task(ignore_result=True, bind=True, max_retries=3); select_for_update(nowait=True); transaction.atomic(); logger.critical | Deadlock entre workers + sin reintentos |
| C4 | `apps/notifications/tasks.py` | timeout=10 en webpush(); @shared_task(ignore_result=True, bind=True, max_retries=3); .only('endpoint','p256dh','auth') en SuscripcionPush | Workers bloqueados sin timeout |
| P6 | `apps/transactions/models.py`, `apps/transfers/models.py`, `apps/savings/models.py`, `apps/budgets/models.py` | MinValueValidator(Decimal('0.01')) en 7 campos monto/meta/monto_limite | Validación débil en montos financieros |
| P7 | `apps/core/views.py` | TruncMonth reemplaza loops duplicados (24→2 queries); select_related en Ingreso/Gasto recientes (elimina N+1); import random movido al tope | 24+ queries redundantes + N+1 |
| P8 | `apps/budgets/views.py` | categoria__color añadido a select_related | N+1 en lista de presupuestos |
| P9 | Varios modelos | db_index=True en Ingreso.fecha, Gasto.fecha, Cuenta.activo, RecurrenciaTransferencia.proxima_ejecucion, RecurrenciaTransferencia.activo, MetaAhorro.activo, Presupuesto.activo + migrate | Full table scan en filtros de uso diario |

| P11 | `config/settings/base.py` | CELERY_RESULT_BACKEND → redis://localhost:6379/1; añadido CELERY_RESULT_EXPIRES = 1800 | Redis compartido con broker + resultados sin expiración |
| P12 | `apps/transactions/views.py` | N+1 loops reemplazados por .values().annotate(); budget_limit real contra Presupuesto | 90+ queries SQL a 2 |
| P13 | `apps/notifications/views.py` | Validación endpoint != None en eliminar_suscripcion | Error 500 expuesto al cliente |
| P17 | `apps/transactions/views.py` | Filtro fecha default 90 días en TransaccionLista | Paginación en memoria sin límite |
| P18 | `apps/accounts/forms.py` | except: → except (ValueError, InvalidOperation) | Capturaba KeyboardInterrupt |
| P20 | `config/settings/base.py` | LOGGING config con console handler + loggers de apps | Logs al void en producción |
| P21+P22 | `config/settings/prod.py` | SECURE_HSTS_SECONDS + X_FRAME_OPTIONS + ALLOWED_HOSTS sin default | Seguridad HTTP insuficiente |
| P25 | `apps/transactions/views.py` | Hecho en P12: budget_limit ahora es query real a Presupuesto | Valor hardcodeado 20000 |

## 2026-06-23 — Fase 18: Próximos Pagos + Límite Crédito

| # | Archivo | Líneas | Cambio | Motivo |
|---|---------|--------|--------|--------|
| 18.1 | `apps/accounts/models.py` | 35-38 | Nuevo campo `limite_credito = DecimalField(default=0)` | Necesario para calcular total_a_pagar en crédito |
| 18.2a | `apps/accounts/forms.py` | 12-22 | Add `limite_credito` field + widget en `#credito-fields` | Input del límite en formulario |
| 18.2b | `apps/accounts/forms.py` | 131-148 | `clean_limite_credito()` con validación | Límite > 0 para crédito, = 0 para débito/efectivo |
| 18.3 | `apps/accounts/templates/accounts/_form_cuenta.html` | 58-75 | Input `limite_credito` dentro de `#credito-fields` + JS auto-complete balance | UX: al tipear límite, balance se auto-completa |
| 18.4 | `apps/accounts/templates/accounts/Cuenta.html` | 51-53 | Mostrar "LÍMITE" en tarjeta crédito | Feedback visual del límite al usuario |
| 18.5 | `apps/core/utils.py` | — | Crear archivo con `calcular_prox_pago()` | Función compartida entre dashboard y notificaciones |
| 18.6a | `apps/notifications/tasks.py` | 1, 12-26 | Import `calcular_prox_pago` desde core/utils; eliminar función inline | DRY: misma lógica en un solo lugar |
| 18.6b | `apps/notifications/management/commands/test_push.py` | 1, 12-25 | Import `calcular_prox_pago` desde core/utils; eliminar función inline | DRY: misma lógica en un solo lugar |
| 18.7 | `apps/core/views.py` | 15-16, 168-188 | Contexto `proximos_pagos` con total_a_pagar, días restantes, ordenado | Dashboard necesita lista de próximos pagos |
| 18.8 | `apps/core/templates/core/dashboard.html` | 79-98 | Loop sobre `proximos_pagos` reemplaza placeholder vacío | Visualización de pagos próximos en dashboard |
| 18.m | `apps/accounts/migrations/0003_cuenta_limite_credito.py` | — | Nueva migración: add field limite_credito to cuenta | Schema requerido por el nuevo campo |
