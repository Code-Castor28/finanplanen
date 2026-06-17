from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Genera un nuevo par de llaves VAPID y las escribe en el .env'

    def handle(self, *args, **options):
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives.asymmetric import ec
            import base64
        except ImportError:
            raise CommandError(
                'La librería "cryptography" no está instalada. '
                'Corre: pip install cryptography'
            )

        key = ec.generate_private_key(ec.SECP256R1(), default_backend())

        priv_raw = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        priv_b64 = (
            priv_raw.decode()
            .replace('-----BEGIN PRIVATE KEY-----\n', '')
            .replace('\n-----END PRIVATE KEY-----\n', '')
            .replace('\n', '')
        )

        pub_raw = key.public_key().public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint,
        )
        pub_b64 = base64.urlsafe_b64encode(pub_raw).rstrip(b'=').decode()

        env_path = settings.BASE_DIR / '.env'
        if not env_path.exists():
            self.stdout.write(self.style.ERROR(f'No se encontró {env_path}'))
            return

        lines = env_path.read_text().splitlines()
        nuevas = []
        seen_private = False
        for line in lines:
            if line.startswith('VAPID_PUBLIC_KEY='):
                nuevas.append(f'VAPID_PUBLIC_KEY={pub_b64}')
            elif line.startswith('VAPID_PRIVATE_KEY='):
                if not seen_private:
                    nuevas.append(f'VAPID_PRIVATE_KEY={priv_b64}')
                    seen_private = True
            elif seen_private and line and not line.startswith('VAPID_') and '=' not in line:
                continue
            elif seen_private and line == '':
                nuevas.append(line)
            elif seen_private and line.startswith('VAPID_ADMIN_EMAIL='):
                nuevas.append(line)
                seen_private = False
            else:
                nuevas.append(line)
        env_path.write_text('\n'.join(nuevas) + '\n')

        self.stdout.write(self.style.SUCCESS('Llaves VAPID generadas y guardadas en .env'))
        self.stdout.write(f'  VAPID_PUBLIC_KEY={pub_b64}')
        self.stdout.write(f'  VAPID_PRIVATE_KEY={priv_b64}')
