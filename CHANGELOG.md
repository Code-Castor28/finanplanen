## v2.1.1 (2026-06-23)

### Refactor

- **MOVILES**: MEJORA DEL TIME NICTIVIDAD EN MOVILES

## v2.1.0 (2026-06-23)

### Feat

- altos — P6-P11 validación, índices, dashboard, Redis
- <div class="sidebar-footer">

### Fix

- medios — P12, P13, P17 N+1, validación, filtro default
- críticos — C1-C5, P19, P23
- mejora del lateral name

### Refactor

- logs y seguridad
- **limite-credito**: anadir un campo limite de credito
- **Próximos-Pagos**: update para cargar los proximos pagos al dashboard

## v2.0.0 (2026-06-22)

### Feat

- **versionado**: cambio para mover el nombre del user arriba
- **versionado**: estrutura del versionado
- seed_colores command - 40 colores predefinidos para todos los inquilinos
- selector visual de colores con busqueda, fix slug en seed_iconos, filtro por inquilino
- seed_iconos command + visual icon picker en _form_cuenta.html
- validar que dia_corte, dia_pago y mes de vencimiento no superen 31
- validacion en tiempo real via HTMX blur en formulario de cuentas
- mascaras y validaciones en formulario de cuentas - balance moneda, vencimiento MM/AA, ultimos_digitos unico, filtros numericos
- add Tippy.js tooltips to profile form
- add Tippy.js tooltips to savings forms
- add Tippy.js tooltips to budget and category forms
- add Tippy.js tooltips to transfer forms
- add Tippy.js tooltips to expense/income forms
- add Tippy.js tooltips to account form
- test_push now builds realistic notifications from real Cuenta data
- add seed_data management command to populate test data for development
- implement idle session timeout in JS and add seed_data management command for testing
- initialize project architecture, documentation, and base frontend templates
- add app icons and site branding assets to static directory
- implement PWA Web Push notification system with VAPID authentication, service worker, and Celery task integration.
- add notifications app with web push subscription management models, views, and API endpoints
- implement push notifications with web-push, add recurrent transfer tasks, and configure PWA support
- implement push notification system with web worker support and user subscription management
- initialize notifications app with Subscription model and push integration assets
- add HTML templates for transactions, transfers, savings, income, and expenses modules
- add Cuenta model to manage financial account data for users and tenants
- add transaction history dashboard template with summary cards and filter controls
- implement budget management interface with creation and editing views
- add base stylesheet with custom variables and core component styles
- implement base stylesheet with global variables, layout structures, and UI component definitions
- implement dynamic sidebar navigation with active state via context processor and base template
- implement dynamic theme color and icon management templates with base styles and layout components
- add comprehensive dashboard template with financial charts and summary reports
- initialize base CSS styles with layout, UI components, and theme variables
- implement base stylesheet with layout, component, and utility variables
- add baseline CSS styles and layout components for the application dashboard
- implement base stylesheet with layout components, variables, and global UI styling
- implement recurring transfers system with Celery tasks and scheduling
- implement Celery task configuration and create savings goals dashboard UI
- add savings goals management, automated deposit tracking via signals, and recurring transfer scheduling support
- implement savings goals feature with CRUD views, models, and interactive dashboard UI
- implement savings goals module with progress tracking, deposits, and automated recurring transfers via Celery.
- implement savings goals module with CRUD operations, dashboard analytics, and Celery configuration
- implement recurring transfers with Celery tasks, budget tracking via signals, and a central dashboard for financial overview
- implement savings goals module with dashboard, management modals, and documentation
- implement core savings goals and deposit management system with CRUD views and UI components
- implement savings module with goal tracking, deposit management, and related views.
- implement base project structure with responsive layout and global UI components
- initialize financial planning project structure with core styles, documentation, and base templates
- implement initial project structure, custom user model, and mobile-first layout foundation
- implement core transfer management features including models, automated balance signal handling, and mobile-first UI foundations.
- initialize core project structure, user models, transaction templates, and transfer app functionality
- implement core modules for transactions and transfers with HTMX-driven views and UI components
- implement core financial modules including transactions, transfers, and theme customization systems
- implement modular expense, transfer, and savings management system with HTMX integration
- implement core financial modules including transactions, transfers, savings, and thematic customizations with multi-tenant support.
- implement income tracking module with UI templates, database models, and HTMX-driven forms
- initial project structure including core, transactions, categories, budgets, and transfers applications
- initialize Django project structure with core apps, base settings, and initial UI templates
- scaffold project architecture with custom user model, multi-tenancy support, and base app structure
- implement core user authentication and project structure with initial application apps and base templates
- implement multi-tenant user authentication, dynamic theming system, and modular app structure
- initialize base project structure with user, theme, and financial apps including dashboard and responsive layout.
- initialize Django project structure with core applications and initial templates

### Fix

- agredado apartado de mantenimiento.
- separar prefijo fas del dato - template anade fas, DB solo guarda nombre del icono
- seed_iconos ahora usa update_or_create + segunda pasada para corregir clase_css erronea
- balance como CharField explicito para que clean_balance pueda quitar comas antes de convertir a Decimal
- clean_balance quita comas antes de validar DecimalField
- span field-error siempre presente para que hx-target='next .field-error' funcione
- balance arranca vacio en cuentas nuevas, no forza 0.00 al perder foco
-  from error
- cambiar hx-target de 'this' a '#modal-content' para evitar duplicacion de contenido en errores
- no cerrar modal al enviar formulario si hay errores de validacion
- validar slug unico en CuentaForm para evitar IntegrityError al crear cuentas duplicadas
- habilitar swap en respuestas 422 via htmx:beforeSwap
- usar HX-Retarget para mostrar errores de transferencia inline
- mostrar errores de validacion en formulario inline de transferencias
- validar que origen != destino en transferencias, calcular total_mes
- tiempo de inactividad mejorado para moviles
- se agrego tooltip
- delete push subs on VAPID mismatch; add clear_subscriptions command
- pass raw VAPID_PRIVATE_KEY directly to pywebpush instead of PEM
- use EllipticCurvePublicKey.from_encoded_point for cryptography >=49 compat
- replace DER-based VAPID keys with raw 32B scalars (RFC 8291) to fix ASN.1 deserialization
- pruevas
- progreso con noti
- mejora base64
- mejora en noti
- cryptography>=41.0,<44.0
- mejora en la clave de noti
- comant para probar el notificaciones
- mejora del boton de notificaciones
- andir celery beat
- add STATIC_ROOT setting to enable collectstatic
- replace unique TextField endpoint with SHA-256 hash to fix MySQL BLOB/TEXT index error
- mejora en el requierement update de django
- version
- new dependencia

### Refactor

- extract visual pickers a includes reutilizables y aplicar en todos los formularios
