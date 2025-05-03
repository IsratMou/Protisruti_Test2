from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.db import transaction

from .models import User, UserProfile, CounselorProfile
from .forms import (
    CustomAuthenticationForm, 
    UserRegistrationForm, 
    UserProfileForm, 
    CounselorRegistrationForm, 
    CounselorProfileForm
)
from .decorators import user_required, counselor_required


def home(request):
    """Home page view"""
    return render(request, 'home.html')


def login_options(request):
    """View to choose between user and counselor login"""
    return render(request, 'login_options.html')


class CustomLoginView(LoginView):
    """Custom login view using our authentication form"""
    form_class = CustomAuthenticationForm
    template_name = 'login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.user_type == 'user':
            return reverse_lazy('user_dashboard')
        elif user.user_type == 'counselor':
            return reverse_lazy('counselor_dashboard')
        else:
            return reverse_lazy('home')
    
    def form_valid(self, form):
        """Override form_valid to add custom messages and validations"""
        # Call the parent class form_valid which calls login() and redirects
        response = super().form_valid(form)
        user = self.request.user
        
        # Add appropriate welcome message based on user type
        if user.user_type == 'user':
            messages.success(self.request, f"Welcome back! You're now logged in as a user.")
        elif user.user_type == 'counselor':
            if user.counselor_profile.verification_status == 'pending':
                messages.warning(self.request, "Your account is still pending verification.")
            elif user.counselor_profile.verification_status == 'rejected':
                messages.error(self.request, "Your account verification was rejected. Please contact support.")
            else:
                messages.success(self.request, f"Welcome back! You're now logged in as a counselor.")
        
        return response


def register_user(request):
    """View for user registration"""
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user = user_form.save()
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
            
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'register_user.html', context)


def register_counselor(request):
    """View for counselor registration"""
    if request.method == 'POST':
        user_form = CounselorRegistrationForm(request.POST)
        profile_form = CounselorProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user = user_form.save()
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.verification_status = 'pending'  # Ensure status is set to pending
                profile.save()
            
            messages.success(request, 'Registration successful. Your account is pending verification.')
            return redirect('login')
    else:
        user_form = CounselorRegistrationForm()
        profile_form = CounselorProfileForm()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'register_counselor.html', context)


def logout_view(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
@user_required
def user_dashboard(request):
    """Dashboard for regular users"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        context = {
            'user_profile': user_profile,
        }
        return render(request, 'user_dashboard.html', context)
    except UserProfile.DoesNotExist:
        messages.error(request, "Profile not found. Please contact support.")
        return redirect('home')


@login_required
@counselor_required
def counselor_dashboard(request):
    """Dashboard for counselors"""
    try:
        counselor_profile = CounselorProfile.objects.get(user=request.user)
        context = {
            'counselor_profile': counselor_profile,
        }
        return render(request, 'counselor_dashboard.html', context)
    except CounselorProfile.DoesNotExist:
        messages.error(request, "Profile not found. Please contact support.")
        return redirect('home')


@login_required
def profile_edit(request):
    """View to edit user or counselor profile"""
    if request.user.user_type == 'user':
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if request.method == 'POST':
                profile_form = UserProfileForm(request.POST, instance=user_profile)
                if profile_form.is_valid():
                    profile_form.save()
                    messages.success(request, 'Your profile has been updated successfully.')
                    return redirect('user_dashboard')
            else:
                profile_form = UserProfileForm(instance=user_profile)
            
            context = {'profile_form': profile_form}
            return render(request, 'edit_user_profile.html', context)
        except UserProfile.DoesNotExist:
            messages.error(request, "Profile not found.")
            return redirect('home')
    
    elif request.user.user_type == 'counselor':
        try:
            counselor_profile = CounselorProfile.objects.get(user=request.user)
            if request.method == 'POST':
                profile_form = CounselorProfileForm(request.POST, request.FILES, instance=counselor_profile)
                if profile_form.is_valid():
                    profile = profile_form.save(commit=False)
                    # Don't update verification status when editing profile
                    profile.verification_status = counselor_profile.verification_status
                    profile.save()
                    messages.success(request, 'Your profile has been updated successfully.')
                    return redirect('counselor_dashboard')
            else:
                profile_form = CounselorProfileForm(instance=counselor_profile)
            
            context = {'profile_form': profile_form}
            return render(request, 'edit_counselor_profile.html', context)
        except CounselorProfile.DoesNotExist:
            messages.error(request, "Profile not found.")
            return redirect('home')
    
    return redirect('home')


def password_reset_request(request):
    """View to handle password reset requests"""
    # This would be implemented with Django's built-in password reset views
    pass