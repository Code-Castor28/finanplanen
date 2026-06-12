from django.urls import resolve

SECTION_MAP = {
    'core:inicio': 'dashboard',
    'accounts:lista': 'accounts',
    'budgets:lista': 'budgets',
    'categories:lista': 'categories',
    'savings:lista': 'savings',
    'transactions:lista': 'transactions',
    'transactions:ingresos': 'ingresos',
    'transactions:gastos': 'gastos',
    'transfers:lista': 'transfers',
    'theme:colores_lista': 'theme_colores',
    'theme:iconos_lista': 'theme_iconos',
    'users:perfil': 'profile',
}


def section(request):
    try:
        match = resolve(request.path_info)
        url_name = f'{match.namespace}:{match.url_name}' if match.namespace else match.url_name
        return {'section': SECTION_MAP.get(url_name, '')}
    except Exception:
        return {}
