from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsBoardMemberOrOwner(BasePermission):
    # check permissions at object level
    def has_object_permission(self, request, view, obj):
        # allow safe methods (GET, HEAD, OPTIONS) for members or owner
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return obj.owner == request.user or obj.members.filter(id=request.user.id).exists()
        # allow PATCH for members or owner of the board
        if request.method == 'PATCH':
            return obj.owner == request.user or obj.members.filter(id=request.user.id).exists()
        # allow DELETE only for owner
        if request.method == 'DELETE':
            return obj.owner == request.user
        # deny other methods by default
        return False

    # check permissions at list level
    def has_permission(self, request, view):
        # allow POST requests for authenticated users (board membership checked in view)
        if request.method == 'POST':
            return request.user.is_authenticated
        # allow GET, PATCH, DELETE for authenticated users (object-level checks apply)
        return request.user.is_authenticated
    

class IsTaskCreatorOrBoardOwner(BasePermission):
    # check permissions at object level
    def has_object_permission(self, request, view, obj):
        # allow DELETE only for task creator or board owner
        if request.method == ['DELETE', 'PATCH']:
            return obj.creator == request.user or obj.board.owner == request.user
        # deny other methods by default
        return False

    # check permissions at list level
    def has_permission(self, request, view):
        # allow DELETE for authenticated users (object-level checks apply)
        return request.user.is_authenticated
    

class IsCommentAuthor(BasePermission):
    # check permissions at object level
    def has_object_permission(self, request, view, obj):
        # allow DELETE only for comment author
        if request.method == 'DELETE':
            return obj.author == request.user
        # deny other methods by default
        return False

    # check permissions at list level
    def has_permission(self, request, view):
        # allow DELETE for authenticated users (object-level checks apply)
        return request.user.is_authenticated