from rest_framework.permissions import BasePermission, SAFE_METHODS

# class IsOwnerOrReadOnly(BasePermission):

#     def has_object_permission(self, request, view, obj):
#         # check if the request method is in the list of safe methods
#         if request.method in SAFE_METHODS:
#             return True

#         # check if the request method is DELETE and if the user is either a superuser or the author of the object
#         elif request.method == "DELETE":
#             return bool(request.user and (request.user.is_superuser or request.user == obj.author))

#         # otherwise, check if the user is the author of the object
#         else:
#             return bool(request.user and request.user == obj.author)

class IsBoardMemberOrOwner(BasePermission):
    # checks permissions at the object level
    def has_object_permission(self, request, view, obj):
        # allows safe methods only for board members or the owner
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return obj.owner == request.user or obj.members.filter(id=request.user.id).exists()
        # allows other methods (e.g. DELETE) only for the owner or a superuser
        return obj.owner == request.user or request.user.is_superuser

    # checks permissions at the list level
    def has_permission(self, request, view):
        # allows post requests for authenticated users
        if request.method == 'POST':
            return request.user.is_authenticated
        # allows get requests for authenticated users (filtering is done in the view)
        return request.user.is_authenticated