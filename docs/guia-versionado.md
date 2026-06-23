# Guía de Versionado de la Aplicación

Esta guía define cómo versionamos el proyecto Django: convención de números de versión, formato de commits, herramientas usadas y el flujo de trabajo diario. Es de lectura obligatoria para todo el equipo de desarrollo.

---

## 1. ¿Por qué versionamos así?

Sin un sistema claro, nadie sabe con certeza qué código está corriendo en producción, qué cambió entre una versión y otra, o si una actualización es segura de aplicar. Versionar bien nos da:

- Trazabilidad exacta entre un número de versión y un commit de Git.
- Un historial legible de cambios (`CHANGELOG.md`) sin tener que leer commits uno por uno.
- Automatización: el número de versión se calcula solo, nadie lo escribe a mano.

---

## 2. Versionado Semántico (SemVer)

Usamos el estándar `MAJOR.MINOR.PATCH` (ejemplo: `2.4.1`).

| Posición | Significado | Cuándo sube |
|---|---|---|
| **MAJOR** | Cambios que rompen compatibilidad | Una integración o flujo existente deja de funcionar como antes |
| **MINOR** | Funcionalidad nueva | Se agrega algo, pero lo anterior sigue funcionando igual |
| **PATCH** | Corrección de errores | Se arregla un bug, sin agregar nada nuevo |

**Ejemplo de evolución real:**

```
1.0.0  → se agrega exportación a PDF        → 1.1.0
1.1.0  → se corrige un bug en esa función   → 1.1.1
1.1.1  → se cambia el formato de la API     → 2.0.0
```

---

## 3. Conventional Commits

Cada commit debe seguir este formato:

```
<tipo>: <descripción breve>
```

**Tipos más usados:**

| Tipo | Uso |
|---|---|
| `feat:` | Nueva funcionalidad |
| `fix:` | Corrección de un bug |
| `docs:` | Cambios solo en documentación |
| `chore:` | Tareas de mantenimiento (dependencias, configuración) |
| `refactor:` | Cambio de código que no agrega función ni corrige bug |
| `test:` | Agregar o modificar tests |

**Ejemplos:**

```
feat: agregar exportación a PDF
fix: corregir cálculo de balance en cuentas
docs: documentar endpoint de transferencias
chore: actualizar dependencias
```

**Cambios que rompen compatibilidad:** se marcan con `!` después del tipo, o agregando `BREAKING CHANGE` en el cuerpo del commit:

```
feat!: cambiar formato de respuesta del endpoint /api/balance
```

### Tabla de impacto en la versión

| Commit | Efecto en la versión |
|---|---|
| `fix:` | `1.0.0` → `1.0.1` |
| `feat:` | `1.0.0` → `1.1.0` |
| `feat!:` o `BREAKING CHANGE` | `1.0.0` → `2.0.0` |

---

## 4. Herramienta: Commitizen

Commitizen lee el historial de commits y genera automáticamente la versión y el `CHANGELOG.md`. Nadie edita estos archivos a mano.

### Instalación

```bash
pip install commitizen
```

### Configuración del proyecto (`pyproject.toml`)

```toml
[tool.commitizen]
name = "cz_conventional_commits"
version = "1.0.0"
version_files = [
    "myapp/__init__.py:__version__"
]
tag_format = "v$version"
version_scheme = "semver"
update_changelog_on_bump = true
```

> La versión se define en un único lugar: `myapp/__init__.py`. Nunca se duplica a mano en `settings.py` ni en ningún otro archivo.

```python
# myapp/__init__.py
__version__ = "1.0.0"
```

`settings/base.py` solo **consume** ese valor, no lo define:

```python
# settings/base.py
from myapp import __version__ as APP_VERSION
```

---

## 5. Flujo de trabajo diario

### Hacer un commit

En lugar de `git commit`, usar:

```bash
cz commit
```

Esto abre un asistente interactivo que pregunta el tipo de cambio y construye el mensaje con el formato correcto.

### Subir una nueva versión

Cuando el equipo decide que es momento de liberar una versión:

```bash
cz bump          # calcula la nueva versión, actualiza __init__.py y el CHANGELOG.md
git push --tags  # sube el tag de Git al repositorio remoto
```

`cz bump` revisa todos los commits desde la última versión, decide automáticamente si sube PATCH, MINOR o MAJOR según las reglas de la tabla anterior, y genera todo sin intervención manual.

### Validar el formato antes de aceptar un commit (obligatorio)

Para que el sistema no dependa de que cada persona se acuerde de usar `cz commit`, el repositorio incluye un hook de `pre-commit` que rechaza cualquier commit que no siga el formato de Conventional Commits. Si tu commit es rechazado, revisa el formato de la tabla en la sección 3.

---

## 6. Git Tags

Cada versión liberada queda marcada con un tag en Git apuntando al commit exacto:

```bash
git tag -a v2.4.1 -m "Corrección de bug en login"
git push origin v2.4.1
```

Esto permite volver en cualquier momento al código exacto que corría en producción en una versión específica, sin ambigüedad.

---

## 7. CHANGELOG.md

Generado automáticamente por `cz bump`. Sigue el formato estándar **Keep a Changelog**:

```
## [2.4.1] - 2026-06-15
### Corregido
- Bug que impedía cerrar sesión en móviles

## [2.4.0] - 2026-06-01
### Agregado
- Exportación de reportes en PDF
```

No se edita a mano. Si el changelog no refleja un cambio real, es porque el commit correspondiente no siguió el formato de Conventional Commits — corregir el commit, no el changelog.

---

## 8. Dónde se muestra la versión

### Disponible en todos los templates

La versión se inyecta globalmente mediante un **context processor**, sin necesidad de pasarla manualmente en cada vista:

```python
# core/context_processors.py
from django.conf import settings

def app_version(request):
    return {
        'app_version': getattr(settings, 'APP_VERSION', '')
    }
```

```python
# settings/base.py
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ...los que ya existan...
                'core.context_processors.app_version',
            ],
        },
    },
]
```

Uso en cualquier template (incluido el pie de la sidebar):

```html
<p class="footer">v{{ app_version }}</p>
```

### En la pantalla de mantenimiento

La misma variable se usa para confirmar, justo después de un despliegue, que la versión nueva quedó activa:

```html
<!-- Maintenance.html -->
<p class="footer">v{{ app_version }}</p>
```

---

## 9. Resumen del flujo completo

```
Commit con formato correcto (cz commit)
        ↓
Hook de pre-commit valida el formato
        ↓
cz bump → calcula versión, actualiza __init__.py, genera CHANGELOG.md
        ↓
git push --tags → sube el tag a Git
        ↓
Deploy → APP_VERSION visible en sidebar y pantalla de mantenimiento
```

---

## 10. Reglas que todo el equipo debe respetar

1. Nunca hacer `git commit` directo sin pasar por `cz commit` o sin seguir el formato de Conventional Commits.
2. Nunca editar `CHANGELOG.md` ni el número de versión a mano.
3. Nunca duplicar `APP_VERSION` en más de un archivo — la única fuente de verdad es `myapp/__init__.py`.
4. Todo cambio que rompa compatibilidad debe marcarse explícitamente con `!` o `BREAKING CHANGE`, sin excepción.
5. Cada versión liberada debe tener su tag correspondiente en Git antes de hacer deploy a producción.
