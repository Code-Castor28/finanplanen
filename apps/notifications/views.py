import hashlib
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from .models import SuscripcionPush


def _hash_endpoint(endpoint):
    return hashlib.sha256(endpoint.encode()).hexdigest()


@login_required
@csrf_protect
@require_POST
def guardar_suscripcion(request):
    try:
        datos = json.loads(request.body)
        endpoint = datos.get('endpoint')
        p256dh = datos.get('keys', {}).get('p256dh')
        auth = datos.get('keys', {}).get('auth')

        if not all([endpoint, p256dh, auth]):
            return JsonResponse({'error': 'Datos incompletos'}, status=400)

        suscripcion, creada = SuscripcionPush.objects.update_or_create(
            endpoint_hash=_hash_endpoint(endpoint),
            defaults={
                'usuario': request.user,
                'endpoint': endpoint,
                'p256dh': p256dh,
                'auth': auth,
                'activo': True,
            },
        )

        return JsonResponse({
            'status': 'ok',
            'accion': 'creada' if creada else 'actualizada',
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_protect
@require_POST
def eliminar_suscripcion(request):
    try:
        datos = json.loads(request.body)
        endpoint = datos.get('endpoint')

        if not endpoint:
            return JsonResponse({'error': 'Datos incompletos'}, status=400)

        SuscripcionPush.objects.filter(
            usuario=request.user,
            endpoint_hash=_hash_endpoint(endpoint),
        ).delete()

        return JsonResponse({'status': 'ok'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
