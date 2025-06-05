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
        ('review', 'Review'),
        ('done', 'Done'),
    )
    # defines the possible priority values for a task
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    # link task to a board
    board = models.ForeignKey(Boards, on_delete=models.CASCADE, related_name='tasks')
    # define task title
    title = models.CharField(max_length=255)
    # define task description
    description = models.TextField(blank=True, null=True)
    # define task status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to-do')
    # define task priority
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    # link assignee to a user (nullable)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    # link reviewer to a user (nullable)
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_tasks')
    # link creator to a user
    creator = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_tasks'
    )
    # define due date for the task
    due_date = models.DateField(null=True, blank=True)
    # store task creation date
    created_at = models.DateTimeField(auto_now_add=True)
    # store task update date
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # define database table name
        db_table = 'tasks'

    def __str__(self):
        # returns a readable representation of the task
        return self.title

class Comments(models.Model):
    # link comment to a task
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, related_name='comments')
    # link comment to a user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    # define comment text
    content = models.TextField()
    # store comment creation date
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # define database table name
        db_table = 'comments'
        # order comments by creation date
        ordering = ['created_at']

    def __str__(self):
        # return readable representation of the comment
        return f"Comment by {self.user} on {self.task}"