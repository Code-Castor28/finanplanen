import platform
from django.utils import timezone
from django.conf import settings
from django.shortcuts import render


class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._is_maintenance_active():
            if request.path.startswith('/admin/'):
                return self.get_response(request)

            end_time = settings.MAINTENANCE_END_TIME
            seconds = 0
            end_time_display = None

            if end_time:
                delta = end_time - timezone.now()
                seconds = max(int(delta.total_seconds()), 0)
                end_time_display = "{} de {} de {}, {}:{} {}".format(
                    end_time.day,
                    end_time.strftime('%B'),
                    end_time.year,
                    end_time.strftime('%I').lstrip('0') or '12',
                    end_time.strftime('%M'),
                    'a.m.' if end_time.hour < 12 else 'p.m.'
                )

            response = render(request, 'Maintenance.html', {
                'seconds_remaining': seconds,
                'support_email': settings.MAINTENANCE_SUPPORT_EMAIL,
                'end_time_display': end_time_display,
            })
            response.status_code = 503
            return response

        return self.get_response(request)

    def _is_maintenance_active(self):
        if not getattr(settings, 'MAINTENANCE_MODE', False):
            return False
        end_time = getattr(settings, 'MAINTENANCE_END_TIME', None)
        if end_time and timezone.now() >= end_time:
            return False
        return True