# community/urls.py
from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.CommunityListView.as_view(), name='list'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('post/<int:pk>/like/', views.PostLikeView.as_view(), name='post_like'),
]
