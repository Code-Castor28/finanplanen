# Auditoría Técnica — FinanPlanen
# Hallazgos y Soluciones por Batch

> Fecha: 2026-06-23
> Stack: Django · Celery · Redis · MySQL
> Total de puntos auditados: 25 + 5 hallazgos adicionales

---

## Matriz de Prioridad

| Nivel | Impacto | Acción |
|---|---|---|
| **CRÍTICO** | Pérdida de dinero, duplicidad de transacciones, corrupción de saldos | Bloquear despliegues. Corregir de inmediato. |
| **ALTO** | Bloqueo de workers, degradación de rendimiento, N+1 en rutas críticas | Resolver en el sprint actual. |
| **MEDIO** | Ineficiencia de queries, logs ausentes, falta de timeouts | Corregir antes de la siguiente versión. |
| **BAJO** | Estructura mejorable, configuración incompleta, detalles menores | Refactorizar en mantenimiento. |

---

---

# 🔴 BATCH 1 — CRÍTICOS

---

## C1 + C2 · `apps/transfers/tasks.py`
### Sin atomicidad ni bloqueo de concurrencia

**Hallazgo:**
La tarea `ejecutar_recurrencias` itera sobre registros y crea `Transferencia` uno por uno con `.create()` dentro de un bucle. No existe `transaction.atomic()` ni `select_for_update()`. Si el servidor falla a mitad del loop, parte de las transferencias quedan creadas y parte no, sin rollback. Si Celery lanza la tarea dos veces en paralelo (fallo del broker o reintento), ambos workers leen los mismos registros simultáneamente y duplican todas las transferencias del día.

**Solución:**

1. Envuelve todo el cuerpo de la tarea en `with transaction.atomic()`. Si algo falla dentro, la base de datos revierte todo sin dejar registros huérfanos.
2. Añade `.select_for_update(nowait=True)` al queryset de `RecurrenciaTransferencia`. Esto bloquea las filas a nivel de BD. Si un segundo worker intenta leer las mismas filas, falla inmediatamente en lugar de procesarlas en paralelo.
3. Convierte el queryset a `list()` antes de iterar, para que el bloqueo se materialice dentro de la transacción.
4. Añade `ignore_result=True` al decorador `@shared_task`. Esta tarea no devuelve datos funcionales; guardar el resultado en Redis es desperdicio de RAM.

**Decisión requerida antes de codificar — bulk_create vs .create() individual:**

`bulk_create()` no dispara señales `post_save`. Tu `apps/transfers/signals.py` actualiza los balances escuchando `post_save` de `Transferencia`. Las dos opciones son incompatibles entre sí:

- **Opción A — `.create()` individual dentro de `transaction.atomic()`:** Conserva las señales sin cambios adicionales. Más lento a nivel de BD (una INSERT por recurrencia), pero seguro y predecible. Recomendada si el volumen diario de recurrencias es menor a 200.
- **Opción B — `bulk_create()` + recálculo manual de balances:** Requiere una función auxiliar que, después del `bulk_create`, calcule el delta neto por cuenta afectada y actualice los balances con `F()` en una sola query. Más rápido, pero añade complejidad y un punto de fallo adicional si el recálculo falla sin que el `bulk_create` se revierta.

**Recomendación para este sistema:** Usar Opción A. El volumen de recurrencias diarias en una app de finanzas personales raramente supera las 200, y el costo de una INSERT individual es despreciable comparado con el riesgo de un recálculo de balances incorrecto. Si en el futuro el volumen crece, migrar a Opción B con tests de integración ya escritos.

---

## C3 · `apps/transactions/signals.py` · `apps/transfers/signals.py` · `apps/savings/signals.py`
### Race condition en actualización de balances

**Hallazgo:**
Las señales actualizan los balances de `Cuenta` y `MetaAhorro` leyendo el valor en memoria del objeto Python y luego sobreescribiéndolo:

```
instance.cuenta.balance += instance.monto
instance.cuenta.save(update_fields=['balance'])
```

Si dos transacciones se guardan al mismo tiempo, ambas señales leen el mismo balance inicial, hacen su suma por separado, y la segunda escritura sobreescribe a la primera. El resultado es un balance incorrecto sin que el sistema lo detecte.

**Solución:**

1. Reemplaza la lectura/escritura en memoria por una actualización atómica a nivel SQL usando `F('balance')`. En lugar de leer el valor y sumarlo en Python, delega la aritmética al motor de base de datos en una sola operación: `Cuenta.objects.filter(pk=instance.cuenta_id).update(balance=F('balance') + instance.monto)`.
2. Envuelve cada `update()` en `with transaction.atomic()`.
3. Añade `logger.info()` después de cada operación con el ID de la instancia, el ID de la cuenta y el monto. Esto crea trazabilidad contable mínima.

**Advertencia para MySQL:**
Estás usando MySQL (`django.db.backends.mysql`). El `transaction.atomic()` dentro de una señal `post_save` abre un savepoint anidado sobre la transacción padre que creó el ingreso o gasto. MySQL tiene soporte de savepoints anidados menos robusto que PostgreSQL. Añade manejo explícito de `IntegrityError` alrededor del bloque atómico dentro de la señal para que un fallo en el update de balance no revierta silenciosamente la creación del ingreso.

**Hallazgo adicional en `apps/savings/signals.py`:**
En `deposito_eliminado`, si `meta_id` apunta a una `MetaAhorro` que fue eliminada previamente por error de datos, la query falla sin captura. En un `post_delete` no hay segunda oportunidad. Envuelve el bloque completo en `try/except Exception` y registra con `logger.critical`.

---

## C4 · `apps/notifications/tasks.py`
### Workers bloqueados por peticiones HTTP sin timeout

**Hallazgo:**
La llamada a `webpush()` no tiene parámetro `timeout`. Si el servidor de push de Google o Mozilla deja la conexión abierta sin responder, el worker de Celery queda bloqueado indefinidamente. Con suficientes tarjetas, todos los workers quedan ocupados y el sistema deja de procesar cualquier otra tarea.

**Solución:**

1. Añade `timeout=10` al llamado de `webpush()`.
2. Añade `ignore_result=True`, `bind=True` y `max_retries=3` al decorador `@shared_task`.
3. **No uses `self.retry()` dentro del bucle de suscripciones individuales.** Si un push falla por error de red, el worker reintentaría toda la tarea desde cero, re-enviando notificaciones a los dispositivos que ya las recibieron. Los fallos individuales de push deben registrarse con `logger.error` y continuar al siguiente con `continue`. El reintento a nivel de tarea solo aplica para fallos globales como ausencia de `VAPID_PRIVATE_KEY` o caída de la base de datos.

---

## C5 · Modelos financieros — `on_delete=CASCADE`
### Borrado en cascada destruye historial financiero

**Hallazgo:**
Todos los modelos financieros tienen `on_delete=models.CASCADE` en sus claves foráneas críticas. Si se elimina una `Cuenta`, se eliminan en cascada todas sus `Transferencia`, `Ingreso` y `Gasto` asociados. Si se elimina una `Categoria`, se eliminan todos los `Presupuesto` de esa categoría. Los registros históricos de movimientos de dinero desaparecen permanentemente sin advertencia.

**Modelos afectados:**
- `Transferencia.origen` y `Transferencia.destino` → ambos apuntan a `Cuenta` con CASCADE
- `Ingreso.cuenta` y `Gasto.cuenta` → apuntan a `Cuenta` con CASCADE
- `DepositoAhorro.meta` → apunta a `MetaAhorro` con CASCADE
- `Presupuesto.categoria` → apunta a `Categoria` con CASCADE

**Solución:**

1. Cambia `on_delete=models.CASCADE` a `on_delete=models.PROTECT` en `Transferencia.origen`, `Transferencia.destino`, `Ingreso.cuenta`, `Gasto.cuenta` y `DepositoAhorro.meta`. Django lanzará `ProtectedError` si alguien intenta eliminar una cuenta que tiene movimientos.
2. Para `Presupuesto.categoria` usa `on_delete=models.SET_NULL` con `null=True, blank=True`. Un presupuesto sin categoría es tolerable; un presupuesto eliminado por borrar una categoría no lo es.
3. Corre `makemigrations` en este orden para evitar conflictos entre apps: `accounts` → `transactions` → `transfers` → `savings` → `budgets`.

**Impacto de UX — cuentas ineliminables:**
Con `PROTECT` en `Ingreso.cuenta`, `Gasto.cuenta`, `Transferencia.origen` y `Transferencia.destino`, cualquier cuenta con al menos un movimiento no podrá eliminarse nunca. Un usuario con años de historial quedará atrapado con cuentas viejas que no puede borrar ni ocultar.

La solución es implementar el campo `activo` que ya existe en `Cuenta` como mecanismo de archivado:
- En la vista de lista de cuentas, filtrar por `activo=True` por defecto para que las cuentas archivadas no aparezcan en la operación diaria
- En la vista de edición de cuenta, permitir marcar `activo=False` como alternativa al borrado
- En los formularios de creación de `Ingreso`, `Gasto` y `Transferencia`, filtrar las cuentas disponibles por `activo=True`
- Opcionalmente, añadir una sección "Archivadas" en la vista de cuentas para que el usuario pueda ver o reactivar cuentas antiguas

Sin este mecanismo, `PROTECT` resuelve el problema de integridad de datos pero crea un problema de usabilidad que el usuario va a reportar como bug.

**Prerequisitos obligatorios — deben completarse ANTES de correr la migración:**

- **P19 es prerequisito bloqueante de C5 (PROTECT):** Añade manejo de `django.db.models.ProtectedError` en `CuentaEliminar` y `MetaAhorroEliminar`. `CategoriaEliminar` no aplica — todas sus FKs son `SET_NULL`. Sin este manejo, el usuario recibe Error 500 al intentar eliminar una cuenta con movimientos desde el momento en que se deploya la migración.
- **P23 es prerequisito bloqueante de C5 (SET_NULL) — clasificado como ALTO:** Proteger todos los accesos a `presupuesto.categoria` en `budgets/views.py`, `budgets/models.py`, `budgets/signals.py` y el template `presupuesto.html`. Sin esto, cualquier presupuesto con categoría eliminada crashea toda la página con Error 500.

---

---

# 🟡 BATCH 2 — ALTOS

---

## P6 · Modelos financieros — Sin `MinValueValidator`
### Montos negativos y cero permitidos en la base de datos

**Hallazgo:**
Los campos `monto` en `Ingreso`, `Gasto`, `Transferencia`, `DepositoAhorro`, `MetaAhorro.meta` y `Presupuesto.monto_limite` son `DecimalField` sin ningún validador de valor mínimo. La base de datos acepta cero y valores negativos. Un monto negativo en una transferencia invierte la dirección del flujo de dinero y corrompe los balances sin que ninguna señal lo detecte como error.

**Hallazgo adicional:**
`Presupuesto.monto_gastado` puede llegar a negativo si se elimina un gasto que ya fue contabilizado y el campo no tiene restricción inferior.

**Solución:**

1. En cada uno de los campos mencionados, añade `validators=[MinValueValidator(Decimal('0.01'))]`. Importa `MinValueValidator` desde `django.core.validators` y `Decimal` desde `decimal`.
2. Para `Presupuesto.monto_gastado` usa `MinValueValidator(Decimal('0'))` en lugar de `0.01`, porque puede ser cero legítimamente cuando no hay gastos del mes.
3. Los validadores no generan cambios en el esquema SQL pero sí se registran en las migraciones. Corre `makemigrations` para que el admin y los formularios los hereden automáticamente.

---

## P7 · `apps/core/views.py` — Dashboard con 24+ queries redundantes
### Loop de 6 meses ejecutado dos veces, N+1 en transacciones recientes

**Hallazgo 1 — Loop de 6 meses duplicado:**
El bloque de `seis_meses` ejecuta 2 queries por mes (una de ingresos, una de gastos) dentro de un `for`. Son 12 queries. Luego el bloque de `savings_rows` repite exactamente el mismo loop con otras 12 queries. Total: 24 queries SQL para datos que podrían obtenerse en 2. `TruncMonth` está importado al tope del archivo pero no se usa en ningún lado.

**Hallazgo 2 — N+1 en transacciones recientes:**
El bloque que construye `movs` itera sobre ingresos y gastos accediendo a `ing.categoria.icono.clase_css` y `ing.categoria.color.hex`. Las queries de ingresos y gastos recientes no tienen ningún `select_related`. Cada acceso a `.categoria`, `.icono` y `.color` dispara una query individual por registro. Con 20 registros y 2 relaciones cada uno, son hasta 40 queries adicionales por visita al dashboard.

**Hallazgo 3 — `fa_random()` con import interno:**
La función tiene `import random` dentro de su cuerpo. El import se ejecuta en cada llamada. Menor pero incorrecto.

**Solución:**

1. Reemplaza ambos loops de 6 meses por una sola query con `TruncMonth` y `annotate(Sum('monto'))` agrupando por mes, fuera de cualquier loop. Construye un diccionario `{(año, mes): total}` y luego itera sobre `seis_meses` consultando ese diccionario en memoria. Haz esto una vez para ingresos y una vez para gastos: 2 queries en total.
2. En las queries de ingresos y gastos recientes agrega `select_related('categoria', 'categoria__icono', 'categoria__color')` desde cero — actualmente no existe ninguno.
3. Mueve `import random` al tope del archivo junto con los demás imports.

---

## P8 · `apps/budgets/views.py` — N+1 en lista de presupuestos

**Hallazgo:**
El `select_related` en `PresupuestoLista.get_queryset()` incluye `categoria` y `categoria__icono` pero no `categoria__color`. En el loop de `presupuestos_json` se accede a `p.categoria.color.hex`, lo que dispara una query adicional por cada presupuesto del mes.

**Solución:**

Añade `categoria__color` al `select_related` existente en `get_queryset()`. Queda como: `select_related('categoria', 'categoria__icono', 'categoria__color')`.

---

## P9 · Modelos — Campos críticos sin `db_index`
### Full table scan en filtros de uso diario

**Hallazgo:**
Los campos usados en los filtros más frecuentes del sistema no tienen índice de base de datos. Con volumen alto, cada query hace un escaneo completo de la tabla.

**Campos prioritarios sin índice:**

| Modelo | Campo | Motivo |
|---|---|---|
| `Ingreso` | `fecha` | Filtro en dashboard, vistas de lista, reportes |
| `Gasto` | `fecha` | Mismo uso que Ingreso |
| `RecurrenciaTransferencia` | `proxima_ejecucion` | Filtro exacto que usa la tarea Celery cada madrugada |
| `RecurrenciaTransferencia` | `activo` | Se combina siempre con proxima_ejecucion |
| `Cuenta` | `activo` | Filtrado en casi todas las queries del sistema |
| `MetaAhorro` | `activo` | Mismo patrón que Cuenta |
| `Presupuesto` | `activo` | Mismo patrón |

**Nota:** `MetaAhorro.slug` ya tiene índice implícito por `unique_together`. `Presupuesto.mes` y `año` también tienen índice compuesto implícito. No requieren `db_index=True` adicional.

**Solución:**

Añade `db_index=True` a cada uno de los campos listados en sus respectivos modelos. Después de todos los cambios, un solo `makemigrations` y `migrate`.

---

## P10 · `apps/transfers/tasks.py` — Sin reintentos controlados

**Hallazgo:**
El archivo de producción aún está en el estado ANTES del Batch 1. No tiene `transaction.atomic()`, `select_for_update()` ni `ignore_result=True`.

**Solución:**

Aplicar primero los cambios del Batch 1 (C1+C2). Respecto a reintentos específicamente: no apliques `self.retry()` en esta tarea. Es una tarea financiera. Un reintento automático después de un fallo parcial puede duplicar transferencias. El manejo de fallo debe ser `logger.critical` con alerta manual, no reintento automático de Celery.

---

## P11 · `config/settings/base.py` — Backend Redis compartido con broker, sin expiración de resultados

**Hallazgo:**
`CELERY_BROKER_URL` y `CELERY_RESULT_BACKEND` apuntan ambos a `redis://localhost:6379/0`. Comparten la misma base de datos Redis. Si en el futuro se agrega caché de Django, sesiones o Django Channels sobre Redis, todos compiten en el mismo espacio de claves y pueden colisionarse.

No existe `CELERY_RESULT_EXPIRES`. Cada ejecución de tarea que no tenga `ignore_result=True` acumula una entrada en Redis indefinidamente, consumiendo RAM del VPS sin límite.

**Solución:**

1. Cambia `CELERY_RESULT_BACKEND` a `redis://localhost:6379/1` en `base.py`. Redis crea la base `/1` automáticamente al primer uso; no requiere comando explícito de creación.
2. Añade `CELERY_RESULT_EXPIRES = 1800` en `base.py`. 30 minutos es suficiente para depuración en caliente.
3. Las tareas con `ignore_result=True` no escriben en el backend, así que el expires solo aplica a las que sí persisten resultado.

**Paso de deploy obligatorio:** Después de editar `base.py` y reiniciar Gunicorn, debes reiniciar también los workers de Celery y el proceso de Celery Beat. Si los workers siguen corriendo con la configuración anterior en memoria, continuarán apuntando a `/0` hasta que se reinicien. El orden correcto es: editar `base.py` → reiniciar Gunicorn → reiniciar Celery workers → reiniciar Celery Beat.

---

---

# 🟢 BATCH 3 — MEDIOS

---

## P12 · `apps/transactions/views.py` — N+1 masivo en IngresoLista y GastoLista
### Una query por categoría dentro de un loop

**Hallazgo:**
En ambas vistas, el bloque de estadísticas por categoría itera sobre todas las categorías del inquilino y ejecuta una query de `aggregate(Sum)` y otra de `.count()` por cada una. Con 15 categorías son 30 queries. Luego el bloque de distribución (`cats_dist`) repite el mismo patrón con otras 15 queries. Total: hasta 90 queries SQL solo en el contexto de la vista de lista, sin contar la paginación.

**Hallazgo adicional:**
En `GastoLista` hay un valor hardcodeado `context['budget_limit'] = 20000` que no tiene relación con los presupuestos reales del inquilino.

**Solución:**

1. Reemplaza ambos loops de categorías por una sola query con `.values('categoria_id').annotate(total=Sum('monto'), count=Count('id'))`. Construye un diccionario `{categoria_id: {total, count}}` y asigna los valores iterando sobre `cats` en memoria. Son 2 queries en total en lugar de 30+.
2. Elimina `budget_limit = 20000` o cámbialo por una query real a `Presupuesto.objects.filter(inquilino=inquilino, mes=hoy.month, año=hoy.year).aggregate(Sum('monto_limite'))`.

---

## P13 · `apps/notifications/views.py` — `eliminar_suscripcion` expone error interno

**Hallazgo:**
El uso de `json.loads(request.body)` directo es aceptable en este contexto (API JSON pura, protegida con `@login_required` y `@csrf_protect`). El problema real es distinto: en `eliminar_suscripcion`, si el cliente no envía el campo `endpoint`, la variable queda como `None` y `_hash_endpoint(None)` lanza `AttributeError` al llamar `.encode()` sobre `None`. El `except Exception` lo captura y devuelve `{'error': str(e)}` con status 500, exponiendo el mensaje de la excepción interna al cliente.

**Solución:**

Añade validación de que `endpoint` no sea `None` en `eliminar_suscripcion` antes de llamar a `_hash_endpoint`, igual que lo haces en `guardar_suscripcion`. Si falta, retorna `JsonResponse({'error': 'Datos incompletos'}, status=400)`.

---

## P14–P15 · Logs y señales

Cubiertos en Batch 1. Las señales ya tienen `logger.info()` en el código DESPUÉS. No hay hallazgos adicionales en el código visible.

---

## P16 · `bulk_create` en recurrencias

Cubierto en C1+C2 con la advertencia sobre señales. Ver Batch 1.

---

## P17 · `apps/transactions/views.py` — `TransaccionLista` pagina en memoria
### ⚠️ Elevar a ALTO si hay usuarios con más de 1 año de historial

**Hallazgo:**
`_build_movimientos` mezcla tres modelos distintos (`Ingreso`, `Gasto`, `Transferencia`) en una lista Python, los ordena en memoria con `.sort()` y luego los pagina con `Paginator`. El problema no es solo el caso sin filtros: si un usuario filtra por un rango de fechas que devuelve 5,000 registros, la página sigue cargando todos en RAM antes de mostrar la primera. La paginación de Django opera sobre la lista ya construida, no sobre la base de datos. Con múltiples usuarios simultáneos en ese escenario, el VPS puede quedarse sin memoria.

**Causa raíz:**
La mezcla de tres modelos en una sola vista ordenada por fecha no tiene solución directa con el ORM de Django. No existe un queryset que una `Ingreso`, `Gasto` y `Transferencia` en una sola query SQL ordenada.

**Soluciones por nivel de inversión:**

- **Mitigación inmediata (bajo costo):** Añadir un filtro de rango de fechas por defecto de 90 días en `_build_movimientos` cuando el usuario no especifica ninguno. Reduce el volumen habitual pero no elimina el problema si el usuario aplica un rango amplio manualmente.

- **Solución estructural (costo medio):** Crear un modelo `Movimiento` que registre todos los eventos en una sola tabla con un campo `tipo` (`ingreso`, `gasto`, `transferencia`) y una FK al registro original. Las señales `post_save` y `post_delete` existentes mantienen esta tabla sincronizada. `TransaccionLista` pasa a hacer una sola query paginada en BD sobre `Movimiento`.

- **Solución SQL directa (costo medio-alto):** Reemplazar `_build_movimientos` por una query raw con `UNION ALL` sobre las tres tablas, ordenada y paginada en el motor de base de datos. Requiere SQL manual pero no cambia el esquema.

**Recomendación:** Si hay inquilinos con más de 12 meses de historial activo, elevar la prioridad a ALTO y planificar la solución estructural. La mitigación de 90 días es un parche, no una solución.

---

---

# 🔵 BATCH 4 — BAJOS

---

## P18 · `apps/accounts/forms.py` — `except:` sin tipo de excepción

**Hallazgo:**
En `clean_balance` hay un bloque `except:` vacío sin especificar el tipo de excepción. Esto captura hasta `KeyboardInterrupt` y `SystemExit`, lo que puede enmascarar errores de sistema críticos y dificultar el diagnóstico en producción.

**Solución:**

Cambia `except:` por `except (ValueError, decimal.InvalidOperation):`. Importa `InvalidOperation` desde `decimal` al tope del archivo.

---

## P19 · Vistas de eliminación — Sin manejo de `ProtectedError`

**Hallazgo:**
Los cambios de `CASCADE` a `PROTECT` del Batch 1 harán que Django lance `django.db.models.ProtectedError` cuando un usuario intente eliminar una `Cuenta` o `MetaAhorro` con registros asociados. Ninguna de estas vistas captura esa excepción actualmente. El resultado es un Error 500 sin mensaje amigable.

**Vistas que requieren manejo de `ProtectedError`:**
- `CuentaEliminar` — porque `Ingreso.cuenta`, `Gasto.cuenta`, `Transferencia.origen` y `Transferencia.destino` tendrán `PROTECT`
- `MetaAhorroEliminar` — porque `DepositoAhorro.meta` tendrá `PROTECT`

**Vistas que NO necesitan manejo:**
- `CategoriaEliminar` — todas las FKs hacia `Categoria` son `SET_NULL` (`Ingreso.categoria`, `Gasto.categoria`) o se cambiarán a `SET_NULL` (`Presupuesto.categoria` en C5). Django nunca lanzará `ProtectedError` al eliminar una categoría.

**Solución:**

En `CuentaEliminar` y `MetaAhorroEliminar`, sobrescribe `form_valid` para capturar `django.db.models.ProtectedError` y retornar una respuesta con mensaje explicativo. Para vistas HTMX, retorna un header `HX-Trigger` con un mensaje de error que el frontend pueda mostrar en un toast.

---

## P20 · Logging — No configurado en settings

**Hallazgo:**
No existe ninguna configuración `LOGGING` en `base.py`, `prod.py` ni `dev.py`. Todos los `logger.info()` y `logger.error()` añadidos en las señales y tareas escriben al void en producción. Los errores críticos de balance no quedan registrados en ningún archivo.

**Solución:**

Añade una configuración `LOGGING` en `base.py` con al menos un handler de consola para desarrollo. En `prod.py`, añade un handler de archivo que escriba a `/var/log/finanplanen/app.log` o similar, con nivel `WARNING` o superior para no saturar el disco. El logger `django` y los loggers de tus apps (`apps.transfers`, `apps.transactions`, `apps.savings`, `apps.notifications`) deben estar declarados explícitamente.

---

## P21 · `config/settings/prod.py` — Faltan directivas de seguridad HTTP

**Hallazgo:**
`prod.py` tiene `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` y `SECURE_SSL_REDIRECT` correctamente configurados. Faltan `SECURE_HSTS_SECONDS` y `X_FRAME_OPTIONS`.

**Solución:**

Añade en `prod.py`:
- `SECURE_HSTS_SECONDS = 31536000` — fuerza HTTPS en el navegador durante 1 año
- `X_FRAME_OPTIONS = 'DENY'` — previene que la app se cargue en iframes externos (clickjacking)

---

## P22 · `config/settings/dev.py` — `ALLOWED_HOSTS = ['*']` sin restricción

**Hallazgo:**
`ALLOWED_HOSTS = ['*']` en `dev.py` es aceptable en desarrollo. El riesgo es que `prod.py` hereda de `base.py` que no define `ALLOWED_HOSTS`. Si por error se usa `base.py` directamente en el servidor (sin cargar `prod.py`), el host queda abierto al wildcard.

**Solución:**

Define `ALLOWED_HOSTS` como variable requerida en `prod.py` sin valor por defecto: `ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')`. Sin el valor en el `.env` de producción, Django fallará explícitamente al arrancar en lugar de quedar abierto.

---

## P23 · Accesos sin verificar a `categoria` tras `SET_NULL` — ⚠️ Elevado a ALTO
### El problema está en Python y en templates, no solo en templates

**Hallazgo:**
Con el cambio de `Presupuesto.categoria` a `SET_NULL`, cualquier `Presupuesto` cuya categoría haya sido eliminada tendrá `categoria=None`. Los accesos a atributos de `categoria` sin verificar nulidad crashean toda la página de presupuestos con `AttributeError` — no un registro individual, toda la página.

Los puntos de fallo están en tres capas, no solo en templates:

**`apps/budgets/views.py`:**
- Línea 74: `'nombre': p.categoria.nombre` — crash si `categoria` es `None`
- Línea 77: `p.categoria.icono_id` — crash si `categoria` es `None`
- Línea 78: `p.categoria.color_id` — crash si `categoria` es `None`

**`apps/budgets/models.py`:**
- Método `__str__`: `self.categoria.nombre` — crash en cualquier representación del objeto si `categoria` es `None`

**`templates/budgets/presupuesto.html`:**
- Líneas 341-348: accesos a `p.categoria.color.hex` y `p.categoria.nombre` sin verificar `None`

**`apps/budgets/signals.py` — hallazgo adicional:**
Si existe una función `actualizar_monto_gastado` que filtra presupuestos por `categoria`, al eliminar una categoría la FK queda en `None`. La señal busca `Presupuesto.objects.filter(categoria=None)` y no encuentra el presupuesto correcto. El `monto_gastado` deja de actualizarse silenciosamente — sin error, sin log, solo datos incorrectos.

**Solución por archivo:**

- **`budgets/views.py`:** En el loop de `presupuestos_json`, reemplaza cada acceso directo por una verificación de `p.categoria_id` antes de acceder. Si es `None`, usa valores por defecto (`'Sin categoría'`, icono genérico, color por defecto).
- **`budgets/models.py`:** En `__str__`, protege con `self.categoria.nombre if self.categoria_id else 'Sin categoría'`.
- **`templates/budgets/presupuesto.html`:** Envuelve cada acceso con `{% if p.categoria %}` antes de acceder a sus atributos.
- **`budgets/signals.py`:** En `actualizar_monto_gastado`, añade una guarda al inicio: si `categoria` es `None`, salir de la función sin hacer nada y emitir `logger.warning` para que el monto desactualizado sea detectable en logs.

---

## P24 · `MAINTENANCE_MODE` en `.env`

**Hallazgo:**
`MAINTENANCE_MODE` tiene `default=False` en el código. Si el `.env` de producción tiene `MAINTENANCE_MODE=True` de una ventana anterior de mantenimiento y no se desactiva, el sistema queda en modo mantenimiento indefinidamente sin error visible.

**Solución:**

Documenta en el runbook de despliegue que `MAINTENANCE_MODE=False` debe verificarse explícitamente en el `.env` de producción antes de cada arranque. Considera añadir un check de salud en el startup que loguee el valor actual de `MAINTENANCE_MODE` al arrancar Gunicorn.

---

## P25 · `budget_limit` hardcodeado en `GastoLista`

**Hallazgo:**
`context['budget_limit'] = 20000` en `GastoLista.get_context_data()` es un valor fijo sin relación con los presupuestos reales del inquilino. Si se muestra al usuario como límite de referencia, es incorrecto para cualquier inquilino cuyo límite real sea diferente.

**Solución:**

Reemplaza el valor fijo por una query a `Presupuesto` que sume `monto_limite` del mes actual del inquilino. Si no hay presupuestos definidos, omite el campo del contexto o devuelve `None` y maneja la ausencia en el template.

---

---

## Resumen de Hallazgos Adicionales (No estaban en la auditoría original)

| Hallazgo | Archivo | Severidad |
|---|---|---|
| Dashboard ejecuta 24 queries duplicadas por el loop de 6 meses repetido dos veces | `apps/core/views.py` | ALTO |
| `TransaccionLista` pagina en memoria, riesgo de OOM con volumen alto | `apps/transactions/views.py` | MEDIO → ALTO si hay usuarios con >1 año de historial |
| `budget_limit = 20000` hardcodeado sin relación con presupuestos reales | `apps/transactions/views.py` | BAJO |
| `fa_random()` tiene `import random` dentro del cuerpo de la función | `apps/core/views.py` | BAJO |
| `eliminar_suscripcion` expone `AttributeError` interno al cliente con status 500 | `apps/notifications/views.py` | MEDIO |

---

## Orden de implementación recomendado

### Batch 1 — Antes de cualquier tráfico de producción

> C5 tiene tres prerequisitos reclasificados: P19 (era BAJO), P23 (era BAJO → ahora ALTO) y el mecanismo de archivado de cuentas. Los tres deben completarse antes de correr la migración de C5.

1. **[P23 — prerequisito de C5, ALTO]** Proteger todos los accesos a `presupuesto.categoria` en `budgets/views.py`, `budgets/models.py`, `templates/budgets/presupuesto.html` y `budgets/signals.py`
2. **[P19 — prerequisito de C5]** Capturar `ProtectedError` en `CuentaEliminar` y `MetaAhorroEliminar` únicamente (`CategoriaEliminar` no aplica)
3. **[C5 — UX prerequisito]** Implementar archivado por `activo=False` en cuentas: filtrar lista por `activo=True`, permitir archivar desde edición, filtrar cuentas activas en formularios de movimientos
4. **[C1+C2]** `select_for_update()` + `transaction.atomic()` en `transfers/tasks.py` — usar **Opción A** (`.create()` individual, conserva señales)
5. **[C3]** `F('balance')` + `transaction.atomic()` en los tres `signals.py`
6. **[C4]** `timeout=10` en `notifications/tasks.py` — eliminar `self.retry()` del loop interno
7. **[C5]** `on_delete=PROTECT` + `SET_NULL` en modelos financieros + migración (solo después de completar pasos 1, 2 y 3)

### Batch 2 — Sprint actual
7. `MinValueValidator` en todos los campos de monto
8. `select_related` anidado en dashboard y presupuestos
9. Loop de 6 meses reemplazado por `TruncMonth` + `annotate`
10. `db_index=True` en campos de filtro críticos
11. Separar broker y backend en Redis `/0` y `/1` → reiniciar workers y Beat después de deployar

### Batch 3 — Antes de siguiente versión
12. Reemplazar loops de categorías por `annotate` en `IngresoLista` y `GastoLista`
13. Validar `endpoint` en `eliminar_suscripcion`
14. Añadir filtro de fechas por defecto en `TransaccionLista`

### Batch 4 — Mantenimiento
15. Configurar `LOGGING` en settings
16. Añadir `SECURE_HSTS_SECONDS` y `X_FRAME_OPTIONS` en `prod.py`
17. Hacer `ALLOWED_HOSTS` requerido sin default en `prod.py`
18. Cambiar `except:` por tipo específico en `accounts/forms.py`
19. Eliminar o conectar `budget_limit` a datos reales
20. Mover `import random` al tope del archivo en `core/views.py`