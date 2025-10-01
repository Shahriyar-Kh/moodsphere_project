# accounts/views.py
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard - routes to role-specific dashboard"""
    
    def get_template_name(self):
        user = self.request.user
        
        if user.is_admin_user:
            return 'dashboards/admin_dashboard.html'
        elif user.is_therapist:
            return 'dashboards/therapist_dashboard.html'
        else:
            return 'dashboards/user_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Common context
        context['recent_analyses'] = EmotionAnalysis.objects.filter(
            user=user
        ).order_by('-created_at')[:5]
        
        # Role-specific context
        if user.role == 'user':
            context['journal_streak'] = self._calculate_streak(user)
            context['recent_entries'] = JournalEntry.objects.filter(
                user=user
            ).order_by('-entry_date')[:5]
            
        elif user.is_therapist:
            context['upcoming_sessions'] = TherapySession.objects.filter(
                therapist=user,
                status='scheduled',
                scheduled_date__gte=timezone.now().date()
            ).order_by('scheduled_date', 'scheduled_time')[:10]
            
        elif user.is_admin_user:
            context['total_users'] = User.objects.count()
            context['total_analyses'] = EmotionAnalysis.objects.count()
            context['pending_verifications'] = TherapistProfile.objects.filter(
                is_verified=False
            ).count()
        
        return context
    
    def _calculate_streak(self, user):
        entries = JournalEntry.objects.filter(user=user).order_by('-entry_date')
        if not entries.exists():
            return 0
        
        streak = 0
        today = timezone.now().date()
        current_date = today
        entry_dates = set(entries.values_list('entry_date', flat=True))
        
        if today not in entry_dates and (today - timedelta(days=1)) not in entry_dates:
            return 0
        
        while current_date in entry_dates:
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak