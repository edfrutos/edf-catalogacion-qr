import os
import jwt
from jwt import PyJWKClient
from dotenv import load_dotenv

load_dotenv()

auth_url = os.getenv('BETTER_AUTH_URL', 'http://localhost:3000').rstrip('/')
jwks_url = f"{auth_url}/api/auth/jwks"


def verify_session(token):
    """
    Verifica un token JWT emitido por Better-Auth (firmado con EdDSA/JWKS).
    """
    if not token:
        return None
    try:
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        # Sin issuer/audience por si Better-Auth usa valores distintos
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA", "ES256"],
            options={"verify_exp": True, "verify_aud": False, "verify_iss": False},
        )
        return payload
    except jwt.ExpiredSignatureError:
        print("[auth_client] Token de Better-Auth expirado.")
        return None
    except jwt.InvalidTokenError:
        print("[auth_client] Token de Better-Auth inválido.")
        return None
    except Exception as e:
        print(f"[auth_client] Error al verificar token: {e}")
        return None


def get_user_from_payload(payload):
    """
    Obtiene el ID de usuario del payload del token.
    """
    if not payload:
        return None
    return payload.get('sub')  # 'sub' suele ser el ID de usuario en JWT
