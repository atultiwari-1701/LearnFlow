from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.csrf import csrf_exempt
from django.urls import resolve

class DisableCSRFMiddlewareForAdmin(MiddlewareMixin):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # If it's an admin view, disable CSRF
        if request.path.startswith('/admin/'):
            return csrf_exempt(callback)(request, *callback_args, **callback_kwargs)
        return None