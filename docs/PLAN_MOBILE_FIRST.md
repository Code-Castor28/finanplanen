# Plan: Rediseño Mobile-First + Sidebar Unificada

## Objetivo
Unificar todas las plantillas (excepto login) bajo `base.html` con un layout responsive mobile-first y una barra lateral idéntica en todas las páginas.

## 1. Arquitectura de la Sidebar

Todas las páginas autenticadas comparten **exactamente el mismo menú lateral**:

```
┌──────────────────────────────┐
│  FinanPlanen                 │  ← logo
│  Gestión Financiera          │
├──────────────────────────────┤
│  📊 Panel Principal          │  core:inicio
├──────────────────────────────┤
│  💳 Cuentas                  │  accounts:lista
│  📋 Transacciones            │  transactions:lista
│  💸 Gastos                   │  transactions:gastos
│  🔄 Transferencias           │  transfers:lista
│  📈 Presupuestos             │  budgets:lista
│  🎯 Ahorros                  │  savings:lista
│  🏷️ Categorías              │  categories:lista
├──────────────────────────────┤
│  🎨 Colores                  │  theme:colores_lista
│  ✨ Iconos                   │  theme:iconos_lista
├──────────────────────────────┤
│  👤 {{ user.nombre }}        │
│  ⚙️ Perfil                   │  users:perfil
│  🚪 Cerrar Sesión            │  users:salir
└──────────────────────────────┘
```

### Breakpoints
| Rango | Comportamiento |
|---|---|
| < 768px | Bottom nav fijo (5 íconos), sidebar oculta, hamburger abre drawer |
| 768–1024px | Sidebar colapsable (hamburger toggle) + bottom nav |
| > 1024px | Sidebar fija 260px, sin bottom nav |

### Bottom Nav (móvil)
5 elementos: **Panel, Cuentas, Transacciones, Presupuesto, Perfil**

## 2. URLs Faltantes

6 apps necesitan `urls.py` nuevo:

| App | Archivo | Rutas |
|---|---|---|
| accounts | `apps/accounts/urls.py` | `lista/` (name: `accounts:lista`) |
| budgets | `apps/budgets/urls.py` | `lista/` (name: `budgets:lista`) |
| categories | `apps/categories/urls.py` | `lista/` (name: `categories:lista`) |
| savings | `apps/savings/urls.py` | `lista/` (name: `savings:lista`) |
| transactions | `apps/transactions/urls.py` | `lista/` (name: `transactions:lista`), `gastos/` (name: `transactions:gastos`) |
| transfers | `apps/transfers/urls.py` | `lista/` (name: `transfers:lista`) |

Se incluyen en `config/urls.py` con `app_name` y namespace.

## 3. Context Processor

`apps/core/context_processors.py` → variable `section` para marcar nav activo.

```
'section': 'dashboard' | 'accounts' | 'transactions' | 'gastos' | 'transfers' | 'budgets' | 'savings' | 'categories' | 'theme' | 'profile'
```

## 4. base.html

Estructura:

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}FinanPlanen{% endblock %}</title>
  {% load static %}{% load theme_tags %}
  {% theme_css_variables %}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <link rel="stylesheet" href="{% static 'css/style.css' %}">
  {% block extra_head %}{% endblock %}
</head>
<body>
  <!-- Overlay -->
  <div class="overlay" id="sidebarOverlay"></div>

  <!-- Sidebar -->
  <aside class="sidebar" id="sidebar">
    <!-- Logo -->
    <!-- Navegación Principal (section) -->
    <!-- Navegación Configuración -->
    <!-- Footer Usuario -->
  </aside>

  <!-- Main -->
  <main class="main">
    <!-- Topbar (hamburger + título) -->
    <div class="topbar">...</div>
    <!-- Content -->
    <div class="content">
      {% block content %}{% endblock %}
    </div>
  </main>

  <!-- Bottom Nav (móvil) -->
  <nav class="mob-nav">...</nav>

  <!-- Toast -->
  <div class="toast" id="toast">...</div>

  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
  <script src="https://unpkg.com/hyperscript.org@0.9.12"></script>
  <script src="{% static 'js/main.js' %}"></script>
  {% block extra_scripts %}{% endblock %}
</body>
</html>
```

El sidebar se renderiza con tags `{% url %}` y la variable `section` para la clase `active`.

## 5. CSS Consolidado

`static/css/style.css` unificará:
- Variables CSS (provenientes de `{% theme_css_variables %}`)
- Layout: `.app`, `.sidebar`, `.main`, `.topbar`, `.content`
- Sidebar: `.sidebar`, `.sidebar-logo`, `.nav-item`, `.nav-section`
- Bottom nav: `.mob-nav`, `.mob-nav-inner`
- Botones: `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-ghost`, `.btn-danger`
- Tablas: `.table`, `.tx-table`, `.sv-table`, `.table-scroll`
- Formularios: `.form-group`, `.field`, `.field-row`
- Modales: `.modal`, `.overlay`, `.modal-content`
- Dashboard específico: `.balance-hero`, `.stat-mini`, `.chart-wrap`
- Cards: `.card`, `.panel`, `.panel-head`
- Toast: `.toast`
- Responsive: 3 breakpoints

## 6. Refactor de Templates

Cada template standalone:
1. Eliminar `<!DOCTYPE html>` hasta `</head>` (head completo)
2. Eliminar `<style>` inline
3. Eliminar sidebar HTML
4. Eliminar bottom nav HTML
5. Eliminar toast HTML
6. Eliminar script tags CDN (HTMX, Hyperscript, FontAwesome)
7. Agregar `{% extends 'base.html' %}`
8. Agregar `{% block title %}`
9. Envolver contenido en `{% block content %}`
10. Envolver JS específico en `{% block extra_scripts %}`
11. Agregar `{% block extra_head %}` si necesita Chart.js

### Templates a refactorizar (7):
| Archivo | App | Notas |
|---|---|---|
| core/dashboard.html | core | Chart.js en extra_head, charts JS en extra_scripts |
| accounts/Cuenta.html | accounts | localStorage CRUD, SVG donut |
| budgets/presupuesto.html | budgets | localStorage CRUD |
| categories/categoria.html | categories | localStorage CRUD |
| savings/ahoro.html | savings | localStorage CRUD |
| transactions/gastos.html | transactions | localStorage CRUD |
| transactions/transaciones.html | transactions | localStorage CRUD |
| transfers/tranferencia.html | transfers | localStorage CRUD |

### Templates que NO se tocan:
- `users/login.html` (standalone, no extiende base)
- `users/register.html` (registro público)
- `users/perfil.html` (ya extiende base)
- `theme/colores.html` (ya extiende base)
- `theme/iconos.html` (ya extiende base)

## 7. Orden de Implementación

1. Crear `docs/PLAN_MOBILE_FIRST.md` ✅
2. Crear `urls.py` para 6 apps
3. Incluir en `config/urls.py`
4. Crear context processor `section`
5. Registrar context processor en settings
6. Escribir CSS completo en `style.css`
7. Escribir `base.html` completo
8. Refactorizar cada template (7 pasos)
9. Verificar con `python manage.py check`
