# standard bib imports
from django.urls import path

# local imports
from .views import BoardListCreateView, BoardDetailView, EmailCheckView, TasksAssignedToMeView

urlpatterns = [
    # link /boards/ endpoint to BoardsListCreateView
    path('boards/', BoardListCreateView.as_view(), name='boards-list-create'),
    # link /boards/<board_id>/ endpoint to BoardsDetailView
    path('boards/<int:board_id>/', BoardDetailView.as_view(), name='boards-detail'),
    # link /email-check/ endpoint to EmailCheckView
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    # link /tasks/assigned-to-me/ endpoint to TasksAssignedToMeView
    path('tasks/assigned-to-me/', TasksAssignedToMeView.as_view(), name='tasks-assigned-to-me'),
]