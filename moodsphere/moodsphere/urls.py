# moodsphere/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from analysis.views import EmotionAnalysisViewSet
from journal.views import JournalEntryViewSet
from therapy.views import TherapistViewSet, TherapySessionViewSet
from accounts.views import DashboardView

# API Router
router = DefaultRouter()
router.register(r'analysis', EmotionAnalysisViewSet, basename='analysis')
router.register(r'journal', JournalEntryViewSet, basename='journal')
router.register(r'therapists', TherapistViewSet, basename='therapist')
router.register(r'sessions', TherapySessionViewSet, basename='session')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('accounts.urls')),
    
    # API endpoints
    path('api/', include(router.urls)),
    
    # Web views
    path('', include('core.urls')),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('community/', include('community.urls')),
    path('analytics/', include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

