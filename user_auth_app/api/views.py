# standard bib imports
from rest_framework import generics

# third party imports
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

# local imports
from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer, CustomAuthTokenSerializer


# class UserProfileList(generics.ListCreateAPIView):
#     queryset = UserProfile.objects.all()
#     serializer_class = UserProfileSerializer

# class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = UserProfile.objects.all()
#     serializer_class = UserProfileSerializer

class RegistrationView(APIView):
    permission_classes = [AllowAny] # gives permission to use this view at any time

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        data = {}

        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account) # get or create is used to make sure to get a token if it alrdy exists
            data = {
            'token': token.key,
            'fullname': saved_account.username,
            'email': saved_account.email,
            'user_id': saved_account.id
            }

        else:
            data=serializer.errors

        return Response(data)
    
class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        data = {}

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'fullname': user.username,
                'email': user.email,
                "user_id": user.id
            }
        else:
            data = serializer.errors
        return Response(data)