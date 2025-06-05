from rest_framework import serializers
from kanmind_app.models import Boards, Tasks, Comments
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
    

class TasksSerializer(serializers.ModelSerializer):
    # define field for board ID
    board = serializers.PrimaryKeyRelatedField(read_only=True)
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

    def get_comments_count(self, obj):
        # return number of comments (placeholder, assuming Comments model exists)
        return obj.comments.count()
    
    def validate(self, data):
        # get board from data
        board = data.get('board', getattr(self.instance, 'board', None))
        # get assignee and reviewer IDs
        assignee_id = data.get('assignee_id')
        reviewer_id = data.get('reviewer_id')
        # validate assignee if provided
        if assignee_id and not board.members.filter(id=assignee_id.id).exists() and assignee_id != board.owner:
            raise serializers.ValidationError("Assignee must be a member or owner of the board.")
        # validate reviewer if provided
        if reviewer_id and not board.members.filter(id=reviewer_id.id).exists() and reviewer_id != board.owner:
            raise serializers.ValidationError("Reviewer must be a member or owner of the board.")
        # prevent updating board in PATCH requests
        if self.instance and 'board' in data:
            raise serializers.ValidationError("Changing the board is not allowed.")
        return data

    def create(self, validated_data):
        # extract write-only fields
        board = validated_data.pop('board')
        assignee_id = validated_data.pop('assignee_id', None)
        reviewer_id = validated_data.pop('reviewer_id', None)
        # create task with creator as current user
        task = Tasks.objects.create(
            board=board, 
            creator=self.context['request'].user, 
            assignee=assignee_id, 
            reviewer=reviewer_id, 
            **validated_data
        )
        return task

    def update(self, instance, validated_data):
        # remove board from validated data if present
        validated_data.pop('board', None)
        # update assignee and reviewer if provided
        instance.assignee = validated_data.pop('assignee_id', instance.assignee)
        instance.reviewer = validated_data.pop('reviewer_id', instance.reviewer)
        # update other fields
        return super().update(instance, validated_data)

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