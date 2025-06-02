from django.urls import path

from rest_framework.authtoken.views import obtain_auth_token

from .views import UserProfileList, UserProfileDetail, RegistrationView


urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', obtain_auth_token, name='login')
]
