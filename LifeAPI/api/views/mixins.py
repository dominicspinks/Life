from django.shortcuts import get_object_or_404
from api.models import UserModule

class UserModuleAuthorizationMixin:
    """
    Mixin to guarantee that the requested UserModule belongs to the currently 
    authenticated user.

    Configure `user_module_kwarg` to match the URL routing parameter for the 
    user module (e.g., 'budget_id' or 'list_id').
    """
    user_module_kwarg = 'module_id'
    _user_module_cache = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        
        # Verify the UserModule belongs to the user right away
        # This will raise a 404 if it is invalid or doesn't belong to them
        self.get_user_module()

    def get_user_module(self):
        """
        Retrieves the verified UserModule. Caches it for the lifetime of the view
        instance to avoid redundant queries during the same request.
        """
        if self._user_module_cache is None:
            module_id = self.kwargs.get(self.user_module_kwarg)
            self._user_module_cache = get_object_or_404(
                UserModule, 
                id=module_id, 
                user=self.request.user
            )
        return self._user_module_cache
