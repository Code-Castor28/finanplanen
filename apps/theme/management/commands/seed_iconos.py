from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.theme.models import Icono
from apps.users.models import Tenant

ICONOS = [
    # ===== TARJETAS Y CUENTAS =====
    ('Billetera', 'fa-wallet'),
    ('Tarjeta de Crédito', 'fa-credit-card'),
    ('Banco', 'fa-building-columns'),
    ('Dinero en Efectivo', 'fa-money-bill'),
    ('Billetes', 'fa-money-bills'),
    ('Monedas', 'fa-coins'),
    ('Dólar', 'fa-dollar-sign'),
    ('Euro', 'fa-euro-sign'),
    ('Balance', 'fa-scale-balanced'),
    ('Cheque', 'fa-money-check'),
    ('Bolsa de Dinero', 'fa-sack-dollar'),
    ('Caja de Ahorros', 'fa-box-open'),
    ('Alcancía', 'fa-piggy-bank'),
    ('Transferencia', 'fa-arrow-right-arrow-left'),
    ('Porcentaje o Comisión', 'fa-percent'),
    ('Intereses', 'fa-chart-simple'),

    # ===== INGRESOS =====
    ('Ingresos Generales', 'fa-arrow-trend-up'),
    ('Salario o Trabajo', 'fa-briefcase'),
    ('Depósito', 'fa-circle-dollar-to-slot'),
    ('Ganancia Flujo', 'fa-money-bill-wave'),
    ('Factura Cobrada', 'fa-file-invoice-dollar'),
    ('Inversión', 'fa-chart-pie'),
    ('Bono o Recompensa', 'fa-award'),
    ('Devolución', 'fa-rotate-left'),
    ('Venta o Etiqueta', 'fa-tag'),
    ('Propina', 'fa-hand-holding-dollar'),
    ('Premio', 'fa-trophy'),
    ('Herencia o Gema', 'fa-gem'),

    # ===== GASTOS =====
    ('Gastos Generales', 'fa-arrow-trend-down'),
    ('Compras Carrito', 'fa-cart-shopping'),
    ('Compras Bolsa', 'fa-bag-shopping'),
    ('Factura por Pagar', 'fa-receipt'),
    ('Recibo', 'fa-file-invoice'),
    ('Impuestos', 'fa-file-lines'),
    ('Multa o Alerta', 'fa-circle-exclamation'),
    ('Suscripciones', 'fa-arrows-rotate'),
    ('Préstamo o Cuota', 'fa-hand-holding-hand'),
    ('Donación', 'fa-hand-holding-heart'),
    ('Gasto Variable', 'fa-chart-line'),

    # ===== ALIMENTACIÓN =====
    ('Comida o Restaurante', 'fa-utensils'),
    ('Plato de Comida', 'fa-bowl-food'),
    ('Hamburguesa', 'fa-burger'),
    ('Pizza', 'fa-pizza-slice'),
    ('Comida Rápida', 'fa-hotdog'),
    ('Zanahoria', 'fa-carrot'),
    ('Fruta', 'fa-apple-whole'),
    ('Vegetales', 'fa-leaf'),
    ('Huevo', 'fa-egg'),
    ('Queso', 'fa-cheese'),
    ('Pan', 'fa-bread-slice'),
    ('Pastel', 'fa-cake-candles'),
    ('Helado', 'fa-ice-cream'),
    ('Café', 'fa-mug-hot'),
    ('Té', 'fa-mug-saucer'),
    ('Cerveza', 'fa-beer-mug-empty'),
    ('Vino', 'fa-wine-bottle'),
    ('Coctel', 'fa-martini-glass-citrus'),
    ('Agua', 'fa-droplet'),
    ('Supermercado', 'fa-basket-shopping'),
    ('Carne', 'fa-drumstick-bite'),
    ('Pescado', 'fa-fish'),
    ('Dulces', 'fa-candy-cane'),

    # ===== TRANSPORTE Y VIAJES =====
    ('Automóvil', 'fa-car'),
    ('Taxi', 'fa-taxi'),
    ('Autobús', 'fa-bus'),
    ('Tren', 'fa-train'),
    ('Metro', 'fa-train-subway'),
    ('Avión', 'fa-plane'),
    ('Bicicleta', 'fa-bicycle'),
    ('Motocicleta', 'fa-motorcycle'),
    ('Gasolina', 'fa-gas-pump'),
    ('Estacionamiento', 'fa-square-parking'),
    ('Peaje o Carretera', 'fa-road'),
    ('Viajes Equipaje', 'fa-suitcase-rolling'),
    ('Pasaporte', 'fa-passport'),
    ('Camión de Carga', 'fa-truck'),
    ('Mudanza', 'fa-truck-moving'),
    ('Mantenimiento Auto', 'fa-car-battery'),
    ('Aceite Motor', 'fa-oil-can'),
    ('Ruta o Mapa', 'fa-route'),

    # ===== COMPRAS Y TECNOLOGÍA =====
    ('Tienda Física', 'fa-store'),
    ('Ropa', 'fa-shirt'),
    ('Calzado', 'fa-shoe-prints'),
    ('Regalo', 'fa-gift'),
    ('Computadora', 'fa-laptop'),
    ('Teléfono Celular', 'fa-mobile-screen-button'),
    ('Televisión', 'fa-tv'),
    ('Videojuegos', 'fa-gamepad'),
    ('Auriculares', 'fa-headphones'),
    ('Cine', 'fa-film'),
    ('Libro', 'fa-book'),
    ('Muebles', 'fa-couch'),
    ('Herramientas', 'fa-wrench'),
    ('Farmacia', 'fa-prescription-bottle'),
    ('Bebé', 'fa-baby'),

    # ===== ENTRETENIMIENTO Y DEPORTES =====
    ('Boleto', 'fa-ticket'),
    ('Música o Guitarra', 'fa-guitar'),
    ('Fútbol', 'fa-futbol'),
    ('Gimnasio', 'fa-dumbbell'),
    ('Natación', 'fa-person-swimming'),
    ('Correr', 'fa-person-running'),
    ('Spa o Yoga', 'fa-spa'),
    ('Cámara', 'fa-camera'),
    ('Arte', 'fa-palette'),
    ('Celebración', 'fa-champagne-glasses'),

    # ===== HOGAR Y SERVICIOS =====
    ('Casa', 'fa-house'),
    ('Hipoteca', 'fa-house-chimney'),
    ('Alquiler Llave', 'fa-key'),
    ('Electricidad', 'fa-bolt'),
    ('Agua Grifo', 'fa-faucet'),
    ('Gas o Fuego', 'fa-fire'),
    ('Internet WiFi', 'fa-wifi'),
    ('Teléfono Fijo', 'fa-phone'),
    ('Limpieza', 'fa-soap'),
    ('Jardín', 'fa-seedling'),
    ('Seguro Hogar', 'fa-shield-cat'),
    ('Cama', 'fa-bed'),
    ('Baño', 'fa-toilet'),
    ('Iluminación', 'fa-lightbulb'),
    ('Ventilación', 'fa-fan'),
    ('Calefacción', 'fa-temperature-high'),

    # ===== SALUD =====
    ('Salud Corazón', 'fa-heart-pulse'),
    ('Hospital', 'fa-hospital'),
    ('Estetoscopio', 'fa-stethoscope'),
    ('Medicinas', 'fa-pills'),
    ('Seguro de Salud', 'fa-shield-halved'),
    ('Ambulancia', 'fa-truck-medical'),
    ('Dentista', 'fa-tooth'),
    ('Visión', 'fa-eye'),
    ('Laboratorio', 'fa-flask'),
    ('Salud Mental', 'fa-brain'),
    ('Vacuna', 'fa-syringe'),
    ('Vendaje', 'fa-bandage'),
    ('Báscula', 'fa-weight-scale'),
    ('Caminar', 'fa-person-walking'),

    # ===== EDUCACIÓN =====
    ('Educación Graduación', 'fa-graduation-cap'),
    ('Lápiz', 'fa-pencil'),
    ('Escuela o Universidad', 'fa-school'),
    ('Libro Abierto', 'fa-book-open'),
    ('Programación', 'fa-laptop-code'),
    ('Clip', 'fa-paperclip'),
    ('Examen o Lista', 'fa-clipboard-list'),
    ('Regla y Lápiz', 'fa-pen-ruler'),
    ('Idiomas', 'fa-language'),
    ('Certificado', 'fa-certificate'),

    # ===== SERVICIOS DIGITALES =====
    ('Nube', 'fa-cloud'),
    ('Identificación', 'fa-id-card'),
    ('Código de Barras', 'fa-barcode'),
    ('Transmisión', 'fa-tower-broadcast'),
    ('Web', 'fa-globe'),
    ('Servidor o Hosting', 'fa-server'),

    # ===== PERSONAS Y MASCOTAS =====
    ('Usuario Individual', 'fa-user'),
    ('Pareja o Amor', 'fa-heart'),
    ('Familia', 'fa-users'),
    ('Hijo', 'fa-child'),
    ('Grupo', 'fa-user-group'),
    ('Perro', 'fa-dog'),
    ('Gato', 'fa-cat'),

    # ===== NOTIFICACIONES Y ACCIONES =====
    ('Campana', 'fa-bell'),
    ('Reloj', 'fa-clock'),
    ('Calendario', 'fa-calendar'),
    ('Email', 'fa-envelope'),
    ('Mensaje', 'fa-message'),
    ('Llamada Volumen', 'fa-phone-volume'),
    ('Agregar', 'fa-plus'),
    ('Quitar', 'fa-minus'),
    ('Éxito', 'fa-circle-check'),
    ('Error', 'fa-circle-xmark'),
    ('Editar', 'fa-pen-to-square'),
    ('Eliminar', 'fa-trash-can'),
    ('Guardar', 'fa-floppy-disk'),
    ('Descargar', 'fa-download'),
    ('Subir', 'fa-upload'),
    ('Buscar', 'fa-magnifying-glass'),
    ('Filtrar', 'fa-filter'),
    ('Configuración', 'fa-gear'),
    ('Compartir', 'fa-share-nodes'),
    ('Estrella', 'fa-star'),
    ('Imprimir', 'fa-print'),
    ('Menú Hamburguesa', 'fa-bars'),

    # ===== METAS Y SEGURIDAD =====
    ('Candado Cerrado', 'fa-lock'),
    ('Huella Digital', 'fa-fingerprint'),
    ('Ojo Oculto', 'fa-eye-slash'),
    ('Meta Objetivo', 'fa-bullseye'),
    ('Bandera de Meta', 'fa-flag-checkered'),
    ('Estadística Barras', 'fa-chart-bar'),
    ('Estadística Columnas', 'fa-chart-column'),
    ('Código QR', 'fa-qrcode'),
    ('Etiquetas', 'fa-tags'),
    ('Nota Adhesiva', 'fa-note-sticky'),
    ('Enlace', 'fa-link'),
    ('Ubicación Pin', 'fa-location-dot'),
    ('Mapa Destino', 'fa-map-location-dot'),
    ('Brújula', 'fa-compass'),
    ('Cohete', 'fa-rocket'),
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
            actualizados = 0
            existentes = 0
            for nombre, clase_css in ICONOS:
                defaults = {
                    'usuario': user,
                    'nombre': nombre,
                    'slug': slugify(clase_css),
                }
                obj, created = Icono.objects.update_or_create(
                    inquilino=tenant,
                    clase_css=clase_css,
                    defaults=defaults,
                )
                if created:
                    creados += 1
                else:
                    if obj.nombre != nombre or obj.slug != defaults['slug']:
                        for k, v in defaults.items():
                            setattr(obj, k, v)
                        obj.save()
                        actualizados += 1
                    else:
                        existentes += 1

            total_creados += creados
            self.stdout.write(
                f'  {tenant.nombre}: {creados} creados, {actualizados} actualizados, {existentes} sin cambios'
            )

            # Second pass: fix icons with correct nombre but wrong clase_css
            clases_seed = {c for _, c in ICONOS}
            mapa_nombre_clase = dict(ICONOS)
            corregidos = 0
            for icono in Icono.objects.filter(inquilino=tenant):
                if icono.clase_css not in clases_seed and icono.nombre in mapa_nombre_clase:
                    clase_correcta = mapa_nombre_clase[icono.nombre]
                    if Icono.objects.filter(inquilino=tenant, clase_css=clase_correcta).exists():
                        # Ya existe otro con la clase correcta, eliminar este (duplicado corrupto)
                        icono.delete()
                        corregidos += 1
                    else:
                        icono.clase_css = clase_correcta
                        icono.slug = slugify(clase_correcta)
                        icono.save()
                        corregidos += 1
            if corregidos:
                self.stdout.write(f'    {corregidos} iconos corregidos (clase_css incorrecta)')

        if total_creados:
            self.stdout.write(self.style.SUCCESS(
                f'Total: {total_creados} iconos creados en todos los inquilinos'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('Todo actualizado.'))
