from time import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.db import transaction

from .models import CounselingSession, CounselorAssignment, CounselorAvailability, User, UserProfile, CounselorProfile

from .forms import (
    CounselingSessionForm,
    CounselorAvailabilityForm,
    CounselorVerificationForm,
    CustomAuthenticationForm,
    UserCounselorAssignmentForm, 
    UserRegistrationForm, 
    UserProfileForm, 
    CounselorRegistrationForm, 
    CounselorProfileForm
)
from .decorators import admin_required, user_required, counselor_required


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


# Add these views to core/views.py

@login_required
@counselor_required
def counselor_dashboard(request):
    """Enhanced dashboard for counselors"""
    try:
        counselor_profile = CounselorProfile.objects.get(user=request.user)
        
        # Get assigned users to this counselor
        assignments = CounselorAssignment.objects.filter(
            counselor=request.user,
            status='active'
        ).select_related('user__user_profile')
        
        # Get upcoming sessions
        upcoming_sessions = CounselingSession.objects.filter(
            assignment__counselor=request.user,
            status='scheduled',
            scheduled_time__gte=timezone.now()
        ).order_by('scheduled_time')[:5]
        
        # Get counselor availability
        availabilities = CounselorAvailability.objects.filter(
            counselor=request.user
        ).order_by('day', 'start_time')
        
        context = {
            'counselor_profile': counselor_profile,
            'assignments': assignments,
            'upcoming_sessions': upcoming_sessions,
            'availabilities': availabilities,
        }
        return render(request, 'counselor_dashboard.html', context)
    except CounselorProfile.DoesNotExist:
        messages.error(request, "Profile not found. Please contact support.")
        return redirect('home')


@login_required
@counselor_required
def manage_availability(request):
    """View for counselors to manage their availability"""
    if request.method == 'POST':
        form = CounselorAvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.counselor = request.user
            
            # Check if this time slot already exists
            existing = CounselorAvailability.objects.filter(
                counselor=request.user,
                day=availability.day,
                start_time=availability.start_time,
                end_time=availability.end_time
            )
            
            if existing.exists():
                existing.update(is_available=availability.is_available)
                messages.success(request, "Availability updated successfully.")
            else:
                availability.save()
                messages.success(request, "New availability added successfully.")
                
            return redirect('manage_availability')
    else:
        form = CounselorAvailabilityForm()
    
    # Get all availabilities for this counselor
    availabilities = CounselorAvailability.objects.filter(
        counselor=request.user
    ).order_by('day', 'start_time')
    
    context = {
        'form': form,
        'availabilities': availabilities
    }
    return render(request, 'manage_availability.html', context)


@login_required
@counselor_required
def delete_availability(request, availability_id):
    """View to delete a counselor availability slot"""
    availability = get_object_or_404(CounselorAvailability, pk=availability_id, counselor=request.user)
    
    if request.method == 'POST':
        availability.delete()
        messages.success(request, "Availability slot deleted successfully.")
        return redirect('manage_availability')
    
    return render(request, 'delete_availability_confirm.html', {'availability': availability})


@login_required
@counselor_required
def view_assignments(request):
    """View for counselors to see their assigned users"""
    assignments = CounselorAssignment.objects.filter(
        counselor=request.user
    ).select_related('user__user_profile').order_by('-assigned_date')
    
    context = {
        'assignments': assignments
    }
    return render(request, 'counselor_assignments.html', context)


@login_required
@counselor_required
def assignment_detail(request, assignment_id):
    """View details of a specific counselor-user assignment"""
    assignment = get_object_or_404(
        CounselorAssignment, 
        pk=assignment_id,
        counselor=request.user
    )
    
    # Get past and upcoming sessions for this assignment
    past_sessions = CounselingSession.objects.filter(
        assignment=assignment,
        scheduled_time__lt=timezone.now()
    ).order_by('-scheduled_time')
    
    upcoming_sessions = CounselingSession.objects.filter(
        assignment=assignment,
        scheduled_time__gte=timezone.now(),
        status='scheduled'
    ).order_by('scheduled_time')
    
    context = {
        'assignment': assignment,
        'past_sessions': past_sessions,
        'upcoming_sessions': upcoming_sessions
    }
    return render(request, 'assignment_detail.html', context)


@login_required
@counselor_required
def schedule_session(request, assignment_id):
    """View for counselors to schedule a session with an assigned user"""
    assignment = get_object_or_404(
        CounselorAssignment, 
        pk=assignment_id,
        counselor=request.user,
        status='active'
    )
    
    if request.method == 'POST':
        form = CounselingSessionForm(request.POST, counselor=request.user)
        if form.is_valid():
            session = form.save(commit=False)
            session.assignment = assignment
            session.save()
            
            messages.success(request, f"Session scheduled successfully with {assignment.user.user_profile.full_name}.")
            return redirect('assignment_detail', assignment_id=assignment.id)
    else:
        form = CounselingSessionForm(counselor=request.user)
    
    context = {
        'form': form,
        'assignment': assignment
    }
    return render(request, 'schedule_session.html', context)


@login_required
@counselor_required
def update_session_status(request, session_id):
    """View to update the status of a counseling session"""
    session = get_object_or_404(
        CounselingSession,
        pk=session_id,
        assignment__counselor=request.user
    )
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in [s[0] for s in CounselingSession.STATUS_CHOICES]:
            session.status = status
            session.save()
            
            # If completed, update the last session date of the assignment
            if status == 'completed':
                session.assignment.last_session = timezone.now()
                session.assignment.save()
                
            messages.success(request, f"Session status updated to {session.get_status_display()}.")
        else:
            messages.error(request, "Invalid session status.")
            
        return redirect('assignment_detail', assignment_id=session.assignment.id)
    
    # If not POST, show confirmation form
    context = {
        'session': session,
        'status_choices': CounselingSession.STATUS_CHOICES
    }
    return render(request, 'update_session_status.html', context)


@login_required
@admin_required
def verify_counselors(request):
    """View for admins to verify counselor accounts"""
    pending_counselors = CounselorProfile.objects.filter(
        verification_status='pending'
    ).select_related('user')
    
    verified_counselors = CounselorProfile.objects.filter(
        verification_status='verified'
    ).select_related('user')
    
    rejected_counselors = CounselorProfile.objects.filter(
        verification_status='rejected'
    ).select_related('user')
    
    context = {
        'pending_counselors': pending_counselors,
        'verified_counselors': verified_counselors,
        'rejected_counselors': rejected_counselors
    }
    return render(request, 'verify_counselors.html', context)


@login_required
@admin_required
def counselor_verification_detail(request, counselor_id):
    """View for admins to review and verify a specific counselor"""
    counselor_profile = get_object_or_404(
        CounselorProfile, 
        user__id=counselor_id
    )
    
    if request.method == 'POST':
        form = CounselorVerificationForm(request.POST, instance=counselor_profile)
        if form.is_valid():
            form.save()
            status = form.cleaned_data['verification_status']
            name = counselor_profile.full_name
            
            if status == 'verified':
                messages.success(request, f"Counselor {name} has been verified successfully.")
            else:
                messages.warning(request, f"Counselor {name} has been rejected.")
                
            # Add code to send email notification to counselor about verification status
            
            return redirect('verify_counselors')
    else:
        form = CounselorVerificationForm(instance=counselor_profile)
    
    context = {
        'form': form,
        'counselor_profile': counselor_profile
    }
    return render(request, 'counselor_verification_detail.html', context)


@login_required
@admin_required
def assign_counselor(request):
    """View for admins to assign users to counselors"""
    if request.method == 'POST':
        form = UserCounselorAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save()
            messages.success(request, f"{assignment.user.user_profile.full_name} has been assigned to {assignment.counselor.counselor_profile.full_name}.")
            return redirect('assign_counselor')
    else:
        form = UserCounselorAssignmentForm()
    
    # Get all active assignments
    active_assignments = CounselorAssignment.objects.filter(
        status='active'
    ).select_related('user__user_profile', 'counselor__counselor_profile')
    
    context = {
        'form': form,
        'active_assignments': active_assignments
    }
    return render(request, 'assign_counselor.html', context)