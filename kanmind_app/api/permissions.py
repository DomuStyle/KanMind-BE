from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        # check if the request method is in the list of safe methods
        if request.method in SAFE_METHODS:
            return True

        # check if the request method is DELETE and if the user is either a superuser or the author of the object
        elif request.method == "DELETE":
            return bool(request.user and (request.user.is_superuser or request.user == obj.author))

        # otherwise, check if the user is the author of the object
        else:
            return bool(request.user and request.user == obj.author)