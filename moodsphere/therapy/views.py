# therapy/views.py
from .models import TherapySession, TherapistProfile, TherapistReview
from .serializers import TherapySessionSerializer, TherapistProfileSerializer

class TherapistViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve therapists"""
    
    serializer_class = TherapistProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TherapistProfile.objects.filter(
            is_verified=True,
            is_accepting_clients=True
        ).select_related('user')
        
        # Filter by specialization
        specialization = self.request.query_params.get('specialization')
        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization)
        
        # Sort by rating
        return queryset.order_by('-average_rating')
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Get therapist availability"""
        therapist = self.get_object()
        return Response({
            'available_slots': therapist.available_slots,
            'is_accepting_clients': therapist.is_accepting_clients
        })


class TherapySessionViewSet(viewsets.ModelViewSet):
    """Manage therapy sessions"""
    
    serializer_class = TherapySessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_therapist:
            return TherapySession.objects.filter(therapist=user)
        else:
            return TherapySession.objects.filter(client=user)
    
    def perform_create(self, serializer):
        """Book a therapy session"""
        therapist_id = self.request.data.get('therapist_id')
        
        try:
            therapist = User.objects.get(id=therapist_id, role='therapist')
            therapist_profile = therapist.therapist_profile
            
            serializer.save(
                client=self.request.user,
                therapist=therapist,
                fee_amount=therapist_profile.consultation_fee
            )
        except User.DoesNotExist:
            raise ValidationError("Therapist not found")
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark session as completed (therapist only)"""
        session = self.get_object()
        
        if request.user != session.therapist:
            return Response(
                {'error': 'Only the therapist can complete the session'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        session.status = 'completed'
        session.session_notes = request.data.get('session_notes', '')
        session.save()
        
        return Response({'status': 'Session marked as completed'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a session"""
        session = self.get_object()
        
        if request.user not in [session.client, session.therapist]:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if cancellation is allowed (e.g., 24 hours before)
        hours_until_session = (
            timezone.make_aware(
                timezone.datetime.combine(session.scheduled_date, session.scheduled_time)
            ) - timezone.now()
        ).total_seconds() / 3600
        
        if hours_until_session < 24:
            return Response(
                {'error': 'Cannot cancel within 24 hours of scheduled time'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.status = 'cancelled'
        session.save()
        
        return Response({'status': 'Session cancelled'})
