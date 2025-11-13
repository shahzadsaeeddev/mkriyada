from .base import *

POSTGRES_DB = os.environ.get("DJANGO_DB_NAME", "mkriyada_db")
POSTGRES_USERNAME = os.environ.get("DJANGO_DB_USER", "neksio")
POSTGRES_PASSWORD = os.environ.get("DJANGO_DB_PASSWORD", "*Beejay123qweasd")
POSTGRES_HOST = os.environ.get("DJANGO_DB_HOST", "db")
POSTGRES_PORT = os.environ.get("DJANGO_DB_PORT", 5432)


if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': POSTGRES_DB,
            'USER': POSTGRES_USERNAME,
            'PASSWORD': POSTGRES_PASSWORD,
            'HOST': POSTGRES_HOST,
            'PORT': POSTGRES_PORT,
        }
    }
    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # SECURE_SSL_REDIRECT = True
    # SESSION_COOKIE_SECURE = True
    # CSRF_COOKIE_SECURE = True


else:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


    DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': POSTGRES_DB,
                'USER': POSTGRES_USERNAME,
                'PASSWORD': POSTGRES_PASSWORD,
                'HOST': POSTGRES_HOST,
                'PORT': POSTGRES_PORT,
            }
    }



OIDC_HOST = os.environ.get("OIDC_HOST", "https://accounts.mkriyada.com")
OIDC_REALM = os.environ.get("OIDC_REALM", "mkriyada")
OIDC_RP_CLIENT_ID = os.environ.get("OIDC_RP_CLIENT_ID", "backend")
OIDC_RP_CLIENT_SECRET = os.environ.get("OIDC_RP_CLIENT_SECRET", "uMqY0flV1ScUq7t659HlH5ltfM8UmbUZ")

OIDC_OP_AUTHORIZATION_ENDPOINT = f'{OIDC_HOST}/realms/{OIDC_REALM}/protocol/openid-connect/auth'
OIDC_OP_TOKEN_ENDPOINT = f'{OIDC_HOST}/realms/{OIDC_REALM}/protocol/openid-connect/token'
OIDC_OP_USER_ENDPOINT = f'{OIDC_HOST}/realms/{OIDC_REALM}/protocol/openid-connect/userinfo'

TOKEN_EXPIRATION_TIME = os.environ.get("TOKEN_EXPIRATION_TIME", 300)  # Set token expiration time in seconds
TOKEN_VERIFY_EXPIRATION = True
TOKEN_VERIFY_SIGNATURE = True
TOKEN_EXPIRATION_LEEWAY = os.environ.get("TOKEN_EXPIRATION_LEEWAY", 60)

OIDC_OP_JWKS_ENDPOINT = 'https://accounts.mkriyada.com/realms/secure/protocol/openid-connect/certs'
OIDC_RP_SIGN_ALGO = os.environ.get("OIDC_RP_SIGN_ALGO", 'RS256')
OIDC_RP_IDP_SIGN_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxaHJJMf2f
UYCYA8CBLL2MXz/L/ELNk7ZuJx4OjRolcdM8lFYVpkhUslWOBcIG0h
/NIXdv5VSH+fODzON3fIAjDMjCV6477Tm1kHD2SC3jp/YtWORn2LkF+
F8Ao8pLy23ERo3ekd6fFKf3gVpuEHanQCiJK5W+P8gUyX3PlKHIi1Xon
QIciDtIsxWtjk2HCWsIqtKShQIsehkcXLKCsWQLPtozVdgXZ3X496tTrm
YtrhJi8Zdkv43vbRxXdQnlXksfy4zxOaExDsSqIDe0to1hxeil57+NLfHUIB
DVLrLNuovwP5FZ+K/pl6aCTsctXgrf2EdebSM/4tRrDEzhf9wiQIDAQAB
-----END PUBLIC KEY-----"""

OIDC_CALLBACK_REDIRECT_URI = 'http://localhost:8000/api/callback/'
OIDC_RP_SCOPES = 'roles email'
OIDC_VERIFY_SSL = False
OIDC_CREATE_USER = True