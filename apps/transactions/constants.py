CATEGORIAS_INGRESO_SLUGS = ['ingreso-debito', 'ingreso-efectivo', 'pago-tarjeta']

CATEGORIAS_AJUSTE_SLUGS = ['ajuste-balance-positivo', 'ajuste-balance-negativo']

CAT_INGRESO_MAP = {
    'debito': ('Ingreso Débito', '#1b5e20'),
    'efectivo': ('Ingreso Efectivo', '#388e3c'),
    'credito': ('Pago Tarjeta', '#1565c0'),
}

CAT_AJUSTE_MAP = {
    'positivo': ('Ajuste Balance +', 'ajuste-balance-positivo', '#6a1b9a'),
    'negativo': ('Ajuste Balance -', 'ajuste-balance-negativo', '#e65100'),
}
