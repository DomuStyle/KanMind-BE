# standard bib imports
from django.db import models

# third party imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# local imports
from kanmind_app.models import Boards
from .serializers import BoardSerializer
from .permissions import IsBoardMemberOrOwner

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
