# journal/views.py
from .models import JournalEntry
from .serializers import JournalEntrySerializer
from datetime import datetime, timedelta

class JournalEntryViewSet(viewsets.ModelViewSet):
    """API endpoints for journal entries"""
    
    serializer_class = JournalEntrySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create journal entry with AI analysis"""
        content = self.request.data.get('content', '')
        
        # Call journal API for analysis
        try:
            response = requests.post(
                f"{settings.FASTAPI_SERVICES['JOURNAL_API']}/journal/analyze",
                json={'text': content},
                timeout=30
            )
            
            if response.status_code == 200:
                analysis = response.json()
                
                serializer.save(
                    user=self.request.user,
                    ai_summary=analysis.get('ai_summary', ''),
                    detected_emotions=analysis.get('emotion_distribution', {}),
                    keywords=analysis.get('keywords', []),
                    sentiment_score=analysis.get('sentiment_score', 0),
                    suggestions=analysis.get('suggestion', ''),
                    entry_date=self.request.data.get('entry_date', timezone.now().date())
                )
            else:
                # Save without analysis if service unavailable
                serializer.save(
                    user=self.request.user,
                    entry_date=self.request.data.get('entry_date', timezone.now().date())
                )
        
        except Exception as e:
            # Fallback: save without analysis
            serializer.save(
                user=self.request.user,
                entry_date=self.request.data.get('entry_date', timezone.now().date())
            )
    
    @action(detail=False, methods=['get'])
    def streak(self, request):
        """Calculate journaling streak"""
        entries = self.get_queryset().order_by('-entry_date')
        
        if not entries.exists():
            return Response({'streak': 0, 'last_entry': None})
        
        streak = 0
        today = timezone.now().date()
        current_date = today
        
        entry_dates = set(entries.values_list('entry_date', flat=True))
        
        # Check if there's an entry today or yesterday to start counting
        if today not in entry_dates and (today - timedelta(days=1)) not in entry_dates:
            return Response({
                'streak': 0,
                'last_entry': entries.first().entry_date
            })
        
        # Count consecutive days
        while current_date in entry_dates:
            streak += 1
            current_date -= timedelta(days=1)
        
        return Response({
            'streak': streak,
            'last_entry': entries.first().entry_date,
            'total_entries': entries.count()
        })
    
    @action(detail=False, methods=['get'])
    def insights(self, request):
        """Get mood insights and trends"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        entries = self.get_queryset().filter(entry_date__gte=start_date)
        
        mood_distribution = {}
        for entry in entries:
            mood = entry.mood
            mood_distribution[mood] = mood_distribution.get(mood, 0) + 1
        
        # Keyword frequency
        all_keywords = []
        for entry in entries:
            all_keywords.extend(entry.keywords)
        
        from collections import Counter
        keyword_freq = Counter(all_keywords).most_common(10)
        
        return Response({
            'total_entries': entries.count(),
            'mood_distribution': mood_distribution,
            'top_keywords': [{'word': word, 'count': count} for word, count in keyword_freq],
            'date_range': {
                'start': start_date,
                'end': timezone.now().date()
            }
        })
