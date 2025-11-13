# accounts/authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from .models import Company


class APIKeyOrUserAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get("Authorization")

        if api_key and api_key.startswith("Api-Key "):
            key = api_key.split(" ")[1]
            try:
                company = Company.objects.get(api_key=key)
                request.company = company
                return (AnonymousUser(), None)
            except Company.DoesNotExist:
                raise AuthenticationFailed("Invalid API Key")

        return None
