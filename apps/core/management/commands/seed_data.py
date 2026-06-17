import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from django.contrib.auth.hashers import make_password
from apps.users.models import Usuario, Tenant
from apps.notifications.models import SuscripcionPush
from apps.theme.models import Color, Icono
from apps.categories.models import Categoria
from apps.accounts.models import Cuenta
from apps.transactions.models import Ingreso, Gasto
from apps.transfers.models import Transferencia
from apps.savings.models import MetaAhorro, DepositoAhorro
from apps.budgets.models import Presupuesto

COLORS = [
    ('Rojo', '#e53935'), ('Azul', '#1e88e5'), ('Verde', '#43a047'),
    ('Naranja', '#fb8c00'), ('Purpura', '#8e24aa'), ('Marron', '#6d4c41'),
    ('Gris', '#757575'), ('Rosa', '#d81b60'), ('Verde Salario', '#2e7d32'),
    ('Azul Freelance', '#1565c0'), ('Dorado', '#f9a825'), ('Turquesa', '#00897b'),
    ('Vinotinto', '#880e4f'), ('Cian', '#00acc1'), ('Lima', '#c0ca33'),
]

ICONS = [
    ('Utensilios', 'fa-utensils'), ('Coche', 'fa-car'), ('Casa', 'fa-house'),
    ('Salud', 'fa-heart-pulse'), ('Juegos', 'fa-gamepad'), ('Internet', 'fa-wifi'),
    ('Compra', 'fa-cart-shopping'), ('Viaje', 'fa-plane'), ('Regalo', 'fa-gift'),
    ('Dinero', 'fa-sack-dollar'), ('Maletin', 'fa-briefcase'), ('Grafico', 'fa-chart-line'),
    ('Tarjeta', 'fa-credit-card'), ('Alcancia', 'fa-piggy-bank'), ('Banco', 'fa-building-columns'),
    ('Laptop', 'fa-laptop-code'), ('Libro', 'fa-book'), ('Gimnasio', 'fa-dumbbell'),
]

CATEGORIAS_INGRESO = [
    ('Salario', 'fa-briefcase', 'Verde Salario'),
    ('Freelance', 'fa-laptop-code', 'Azul Freelance'),
    ('Inversiones', 'fa-chart-line', 'Dorado'),
    ('Regalos', 'fa-gift', 'Turquesa'),
]

CATEGORIAS_GASTO = [
    ('Comida', 'fa-utensils', 'Rojo'),
    ('Transporte', 'fa-car', 'Azul'),
    ('Vivienda', 'fa-house', 'Marron'),
    ('Salud', 'fa-heart-pulse', 'Verde'),
    ('Ocio', 'fa-gamepad', 'Naranja'),
    ('Suscripciones', 'fa-wifi', 'Purpura'),
    ('Ropa', 'fa-cart-shopping', 'Rosa'),
    ('Gimnasio', 'fa-dumbbell', 'Lima'),
]

CUENTAS_TEMPLATE = [
    ('Cuenta Principal', 'debito', 'Banco de Reservas', '1234'),
    ('Ahorros', 'debito', 'Banco Popular', '5678'),
    ('Efectivo', 'efectivo', '', ''),
    ('Visa Oro', 'credito', 'Banco de Reservas', '9012'),
    ('Mastercard Black', 'credito', 'Banco Popular', '3456'),
    ('BHD León', 'debito', 'BHD León', '7890'),
]

NOMBRES_COMERCIO = [
    'Supermercado Nacional', 'Sirena', 'Ave y Cia', 'Texaco', 'Shell',
    'Aguas del Norte', 'Claro', 'Altice', 'Uber', 'Indrive',
    'McDonald\'s', 'Pizza Hut', 'Burger King', 'Hard Rock Cafe',
    'Cineplex', 'Dave & Buster\'s', 'La Sirena', 'Jumbo',
    'Corotos.com', 'Amazon', 'Netflix', 'Spotify', 'Disney+',
    'Farmacia Carol', 'Farmacia Popular', 'Hospital Metropolitano',
    'CLEAN & EASY', 'Lavandería Lavatex',
    'Tienda Olimpica', 'IKEA', 'Adidas', 'Nike',
    'Planeta Azul', 'JetBlue', 'Delta Airlines',
    'Banco Popular', 'Banco de Reservas', 'BHD León',
    'Orange', 'Viva', 'Wingo',
]


def _sig(seq):
    return (seq._sa_instance_state or None) or True


class Command(BaseCommand):
    help = 'Crea datos de prueba masivos para evaluar rendimiento'

    def add_arguments(self, parser):
        parser.add_argument('--usuarios', type=int, default=2)
        parser.add_argument('--meses', type=int, default=12)
        parser.add_argument('--gastos', type=int, default=500)
        parser.add_argument('--ingresos', type=int, default=200)
        parser.add_argument('--reset', action='store_true')

    def handle(self, *args, **options):
        num_usuarios = options['usuarios']
        meses = options['meses']
        num_gastos = options['gastos']
        num_ingresos = options['ingresos']
        reset = options['reset']

        hoy = date.today()
        desde = hoy - timedelta(days=meses * 30)

        if reset:
            self._reset_data()

        usuarios = self._crear_usuarios(num_usuarios)
        stats_globales = {
            'usuarios': 0, 'colores': 0, 'iconos': 0,
            'cuentas': 0, 'categorias': 0, 'ingresos': 0,
            'gastos': 0, 'transferencias': 0, 'metas': 0,
            'depositos': 0, 'presupuestos': 0,
        }

        for usuario in usuarios:
            inquilino = usuario.inquilino
            colores = self._crear_colores(inquilino, usuario)
            iconos = self._crear_iconos(inquilino, usuario)
            cat_ingreso = self._crear_categorias(
                inquilino, usuario, CATEGORIAS_INGRESO, colores, iconos
            )
            cat_gasto = self._crear_categorias(
                inquilino, usuario, CATEGORIAS_GASTO, colores, iconos
            )
            cuentas = self._crear_cuentas(inquilino, usuario, colores, iconos)

            cuentas_deb = [c for c in cuentas if c.tipo == 'debito']
            cuentas_ef = [c for c in cuentas if c.tipo == 'efectivo']
            cuentas_cr = [c for c in cuentas if c.tipo == 'credito']
            cuentas_ingreso = cuentas_deb + cuentas_ef

            ingresos = self._crear_ingresos(
                inquilino, usuario, cuentas_ingreso, cat_ingreso,
                num_ingresos, desde, hoy
            )
            gastos = self._crear_gastos(
                inquilino, usuario, cuentas, cat_gasto,
                num_gastos, desde, hoy
            )

            transfers = []
            if cuentas_deb:
                transfers = self._crear_transferencias(
                    inquilino, usuario, cuentas_deb, desde, hoy
                )

            metas = self._crear_metas(inquilino, usuario, colores, iconos)
            depositos = []
            for meta in metas:
                d = self._crear_depositos(inquilino, usuario, meta, desde, hoy)
                depositos.extend(d)

            presupuestos = self._crear_presupuestos(
                inquilino, usuario, cat_gasto, meses
            )

            self._recalcular_balances(cuentas)
            self._recalcular_metas(metas)
            self._recalcular_presupuestos(inquilino, presupuestos)

            stats_globales['usuarios'] += 1
            stats_globales['colores'] += len(colores)
            stats_globales['iconos'] += len(iconos)
            stats_globales['categorias'] += len(cat_ingreso) + len(cat_gasto)
            stats_globales['cuentas'] += len(cuentas)
            stats_globales['ingresos'] += len(ingresos)
            stats_globales['gastos'] += len(gastos)
            stats_globales['transferencias'] += len(transfers)
            stats_globales['metas'] += len(metas)
            stats_globales['depositos'] += len(depositos)
            stats_globales['presupuestos'] += len(presupuestos)

            self.stdout.write(f'  ✓ {usuario.nombre_usuario}: '
                              f'{len(ingresos)} ingresos, {len(gastos)} gastos, '
                              f'{len(transfers)} transferencias')

        total = sum(stats_globales.values())
        detalle = ', '.join(f'{k}: {v}' for k, v in stats_globales.items())
        self.stdout.write(f'\n✅ {total} registros creados ({detalle})')

    def _reset_data(self):
        self.stdout.write('Eliminando datos existentes...')
        Presupuesto.objects.all().delete()
        DepositoAhorro.objects.all().delete()
        MetaAhorro.objects.all().delete()
        Transferencia.objects.all().delete()
        Gasto.objects.all().delete()
        Ingreso.objects.all().delete()
        Cuenta.objects.all().delete()
        Categoria.objects.all().delete()
        SuscripcionPush.objects.all().delete()
        Icono.objects.all().delete()
        Color.objects.all().delete()
        Usuario.objects.filter(is_superuser=False).delete()
        Tenant.objects.exclude(usuario__is_superuser=True).delete()
        self.stdout.write('  OK')

    def _crear_usuarios(self, num):
        usuarios = []
        for i in range(num):
            username = f'testuser{i+1}'
            u, created = Usuario.objects.get_or_create(
                nombre_usuario=username,
                defaults={
                    'nombre': f'Test{i+1}',
                    'apellido': 'Usuario',
                    'correo': f'{username}@test.com',
                    'password': make_password('Test123456'),
                    'ingreso_mensual': Decimal(f'{random.randint(30000, 90000)}.00'),
                },
            )
            if created:
                u.refresh_from_db()
            usuarios.append(u)
        self.stdout.write(f'  ✓ {len(usuarios)} usuarios creados', self.style.SUCCESS)
        return usuarios

    def _crear_colores(self, inquilino, usuario):
        objs = []
        for nombre, hex_val in COLORS:
            slug = nombre.lower().replace(' ', '-')
            obj = Color.objects.create(
                inquilino=inquilino, usuario=usuario,
                nombre=nombre, slug=slug, hex=hex_val,
            )
            objs.append(obj)
        return objs

    def _crear_iconos(self, inquilino, usuario):
        objs = []
        for nombre, clase in ICONS:
            slug = nombre.lower().replace(' ', '-')
            obj = Icono.objects.create(
                inquilino=inquilino, usuario=usuario,
                nombre=nombre, slug=slug, clase_css=clase,
            )
            objs.append(obj)
        return objs

    def _crear_categorias(self, inquilino, usuario, plantilla, colores, iconos):
        objs = []
        color_map = {c.nombre: c for c in colores}
        icono_map = {i.nombre: i for i in iconos}
        for nombre, icono_nombre, color_nombre in plantilla:
            color = color_map.get(color_nombre)
            icono = icono_map.get(icono_nombre)
            slug = nombre.lower().replace(' ', '-')
            obj = Categoria.objects.create(
                inquilino=inquilino, usuario=usuario,
                nombre=nombre, slug=slug,
                icono=icono, color=color,
            )
            objs.append(obj)
        return objs

    def _crear_cuentas(self, inquilino, usuario, colores, iconos):
        objs = []
        hoy = date.today()
        for i, (nombre, tipo, emisor, digitos) in enumerate(CUENTAS_TEMPLATE):
            slug = f'{nombre.lower().replace(" ", "-")}-{usuario.pk}'
            color = colores[i % len(colores)]
            icono = iconos[i % len(iconos)]
            kwargs = {
                'inquilino': inquilino,
                'usuario': usuario,
                'nombre': nombre,
                'slug': slug,
                'tipo': tipo,
                'color': color,
                'icono': icono,
                'balance': Decimal('0.00'),
                'emisor': emisor,
                'ultimos_digitos': digitos,
                'activo': True,
            }
            if tipo == 'credito':
                kwargs['dia_corte'] = str(random.choice([5, 10, 15, 20]))
                kwargs['dia_pago'] = str(random.choice([8, 13, 18, 23, 28]))
                kwargs['vencimiento'] = f'12/2{random.randint(6, 9)}'
            # Primeras 2 tarjetas crédito: dia_pago cercano para probar push
            if tipo == 'credito' and len([c for c in objs if c.tipo == 'credito']) < 2:
                kwargs['dia_pago'] = str(min(hoy.day + random.choice([0, 2, 5, 7]), 28))
            obj = Cuenta.objects.create(**kwargs)
            objs.append(obj)
        return objs

    def _crear_ingresos(self, inquilino, usuario, cuentas, categorias, total, desde, hoy):
        if not cuentas or not categorias or total == 0:
            return []
        objs = []
        dias_total = (hoy - desde).days
        for _ in range(total):
            dias_offset = random.randint(0, max(dias_total, 1))
            fecha = desde + timedelta(days=dias_offset)
            monto = Decimal(f'{random.uniform(5000, 80000):.2f}')
            objs.append(Ingreso(
                inquilino=inquilino, usuario=usuario,
                cuenta=random.choice(cuentas),
                categoria=random.choice(categorias),
                monto=monto, fecha=fecha,
                nota=random.choice(NOMBRES_COMERCIO),
            ))
        return Ingreso.objects.bulk_create(objs, batch_size=500)

    def _crear_gastos(self, inquilino, usuario, cuentas, categorias, total, desde, hoy):
        if not cuentas or not categorias or total == 0:
            return []
        objs = []
        dias_total = (hoy - desde).days
        for _ in range(total):
            dias_offset = random.randint(0, max(dias_total, 1))
            fecha = desde + timedelta(days=dias_offset)
            monto = Decimal(f'{random.uniform(150, 25000):.2f}')
            objs.append(Gasto(
                inquilino=inquilino, usuario=usuario,
                cuenta=random.choice(cuentas),
                categoria=random.choice(categorias),
                monto=monto, fecha=fecha,
                nota=random.choice(NOMBRES_COMERCIO),
            ))
        return Gasto.objects.bulk_create(objs, batch_size=500)

    def _crear_transferencias(self, inquilino, usuario, cuentas, desde, hoy):
        if len(cuentas) < 2:
            return []
        objs = []
        dias_total = (hoy - desde).days
        for _ in range(min(30, len(cuentas) * 5)):
            origen, destino = random.sample(cuentas, 2)
            dias_offset = random.randint(0, max(dias_total, 1))
            fecha = desde + timedelta(days=dias_offset)
            monto = Decimal(f'{random.uniform(1000, 15000):.2f}')
            objs.append(Transferencia(
                inquilino=inquilino, usuario=usuario,
                origen=origen, destino=destino,
                monto=monto, fecha=fecha,
                nota='Transferencia entre cuentas',
            ))
        return Transferencia.objects.bulk_create(objs)

    def _crear_metas(self, inquilino, usuario, colores, iconos):
        metas_data = [
            ('Viaje a Europa', Decimal('250000.00'), 365),
            ('Fondo de Emergencia', Decimal('100000.00'), 180),
            ('Nuevo Celular', Decimal('45000.00'), 90),
        ]
        objs = []
        for nombre, meta_monto, dias in metas_data:
            color = random.choice(colores)
            icono = random.choice(iconos)
            slug = nombre.lower().replace(' ', '-') + f'-{usuario.pk}'
            obj = MetaAhorro.objects.create(
                inquilino=inquilino, usuario=usuario,
                nombre=nombre, slug=slug, meta=meta_monto,
                monto_actual=Decimal('0.00'),
                fecha_limite=date.today() + timedelta(days=dias),
                color=color, icono=icono,
            )
            objs.append(obj)
        return objs

    def _crear_depositos(self, inquilino, usuario, meta, desde, hoy):
        objs = []
        dias_total = (hoy - desde).days
        num = random.randint(3, 8)
        for _ in range(num):
            dias_offset = random.randint(0, max(dias_total, 1))
            fecha = desde + timedelta(days=dias_offset)
            monto = Decimal(f'{random.uniform(500, 5000):.2f}')
            obj = DepositoAhorro.objects.create(
                inquilino=inquilino, usuario=usuario,
                meta=meta, monto=monto, fecha=fecha,
                nota=f'Depósito #{_+1}',
            )
            objs.append(obj)
        return objs

    def _crear_presupuestos(self, inquilino, usuario, categorias, meses):
        if not categorias:
            return []
        objs = []
        hoy = date.today()
        cat_principal = categorias[0] if categorias else None
        for i in range(meses):
            m = hoy.month - i
            y = hoy.year
            while m <= 0:
                m += 12
                y -= 1
            limite = Decimal(f'{random.randint(15000, 40000)}.00')
            objs.append(Presupuesto(
                inquilino=inquilino, usuario=usuario,
                categoria=cat_principal,
                monto_limite=limite, monto_gastado=Decimal('0.00'),
                mes=m, año=y,
            ))
        return Presupuesto.objects.bulk_create(objs)

    def _recalcular_balances(self, cuentas):
        for cuenta in cuentas:
            total_ing = Ingreso.objects.filter(
                cuenta=cuenta
            ).aggregate(s=Sum('monto'))['s'] or 0
            total_gas = Gasto.objects.filter(
                cuenta=cuenta
            ).aggregate(s=Sum('monto'))['s'] or 0
            total_transf_in = Transferencia.objects.filter(
                destino=cuenta
            ).aggregate(s=Sum('monto'))['s'] or 0
            total_transf_out = Transferencia.objects.filter(
                origen=cuenta
            ).aggregate(s=Sum('monto'))['s'] or 0
            cuenta.balance = total_ing - total_gas + total_transf_in - total_transf_out
            cuenta.save(update_fields=['balance'])

    def _recalcular_metas(self, metas):
        for meta in metas:
            total = DepositoAhorro.objects.filter(
                meta=meta
            ).aggregate(s=Sum('monto'))['s'] or 0
            MetaAhorro.objects.filter(pk=meta.pk).update(monto_actual=total)

    def _recalcular_presupuestos(self, inquilino, presupuestos):
        for p in presupuestos:
            total = Gasto.objects.filter(
                inquilino=inquilino,
                categoria=p.categoria,
                fecha__month=p.mes,
                fecha__year=p.año,
            ).aggregate(s=Sum('monto'))['s'] or 0
            Presupuesto.objects.filter(pk=p.pk).update(monto_gastado=total)
