from django.db import models
from accounts.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class TherapySession(models.Model):
    """Therapy session bookings"""
    
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='therapy_sessions')
    therapist = models.ForeignKey(
        User, on_delete=models.CASCADE, 
        related_name='therapist_sessions',
        limit_choices_to={'role': 'therapist'}
    )
    
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    
    session_type = models.CharField(max_length=50, default='individual')
    session_notes = models.TextField(blank=True)
    client_notes = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    meeting_link = models.URLField(blank=True)
    
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date', '-scheduled_time']
    
    def __str__(self):
        return f"{self.client.username} with {self.therapist.username}"


class TherapistReview(models.Model):
    """Reviews for therapists"""
    
    therapist = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='received_reviews',
        limit_choices_to={'role': 'therapist'}
    )
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    session = models.ForeignKey(TherapySession, on_delete=models.CASCADE, related_name='reviews')
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']