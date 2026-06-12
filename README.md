<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=wave&color=gradient&customColorList=6,11,20&height=200&section=header&text=Finanplanen&fontSize=50&fontColor=fff&animation=twinkling&fontAlignY=35&desc=Gesti%C3%B3n%20de%20finanzas%20personales&descAlignY=60&descSize=18" />
</p>

<h1 align="center">Finanplanen</h1>
<p align="center">Aplicación web fullstack para la gestión de finanzas personales con soporte multi-inquilino</p>

---

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&pause=1000&color=6C63FF&center=true&vCenter=true&width=435&lines=Django+4.2+%2B+MySQL;Control+total+de+tus+finanzas;Multi-inquilino+%26+automatizado" alt="Typing SVG" />
</p>

<!-- BADGES FILA 1: Stack -->
<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
  <img src="https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white" />
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" />
</p>

<!-- BADGES FILA 2: Repo stats -->
<p align="center">
  <img src="https://img.shields.io/github/stars/Code-Castor28/finanplanen?style=for-the-badge" />
  <img src="https://img.shields.io/github/forks/Code-Castor28/finanplanen?style=for-the-badge" />
  <img src="https://img.shields.io/github/issues/Code-Castor28/finanplanen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Status-En%20Desarrollo-orange?style=for-the-badge" />
</p>

---

## 📌 Descripción

**Finanplanen** es una aplicación web diseñada para ayudarte a tomar el control total de tus finanzas personales. Permite registrar ingresos y gastos, administrar múltiples cuentas (crédito, débito, efectivo), establecer presupuestos mensuales por categoría, definir metas de ahorro, y programar transferencias recurrentes entre cuentas. Con soporte multi-inquilino, es ideal tanto para uso personal como para pequeños equipos o familias que deseen centralizar su gestión financiera.

---

## 🛠️ Stack

| Capa | Tecnología |
|---|---|
| Backend | Django 4.2.20 |
| Base de datos | MySQL |
| Frontend | HTML5 · CSS3 · JavaScript |
| Autenticación | Django Auth |
| Tareas asíncronas | Celery + Redis |
| Imágenes | Pillow |

---

## ⚙️ Instalación

### Requisitos previos
- Python 3.10+
- MySQL corriendo localmente
- Redis (para Celery)
- Git

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Code-Castor28/finanplanen.git
cd finanplanen

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 5. Crear la base de datos MySQL
mysql -u root -p -e "CREATE DATABASE finanplanen CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 6. Aplicar migraciones
python manage.py migrate

# 7. Crear superusuario
python manage.py createsuperuser

# 8. Correr el servidor
python manage.py runserver
```

Abrí `http://127.0.0.1:8000` en tu navegador.

---

## 🌱 Variables de entorno

Creá un archivo `.env` en la raíz del proyecto basado en `.env.example`:

| Variable | Descripción | Ejemplo |
|---|---|---|
| `SECRET_KEY` | Clave secreta de Django | `django-insecure-...` |
| `DEBUG` | Modo depuración | `True` |
| `DB_NAME` | Nombre de la base de datos | `finanplanen` |
| `DB_USER` | Usuario de la base de datos | `root` |
| `DB_PASSWORD` | Contraseña de la base de datos | |
| `DB_HOST` | Host de la base de datos | `172.31.128.1` |
| `DB_PORT` | Puerto de la base de datos | `3306` |
| `ALLOWED_HOSTS` | Hosts permitidos | `*` |

---

## 🗂️ Estructura del proyecto

```
finanplanen/
├── apps/
│   ├── accounts/          # Cuentas financieras (crédito, débito, efectivo)
│   ├── budgets/           # Presupuestos mensuales por categoría
│   ├── categories/        # Categorías y etiquetas
│   ├── core/              # Dashboard principal e infraestructura
│   ├── savings/           # Metas de ahorro y depósitos
│   ├── theme/             # Personalización de temas (colores, íconos)
│   ├── transactions/      # Ingresos y gastos
│   ├── transfers/         # Transferencias entre cuentas
│   └── users/             # Usuarios, autenticación e inquilinos
├── config/
│   └── settings/          # Configuración de Django (base, dev, prod)
├── static/                # Archivos estáticos (CSS, JS)
├── templates/             # Templates HTML
├── media/                 # Archivos subidos (comprobantes, etc.)
├── manage.py
├── requirements.txt
└── .env.example
```

---

## 🚀 Uso

### Módulos principales

| Módulo | Descripción |
|---|---|
| **Dashboard** | Panel principal con resumen de balance total, ingresos/gastos del mes, gráficos de evolución (6 meses) y distribución por categorías |
| **Cuentas** | Administración de cuentas de crédito, débito y efectivo con saldo en tiempo real |
| **Transacciones** | Registro de ingresos y gastos con soporte para comprobantes |
| **Presupuestos** | Límites de gasto mensual por categoría con indicador de progreso y alertas de exceso |
| **Metas de ahorro** | Definición de objetivos de ahorro con seguimiento de depósitos y porcentaje de avance |
| **Transferencias** | Transferencias entre cuentas con soporte para recurrencias (diarias, semanales, mensuales) |
| **Categorías** | Organización de transacciones por categorías y etiquetas |

### Tareas programadas (Celery Beat)

- **Ejecución de recurrencias** (diaria a las 6:00 AM) — procesa transferencias recurrentes
- **Recordatorio de tarjetas de crédito** (diaria a las 9:00 AM) — notifica próximos pagos

---

<p align="center">Hecho con ❤️ por <a href="https://github.com/Code-Castor28">Code-Castor28</a></p>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=wave&color=gradient&customColorList=6,11,20&height=100&section=footer" />
</p>
