# Reporte de Auditoría Técnica y Seguridad: Estado de la Aplicación

Este documento recopila de manera estructurada los puntos de revisión del código fuente (Django, Celery y ORM) para clasificar vulnerabilidades, riesgos de concurrencia, problemas de rendimiento y fallas de configuración antes del paso a producción.

---

## 1. Capa de Datos y Persistencia (`models.py`, ORM & SQL)

Revisión de la integridad referencial, consistencia transaccional y rendimiento de las consultas a la base de datos.

- [ ] **Validación de Datos Críticos en el Backend:**
  - *Foco:* Modelos financieros o de balances (`Transferencia`, `Cuenta`).
  - *Riesgo:* Confianza ciega en parámetros de entrada que pueden alterar la lógica contable (ej. montos negativos o en cero).
  - *Criterio:* Forzar validaciones en el método `clean()` del modelo o aplicar `MinValueValidator(0.01)` a nivel de campo.
- [ ] **Restricciones de Integridad Única (Race Conditions a Nivel SQL):**
  - *Foco:* Evitar inserciones duplicadas concurrentes.
  - *Riesgo:* Validaciones de unicidad ejecutadas únicamente en vistas o formularios fallan si dos peticiones idénticas entran al mismo milisegundo.
  - *Criterio:* Implementar restricciones nativas en el `Meta` del modelo usando `UniqueConstraint` o `unique_together`.
- [ ] **Políticas de Borrado Inseguras (`models.CASCADE`):**
  - *Foco:* Claves foráneas (`ForeignKey`) en modelos de historial, auditoría o transacciones.
  - *Riesgo:* Eliminación involuntaria de registros financieros históricos si se elimina una entidad padre (ej. un usuario o una cuenta).
  - *Criterio:* Reemplazar destructores en cascada por `models.PROTECT` o `models.SET_NULL` (si el campo permite nulos) para blindar la contabilidad.
- [ ] **Problema del N+1 en Consultas del ORM:**
  - *Foco:* Iteraciones de consultas que acceden a relaciones directas o inversas.
  - *Riesgo:* Degradación del rendimiento del VPS al ejecutar cientos de queries SQL individuales dentro de bucles.
  - *Criterio:* Uso estricto y explícito de `select_related()` para claves foráneas y `prefetch_related()` para relaciones muchos a muchos.
- [ ] **Uso Eficiente de Índices:**
  - *Foco:* Campos clave utilizados de manera recurrente en sentencias `.filter()`, `.exclude()` o `.order_by()`.
  - *Riesgo:* Consultas lentas (Table Scans completos) a medida que crece el volumen de filas.
  - *Criterio:* Declarar `db_index=True` en campos críticos de búsqueda (ej. estados de activación, fechas de ejecución, llaves foráneas).
- [ ] **Optimización del Consumo de RAM en Queries Masivas:**
  - *Foco:* Carga de colecciones grandes de objetos en memoria.
  - *Riesgo:* Desbordamiento de memoria RAM en el servidor por arrastrar campos pesados que no se van a procesar.
  - *Criterio:* Restringir campos usando `.only()` / `.defer()`, o migrar a `.values()` / `.values_list()` cuando no se requieran instancias vivas del modelo.
- [ ] **Uso de Consultas SQL Raw:**
  - *Foco:* Implementaciones directas con `.raw()` o `connection.cursor().execute()`.
  - *Riesgo:* Inyección de código SQL (SQLi) si se concatenan cadenas dinámicas.
  - *Criterio:* Prohibir el formateo de cadenas (`f-strings` o `%`). Los parámetros externos deben pasarse obligatoriamente como argumentos de la query.

---

## 2. Lógica de Negocio y Concurrencia Asíncrona (`tasks.py` & `signals.py`)

Revisión del entorno asíncrono para garantizar la idempotencia de las tareas y el comportamiento predecible del sistema.

- [ ] **Idempotencia y Bloqueos de Concurrencia:**
  - *Foco:* Tareas recurrentes de cobros, transferencias o procesamiento de datos sensibles.
  - *Riesgo:* Ejecución duplicada de la misma tarea por reintentos automáticos del Broker (Redis) o ejecuciones simultáneas de workers.
  - *Criterio:* Bloquear filas usando `.select_for_update(nowait=True)` dentro de una transacción atómica o implementar *locks* distribuidos mediante Redis.
- [ ] **Garantía de Atomicidad (Rollbacks):**
  - *Foco:* Operaciones lógicas que involucran múltiples escrituras o modificaciones en bloque.
  - *Riesgo:* Fallas a mitad de un bucle que dejan la base de datos en un estado inconsistente (ej. mitad de registros procesados y mitad no).
  - *Criterio:* Envolver el flujo completo bajo el contexto de `with transaction.atomic()`.
- [ ] **Uso de Operaciones Masivas (`Bulk Operations`):**
  - *Foco:* Creación o actualización de múltiples registros en background.
  - *Riesgo:* Cuello de botella en el motor de base de datos por ejecutar operaciones de guardado individuales (`.save()`) dentro de un bucle `for`.
  - *Criterio:* Agrupar las instancias en memoria y ejecutar `bulk_create()` o `bulk_update()`.
- [ ] **Serialización y Paso de Parámetros en Celery:**
  - *Foco:* Argumentos enviados a través de llamadas `.delay()` o `.apply_async()`.
  - *Riesgo:* Corrupción o desfase de datos al serializar instancias completas de modelos Django.
  - *Criterio:* Pasar únicamente tipos de datos primitivos (ej. el ID numérico o UUID) y volver a consultar el objeto fresco desde la base de datos dentro de la tarea.
- [ ] **Políticas de Control de Resultados (`ignore_result`):**
  - *Foco:* Tareas recurrentes de alta frecuencia que no devuelven datos funcionales.
  - *Riesgo:* Saturación de la memoria RAM del backend (Redis) por almacenamiento innecesario del estado de éxito de las tareas.
  - *Criterio:* Forzar `@shared_task(ignore_result=True)` y configurar un tiempo de vida restrictivo con `CELERY_RESULT_EXPIRES`.
- [ ] **Manejo Explicito de Reintentos en I/O Bound:**
  - *Foco:* Tareas dependientes de servicios de terceros (APIs externas, pasarelas de pago, Web Push).
  - *Riesgo:* Pérdida total de la ejecución ante caídas intermitentes de red si no hay una estrategia de reintentos.
  - *Criterio:* Configurar el decorador con `bind=True`, definir `max_retries` y controlar el flujo con `self.retry(countdown=...)`.
- [ ] **Límites de Tiempo Activos (Timeouts):**
  - *Foco:* Peticiones HTTP externas síncronas ejecutadas por los workers.
  - *Riesgo:* Bloqueo indefinido del worker de Celery si el servidor externo deja la conexión abierta.
  - *Criterio:* Declarar obligatoriamente un parámetro `timeout` en cada petición realizada (ej. `requests.get(url, timeout=5)`).
- [ ] **Efectos Secundarios Ocultos en Señales (Signals):**
  - *Foco:* Desencadenadores síncronos de tipo `post_save` o `pre_save`.
  - *Riesgo:* Ralentización de la experiencia del usuario en el hilo principal por ejecutar tareas pesadas en señales. Fallas de consistencia debido a que las operaciones `bulk` no disparan señales.
  - *Criterio:* Desacoplar procesos pesados de las señales moviéndolos a tareas de Celery o inyectándolos explícitamente en el flujo de los servicios.

---

## 3. Capa de API y Presentación (`views.py` / `api.py`)

Revisión de los puntos de entrada expuestos al cliente para mitigar vulnerabilidades de control de acceso e inyecciones.

- [ ] **Verificación de Propiedad del Recurso (Mitigación de BOLA / ID Hunting):**
  - *Foco:* Endpoints de actualización, lectura o borrado que reciben identificadores (IDs / UUIDs).
  - *Riesgo:* Un usuario autenticado manipula los IDs de las peticiones para alterar o consultar recursos de otros inquilinos o usuarios.
  - *Criterio:* Filtrar las consultas ORM asegurando la relación de pertenencia. Ej: `Modelo.objects.filter(id=id, usuario=request.user)`. Evitar consultas genéricas basadas solo en la clave primaria.
- [ ] **Seguridad en la Deserialización de Payloads:**
  - *Foco:* Procesamiento de datos crudos en formato JSON recibidos en peticiones POST/PUT.
  - *Riesgo:* Evasión de reglas de negocio o inyección de tipos de datos incorrectos si se procesa el cuerpo usando únicamente `json.loads(request.body)`.
  - *Criterio:* Canalizar de manera obligatoria la validación de payloads a través de Formularios de Django o Serializadores de Django REST Framework (DRF).

---

## 4. Configuración Global y Entorno (`settings.py`)

Validación de las variables de entorno, seguridad de las sesiones y transporte seguro de datos.

- [ ] **Estado del Modo Depuración:**
  - *Riesgo:* Exposición de trazas de código, variables internas y estructura de base de datos ante errores en producción.
  - *Criterio:* Asegurar estrictamente que `DEBUG = False`.
- [ ] **Aislamiento de Secretos:**
  - *Riesgo:* Filtración de credenciales críticas si se escriben directamente en el repositorio de código.
  - *Criterio:* Extraer llaves, contraseñas y tokens (`SECRET_KEY`, credenciales de BD, llaves VAPID) a variables de entorno administradas en el VPS.
- [ ] **Restricción de Dominios (`ALLOWED_HOSTS`):**
  - *Riesgo:* Vulnerabilidad a ataques de envenenamiento de cabecera HTTP Host si se mantiene el comodín `['*']`.
  - *Criterio:* Listar explícitamente los dominios o IPs controladas del entorno de producción.
- [ ] **Seguridad en Directivas de Cookies y Transporte:**
  - *Riesgo:* Interceptación de tokens de sesión o suplantación de identidad (CSRF) sobre conexiones HTTP inseguras.
  - *Criterio:* Habilitar las banderas de protección `SECURE_SSL_REDIRECT = True`, `SESSION_COOKIE_SECURE = True`, y `CSRF_COOKIE_SECURE = True`.
- [ ] **Mecanismo Seguro de Serialización en Celery:**
  - *Riesgo:* Vulnerabilidades de Ejecución de Código Remoto (RCE) si el broker acepta formatos permisivos.
  - *Criterio:* Forzar los parámetros `CELERY_ACCEPT_CONTENT`, `CELERY_TASK_SERIALIZER` y `CELERY_RESULT_SERIALIZER` estrictamente al valor `['json']`. Prohibir el uso de `pickle`.

---

## 5. Observabilidad, Excepciones y Trazabilidad (Logs)

Auditoría de los mecanismos de registro de eventos y gestión de fallas del sistema.

- [ ] **Captura y Control de Excepciones Silenciosas:**
  - *Foco:* Bloques de código propensos a fallas operativas.
  - *Riesgo:* Uso de patrones ciegos como `except: pass` que ocultan errores de ejecución e impiden su diagnóstico.
  - *Criterio:* Registrar toda excepción no esperada usando `logger.error()` o `logger.critical()` pasando el parámetro `exc_info=True` para guardar la traza completa del error.
- [ ] **Fuga de Información Confidencial en Logs:**
  - *Foco:* Datos impresos en los archivos de salida del servidor.
  - *Riesgo:* Exposición de llaves privadas, payloads de notificaciones, secretos o tokens confidenciales en texto plano dentro del VPS.
  - *Criterio:* Sanitizar los diccionarios o mensajes antes de enviarlos al objeto `logger`.
- [ ] **Trazabilidad de Movimientos Contables:**
  - *Foco:* Registros de auditoría forense para el módulo de transferencias y cuentas.
  - *Criterio:* Emitir de manera obligatoria logs estructurados e invariables cada vez que ocurra un movimiento de saldos o ejecuciones de recurrencias.

---

## Matriz de Prioridad para Hallazgos

Aplica esta escala para evaluar la gravedad de cada vulnerabilidad o defecto detectado durante la revisión del código:

| Nivel de Riesgo | Impacto Operativo / Seguridad | Acción Requerida |
| :--- | :--- | :--- |
| **CRÍTICO** | Pérdida latente de dinero, duplicidad de cobros reales, vulnerabilidad RCE activa, omisión de control de acceso (BOLA), fuga de llaves privadas. | Bloquear despliegues de inmediato hasta aplicar el hotfix. |
| **ALTO** | Bloqueo o congelamiento de workers de Celery, desbordamiento de memoria RAM en el VPS, consultas N+1 en flujos críticos del negocio. | Asignar prioridad alta para resolver en el sprint en desarrollo. |
| **MEDIO** | Filtrado ineficiente de colecciones en memoria Python en lugar de SQL, ausencia de logs de auditoría, falta de timeouts en llamadas externas. | Corregir antes de la siguiente ventana de liberación de versión. |
| **BAJO** | Estructura interna de archivos confusa, inconsistencias menores en nombres de tareas, optimizaciones micro-operativas. | Refactorizar según disponibilidad en ventanas de mantenimiento. |