from rest_framework import serializers
from kanmind_app.models import Boards, Tasks
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    # define field for user's full name
    fullname = serializers.SerializerMethodField()

    class Meta:
        # link serializer to User model
        model = User
        # define fields to serialize
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        # return user's full name combining first and last name
        return f"{obj.first_name} {obj.last_name}".strip()


class TasksSerializer(serializers.ModelSerializer):
    # define field for assignee using UserSerializer
    assignee = UserSerializer(read_only=True)
    # define field for reviewer using UserSerializer
    reviewer = UserSerializer(read_only=True)
    # define field for comments count
    comments_count = serializers.SerializerMethodField()

    class Meta:
        # link serializer to Tasks model
        model = Tasks
        # define fields to serialize
        fields = [
            'id', 
            'title', 
            'description', 
            'status', 
            'priority', 
            'assignee', 
            'reviewer', 
            'due_date', 
            'comments_count'
        ]

    def get_comments_count(self, obj):
        # return number of comments (placeholder, assuming Comments model exists)
        return obj.comments.count() if hasattr(obj, 'comments') else 0

class BoardsDetailSerializer(serializers.ModelSerializer):
    # define field for owner data using UserSerializer
    owner_data = UserSerializer(source='owner', read_only=True)
    # define field for members data using UserSerializer
    members_data = UserSerializer(source='members', many=True, read_only=True)
    # define field for tasks using TasksSerializer
    tasks = TasksSerializer(many=True, read_only=True)
    # define field for members as IDs for write operations
    members = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=User.objects.all(), 
        write_only=True,
        required=False
    )

    class Meta:
        # link serializer to Boards model
        model = Boards
        # define fields to serialize
        fields = [
            'id', 
            'title', 
            'owner_id', 
            'owner_data', 
            'members', 
            'members_data', 
            'tasks'
        ]
        # define read-only fields
        read_only_fields = ['owner_id', 'owner_data', 'members_data', 'tasks']

    def update(self, validated_data):
        # extract members from validated data
        members = validated_data.pop('members', None)
        # update board instance
        instance = super().update(validated_data)
        # update members if provided
        if members is not None:
            # clear existing members except owner
            instance.members.clear()
            # add new members
            for member in members:
                if member != instance.owner:  # prevent adding owner as member
                    instance.members.add(member)
            # ensure owner is always a member
            instance.members.add(instance.owner)
        return instance
        
class BoardSerializer(serializers.ModelSerializer):
    # define field for members count
    member_count = serializers.SerializerMethodField()
    # define field for total tasks count
    ticket_count = serializers.SerializerMethodField()
    # define field for to-do tasks count
    tasks_to_do_count = serializers.SerializerMethodField()
    # define field for high-priority tasks count
    tasks_high_prio_count = serializers.SerializerMethodField()
    # define field for owner ID
    owner_id = serializers.PrimaryKeyRelatedField(source='owner', read_only=True)
    # define field for members IDs (for POST requests)
    members = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=User.objects.all(), 
        write_only=True,
        required=False
    )

    class Meta:
        # link serializer to Boards model
        model = Boards
        # define fields to serialize
        fields = [
            'id', 
            'title', 
            'member_count', 
            'ticket_count', 
            'tasks_to_do_count', 
            'tasks_high_prio_count', 
            'owner_id', 
            'members'
        ]
        # set title field as required
        extra_kwargs = {'title': {'required': True}}

    def get_member_count(self, obj):
        # return count of board members
        return obj.members.count()

    def get_ticket_count(self, obj):
        # return total count of tasks for the board
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        # return count of tasks in 'to-do' status
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        # return count of tasks with high priority
        return obj.tasks.filter(priority='high').count()

    def create(self, validated_data):
        # extract members from validated data
        members = validated_data.pop('members', [])
        # create new board with authenticated user as owner
        board = Boards.objects.create(owner=self.context['request'].user, **validated_data)
        # add members to the board (excluding owner)
        for member in members:
            if member != self.context['request'].user:  # prevent adding owner twice
                board.members.add(member)
        return board