from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event, SwapRequest

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class EventSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    owner_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'start_time', 'end_time', 'status', 'owner', 'owner_username', 'owner_name', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']
    
    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}".strip() or obj.owner.username


class SwapRequestSerializer(serializers.ModelSerializer):
    requester_username = serializers.CharField(source='requester.username', read_only=True)
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    requester_slot_details = EventSerializer(source='requester_slot', read_only=True)
    recipient_slot_details = EventSerializer(source='recipient_slot', read_only=True)
    
    class Meta:
        model = SwapRequest
        fields = [
            'id', 'requester', 'recipient', 'requester_username', 'recipient_username',
            'requester_slot', 'recipient_slot', 'requester_slot_details', 'recipient_slot_details',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['requester', 'recipient', 'status', 'created_at', 'updated_at']