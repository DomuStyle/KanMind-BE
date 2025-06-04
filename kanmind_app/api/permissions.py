from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsBoardMemberOrOwner(BasePermission):
    # check permissions at object level
    def has_object_permission(self, request, view, obj):
        # allow safe methods (GET, HEAD, OPTIONS) for members or owner
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return obj.owner == request.user or obj.members.filter(id=request.user.id).exists()
        # allow PATCH for members or owner
        elif request.method == 'PATCH':
            return obj.owner == request.user or obj.members.filter(id=request.user.id).exists()
        # allow DELETE only for owner
        elif request.method == 'DELETE':
            return obj.owner == request.user
        # deny other methods by default
        return False

    # check permissions at list level
    def has_permission(self, request, view):
        # allow POST requests for authenticated users
        if request.method == 'POST':
            return request.user.is_authenticated
        # allow GET requests for authenticated users (filtering done in view)
        return request.user.is_authenticated