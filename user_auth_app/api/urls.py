# standard bib imports
from django.urls import path

# third party imports
from rest_framework.authtoken.views import obtain_auth_token

# local imports
from .views import RegistrationView, CustomLoginView


urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CustomLoginView.as_view(), name='login')
]
