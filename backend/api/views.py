from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Event, SwapRequest
from .serializers import UserSerializer, EventSerializer, SwapRequestSerializer


def send_notification(user_id, notification_data):
    """Send real-time notification via WebSocket"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {
            'type': 'notification_message',
            'data': notification_data
        }
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': serializer.data,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    from django.contrib.auth import authenticate
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        serializer = UserSerializer(user)
        return Response({
            'user': serializer.data,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Event.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        event = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in ['BUSY', 'SWAPPABLE', 'SWAP_PENDING']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        event.status = new_status
        event.save()
        serializer = self.get_serializer(event)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_swappable_slots(request):
    # Get all swappable slots except the current user's
    slots = Event.objects.filter(status='SWAPPABLE').exclude(owner=request.user)
    serializer = EventSerializer(slots, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_swap_request(request):
    my_slot_id = request.data.get('mySlotId')
    their_slot_id = request.data.get('theirSlotId')
    
    if not my_slot_id or not their_slot_id:
        return Response({'error': 'Both slot IDs are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Verify my slot
        my_slot = Event.objects.get(id=my_slot_id, owner=request.user)
        if my_slot.status != 'SWAPPABLE':
            return Response({'error': 'Your slot is not swappable'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify their slot
        their_slot = Event.objects.get(id=their_slot_id)
        if their_slot.owner == request.user:
            return Response({'error': 'Cannot swap with your own slot'}, status=status.HTTP_400_BAD_REQUEST)
        if their_slot.status != 'SWAPPABLE':
            return Response({'error': 'Target slot is not swappable'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create swap request and update slot statuses
        with transaction.atomic():
            swap_request = SwapRequest.objects.create(
                requester=request.user,
                recipient=their_slot.owner,
                requester_slot=my_slot,
                recipient_slot=their_slot,
                status='PENDING'
            )
            
            my_slot.status = 'SWAP_PENDING'
            my_slot.save()
            
            their_slot.status = 'SWAP_PENDING'
            their_slot.save()
        
        # Send real-time notification to recipient
        send_notification(their_slot.owner.id, {
            'type': 'swap_request_received',
            'message': f'{request.user.username} wants to swap slots with you!',
            'swap_request_id': swap_request.id,
            'requester_slot': my_slot.title,
            'recipient_slot': their_slot.title
        })
        
        serializer = SwapRequestSerializer(swap_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except Event.DoesNotExist:
        return Response({'error': 'One or both slots not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_to_swap(request, request_id):
    accept = request.data.get('accept')
    
    if accept is None:
        return Response({'error': 'Accept parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        swap_request = SwapRequest.objects.get(id=request_id, recipient=request.user, status='PENDING')
        
        with transaction.atomic():
            if accept:
                # Accept the swap - exchange owners
                requester_slot = swap_request.requester_slot
                recipient_slot = swap_request.recipient_slot
                
                # Swap the owners
                temp_owner = requester_slot.owner
                requester_slot.owner = recipient_slot.owner
                recipient_slot.owner = temp_owner
                
                # Set status back to BUSY
                requester_slot.status = 'BUSY'
                recipient_slot.status = 'BUSY'
                
                requester_slot.save()
                recipient_slot.save()
                
                swap_request.status = 'ACCEPTED'
                
                # Send notification to requester
                send_notification(swap_request.requester.id, {
                    'type': 'swap_request_accepted',
                    'message': f'{request.user.username} accepted your swap request!',
                    'swap_request_id': swap_request.id
                })
            else:
                # Reject the swap - revert to SWAPPABLE
                swap_request.requester_slot.status = 'SWAPPABLE'
                swap_request.recipient_slot.status = 'SWAPPABLE'
                swap_request.requester_slot.save()
                swap_request.recipient_slot.save()
                
                swap_request.status = 'REJECTED'
                
                # Send notification to requester
                send_notification(swap_request.requester.id, {
                    'type': 'swap_request_rejected',
                    'message': f'{request.user.username} rejected your swap request.',
                    'swap_request_id': swap_request.id
                })
            
            swap_request.save()
        
        serializer = SwapRequestSerializer(swap_request)
        return Response(serializer.data)
    
    except SwapRequest.DoesNotExist:
        return Response({'error': 'Swap request not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_swap_requests(request):
    # Get incoming requests (where user is recipient)
    incoming = SwapRequest.objects.filter(recipient=request.user, status='PENDING')
    # Get outgoing requests (where user is requester)
    outgoing = SwapRequest.objects.filter(requester=request.user)
    
    incoming_serializer = SwapRequestSerializer(incoming, many=True)
    outgoing_serializer = SwapRequestSerializer(outgoing, many=True)
    
    return Response({
        'incoming': incoming_serializer.data,
        'outgoing': outgoing_serializer.data
    })