# FinanPlanen — Instrucciones para el Agente

## Identidad del Proyecto
- **Nombre**: `finanplanen`
- **Descripción**: Aplicación web de gestión financiera personal
- **Stack**: Django 4.2.20 + MySQL + HTMX + Celery + Nginx + Gunicorn
- **CSS**: CSS puro
- **Gráficos**: Chart.js vía CDN (dashboard, analytics)
- **Sin frameworks JS** — no React, Vue, Angular, etc.
- **Zona horaria**: America/Santo_Domingo
- **Moneda**: RD$ — formato: coma (,) para miles, punto (.) para centavos (ej: RD$ 1,500.00)
- **Config**: variables de entorno vía `django-environ` + `.env`

## Convenciones

### Idioma
- **Todo el proyecto en español**: nombres de modelos, campos, apps, URLs, templates, comentarios, commits, mensajes
- Excepción: `Inquilino` (Tenant) se mantiene como clase `Tenant` en código por ser término técnico universal, pero se referencia como "Inquilino" en documentación

### Django
- Apps dentro de `apps/`: `users`, `accounts`, `transactions`, `categories`, `budgets`, `savings`, `transfers`, `theme`, `core`
- Settings divididos: `config/settings/base.py`, `dev.py`, `prod.py`
- Modelos viven en `models.py` de cada app
- **Settings clave:**
  - `AUTH_USER_MODEL = 'users.Usuario'`
  - `LOGIN_URL = '/acceso/ingresar/'`
  - `LOGIN_REDIRECT_URL = 'core:inicio'`

### Montos
- Todos los valores monetarios: `DecimalField(max_digits=12, decimal_places=2)`
- Montos de transacciones siempre **positivos**; el campo `tipo` discrimina (IN/EX/CP)

### Nombres
- Modelos: singular, PascalCase (`Transaccion`, no `Transacciones`)
- URLs: minúsculas con guiones bajos
- Templates: minúsculas con guiones bajos, nombrados según la app
- Vistas: class-based views preferidas (`ListView`, `CreateView`, etc.)

### Templates
- Layout base: `templates/base.html`
- Templates de app: `templates/{app_name}/` (o dentro de cada app en su carpeta `templates/{app_name}/`)
- Parciales HTMX: prefijo `_`, ej. `_lista_transacciones.html`
- Sin Jinja2 — usar Django template language

### Apps y Responsabilidades
| App | Responsabilidad |
|---|---|
| `users` | Registro, inicio de sesión, perfil |
| `accounts` | CRUD cuentas financieras |
| `categories` | CRUD Categorías + Etiquetas |
| `transactions` | CRUD transacciones universal |
| `budgets` | Presupuestos mensuales por categoría |
| `savings` | Metas de ahorro + depósitos |
| `transfers` | Transferencias + recurrentes |
| `theme` | Registro de colores e iconos, variables CSS |
| `core` | Dashboard, inicio, utilidades compartidas |

### Modelos
13 modelos en total. Ver ARCHITECTURE.md para campos completos.
1. Tenant (Inquilino)
2. Usuario (AbstractUser)
3. Cuenta
4. Categoria
5. Etiqueta
6. Transaccion
7. Transferencia
8. TransferenciaRecurrente
9. MetaAhorro
10. DepositoAhorro
11. Presupuesto
12. Color
13. Icono

### Signals
- `Cuenta.saldo` — actualizado al guardar/borrar Transaccion o Transferencia
- `Presupuesto.monto_gastado` — actualizado al guardar/borrar Transaccion con categoría+mes correspondiente
- `MetaAhorro.monto_actual` — actualizado al guardar/borrar DepositoAhorro

### Theme / Diseño
- `Color` e `Icono` en `apps/theme/` — paleta registrada por el usuario
- `Cuenta`, `Categoria`, `Etiqueta`, `MetaAhorro` — FK a `Color` e `Icono` (no strings crudos)
- Colores auto-generan propiedades CSS personalizadas (`--clr-{slug}`) vía template tag en `base.html`

## Decisiones Clave (nunca sobreescribir)
- **Sin DRF** — no REST API, no serializers
- **Sin npm** — no Node toolchain, no bundlers
- **Vistas protegidas** — toda vista que renderice contenido del usuario autenticado lleva `@login_required` o hereda de `LoginRequiredMixin`
- **Tarjetas crédito** = cuentas con tipo=CR, transacciones pendientes vía `pagado=False`
- **Transferencias** = 1 registro Transferencia + 2 registros Transaccion (débito/crédito)
- **Etiquetas** = M2M con Categoria (no subcategorías jerárquicas)
- **Gastos** = `Transaccion.objects.filter(tipo='EX')`
- **Ingresos** = `Transaccion.objects.filter(tipo='IN')`

## Instrucciones de Sesión
- Leer `ARCHITECTURE.md` y `AGENTS.md` al inicio de cada sesión
- No asumir que una librería existe — revisar `requirements.txt` antes de importar
- Ejecutar type checks y Django checks básicos después de cambios en modelos
- Preguntar antes de ejecutar `makemigrations` o `migrate`
- Nunca hacer commit sin solicitud explícita del usuario
- Mantener ARCHITECTURE.md sincronizado con la evolución del proyecto
- Cualquier decisión arquitectónica que contradiga AGENTS.md debe discutirse explícitamente con el usuario primero
- Marcar tareas completadas en TASKS.md (`- [x]`) al finalizar cada una

# Instrucciones para Agentes de Código (AI)

## Workflow obligatorio

Antes de escribir **cualquier línea de código**, sigue este orden:

### 1. Crear tarea en `docs/TASKS.md`
- Agrega el ítem en la fase correspondiente con formato `- [ ] N.N Descripción`
- Si no existe la fase, créala

### 2. Crear entrada en `docs/BITACORA.md`
- Agrega una fila en la tabla con: fecha, archivo, líneas, descripción del cambio, motivo
- Formato: `YYYY-MM-DD | archivo | líneas | qué cambió | por qué`

### 3. Solo entonces: codificar

## Reglas

- Cada cambio en un archivo debe tener su correspondiente entrada en la bitácora
- Si el cambio involucra migraciones, ejecuta `makemigrations` y `migrate` y documéntalo
- Si el cambio requiere modificar tests, actualízalos antes de marcar la tarea como `[x]`
- No marques una tarea como completada hasta haber verificado que funciona (test, lint, typecheck)
- La bitácora es el registro fuente de verdad — debe estar siempre actualizada antes de hacer commit
- Cuando trabajes con hallazgos de `docs/AUDITORIA.md`, referencia el número de hallazgo en la bitácora (ej. "Sección 1, item 1")