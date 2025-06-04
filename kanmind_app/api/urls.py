# standard bib imports
from django.urls import path

# local imports
from .views import BoardListCreateView, BoardDetailView, EmailCheckView

urlpatterns = [
    # link /boards/ endpoint to BoardsListCreateView
    path('boards/', BoardListCreateView.as_view(), name='boards-list-create'),
    # link /boards/<board_id>/ endpoint to BoardsDetailView
    path('boards/<int:board_id>/', BoardDetailView.as_view(), name='boards-detail'),
    # link /email-check/ endpoint to EmailCheckView
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]