# Módulo Ingresos

## Problema
No existe forma de registrar dinero que entra a una cuenta. Actualmente:
- Al crear una cuenta se asigna un balance inicial
- Gasto descuenta del balance vía signal
- Transferencia mueve entre cuentas
- **No hay forma de aumentar el balance** (depósitos, salario, pago TC, recarga efectivo)

## Solución
Modelo `Ingreso` en `apps/transactions` — el opuesto de `Gasto`.

## Modelo

### `Ingreso`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `inquilino` | FK `Tenant` | multi-tenencia |
| `usuario` | FK `Usuario` | creador |
| `cuenta` | FK `Cuenta` | qué cuenta recibe el dinero |
| `categoria` | FK `Categoria` (nullable) | tipo de ingreso (salario, pago TC, depósito, etc.) |
| `monto` | `DecimalField(max_digits=12, decimal_places=2)` | RD$ |
| `fecha` | `DateField` | cuándo entró |
| `nota` | `TextField` (blank) | descripción |
| `comprobante` | `FileField(upload_to='comprobantes/', blank=True)` | opcional |
| `creado` | `DateTimeField(auto_now_add)` | |
| `actualizado` | `DateTimeField(auto_now)` | |

**Meta:** `ordering = ['-fecha', '-creado']`

## Signals

### `ingreso_creado` (post_save)
```python
if created:
    instance.cuenta.balance += instance.monto
    instance.cuenta.save(update_fields=['balance'])
```

### `ingreso_eliminado` (post_delete)
```python
instance.cuenta.balance -= instance.monto
instance.cuenta.save(update_fields=['balance'])
```

## Form

`IngresoForm(ModelForm)` con:
- `cuenta`: `Select(attrs={'class': 'form-control'})`
- `categoria`: `Select(attrs={'class': 'form-control'})`
- `monto`: `NumberInput` con prefijo RD$ (mismo estilo que GastoForm)
- `fecha`: `DateInput(attrs={'type': 'date', 'class': 'form-control'})`
- `nota`: `Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ej. Pago de nómina'})`
- `comprobante`: `FileInput(attrs={'class': 'form-control'})`

## Vistas CRUD HTMX

Mismo patrón que `GastoLista`/`GastoCrear`/`GastoEditar`/`GastoEliminar`:

### `IngresoLista(InquilinoMixin, ListView)`
- `model = Ingreso`
- `template_name = 'transactions/ingresos.html'`
- `paginate_by = 20`
- Filtros: fecha_desde, fecha_hasta, cuenta, categoria
- `context['section'] = 'ingresos'`
- No HX-Request: carga cuentas, categorías, totales del mes, distribución

### `IngresoCrear(InquilinoMixin, CreateView)`
- HX-Redirect a `transactions:ingresos`

### `IngresoEditar(InquilinoMixin, UpdateView)`
- HX-Redirect a `transactions:ingresos`

### `IngresoEliminar(InquilinoMixin, DeleteView)`
- Template: `theme/_confirmar_eliminar.html`

## URLs (en `apps/transactions/urls.py`)

```
ingresos/           → IngresoLista      (name='ingresos')
ingresos/crear/     → IngresoCrear      (name='ingreso_crear')
ingresos/editar/<pk>/ → IngresoEditar   (name='ingreso_editar')
ingresos/eliminar/<pk>/ → IngresoEliminar (name='ingreso_eliminar')
```

## Templates

### `transactions/ingresos.html`
- Layout dos columnas (same as gastos.html):
  - Izquierda: formulario inline para registrar ingreso + banner gradient
  - Derecha: tarjetas de categorías con totales + barras de distribución
- Botón "Nuevo Ingreso" en header que abre modal
- Sección `#ingreso-list` con tabla + paginación HTMX

### `transactions/_lista_ingresos.html`
- Tabla con columnas: Fecha, Cuenta, Categoría, Nota, Monto (verde positivo), Comprobante, Acciones
- Paginación HTMX

### `transactions/_form_ingreso.html`
- Modal form con campos: cuenta, categoría, monto (RD$), fecha, nota, comprobante

## Sidebar (base.html)

Agregar enlace antes de Gastos:
```html
<a href="{% url 'transactions:ingresos' %}" class="nav-item{% if section == 'ingresos' %} active{% endif %}">
  <i class="fas fa-arrow-trend-up"></i><span>Ingresos</span>
</a>
```

Mismo en mobile nav.

## Transacciones (vista unificada)

Actualizar `TransaccionLista.get_queryset()` para combinar:
- `Ingreso` (tipo=ingreso, monto positivo)
- `Gasto` (tipo=gasto, monto negativo)
- `Transferencia` (tipo=transferencia)

Actualizar `_lista_transacciones.html` para mostrar los tres tipos con colores:
- Ingreso → verde, icono `fa-arrow-trend-up`
- Gasto → rojo, icono `fa-arrow-trend-down`
- Transferencia → azul, icono `fa-right-left`

Tarjetas de resumen:
- **Ingresos** = total ingresos
- **Gastos** = total gastos  
- **Balance** = `total_cuentas` (balance actual de todas las cuentas)

## Efecto en Cuentas

Al crear un Ingreso vinculado a una Cuenta:
1. Signal `ingreso_creado` → `Cuenta.balance += monto`
2. La tarjeta de esa cuenta en `Cuentas.html` refleja el nuevo balance automáticamente
3. Ej: pagar TC de RD$ 5,000 → crear Ingreso en la cuenta de crédito → balance sube RD$ 5,000
4. Ej: cobrar salario RD$ 30,000 → crear Ingreso en cuenta débito/efectivo → balance sube RD$ 30,000
