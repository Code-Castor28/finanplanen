from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.theme.models import Color
from apps.users.models import Tenant

COLORES = [
    ('Verde esmeralda', '#2ECC71'),
    ('Verde', '#27AE60'),
    ('Verde oscuro', '#1E8449'),
    ('Verde menta', '#A8E6CF'),
    ('Verde lima', '#AED581'),
    ('Rojo', '#E74C3C'),
    ('Rojo oscuro', '#C0392B'),
    ('Rojo coral', '#FF6B6B'),
    ('Rosa', '#E91E63'),
    ('Rosa pastel', '#F8BBD0'),
    ('Azul', '#3498DB'),
    ('Azul oscuro', '#2980B9'),
    ('Azul marino', '#1A5276'),
    ('Azul cielo', '#87CEEB'),
    ('Azul acero', '#4A90D9'),
    ('Celeste', '#D6EAF8'),
    ('Amarillo', '#F1C40F'),
    ('Amarillo pastel', '#FFF9C4'),
    ('Mostaza', '#FFD54F'),
    ('Naranja', '#E67E22'),
    ('Naranja oscuro', '#D35400'),
    ('Durazno', '#FFCC80'),
    ('Morado', '#9B59B6'),
    ('Morado oscuro', '#8E44AD'),
    ('Lavanda', '#B39DDB'),
    ('Vino tinto', '#6C3483'),
    ('Teal', '#1ABC9C'),
    ('Verde azulado', '#16A085'),
    ('Gris claro', '#BDC3C7'),
    ('Gris', '#95A5A6'),
    ('Gris oscuro', '#7F8C8D'),
    ('Marrón', '#795548'),
    ('Oro', '#D4AF37'),
    ('Plata', '#C0C0C0'),
    ('Lima', '#CDDC39'),
    ('Índigo', '#3F51B5'),
    ('Cian', '#00BCD4'),
    ('Ámbar', '#FFC107'),
    ('Deep púrpura', '#673AB7'),
    ('Salmón', '#FA8072'),
]


class Command(BaseCommand):
    help = 'Crea los colores predefinidos para todos los inquilinos'

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
            for nombre, hex_color in COLORES:
                slug = slugify(hex_color.lstrip('#'))
                defaults = {
                    'usuario': user,
                    'nombre': nombre,
                    'slug': slug,
                }
                obj, created = Color.objects.update_or_create(
                    inquilino=tenant,
                    hex=hex_color,
                    defaults=defaults,
                )
                if created:
                    creados += 1
                else:
                    if obj.nombre != nombre or obj.slug != slug:
                        obj.nombre = nombre
                        obj.slug = slug
                        obj.save()
                        actualizados += 1
                    else:
                        existentes += 1

            total_creados += creados
            self.stdout.write(
                f'  {tenant.nombre}: {creados} creados, {actualizados} actualizados, {existentes} sin cambios'
            )

            # Second pass: fix colors with correct nombre but wrong hex
            hex_seed = {c for _, c in COLORES}
            mapa_nombre_hex = dict(COLORES)
            corregidos = 0
            for color in Color.objects.filter(inquilino=tenant):
                if color.hex not in hex_seed and color.nombre in mapa_nombre_hex:
                    hex_correcto = mapa_nombre_hex[color.nombre]
                    if Color.objects.filter(inquilino=tenant, hex=hex_correcto).exists():
                        color.delete()
                        corregidos += 1
                    else:
                        color.hex = hex_correcto
                        color.save()
                        corregidos += 1
            if corregidos:
                self.stdout.write(f'    {corregidos} colores corregidos (hex incorrecto)')

        if total_creados:
            self.stdout.write(self.style.SUCCESS(
                f'Total: {total_creados} colores creados en todos los inquilinos'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('Todo actualizado.'))
