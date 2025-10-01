# journal/serializers.py
from rest_framework import serializers
from .models import JournalEntry

class JournalEntrySerializer(serializers.ModelSerializer):
    mood_display = serializers.CharField(source='get_mood_display', read_only=True)
    
    class Meta:
        model = JournalEntry
        fields = [
            'id', 'title', 'content', 'mood', 'mood_display',
            'ai_summary', 'detected_emotions', 'keywords',
            'sentiment_score', 'suggestions', 'image',
            'voice_note', 'is_private', 'entry_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'ai_summary', 'detected_emotions', 'keywords',
            'sentiment_score', 'suggestions', 'created_at', 'updated_at'
        ]
