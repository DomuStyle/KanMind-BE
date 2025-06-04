# standard bib imports
from django.urls import path

# local imports
from .views import BoardListCreateView

urlpatterns = [
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
]