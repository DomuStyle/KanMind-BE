from rest_framework import serializers
from kanmind_app.models import Boards, Tasks, Comments
from django.contrib.auth.models import User
import logging


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


class CommentSerializer(serializers.ModelSerializer):
    # define field for author name
    author = serializers.SerializerMethodField()
    # define field for created_at in ISO format
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)

    class Meta:
        # link serializer to Comments model
        model = Comments
        # define fields to serialize
        fields = ['id', 'created_at', 'author', 'content']
        # define read-only fields
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        # return author's full name
        return f"{obj.author.first_name} {obj.author.last_name}".strip()

    def validate_content(self, value):
        # ensure content is not empty
        if not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value
    
logger = logging.getLogger(__name__)

class TasksSerializer(serializers.ModelSerializer):
    # define field for board ID (read and write)
    board = serializers.PrimaryKeyRelatedField(
        queryset=Boards.objects.all()
    )
    # define field for assignee using UserSerializer
    assignee = UserSerializer(read_only=True)
    # define field for reviewer using UserSerializer
    reviewer = UserSerializer(read_only=True)
    # define field for assignee ID (write-only)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    # define field for reviewer ID (write-only)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    # define field for comments count
    comments_count = serializers.SerializerMethodField()

    # define meta class
    class Meta:
        # link serializer to Tasks model
        model = Tasks
        # define fields to serialize
        fields = [
            'id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'assignee_id',
            'reviewer',
            'reviewer_id',
            'due_date',
            'comments_count'
        ]
        # define read-only fields
        read_only_fields = ['id', 'assignee', 'reviewer', 'comments_count']

    # define method to get comments count
    def get_comments_count(self, obj):
        # return number of comments
        return obj.comments.count()

    # define validation method
    def validate(self, data):
        # log request data for debugging
        logger.debug(f"Request data: {data}")
        # get board from data
        board = data.get('board')
        # log board for debugging
        logger.debug(f"Board in validate: {board}")
        # validate board presence
        if not board:
            # raise validation error
            raise serializers.ValidationError("Board ID is required.")
        # validate assignee if provided
        if 'assignee_id' in data and data['assignee_id']:
            # check membership or ownership
            if not board.members.filter(id=data['assignee_id'].id).exists() and data['assignee_id'] != board.owner:
                # raise validation error
                raise serializers.ValidationError("Assignee must be a member or owner of the board.")
        # validate reviewer if provided
        if 'reviewer_id' in data and data['reviewer_id']:
            # check membership or ownership
            if not board.members.filter(id=data['reviewer_id'].id).exists() and data['reviewer_id'] != board.owner:
                # raise validation error
                raise serializers.ValidationError("Reviewer must be a member or owner of the board.")
        # prevent updating board in PATCH
        if self.instance and 'board' in data:
            # raise validation error
            raise serializers.ValidationError("Changing the board is not allowed.")
        # return validated data
        return data

    # define create method
    def create(self, validated_data):
        # extract write-only fields
        board = validated_data.pop('board')
        assignee_id = validated_data.pop('assignee_id', None)
        reviewer_id = validated_data.pop('reviewer_id', None)
        # create task with creator as current user
        task = Tasks.objects.create(
            # set board
            board=board,
            # set creator
            creator=self.context['request'].user,
            # set assignee
            assignee=assignee_id,
            # set reviewer
            reviewer=reviewer_id,
            # include other fields
            **validated_data
        )
        # return created task
        return task

    # define update method
    def update(self, instance, validated_data):
        # remove board from validated data
        validated_data.pop('board', None)
        # update assignee
        instance.assignee = validated_data.pop('assignee_id', instance.assignee)
        # update reviewer
        instance.reviewer = validated_data.pop('reviewer_id', instance.reviewer)
        # update other fields
        return super().update(instance, validated_data)


class BoardsDetailSerializer(serializers.ModelSerializer):
    # define field for owner id
    owner_id = serializers.PrimaryKeyRelatedField(source='owner', read_only=True)
    # define field for owner data
    owner_data = UserSerializer(source='owner', read_only=True)
    # define field for members (read-only)
    members = UserSerializer(many=True, read_only=True)
    # define field for members data
    members_data = UserSerializer(source='members', many=True, read_only=True)
    # define field for tasks
    tasks = TasksSerializer(many=True, read_only=True)
    # define field for member IDs for write operations (PATCH)
    member_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        required=False
    )

    # define meta class for serializer configuration
     # define meta class
    class Meta:
        # link serializer to Boards model
        model = Boards
        # define fields to serialize
        fields = ['id', 'title', 'owner_id', 'owner_data', 'members', 'members_data', 'tasks', 'member_ids']
        # define read-only fields
        read_only_fields = ['id', 'owner_id', 'owner_data', 'members', 'members_data', 'tasks']

     # define update method for PATCH requests
    def update(self, instance, validated_data):
        # extract member IDs from validated data
        members = validated_data.pop('member_ids', None)
        # update board instance
        instance = super().update(instance, validated_data)
        # update members if provided
        if members is not None:
            # clear existing members
            instance.members.clear()
            # add new members
            for member in members:
                # add each member to the board
                instance.members.add(member)
            # ensure owner is always a member
            if instance.owner not in instance.members.all():
                # add owner to members
                instance.members.add(instance.owner)
        # return updated instance
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