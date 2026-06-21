from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.theme.models import Icono
from apps.users.models import Tenant

ICONOS = [
    # ===== Tarjetas y Cuentas =====
    ('Billetera', 'fa-wallet'),
    ('Tarjeta crédito', 'fa-credit-card'),
    ('Banco', 'fa-building-columns'),
    ('Dinero', 'fa-money-bill'),
    ('Billetes', 'fa-money-bills'),
    ('Monedas', 'fa-coins'),
    ('Dólar', 'fa-dollar-sign'),
    ('Euro', 'fa-euro-sign'),
    ('Balance', 'fa-scale-balanced'),
    ('Cheque', 'fa-money-check'),
    ('Efectivo', 'fa-sack-dollar'),
    ('Caja', 'fa-box-open'),
    ('Cofre', 'fa-chest'),
    ('Alcancía', 'fa-piggy-bank'),
    ('Transferencia', 'fa-arrow-right-arrow-left'),
    ('Comisión', 'fa-percent'),
    ('Interés', 'fa-chart-simple'),
    # ===== Ingresos =====
    ('Ingresos', 'fa-arrow-trend-up'),
    ('Salario', 'fa-briefcase'),
    ('Depósito', 'fa-circle-dollar-to-slot'),
    ('Ganancia', 'fa-money-bill-wave'),
    ('Renta', 'fa-file-invoice-dollar'),
    ('Inversión', 'fa-chart-pie'),
    ('Dividendo', 'fa-percent'),
    ('Bono', 'fa-award'),
    ('Devolución', 'fa-rotate-left'),
    ('Venta', 'fa-tag'),
    ('Propina', 'fa-hand-holding-dollar'),
    ('Premio', 'fa-trophy'),
    ('Herencia', 'fa-gem'),
    ('Préstamo', 'fa-hand-holding-hand'),
    # ===== Gastos =====
    ('Gastos', 'fa-arrow-trend-down'),
    ('Compras', 'fa-cart-shopping'),
    ('Bolsa', 'fa-bag-shopping'),
    ('Factura', 'fa-receipt'),
    ('Recibo', 'fa-file-invoice'),
    ('Impuesto', 'fa-file'),
    ('Multa', 'fa-circle-exclamation'),
    ('Suscripción', 'fa-arrows-rotate'),
    ('Cuota', 'fa-hand-holding-hand'),
    ('Donación', 'fa-hand-holding-heart'),
    ('Gasto fijo', 'fa-clock'),
    ('Gasto variable', 'fa-chart-line'),
    ('Emergencia', 'fa-truck-medical'),
    ('Deuda', 'fa-file-invoice'),
    # ===== Alimentación =====
    ('Comida', 'fa-utensils'),
    ('Restaurante', 'fa-plate-wheat'),
    ('Hamburguesa', 'fa-burger'),
    ('Pizza', 'fa-pizza-slice'),
    ('Comida rápida', 'fa-hotdog'),
    ('Ensalada', 'fa-carrot'),
    ('Fruta', 'fa-apple-whole'),
    ('Verdura', 'fa-leaf'),
    ('Huevos', 'fa-egg'),
    ('Queso', 'fa-cheese'),
    ('Pan', 'fa-bread-slice'),
    ('Pastel', 'fa-cake-candles'),
    ('Helado', 'fa-ice-cream'),
    ('Café', 'fa-mug-hot'),
    ('Té', 'fa-mug-saucer'),
    ('Cerveza', 'fa-beer-mug'),
    ('Vino', 'fa-wine-bottle'),
    ('Coctel', 'fa-cocktail'),
    ('Agua', 'fa-droplet'),
    ('Supermercado', 'fa-basket-shopping'),
    ('Carne', 'fa-drumstick-bite'),
    ('Pescado', 'fa-fish'),
    ('Postre', 'fa-candy-cane'),
    ('Desayuno', 'fa-sun'),
    ('Almuerzo', 'fa-cloud-sun'),
    ('Cena', 'fa-moon'),
    # ===== Transporte =====
    ('Auto', 'fa-car'),
    ('Taxi', 'fa-taxi'),
    ('Bus', 'fa-bus'),
    ('Tren', 'fa-train'),
    ('Metro', 'fa-train-subway'),
    ('Avión', 'fa-plane'),
    ('Bicicleta', 'fa-bicycle'),
    ('Moto', 'fa-motorcycle'),
    ('Gasolina', 'fa-gas-pump'),
    ('Estacionamiento', 'fa-square-parking'),
    ('Peaje', 'fa-road'),
    ('Viaje', 'fa-suitcase-rolling'),
    ('Pasaporte', 'fa-passport'),
    ('Carga', 'fa-truck'),
    ('Mudanza', 'fa-truck-moving'),
    ('Batería', 'fa-car-battery'),
    ('Aceite', 'fa-oil-can'),
    ('Ruta', 'fa-route'),
    # ===== Compras =====
    ('Tienda', 'fa-store'),
    ('Ropa', 'fa-shirt'),
    ('Zapatos', 'fa-shoe-prints'),
    ('Joyería', 'fa-gem'),
    ('Regalo', 'fa-gift'),
    ('Electrónica', 'fa-laptop'),
    ('Celular', 'fa-mobile-screen'),
    ('TV', 'fa-tv'),
    ('Videojuego', 'fa-gamepad'),
    ('Música', 'fa-headphones'),
    ('Cine', 'fa-film'),
    ('Libro', 'fa-book'),
    ('Mascota', 'fa-paw'),
    ('Juguete', 'fa-chess-knight'),
    ('Decoración', 'fa-paintbrush'),
    ('Mueble', 'fa-couch'),
    ('Herramienta', 'fa-wrench'),
    ('Farmacia', 'fa-prescription-bottle'),
    ('Bebé', 'fa-baby'),
    ('Boda', 'fa-ring'),
    # ===== Entretenimiento =====
    ('Boleto', 'fa-ticket'),
    ('Palomitas', 'fa-popcorn'),
    ('Concierto', 'fa-guitar'),
    ('Deporte', 'fa-futbol'),
    ('Gimnasio', 'fa-dumbbell'),
    ('Piscina', 'fa-person-swimming'),
    ('Correr', 'fa-person-running'),
    ('Yoga', 'fa-spa'),
    ('Foto', 'fa-camera'),
    ('Arte', 'fa-palette'),
    ('Fiesta', 'fa-champagne-glasses'),
    ('Baile', 'fa-music'),
    ('Lectura', 'fa-book-open'),
    ('Play', 'fa-play'),
    ('Pausa', 'fa-pause'),
    # ===== Hogar =====
    ('Casa', 'fa-house'),
    ('Hipoteca', 'fa-house-chimney'),
    ('Alquiler', 'fa-key'),
    ('Electricidad', 'fa-bolt'),
    ('Agua', 'fa-faucet'),
    ('Gas', 'fa-fire'),
    ('Internet', 'fa-wifi'),
    ('Teléfono', 'fa-phone'),
    ('Mantenimiento', 'fa-wrench'),
    ('Limpieza', 'fa-soap'),
    ('Jardín', 'fa-seedling'),
    ('Seguro hogar', 'fa-shield-house'),
    ('Habitación', 'fa-bed'),
    ('Baño', 'fa-toilet'),
    ('Luz', 'fa-lightbulb'),
    ('Aire', 'fa-fan'),
    ('Calefacción', 'fa-temperature-high'),
    # ===== Salud =====
    ('Salud', 'fa-heart-pulse'),
    ('Hospital', 'fa-hospital'),
    ('Doctor', 'fa-stethoscope'),
    ('Medicina', 'fa-pills'),
    ('Seguro salud', 'fa-shield'),
    ('Emergencia', 'fa-truck-medical'),
    ('Dentista', 'fa-tooth'),
    ('Visión', 'fa-eye'),
    ('Análisis', 'fa-flask'),
    ('Terapia', 'fa-brain'),
    ('Vacuna', 'fa-syringe'),
    ('Venda', 'fa-bandage'),
    ('Peso', 'fa-weight-scale'),
    ('Ejercicio', 'fa-person-walking'),
    # ===== Educación =====
    ('Educación', 'fa-graduation-cap'),
    ('Curso', 'fa-pencil'),
    ('Universidad', 'fa-school'),
    ('Libros', 'fa-book-open'),
    ('Online', 'fa-laptop-code'),
    ('Papelería', 'fa-paperclip'),
    ('Examen', 'fa-clipboard-list'),
    ('Estudio', 'fa-pen-ruler'),
    ('Idioma', 'fa-language'),
    ('Certificado', 'fa-certificate'),
    # ===== Servicios =====
    ('Suscripción', 'fa-arrows-rotate'),
    ('Seguro', 'fa-shield-check'),
    ('Almacenamiento', 'fa-cloud'),
    ('Membresía', 'fa-id-card'),
    ('Tarifa', 'fa-barcode'),
    ('Streaming', 'fa-tower-broadcast'),
    ('Dominio', 'fa-globe'),
    ('Hosting', 'fa-server'),
    # ===== Personas =====
    ('Usuario', 'fa-user'),
    ('Pareja', 'fa-heart'),
    ('Familia', 'fa-users'),
    ('Hijo', 'fa-child'),
    ('Amigo', 'fa-user-group'),
    ('Mascota', 'fa-dog'),
    ('Gato', 'fa-cat'),
    ('Boda', 'fa-ring'),
    ('Cumpleaños', 'fa-cake-candles'),
    # ===== Notificaciones =====
    ('Notificación', 'fa-bell'),
    ('Alarma', 'fa-alarm-clock'),
    ('Recordatorio', 'fa-clock'),
    ('Calendario', 'fa-calendar'),
    ('Correo', 'fa-envelope'),
    ('Mensaje', 'fa-message'),
    ('Llamada', 'fa-phone-volume'),
    ('Alerta', 'fa-circle-exclamation'),
    # ===== Acciones =====
    ('Agregar', 'fa-plus'),
    ('Quitar', 'fa-minus'),
    ('OK', 'fa-circle-check'),
    ('Cancelar', 'fa-circle-xmark'),
    ('Editar', 'fa-pen-to-square'),
    ('Eliminar', 'fa-trash-can'),
    ('Guardar', 'fa-floppy-disk'),
    ('Descargar', 'fa-download'),
    ('Subir', 'fa-upload'),
    ('Buscar', 'fa-search'),
    ('Filtrar', 'fa-filter'),
    ('Configurar', 'fa-gear'),
    ('Compartir', 'fa-share-nodes'),
    ('Favorito', 'fa-star'),
    ('Like', 'fa-thumbs-up'),
    ('Imprimir', 'fa-print'),
    ('Cerrar', 'fa-xmark'),
    ('Menú', 'fa-bars'),
    ('Más', 'fa-ellipsis-vertical'),
    ('Sincronizar', 'fa-arrows-rotate'),
    ('Abrir', 'fa-folder-open'),
    ('Nuevo', 'fa-file-circle-plus'),
    # ===== Seguridad =====
    ('Candado', 'fa-lock'),
    ('Protegido', 'fa-shield-halved'),
    ('PIN', 'fa-fingerprint'),
    ('Privacidad', 'fa-eye-slash'),
    ('Contraseña', 'fa-key'),
    ('Verificado', 'fa-shield-check'),
    ('SSL', 'fa-lock'),
    # ===== Metas y Ahorros =====
    ('Meta', 'fa-bullseye'),
    ('Ahorro', 'fa-piggy-bank'),
    ('Presupuesto', 'fa-chart-simple'),
    ('Plan', 'fa-clipboard-list'),
    ('Objetivo', 'fa-flag-checkered'),
    ('Crecimiento', 'fa-arrow-trend-up'),
    ('Estadística', 'fa-chart-bar'),
    ('Reporte', 'fa-chart-column'),
    # ===== Extra =====
    ('QR', 'fa-qrcode'),
    ('Tag', 'fa-tags'),
    ('Nota', 'fa-note-sticky'),
    ('Link', 'fa-link'),
    ('Globo', 'fa-globe'),
    ('Pin', 'fa-location-dot'),
    ('Mapa', 'fa-map-location-dot'),
    ('Brújula', 'fa-compass'),
    ('Reloj', 'fa-clock'),
    ('Temporizador', 'fa-timer'),
    ('Sol', 'fa-sun'),
    ('Luna', 'fa-moon'),
    ('Nube', 'fa-cloud'),
    ('Lluvia', 'fa-cloud-rain'),
    ('Trueno', 'fa-cloud-bolt'),
    ('Hoja', 'fa-leaf'),
    ('Árbol', 'fa-tree'),
    ('Flor', 'fa-seedling'),
    ('Corona', 'fa-crown'),
    ('Medalla', 'fa-medal'),
    ('Rocket', 'fa-rocket'),
    ('Infinito', 'fa-infinity'),
    ('Bandera', 'fa-flag'),
    ('Corazón', 'fa-heart'),
    ('Estrella', 'fa-star'),
    ('Check', 'fa-check'),
    ('Cruz', 'fa-xmark'),
    ('Info', 'fa-circle-info'),
    ('Ayuda', 'fa-circle-question'),
    ('Advertencia', 'fa-triangle-exclamation'),
]

ICONOS.sort(key=lambda x: x[0].lower())


class Command(BaseCommand):
    help = 'Crea los iconos predefinidos para todos los inquilinos'

    def add_arguments(self, parser):
        parser.add_argument('--tenant', type=str, help='Slug del inquilino (opcional)')

    def handle(self, *args, **options):
        qs = Tenant.objects.filter(activo=True)
        if options['tenant']:
            qs = qs.filter(slug=options['tenant'])

        if not qs.exists():
            self.stdout.write(self.style.WARNING('No hay inquilinos activos.'))
            return

        total_creados = 0
        for tenant in qs:
            user = tenant.usuario_set.first()
            if not user:
                self.stdout.write(self.style.WARNING(
                    f'  {tenant.nombre}: sin usuarios, saltando'
                ))
                continue

            creados = 0
            existentes = 0
            for nombre, clase_css in ICONOS:
                obj, created = Icono.objects.get_or_create(
                    inquilino=tenant,
                    clase_css=clase_css,
                    defaults={
                        'usuario': user,
                        'nombre': nombre,
                        'slug': slugify(nombre),
                    },
                )
                if created:
                    creados += 1
                else:
                    existentes += 1

            total_creados += creados
            self.stdout.write(
                f'  {tenant.nombre}: {creados} creados, {existentes} ya existentes'
            )

        if total_creados:
            self.stdout.write(self.style.SUCCESS(
                f'Total: {total_creados} iconos creados en todos los inquilinos'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('Todo actualizado.'))
