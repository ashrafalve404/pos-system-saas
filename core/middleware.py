from django.utils.deprecation import MiddlewareMixin


class OrganizationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            request.organization = getattr(request.user, 'organization', None)
            request.current_store = getattr(request.user, 'store', None)
        else:
            request.organization = None
            request.current_store = None
        return None
