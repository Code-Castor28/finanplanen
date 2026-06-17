# FinanPlanen — Arquitectura

## Resumen del Proyecto

Aplicación web de gestión financiera personal construida con Django 4 + HTMX. Los usuarios gestionan cuentas, transacciones, presupuestos, metas de ahorro y transferencias mediante una interfaz renderizada del lado del servidor tipo SPA.

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Django 4.x (Python 3.11+) |
| Frontend | Django Templates + HTMX (sin framework JS) |
| Base de datos | MySQL 8.x (todos los entornos) |
| Cola de tareas | Celery + Redis (recordatorios email + push) |
| Notificaciones push | pywebpush + VAPID + Service Worker |
| Servidor WSGI | Gunicorn |
| Proxy inverso | Nginx |
| CSS | CSS puro |
| Gráficos | Chart.js (vía CDN) |

## Estructura del Proyecto

```
finanplanen/
├── apps/
│   ├── accounts/           # CRUD cuentas bancarias
│   ├── budgets/            # Presupuestos mensuales por categoría
│   ├── categories/         # Categorías + Etiquetas
│   ├── core/               # Inicio, dashboard, utilidades compartidas
│   ├── notifications/      # Suscripciones push, PWA, tarea Celery recordatorios
│   ├── savings/            # Metas de ahorro + depósitos
│   ├── theme/              # Registro de colores e iconos, variables CSS
│   ├── transactions/       # CRUD transacciones (ingresos/gastos/tarjeta)
│   ├── transfers/          # Transferencias entre cuentas + recurrentes
│   └── users/              # Registro, inicio sesión, perfil
├── config/
│   ├── settings/           # base.py, dev.py, prod.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── static/
│   ├── css/
│   ├── js/
│   └── img/
├── templates/
│   ├── base.html           # Layout maestro (sidebar, navbar, colores, estructura)
│   └── sw.js               # Service Worker (notificaciones push PWA)
├── media/                  # Archivos subidos (avatares, comprobantes)
├── requirements.txt        # Dependencias (Django, django-environ, etc.)
├── manage.py
├── ARCHITECTURE.md
└── AGENTS.md
```

## Modelo de Datos (14 Modelos)

### 1. Inquilino (Tenant)
| Campo | Tipo | Notas |
|---|---|---|
| id | AutoField | PK |
| nombre | CharField(100) | |
| slug | SlugField | Unique |
| activo | BooleanField | Default True |
| creado | DateTimeField | auto_now_add |
| actualizado | DateTimeField | auto_now |

### 2. Usuario (Django AbstractUser)
| Campo | Tipo | Notas |
|---|---|---|
| id | AutoField | PK |
| inquilino | ForeignKey(Inquilino) | CASCADE, auto-creado al registrarse |
| nombre_usuario | CharField(150) | Unique |
| correo | EmailField | Unique |
| contraseña | CharField | Hasheada |
| nombre | CharField(30) | |
| apellido | CharField(150) | |
| telefono | CharField(15) | Nullable |
| avatar | ImageField | Nullable |
| ingreso_mensual | DecimalField(12,2) | Default 0 |
| creado | DateTimeField | auto_now_add |
| actualizado | DateTimeField | auto_now |

### 3. Cuenta
| Campo | Tipo | Notas |
|---|---|---|
| id | AutoField | PK |
| inquilino | ForeignKey(Inquilino) | CASCADE, auto-set desde usuario.inquilino |
| usuario | ForeignKey(Usuario) | CASCADE |
| nombre | CharField(100) | |
| tipo | CharField(2) | Choices: DE (débito), CR (crédito), EF (efectivo), IN (inversión), EM (emergencia) |
| saldo | DecimalField(12,2) | |
| limite_credito | DecimalField(12,2) | Nullable, solo CR |
| fecha_corte | IntegerField(1-31) | Nullable, solo CR |
| fecha_pago | IntegerField(1-31) | Nullable, solo CR |
| icono | ForeignKey(Icono) | Icono registrado en tema |
| color | ForeignKey(Color) | Color registrado en tema |
| activa | BooleanField | Default True |
| creado | DateTimeField | auto_now_add |
| actualizado | DateTimeField | auto_now |

### 4. Categoria
| Campo | Tipo | Notas |
|---|---|---|
| id | AutoField | PK |
| inquilino | ForeignKey(Inquilino) | CASCADE, auto-set desde usuario.inquilino |
| usuario | ForeignKey(Usuario) | CASCADE |
| nombre | CharField(100) | |
| tipo | CharField(1) | IN = ingreso, EX = gasto |
| icono | ForeignKey(Icono) | Icono registrado en tema |
| color | ForeignKey(Color) | Color registrado en tema |
| activa | BooleanField | Default True |
| creado | DateTimeField | auto_now_add |
| actualizado | DateTimeField | auto_now |

### 5. Etiqueta (sub-items de categorías)
| Campo | Tipo | Notas |
|---|---|---|
| id | AutoField | PK |
| inquilino | ForeignKey(Inquilino) | CASCADE, auto-set desde usuario.inquilino |
| usuario | ForeignKey(Usuario) | CASCADE |
| nombre | CharField(100) | |
| categorias | ManyToManyField(Categoria) | Una etiqueta puede pertenecer a varias categorías |
| color | ForeignKey(Color) | Color registrado en tema |
| activa | BooleanField | Default True |
| creado | DateTimeField | auto_now_add |

### 6. Transaccion
| Campo | Tipo | Notas |
|---|---|---|
| id | AutoField | PK |
| inquilino | ForeignKey(Inquilino) | CASCADE, auto-set desde usuario.inquilino |
| usuario | ForeignKey(Usuario) | CASCADE |
| cuenta | ForeignKey(Cuenta) | CASCADE |
| categoria | ForeignKey(Categoria) | SET_NULL, nullable |
| etiquetas | ManyToManyField(Etiqueta) | |
| tipo | CharField(3) | IN = ingreso, EX = gasto, CP = pago tarjeta |
| monto | DecimalField(12,2) | Siempre positivo |
| descripcion | CharField(255) | |
| fecha | DateField | |
| pagado | BooleanField | True = completado, False = pendiente (tarjeta crédito) |
| comprobante | ImageField | Nullable |
| es_recurrente | BooleanField | Default False |
| creado | DateTimeField | auto_now_add |
| actualizado | DateTimeField | auto_now |
| **Índices** | | inquilino + fecha DESC, cuenta + fecha, categoria + fecha |

### 7. Transferencia
| Campo | Tipo | Notas |
|---|---|---|
| id | AutoField | PK |
| inquilino | ForeignKey(Inquilino) | CASCADE, auto-set desde usuario.inquilino |
| usuario | ForeignKey(Usuario) | CASCADE |
| cuenta_origen | ForeignKey(Cuenta) | Related name: transferencias_salientes |
| cuenta_destino | ForeignKey(Cuenta) | Related name: transferencias_entrantes |
| monto | DecimalField(12,2) | |
| descripcion | CharField(255) | |
| fecha | DateField | |
| creado | DateTimeField | auto_now_add |

### 8. TransferenciaRecurrente
| Campo | Tipo | Notas |
|---|---|---|
| id | AutoField | PK |
| inquilino | ForeignKey(Inquilino) | CASCADE, auto-set desde usuario.inquilino |
| usuario | ForeignKey(Usuario) | CASCADE |
| cuenta_origen | ForeignKey(Cuenta) | |
| cuenta_destino | ForeignKey(Cuenta) | |
| monto | DecimalField(12,2) | |
| descripcion | CharField(255) | |
| frecuencia | CharField(10) | diario, semanal, quincenal, mensual, anual |
| proxima_fecha | DateField | |
| activa | BooleanField | Default True |
| creado | DateTimeField | auto_now_add |

### 9. MetaAhorro
| Campo | Tipo | Notas |
|---|---|---|
| id | AutoField | PK |
| inquilino | ForeignKey(Inquilino) | CASCADE, auto-set desde usuario.inquilino |
| usuario | ForeignKey(Usuario) | CASCADE |
| nombre | CharField(100) | |
| meta_monto | DecimalField(12,2) | |
| monto_actual | DecimalField(12,2) | Default 0 |
| fecha_limite | DateField | Nullable |
| icono | ForeignKey(Icono) | Icono registrado en tema |
| color | ForeignKey(Color) | Color registrado en tema |
| activa | BooleanField | Default True |
| creado | DateTimeField | auto_now_add |
| actualizado | DateTimeField | auto_now |

### 10. DepositoAhorro
| Campo | Tipo | Notas |
|---|---|---|
| id | AutoField | PK |
| inquilino | ForeignKey(Inquilino) | CASCADE, auto-set desde usuario.inquilino |
| meta | ForeignKey(MetaAhorro) | CASCADE |
| monto | DecimalField(12,2) | |
| fecha | DateField | |
| nota | CharField(255) | Nullable |
| creado | DateTimeField | auto_now_add |

### 11. Presupuesto
| Campo | Tipo | Notas |
|---|---|---|
| id | AutoField | PK |
| inquilino | ForeignKey(Inquilino) | CASCADE, auto-set desde usuario.inquilino |
| usuario | ForeignKey(Usuario) | CASCADE |
| categoria | ForeignKey(Categoria) | CASCADE |
| mes | DateField | Primer día del mes (YYYY-MM-01) |
| limite_monto | DecimalField(12,2) | |
| monto_gastado | DecimalField(12,2) | Default 0 (desnormalizado, actualizado vía signal) |
| creado | DateTimeField | auto_now_add |
| actualizado | DateTimeField | auto_now |
| **Unique** | | inquilino + categoria + mes |
| **Índice** | | inquilino + mes |

### 12. Color
| Campo | Tipo | Notas |
|---|---|---|
| id | AutoField | PK |
| inquilino | ForeignKey(Inquilino) | CASCADE |
| usuario | ForeignKey(Usuario) | CASCADE |
| nombre | CharField(100) | Ej: "Rojo gastos" |
| slug | SlugField | Usado para variable CSS: `--clr-{slug}` |
| hex | CharField(7) | #RRGGBB |
| activo | BooleanField | Default True |
| creado | DateTimeField | auto_now_add |
| actualizado | DateTimeField | auto_now |
| **Unique** | | inquilino + slug |

### 13. Icono
| Campo | Tipo | Notas |
|---|---|---|
| id | AutoField | PK |
| inquilino | ForeignKey(Inquilino) | CASCADE |
| usuario | ForeignKey(Usuario) | CASCADE |
| nombre | CharField(100) | Ej: "Casa", "Comida" |
| slug | SlugField | |
| clase_css | CharField(100) | Clase CSS para renderizar |
| activo | BooleanField | Default True |
| creado | DateTimeField | auto_now_add |
| actualizado | DateTimeField | auto_now |
| **Unique** | | inquilino + slug |

### 14. SuscripcionPush
| Campo | Tipo | Notas |
|---|---|---|
| id | AutoField | PK |
| usuario | ForeignKey(Usuario) | CASCADE |
| endpoint | TextField | Unique — URL de Google/Apple FCM |
| p256dh | TextField | Llave pública del navegador (cifrado) |
| auth | TextField | Token de autenticación del navegador |
| creado_en | DateTimeField | auto_now_add |
| activo | BooleanField | Default True |

## Relaciones entre Entidades

```
Inquilino (1) ──< Usuario (N)
Inquilino (1) ──< Cuenta (N)
Inquilino (1) ──< Categoria (N)
Inquilino (1) ──< Etiqueta (N)
Inquilino (1) ──< Transaccion (N)
Inquilino (1) ──< Transferencia (N)
Inquilino (1) ──< TransferenciaRecurrente (N)
Inquilino (1) ──< MetaAhorro (N)
Inquilino (1) ──< DepositoAhorro (N)
Inquilino (1) ──< Presupuesto (N)
Inquilino (1) ──< Color (N)
Inquilino (1) ──< Icono (N)
Usuario (1) ──< Cuenta (N)
Usuario (1) ──< Categoria (N)
Usuario (1) ──< Etiqueta (N)
Usuario (1) ──< Color (N)
Usuario (1) ──< Icono (N)
Categoria (M) ──< Etiqueta (N)       [ManyToMany]
Usuario (1) ──< Transaccion (N)
Cuenta (1) ──< Transaccion (N)
Categoria (1) ──< Transaccion (N)    [SET_NULL]
Transaccion (M) ──< Etiqueta (N)     [ManyToMany]
Usuario (1) ──< Transferencia (N)
Cuenta (1) ──< Transferencia (N)     [cuenta_origen]
Cuenta (1) ──< Transferencia (N)     [cuenta_destino]
Usuario (1) ──< TransferenciaRecurrente (N)
Usuario (1) ──< MetaAhorro (N)
MetaAhorro (1) ──< DepositoAhorro (N)
Usuario (1) ──< Presupuesto (N)
Categoria (1) ──< Presupuesto (N)
Color (1) ──< Cuenta (N)             [FK color]
Color (1) ──< Categoria (N)          [FK color]
Color (1) ──< Etiqueta (N)           [FK color]
Color (1) ──< MetaAhorro (N)         [FK color]
Icono (1) ──< Cuenta (N)             [FK icono]
Icono (1) ──< Categoria (N)          [FK icono]
Icono (1) ──< MetaAhorro (N)         [FK icono]
Usuario (1) ──< SuscripcionPush (N)   [FK usuario]
```

## Diseño de URLs

```
/                                     → core:inicio (dashboard)
/acceso/ingresar/                     → usuarios:ingresar
/acceso/salir/                        → usuarios:salir
/acceso/registro/                     → usuarios:registro
/acceso/perfil/                       → usuarios:perfil

/cuentas/                             → cuentas:lista
/cuentas/crear/                       → cuentas:crear
/cuentas/<id>/editar/                 → cuentas:editar
/cuentas/<id>/eliminar/               → cuentas:eliminar

/transacciones/                       → transacciones:lista
/transacciones/crear/                 → transacciones:crear
/transacciones/<id>/editar/           → transacciones:editar
/transacciones/<id>/eliminar/         → transacciones:eliminar
/transacciones/<id>/comprobante/      → transacciones:subir_comprobante

/categorias/                          → categorias:lista
/categorias/crear/                    → categorias:crear
/categorias/<id>/editar/              → categorias:editar
/categorias/<id>/eliminar/            → categorias:eliminar
/categorias/<id>/etiquetas/           → categorias:gestionar_etiquetas

/etiquetas/crear/                     → categorias:etiqueta_crear
/etiquetas/<id>/editar/               → categorias:etiqueta_editar
/etiquetas/<id>/eliminar/             → categorias:etiqueta_eliminar

/presupuestos/                        → presupuestos:lista
/presupuestos/crear/                  → presupuestos:crear
/presupuestos/<id>/editar/            → presupuestos:editar
/presupuestos/<id>/eliminar/          → presupuestos:eliminar

/ahorros/                             → ahorros:lista
/ahorros/crear/                       → ahorros:crear
/ahorros/<id>/                        → ahorros:detalle
/ahorros/<id>/editar/                 → ahorros:editar
/ahorros/<id>/eliminar/               → ahorros:eliminar
/ahorros/<id>/depositar/              → ahorros:agregar_deposito

/transferencias/                      → transferencias:lista
/transferencias/crear/                → transferencias:crear
/transferencias/<id>/eliminar/        → transferencias:eliminar
/transferencias/recurrentes/          → transferencias:recurrentes_lista
/transferencias/recurrentes/crear/    → transferencias:recurrentes_crear
/transferencias/recurrentes/<id>/editar/ → transferencias:recurrentes_editar
/transferencias/recurrentes/<id>/alternar/ → transferencias:recurrentes_alternar

/tema/colores/                        → tema:colores_lista
/tema/colores/crear/                  → tema:colores_crear
/tema/colores/<id>/editar/            → tema:colores_editar
/tema/colores/<id>/eliminar/          → tema:colores_eliminar
/tema/iconos/                         → tema:iconos_lista
/tema/iconos/crear/                   → tema:iconos_crear
/tema/iconos/<id>/editar/             → tema:iconos_editar
/tema/iconos/<id>/eliminar/          → tema:iconos_eliminar

/notificaciones/api/guardar/        → notificaciones:guardar
/notificaciones/api/eliminar/       → notificaciones:eliminar
/sw.js                              → service-worker (TemplateView)
```

## Decisiones Arquitectónicas Clave

1. **Sin Django REST Framework** — toda interacción vía Django templates + respuestas parciales HTMX
2. **Sin npm/Node** — Chart.js cargado desde CDN
3. **Modelo Transaccion universal** — ingresos, gastos y pagos de tarjeta son registros `Transaccion`; signo siempre positivo, campo `tipo` discrimina
4. **Todas las páginas extienden `base.html`** — layout consistente con sidebar, colores, header y footer
5. **Transferencia crea 2 registros Transaccion** — débito de origen + crédito a destino, más un registro `Transferencia` de enlace
6. **Tarjetas de crédito como Cuentas** — con `fecha_corte` y `fecha_pago`; transacciones pendientes tienen `pagado=False`; tareas Celery envían recordatorios push a T-7, T-5, T-2 y el mismo día del pago
7. **Etiquetas como sub-items** — M2M con Categoria para pertenecer a múltiples categorías; sin subcategorías jerárquicas
8. **Presupuesto.monto_gastado** — desnormalizado, actualizado vía signal Django al guardar/borrar Transaccion
9. **Todos los montos** — almacenados como `DecimalField(max_digits=12, decimal_places=2)`
10. **Saldo de Cuenta** — desnormalizado, actualizado vía signal al guardar/borrar Transaccion o Transferencia
11. **Soft-delete** — modelos tienen campo `activo` en lugar de borrado físico
12. **Aislamiento por Inquilino** — todos los modelos de datos llevan FK a `Inquilino`, auto-poblado desde `usuario.inquilino`. Cada usuario es su propio inquilino (1:1). El modelo `Inquilino` existe para futuras necesidades SaaS (facturación, config, plan).
13. **Colores e iconos dinámicos** — `Color` e `Icono` son modelos registrados por el usuario en la app `tema`. `Cuenta`, `Categoria`, `Etiqueta` y `MetaAhorro` los referencian vía FK. Los colores generan propiedades CSS personalizadas (`--clr-{slug}`) inyectadas en `base.html` vía template tag.
14. **Notificaciones push sin APIs externas** — usando pywebpush + VAPID. El servidor Django envía notificaciones directo al navegador del usuario vía Google FCM / Apple APNs, sin costo. El Service Worker `sw.js` recibe el mensaje incluso con la app cerrada.

## Sistema de Variables CSS

Cada `Color` registrado genera una propiedad CSS personalizada disponible en todas las plantillas.

**Template tag** (`{% theme_css_variables %}`) colocado en `base.html` `<head>` renderiza:

```html
<style>
  :root {
    --clr-rojo-gastos: #FF5733;
    --clr-verde-ingresos: #33FF57;
    --clr-azul-ahorros: #3357FF;
  }
</style>
```

Todas las plantillas referencian colores vía `var(--clr-{slug})` en lugar de valores hex hardcodeados. Si un usuario actualiza un color, el cambio se propaga en todas partes instantáneamente.

## Flujo de Tarjetas de Crédito

1. Usuario compra algo → se crea `Transaccion` con `tipo='CP'`, `pagado=False`, `cuenta=tarjeta_credito`
2. Cuando el usuario paga el extracto → `Transferencia` desde cuenta débito a cuenta crédito
3. Al pagar, todas las `Transaccion` pendientes de esa tarjeta con `fecha <= fecha_pago` se marcan `pagado=True`
4. Tarea periódica Celery revisa `fecha_pago` diariamente y envía notificaciones push a T-7, T-5, T-2 y el día del pago

## Tareas Celery

| Tarea | Horario | Ubicación | Descripción |
|---|---|---|---|
| ejecutar_recurrencias | 06:00 diario | `apps.transfers.tasks` | Crea Transferencias para recurrentes vencidas |
| enviar_recordatorios_push | 09:00 diario | `apps.notifications.tasks` | Envía notificaciones push (T-7, T-5, T-2, T-0) vía pywebpush |

## Flujo de Notificaciones Push

```
Usuario activa alertas en Perfil
  → JS registra Service Worker /sw.js
  → Navegador genera { endpoint, p256dh, auth }
  → POST /notificaciones/api/guardar/ → SuscripcionPush en MySQL
  ↓
09:00 — Celery Beat ejecuta enviar_recordatorios_push
  → Consulta tarjetas crédito activas
  → Calcula próxima fecha de pago
  → Si diff = 7, 5, 2 ó 0 días → webpush() vía pywebpush
  → Google/Apple FCM entrega al dispositivo
  → sw.js muestra notificación nativa
  ↓
Si el push responde 404/410 → SuscripcionPush.delete() (limpieza automática)
```
