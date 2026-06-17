import base64

from django.conf import settings
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def get_vapid_private_key_pem():
    raw_priv_str = settings.VAPID_PRIVATE_KEY
    raw_pub_str = settings.VAPID_PUBLIC_KEY

    if not raw_priv_str or not raw_pub_str:
        raise ValueError("Las llaves VAPID no están configuradas en el entorno.")

    if raw_priv_str.startswith('-----BEGIN '):
        return raw_priv_str

    raw_priv = base64.urlsafe_b64decode(raw_priv_str + '==')
    raw_pub = base64.urlsafe_b64decode(raw_pub_str + '==')

    private_value = int.from_bytes(raw_priv, byteorder='big')
    public_numbers = ec.EllipticCurvePublicNumbers.from_encoded_point(
        ec.SECP256R1(), raw_pub,
    )
    private_numbers = ec.EllipticCurvePrivateNumbers(
        private_value=private_value,
        public_numbers=public_numbers,
    )

    key_object = private_numbers.private_key()
    return key_object.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode('utf-8')
