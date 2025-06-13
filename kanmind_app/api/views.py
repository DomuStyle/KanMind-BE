# standard bib imports
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

# third party imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# local imports
from kanmind_app.models import Boards, Tasks, Comments
from .serializers import BoardSerializer, BoardsDetailSerializer, UserSerializer, TasksSerializer, CommentSerializer
from .permissions import IsBoardMemberOrOwner, IsTaskCreatorOrBoardOwner, IsCommentAuthor


class BoardListCreateView(APIView):
    # defines the required permission class
    permission_classes = [IsBoardMemberOrOwner]

    def get(self, request):
        # filters boards where the user is either the owner or a member
        boards = Boards.objects.filter(
            models.Q(owner=request.user) | models.Q(members=request.user)
        ).distinct()
        # serializes the filtered boards
        serializer = BoardSerializer(boards, many=True)
        # returns the serialized data with status 200
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # creates a serializer with the request data
        serializer = BoardSerializer(data=request.data, context={'request': request})
        # checks if the data is valid
        if serializer.is_valid():
            # saves the new board
            serializer.save()
            # returns the data of the new board with status 201
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # returns an error if the data is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
# define board detail view
class BoardDetailView(APIView):
    # define required permission class
    permission_classes = [IsBoardMemberOrOwner]

    # define method to get board by id
    def get_object(self, board_id):
        # try to retrieve board instance
        try:
            # return board object
            return Boards.objects.get(id=board_id)
        # handle case where board does not exist
        except Boards.DoesNotExist:
            return None

    def get(self, request, board_id):
        # get board instance
        board = self.get_object(board_id)
        # return 404 if board not found
        if not board:
            # return error response
            return Response({'error': 'Board not found'}, status=status.HTTP_404_NOT_FOUND)
        # check permissions
        self.check_object_permissions(request, board)
        # serialize board
        serializer = BoardsDetailSerializer(board)
        # return required fields for get
        return Response({
            # include board id
            'id': serializer.data['id'],
            # include board title
            'title': serializer.data['title'],
            # include owner id
            'owner_id': serializer.data['owner_id'],
            # include members
            'members': serializer.data['members'],
            # include tasks
            'tasks': serializer.data['tasks']
        }, status=status.HTTP_200_OK)

    def patch(self, request, board_id):
        # get board instance
        board = self.get_object(board_id)
        # return 404 if board not found
        if not board:
            # return error response
            return Response({'error': 'Board not found'}, status=status.HTTP_404_NOT_FOUND)
        # check permissions
        self.check_object_permissions(request, board)
        # create serializer with request data
        serializer = BoardsDetailSerializer(board, data=request.data, partial=True)
        # check if data is valid
        if serializer.is_valid():
            # try to save updated board
            try:
                # save serializer
                serializer.save()
                # return required fields for patch
                return Response({
                    # include board id
                    'id': serializer.data['id'],
                    # include board title
                    'title': serializer.data['title'],
                    # include owner data
                    'owner_data': serializer.data['owner_data'],
                    # include members data
                    'members_data': serializer.data['members_data']
                }, status=status.HTTP_200_OK)
            # handle serialization errors
            except Exception as e:
                # return error response
                return Response({'error': f'Serialization error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # return errors if data is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, board_id):
        # get board instance
        board = self.get_object(board_id)
        # return 404 if board not found
        if not board:
            # return error response
            return Response({'error': 'Board not found'}, status=status.HTTP_404_NOT_FOUND)
        # check permissions
        self.check_object_permissions(request, board)
        # delete board
        board.delete()
        # return null with status 204
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    

class EmailCheckView(APIView):
    # define required permission class
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # get email from query parameters
        email = request.query_params.get('email')
        # check if email is provided
        if not email:
            return Response({'error': 'Email parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        # validate email format
        try:
            validate_email(email)
        except ValidationError:
            return Response({'error': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)
        # check if user with email exists
        try:
            user = User.objects.get(email=email)
            # serialize user data
            serializer = UserSerializer(user)
            # return user data with status 200
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # return 404 if email not found
            return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)


class TasksAssignedToMeView(APIView):
    # define required permission class
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # filter tasks where user is assignee
        tasks = Tasks.objects.filter(assignee=request.user)
        # serialize filtered tasks
        serializer = TasksSerializer(tasks, many=True)
        # return serialized data with status 200
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    
class TasksReviewingView(APIView):
    # define required permission class
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # filter tasks where user is reviewer
        tasks = Tasks.objects.filter(reviewer=request.user)
        # serialize filtered tasks
        serializer = TasksSerializer(tasks, many=True)
        # return serialized data with status 200
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class TasksCreateView(APIView):
    # define required permission class
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # create serializer with request data
        serializer = TasksSerializer(data=request.data, context={'request': request})
        # check if data is valid
        if serializer.is_valid():
            # get board from validated data
            board = serializer.validated_data['board']
            # check if user is member or owner of the board
            if not (board.owner == request.user or board.members.filter(id=request.user.id).exists()):
                return Response({'error': 'You must be a member or owner of the board to create a task.'}, status=status.HTTP_403_FORBIDDEN)
            # save new task
            task = serializer.save()
            # return new task data with status 201
            return Response(TasksSerializer(task).data, status=status.HTTP_201_CREATED)
        # return errors if data is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TasksDetailView(APIView):
    # define required permission classes
    permission_classes = [IsAuthenticated, IsTaskCreatorOrBoardOwner]

    # define method to get task
    def get_object(self, task_id):
        # try to retrieve task
        try:
            # return task object
            return Tasks.objects.get(id=task_id)
        # handle case where task does not exist
        except Tasks.DoesNotExist:
            # return none
            return None

    # define patch method
    def patch(self, request, task_id):
        # get task instance
        task = self.get_object(task_id)
        # return 404 if task not found
        if not task:
            # return error response
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        # # check if user is member or owner of the board
        # if not (task.board.owner == request.user or task.board.members.filter(id=request.user.id).exists()):
        #     return Response({'error': 'You must be a member or owner of the board to update this task.'}, status=status.HTTP_403_FORBIDDEN)
        # create serializer with request data
        serializer = TasksSerializer(task, data=request.data, partial=True, context={'request': request})
        # check if data is valid
        if serializer.is_valid():
            # save updated task
            serializer.save()
            # return updated task data
            return Response(serializer.data, status=status.HTTP_200_OK)
        # return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # define delete method
    def delete(self, request, task_id):
        # get task instance
        task = self.get_object(task_id)
        # return 404 if task not found
        if not task:
            # return error response
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        # check if user is creator or board owner
        if not (task.creator == request.user or task.board.owner == request.user):
            # return error response
            return Response({'error': 'Only the task creator or board owner can delete this task.'}, status=status.HTTP_403_FORBIDDEN)
        # delete task
        task.delete()
        # return null
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    

class TaskCommentsView(APIView):
    # define required permission classes
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def get_task(self, task_id):
        # retrieve task by ID or return None
        try:
            return Tasks.objects.get(id=task_id)
        except Tasks.DoesNotExist:
            return None

    def get(self, request, task_id):
        # get task instance
        task = self.get_task(task_id)
        # return 404 if task not found
        if not task:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        # check if user is member or owner of the board
        if not (task.board.owner == request.user or task.board.members.filter(id=request.user.id).exists()):
            return Response({'error': 'You must be a member or owner of the board to view comments.'}, status=status.HTTP_403_FORBIDDEN)
        # get all comments for the task
        comments = task.comments.all()
        # serialize comments
        serializer = CommentSerializer(comments, many=True)
        # return serialized data with status 200
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, task_id):
        # get task instance
        task = self.get_task(task_id)
        # return 404 if task not found
        if not task:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        # check if user is member or owner of the board
        if not (task.board.owner == request.user or task.board.members.filter(id=request.user.id).exists()):
            return Response({'error': 'You must be a member or owner of the board to create a comment.'}, status=status.HTTP_403_FORBIDDEN)
        # create serializer with request data
        serializer = CommentSerializer(data=request.data, context={'request': request})
        # check if data is valid
        if serializer.is_valid():
            # create comment with current user as author
            comment = Comments.objects.create(
                task=task,
                author=request.user,
                content=serializer.validated_data['content']
            )
            # serialize created comment
            comment_serializer = CommentSerializer(comment)
            # return created comment data with status 201
            return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
        # return errors if data is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskCommentDetailView(APIView):
    # define required permission classes
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_task(self, task_id):
        # retrieve task by ID or return None
        try:
            return Tasks.objects.get(id=task_id)
        except Tasks.DoesNotExist:
            return None

    def get_comment(self, task, comment_id):
        # retrieve comment by ID for the given task or return None
        try:
            return task.comments.get(id=comment_id)
        except Comments.DoesNotExist:
            return None

    def delete(self, request, task_id, comment_id):
        # get task instance
        task = self.get_task(task_id)
        # return 404 if task not found
        if not task:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        # get comment instance
        comment = self.get_comment(task, comment_id)
        # return 404 if comment not found
        if not comment:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        # check permissions (handled by IsCommentAuthor)
        self.check_object_permissions(request, comment)
        # delete comment
        comment.delete()
        # return null with status 204
        return Response(None, status=status.HTTP_204_NO_CONTENT)