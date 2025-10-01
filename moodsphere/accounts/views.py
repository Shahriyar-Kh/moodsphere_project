# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, TherapistProfile
from .serializers import UserSerializer, RegisterSerializer
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm

class RegisterView(View):
    """User registration view"""
    
    template_name = 'accounts/register.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Create therapist profile if role is therapist
            if user.role == 'therapist':
                TherapistProfile.objects.create(
                    user=user,
                    license_number='',
                    specialization='',
                    years_experience=0,
                    qualification=''
                )
            
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('accounts:login')
        
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    """User login view"""
    
    template_name = 'accounts/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = UserLoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                user.last_activity = timezone.now()
                user.save()
                
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                
                # Redirect based on role
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    """User logout view"""
    
    @method_decorator(login_required)
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
        return redirect('core:home')


class ProfileView(TemplateView):
    """View user profile"""
    
    template_name = 'accounts/profile.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['user'] = user
        context['is_therapist'] = user.is_therapist
        
        if user.is_therapist:
            context['therapist_profile'] = user.therapist_profile
            context['total_sessions'] = TherapySession.objects.filter(
                therapist=user
            ).count()
            context['completed_sessions'] = TherapySession.objects.filter(
                therapist=user, status='completed'
            ).count()
        else:
            context['total_analyses'] = EmotionAnalysis.objects.filter(
                user=user
            ).count()
            context['total_entries'] = JournalEntry.objects.filter(
                user=user
            ).count()
        
        return context


class ProfileUpdateView(View):
    """Update user profile"""
    
    template_name = 'accounts/profile_update.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        form = ProfileUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        
        return render(request, self.template_name, {'form': form})


class PasswordChangeView(View):
    """Change user password"""
    
    template_name = 'accounts/password_change.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        user = request.user
        
        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return render(request, self.template_name)
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return render(request, self.template_name)
        
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, self.template_name)
        
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        
        messages.success(request, 'Password changed successfully!')
        return redirect('accounts:profile')


# API Views for REST endpoints
class RegisterAPIView(APIView):
    """API endpoint for user registration"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    """API endpoint for user login"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Update last activity
        user.last_activity = timezone.now()
        user.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class ProfileAPIView(APIView):
    """API endpoint for user profile"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

