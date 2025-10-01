# analysis/serializers.py
from rest_framework import serializers
from .models import EmotionAnalysis

class EmotionAnalysisSerializer(serializers.ModelSerializer):
    analysis_type_display = serializers.CharField(source='get_analysis_type_display', read_only=True)
    
    class Meta:
        model = EmotionAnalysis
        fields = [
            'id', 'user', 'analysis_type', 'analysis_type_display',
            'input_text', 'dominant_emotion', 'emotion_scores',
            'confidence_score', 'created_at', 'processing_time'
        ]
        read_only_fields = ['user', 'created_at']
