from typing import Callable
from django.http import HttpRequest, HttpResponse


class TenantMiddleware:
    """Attach request.entreprise for the current authenticated user.

    This makes it easier and safer to access the tenant context across views and services.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = getattr(request, 'user', None)
        ent = None
        if user and getattr(user, 'is_authenticated', False):
            # Try user.profil.entreprise first, then user.entreprise
            profil = getattr(user, 'profil', None)
            if profil is not None:
                ent = getattr(profil, 'entreprise', None)
            if ent is None:
                ent = getattr(user, 'entreprise', None)
        request.entreprise = ent
        return self.get_response(request)
