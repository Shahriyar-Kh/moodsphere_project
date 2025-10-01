# analytics/urls.py
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.AnalyticsView.as_view(), name='overview'),
    path('mood-trends/', views.MoodTrendsView.as_view(), name='mood_trends'),
    path('goals/', views.GoalsView.as_view(), name='goals'),
    path('goals/create/', views.GoalCreateView.as_view(), name='goal_create'),
    path('export/', views.ExportDataView.as_view(), name='export'),
]