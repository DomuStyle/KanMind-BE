from django.db import models
from django.contrib.auth.models import User

class Boards(models.Model):
    # defines the title of the board
    title = models.CharField(max_length=255)
    # links the owner of the board to a user
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards')
    # defines a many-to-many relationship for board members
    members = models.ManyToManyField(User, through='BoardMember', related_name='boards')
    # stores the creation date of the board
    created_at = models.DateTimeField(auto_now_add=True)
    # stores the update date of the board
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # defines the name of the table in the database
        db_table = 'boards'

    def __str__(self):
        # returns a readable representation of the board
        return self.title

class BoardMember(models.Model):
    # links a user to a board
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # links the board to a user
    board = models.ForeignKey(Boards, on_delete=models.CASCADE)
    # stores the date when the user joined the board
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # defines the name of the table in the database
        db_table = 'board_members'
        # ensures that a user can only be a member of a board once
        unique_together = ('user', 'board')

class Tasks(models.Model):
    # defines the possible status values for a task
    STATUS_CHOICES = (
        ('to-do', 'To Do'),
        ('in-progress', 'In Progress'),
        ('done', 'Done'),
    )
    # defines the possible priority values for a task
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    # links the task to a board
    board = models.ForeignKey(Boards, on_delete=models.CASCADE, related_name='tasks')
    # defines the title of the task
    title = models.CharField(max_length=255)
    # defines the status of the task
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to-do')
    # defines the priority of the task
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    # stores the creation date of the task
    created_at = models.DateTimeField(auto_now_add=True)
    # stores the update date of the task
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # defines the name of the table in the database
        db_table = 'tasks'

    def __str__(self):
        # returns a readable representation of the task
        return self.title