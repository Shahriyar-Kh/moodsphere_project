from django.db import models
from accounts.models import User

class JournalEntry(models.Model):
    """Enhanced journal entries with AI analysis"""
    
    MOOD_CHOICES = (
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('anxious', 'Anxious'),
        ('calm', 'Calm'),
        ('excited', 'Excited'),
        ('neutral', 'Neutral'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries')
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    
    ai_summary = models.TextField(blank=True)
    detected_emotions = models.JSONField(default=dict)
    keywords = models.JSONField(default=list)
    sentiment_score = models.FloatField(default=0)
    suggestions = models.TextField(blank=True)
    
    image = models.ImageField(upload_to='journal_images/', null=True, blank=True)
    voice_note = models.FileField(upload_to='journal_audio/', null=True, blank=True)
    
    is_private = models.BooleanField(default=True)
    
    entry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-entry_date', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.entry_date}"