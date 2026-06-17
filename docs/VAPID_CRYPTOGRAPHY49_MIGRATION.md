# Migración VAPID: Problema con cryptography ≥46 y solución

## Stack
- Django 4.2 + pywebpush 2.3.0 + py-vapid 1.9.4 + cryptography ≥46
- Almacenamiento de llaves: `.env` vía `django-environ`

---

## 1. El problema

### 1.1 Síntoma inicial
Al ejecutar `python manage.py test_push`:
```
✗ pope — Could not deserialize key data. The data may be in an incorrect
  format, it may be encrypted with an unsupported algorithm, or it may be
  an unsupported key type (e.g. EC curves with explicit parameters).
  Details: ASN.1 parsing error: invalid length
```

### 1.2 Causa raíz (doble)
Había **dos errores independientes** encadenados:

| # | Error | Causa |
|---|-------|-------|
| 1 | `ASN.1 parsing error: invalid length` | El `.env` contenía la llave privada en formato DER completo (~130 bytes). `py-vapid` + `cryptography` variaban en su capacidad de parsear DER entre versiones. |
| 2 | `AttributeError: 'EllipticCurvePublicNumbers' has no attribute 'from_encoded_point'` | `cryptography>=46` resuelve a 49.x en el servidor. En cryptography 49 se eliminó el método `from_encoded_point` de la clase `EllipticCurvePublicNumbers`. Ahora vive en `EllipticCurvePublicKey`. |
| 3 | `Could not deserialize key data. Details: header too long` | `Vapid.from_string()` en `py-vapid` **no maneja formato PEM**. Al recibir un string con headers `-----BEGIN EC PRIVATE KEY-----`, hace `base64_decode` de todo el string incluyendo los headers, produciendo basura. |

### 1.3 Flujo del error #3 (el más sutil)

```
from_string(private_key="-----BEGIN EC PRIVATE KEY-----\nMHcC...\n-----END EC PRIVATE KEY-----")

  1. pkey = private_key.encode().replace(b"\n", b"")
     → "-----BEGIN EC PRIVATE KEY-----MHcC...-----END EC PRIVATE KEY-----"

  2. key = b64urldecode(pkey)
     → base64_decode ignora caracteres inválidos, pero los caracteres
       válidos dentro de los headers (E, C, P, R, I, V, A, T, K, Y, M)
       se mezclan con el payload real → 160 bytes de basura

  3. len(key) != 32
     → cae en from_der(), que intenta load_der_private_key(basura)
     → "header too long" → "Could not deserialize key data"
```

**El método `from_pem()` existe** en py-vapid pero `from_string()` **no lo usa**.

---

## 2. La solución

### 2.1 Estrategia
No almacenar PEM ni DER en `.env`. Guardar solo el **scalar privado de 32 bytes** (RFC 8291) en base64url sin padding. `Vapid.from_string()` detecta 32 bytes y rutea a `from_raw()`, que reconstruye la llave correctamente vía `ec.derive_private_key()`.

### 2.2 Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `apps/notifications/utils.py` | **Eliminado** — ya no se necesita reconstruir PEM manualmente |
| `apps/notifications/management/commands/test_push.py` | Pasa `settings.VAPID_PRIVATE_KEY` directamente a `webpush()` en lugar de `get_vapid_private_key_pem()` |
| `apps/notifications/tasks.py` | Ídem |
| `apps/notifications/management/commands/generate_vapid_keys.py` | Ya generaba raw 32B scalar + 65B public point (correcto desde el inicio) |

### 2.3 Flujo corregido

```
.env:
  VAPID_PRIVATE_KEY=Ko_lS19HrJ4rJJLSpefswHJ8zCXane0lyhkLZAjGOdQ  (43 chars, 32 bytes)

webpush(vapid_private_key=settings.VAPID_PRIVATE_KEY)
  → Vapid.from_string("Ko_lS19HrJ4rJJLSpefswHJ8zCXane0lyhkLZAjGOdQ")
    → b64urldecode → 32 bytes ✓
    → from_raw()
      → ec.derive_private_key(private_value, SECP256R1())
      → Vapid01(private_key) listo para firmar JWT
```

### 2.4 Nota sobre cryptography 49
Si en el futuro decides reconstruir llaves EC en tu propio código (sin py-vapid), usa:

```python
# ❌ Eliminado en cryptography 49:
ec.EllipticCurvePublicNumbers.from_encoded_point(curve, data)

# ✅ Nuevo (disponible desde cryptography 36):
public_key = ec.EllipticCurvePublicKey.from_encoded_point(curve, data)
public_numbers = public_key.public_numbers()
```

---

## 3. Comandos de mantenimiento

```bash
# Regenerar llaves (borra las anteriores)
python manage.py generate_vapid_keys

# Limpiar suscripciones viejas (después de regenerar llaves)
python manage.py clear_subscriptions

# Probar envío
python manage.py test_push
```

---

## 4. Lecciones aprendidas

1. **No almacenar DER en `.env`** — los formatos ASN.1/DER son frágiles entre versiones de `cryptography`.
2. **`Vapid.from_string()` no maneja PEM** — nunca pases un PEM a `webpush()` como `vapid_private_key`. Pasa el raw scalar en base64url.
3. **El método `from_encoded_point` vive en `EllipticCurvePublicKey`** desde cryptography 36. La versión en `EllipticCurvePublicNumbers` se eliminó en la 49.
4. **Siempre recrear suscripciones push** después de regenerar las llaves VAPID. Las suscripciones existentes quedan huérfanas (error `VapidPkHashMismatch` o `403 Forbidden`).
