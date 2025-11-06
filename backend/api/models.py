from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    STATUS_CHOICES = [
        ('BUSY', 'Busy'),
        ('SWAPPABLE', 'Swappable'),
        ('SWAP_PENDING', 'Swap Pending'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='BUSY')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.title} - {self.owner.username}"


class SwapRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]
    
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swap_requests_sent')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swap_requests_received')
    requester_slot = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='swap_requests_as_requester')
    recipient_slot = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='swap_requests_as_recipient')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Swap Request: {self.requester.username} -> {self.recipient.username}"