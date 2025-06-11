from rest_framework.permissions import BasePermission, SAFE_METHODS
from kanmind_app.models import Tasks

class IsBoardMemberOrOwner(BasePermission):
    # define method to check object-level permissions
    def has_object_permission(self, request, view, obj):
        # handle Tasks objects
        if isinstance(obj, Tasks):
            # get board from task
            board = obj.board
        # handle Boards objects
        else:
            # use object directly
            board = obj
        # allow GET for members or owner
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            # check membership or ownership
            return board.owner == request.user or board.members.filter(id=request.user.id).exists()
        # allow PATCH for members or owner
        if request.method == 'PATCH':
            # check membership or ownership
            return board.owner == request.user or board.members.filter(id=request.user.id).exists()
        # allow DELETE for owner
        if request.method == 'DELETE':
            # check ownership
            return board.owner == request.user
        # deny other methods
        return False

    # define method to check list-level permissions
    def has_permission(self, request, view):
        # allow POST for authenticated users
        if request.method == 'POST':
            # check authentication
            return request.user.is_authenticated
        # allow other methods for authenticated users
        return request.user.is_authenticated
    

class IsTaskCreatorOrBoardOwner(BasePermission):
    # check permissions at object level
    def has_object_permission(self, request, view, obj):
        # allow DELETE only for task creator or board owner
        if request.method == 'DELETE':
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