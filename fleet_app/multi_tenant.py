from functools import wraps
from django.http import Http404
from django.shortcuts import get_object_or_404


def object_belongs_to_tenant(model, lookup_kwarg='pk', entreprise_field='entreprise', user_field='user'):
    """
    Decorator for detail/update/delete views to enforce multi-tenant isolation.
    Priority:
    - If model has an entreprise field and request.user has an entreprise attribute,
      the object must match request.user.entreprise.
    - Otherwise, fallback to user field matching request.user.
    Raises 404 when access is not permitted.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            lookup_value = kwargs.get(lookup_kwarg)
            if lookup_value is None:
                return view_func(request, *args, **kwargs)

            filters = {'pk': lookup_value}
            if hasattr(model, '_meta') and any(f.name == entreprise_field for f in model._meta.fields) and hasattr(request.user, entreprise_field):
                filters[entreprise_field] = getattr(request.user, entreprise_field)
            else:
                filters[user_field] = request.user

            try:
                obj = get_object_or_404(model, **filters)
            except Exception:
                raise Http404()

            request._secured_object = obj
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def queryset_filter_by_tenant(qs, request, entreprise_field='entreprise', user_field='user'):
    """Filter a queryset by entreprise when available, else by user."""
    model = qs.model
    if hasattr(model, '_meta') and any(f.name == entreprise_field for f in model._meta.fields) and hasattr(request.user, entreprise_field):
        return qs.filter(**{entreprise_field: getattr(request.user, entreprise_field)})
    return qs.filter(**{user_field: request.user})
