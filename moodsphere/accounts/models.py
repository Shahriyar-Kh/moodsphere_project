from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    """Extended User model with role-based access"""
    
    ROLE_CHOICES = (
        ('user', 'User'),
        ('therapist', 'Therapist'),
        ('admin', 'Administrator'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    is_profile_public = models.BooleanField(default=False)
    allow_messages = models.BooleanField(default=True)
    
    subscription_plan = models.CharField(max_length=20, default='free')
    subscription_expires = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_therapist(self):
        return self.role == 'therapist'
    
    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser


class TherapistProfile(models.Model):
    """Extended profile for therapist users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='therapist_profile')
    license_number = models.CharField(max_length=100, unique=True)
    specialization = models.CharField(max_length=200)
    years_experience = models.IntegerField(validators=[MinValueValidator(0)])
    qualification = models.TextField()
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    is_accepting_clients = models.BooleanField(default=True)
    available_slots = models.JSONField(default=dict)
    
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_reviews = models.IntegerField(default=0)
    
    is_verified = models.BooleanField(default=False)
    verification_document = models.FileField(upload_to='verifications/', null=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"