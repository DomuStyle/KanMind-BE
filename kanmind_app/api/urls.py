# standard bib imports
from django.urls import path

# local imports
from .views import (
    BoardListCreateView, 
    BoardDetailView, 
    EmailCheckView, 
    TasksAssignedToMeView, 
    TasksReviewingView,
    TasksCreateView,
    TasksDetailView
    )

urlpatterns = [
    # link /boards/ endpoint to BoardsListCreateView
    path('boards/', BoardListCreateView.as_view(), name='boards-list-create'),
    # link /boards/<board_id>/ endpoint to BoardsDetailView
    path('boards/<int:board_id>/', BoardDetailView.as_view(), name='boards-detail'),
    # link /email-check/ endpoint to EmailCheckView
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    # link /tasks/assigned-to-me/ endpoint to TasksAssignedToMeView
    path('tasks/assigned-to-me/', TasksAssignedToMeView.as_view(), name='tasks-assigned-to-me'),
    # link /tasks/reviewing/ endpoint to TasksReviewingView
    path('tasks/reviewing/', TasksReviewingView.as_view(), name='tasks-reviewing'),
    # link /tasks/ endpoint to TasksCreateView
    path('tasks/', TasksCreateView.as_view(), name='tasks-create'),
    # link /tasks/<task_id>/ endpoint to TasksDetailView
    path('tasks/<int:task_id>/', TasksDetailView.as_view(), name='tasks-detail'),
]