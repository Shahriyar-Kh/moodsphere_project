# analysis/views.py
import requests
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import EmotionAnalysis
from .serializers import EmotionAnalysisSerializer

class EmotionAnalysisViewSet(viewsets.ModelViewSet):
    """API endpoints for emotion analysis"""
    
    serializer_class = EmotionAnalysisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return EmotionAnalysis.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def analyze_text(self, request):
        """Analyze text emotion via FastAPI"""
        text = request.data.get('text', '')
        
        if not text:
            return Response(
                {'error': 'Text is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Call FastAPI text analysis service
            response = requests.post(
                f"{settings.FASTAPI_SERVICES['TEXT_ANALYSIS']}/analyze",
                json={'text': text},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Save analysis to database
                analysis = EmotionAnalysis.objects.create(
                    user=request.user,
                    analysis_type='text',
                    input_text=text,
                    dominant_emotion=result.get('emotion', 'neutral'),
                    emotion_scores=result.get('emotion_distribution', {}),
                    confidence_score=max(result.get('emotion_distribution', {}).values()) if result.get('emotion_distribution') else 0
                )
                
                return Response({
                    'analysis_id': analysis.id,
                    'result': result
                })
            else:
                return Response(
                    {'error': 'Analysis service error'}, 
                    status=status.HTTP_502_BAD_GATEWAY
                )
        
        except requests.exceptions.RequestException as e:
            return Response(
                {'error': f'Service unavailable: {str(e)}'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    @action(detail=False, methods=['post'])
    def analyze_face(self, request):
        """Analyze face emotion via FastAPI"""
        image_data = request.data.get('image', '')
        
        if not image_data:
            return Response(
                {'error': 'Image data is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            response = requests.post(
                f"{settings.FASTAPI_SERVICES['FACE_ANALYSIS']}/analyze_face",
                json={'image': image_data},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                analysis = EmotionAnalysis.objects.create(
                    user=request.user,
                    analysis_type='face',
                    dominant_emotion=result.get('emotion', 'neutral'),
                    emotion_scores={'emotion': result.get('emotion', 'neutral')},
                    confidence_score=0.85
                )
                
                return Response({
                    'analysis_id': analysis.id,
                    'result': result
                })
            else:
                return Response(
                    {'error': 'Face analysis failed'}, 
                    status=status.HTTP_502_BAD_GATEWAY
                )
        
        except requests.exceptions.RequestException as e:
            return Response(
                {'error': f'Service unavailable: {str(e)}'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    @action(detail=False, methods=['post'])
    def analyze_speech(self, request):
        """Analyze speech emotion via FastAPI"""
        audio_data = request.data.get('audio', '')
        transcript = request.data.get('transcript', '')
        
        if not audio_data:
            return Response(
                {'error': 'Audio data is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            response = requests.post(
                f"{settings.FASTAPI_SERVICES['SPEECH_ANALYSIS']}/analyze_speech",
                json={'audio': audio_data, 'transcript': transcript},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                analysis = EmotionAnalysis.objects.create(
                    user=request.user,
                    analysis_type='speech',
                    input_text=transcript,
                    dominant_emotion=result.get('emotion', 'neutral'),
                    emotion_scores=result.get('probabilities', {}),
                    confidence_score=max(result.get('probabilities', {}).values()) if result.get('probabilities') else 0
                )
                
                return Response({
                    'analysis_id': analysis.id,
                    'result': result
                })
            else:
                return Response(
                    {'error': 'Speech analysis failed'}, 
                    status=status.HTTP_502_BAD_GATEWAY
                )
        
        except requests.exceptions.RequestException as e:
            return Response(
                {'error': f'Service unavailable: {str(e)}'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get user's analysis history"""
        analysis_type = request.query_params.get('type', None)
        queryset = self.get_queryset()
        
        if analysis_type:
            queryset = queryset.filter(analysis_type=analysis_type)
        
        queryset = queryset.order_by('-created_at')[:50]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get analysis statistics for the user"""
        queryset = self.get_queryset()
        
        total_analyses = queryset.count()
        by_type = {}
        
        for analysis_type in ['text', 'face', 'speech']:
            by_type[analysis_type] = queryset.filter(analysis_type=analysis_type).count()
        
        # Emotion frequency
        emotion_counts = {}
        for analysis in queryset:
            emotion = analysis.dominant_emotion
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        return Response({
            'total_analyses': total_analyses,
            'by_type': by_type,
            'emotion_frequency': emotion_counts,
            'most_common_emotion': max(emotion_counts, key=emotion_counts.get) if emotion_counts else None
        })
