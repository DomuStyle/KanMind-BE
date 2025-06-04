from rest_framework import serializers
from kanmind_app.models import Boards
from django.contrib.auth.models import User

class BoardSerializer(serializers.ModelSerializer):
    # defines the field for the number of members as a SerializerMethodField
    member_count = serializers.SerializerMethodField()
    # defines the field for the total number of tasks
    ticket_count = serializers.SerializerMethodField()
    # defines the field for the number of to-do tasks
    tasks_to_do_count = serializers.SerializerMethodField()
    # defines the field for the number of tasks with high priority
    tasks_high_prio_count = serializers.SerializerMethodField()
    # defines the field for the id of the owner
    owner_id = serializers.PrimaryKeyRelatedField(source='owner', read_only=True)
    # defines the field for member ids (only for post requests)
    members = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=User.objects.all(), 
        write_only=True,
        required=False
    )

    class Meta:
        # links the serializer to the board model
        model = Boards
        # defines the fields to be serialized
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
        # sets the title field as required
        extra_kwargs = {'title': {'required': True}}

    def get_member_count(self, obj):
        # returns the number of members in the board
        return obj.members.count()

    def get_ticket_count(self, obj):
        # returns the total number of tasks in the board
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        # returns the number of tasks with status 'to-do'
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        # returns the number of tasks with high priority
        return obj.tasks.filter(priority='high').count()

    def create(self, validated_data):
        # extracts members from the validated data
        members = validated_data.pop('members', [])
        # creates a new board with the authenticated user as the owner
        board = Boards.objects.create(owner=self.context['request'].user, **validated_data)
        # adds members to the board (excluding the owner)
        for member in members:
            if member != self.context['request'].user:  # prevents the owner from being added twice
                board.members.add(member)
        return board