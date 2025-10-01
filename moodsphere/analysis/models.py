from django.db import models
from accounts.models import User

class EmotionAnalysis(models.Model):
    """Store emotion analysis results"""
    
    ANALYSIS_TYPE_CHOICES = (
        ('text', 'Text Analysis'),
        ('face', 'Face Analysis'),
        ('speech', 'Speech Analysis'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    analysis_type = models.CharField(max_length=10, choices=ANALYSIS_TYPE_CHOICES)
    
    input_text = models.TextField(blank=True)
    input_file = models.FileField(upload_to='analysis_inputs/', null=True, blank=True)
    
    dominant_emotion = models.CharField(max_length=50)
    emotion_scores = models.JSONField(default=dict)
    confidence_score = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(auto_now=True)
    processing_time = models.FloatField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.analysis_type} - {self.dominant_emotion}"