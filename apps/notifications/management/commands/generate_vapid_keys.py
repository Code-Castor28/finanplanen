import base64

from django.core.management.base import BaseCommand
from django.conf import settings
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


class Command(BaseCommand):
    help = 'Genera un par de llaves VAPID estándar (raw 32B) y las guarda en .env'

    def handle(self, *args, **options):
        key = ec.generate_private_key(ec.SECP256R1())

        priv_raw = key.private_numbers().private_value.to_bytes(32, 'big')
        priv_b64 = base64.urlsafe_b64encode(priv_raw).rstrip(b'=').decode()

        pub_raw = key.public_key().public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint,
        )
        pub_b64 = base64.urlsafe_b64encode(pub_raw).rstrip(b'=').decode()

        env_path = settings.BASE_DIR / '.env'
        if not env_path.exists():
            self.stdout.write(self.style.ERROR(f'No se encontró {env_path}'))
            return

        content = env_path.read_text()
        lines = content.splitlines()
        nuevas = []
        for line in lines:
            if line.startswith('VAPID_PUBLIC_KEY='):
                nuevas.append(f'VAPID_PUBLIC_KEY={pub_b64}')
            elif line.startswith('VAPID_PRIVATE_KEY='):
                nuevas.append(f'VAPID_PRIVATE_KEY={priv_b64}')
            else:
                nuevas.append(line)
        env_path.write_text('\n'.join(nuevas) + '\n')

        self.stdout.write(self.style.SUCCESS('Llaves VAPID generadas y guardadas en .env'))
        self.stdout.write(f'  VAPID_PUBLIC_KEY={pub_b64}')
        self.stdout.write(f'  VAPID_PRIVATE_KEY={priv_b64}')
