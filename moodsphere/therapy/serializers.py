# therapy/serializers.py
from rest_framework import serializers
from accounts.models import User, TherapistProfile
from .models import TherapySession, TherapistReview

class TherapistProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = TherapistProfile
        fields = [
            'id', 'user', 'user_name', 'user_email',
            'license_number', 'specialization', 'years_experience',
            'qualification', 'consultation_fee', 'is_accepting_clients',
            'average_rating', 'total_reviews', 'is_verified'
        ]
        read_only_fields = ['average_rating', 'total_reviews', 'is_verified']


class TherapySessionSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    therapist_name = serializers.CharField(source='therapist.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TherapySession
        fields = [
            'id', 'client', 'client_name', 'therapist', 'therapist_name',
            'scheduled_date', 'scheduled_time', 'duration_minutes',
            'session_type', 'status', 'status_display', 'meeting_link',
            'fee_amount', 'is_paid', 'created_at'
        ]
        read_only_fields = ['client', 'fee_amount', 'created_at']

