from time import timezone
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from .models import CounselingSession, CounselorAssignment, CounselorAvailability, User, UserProfile, CounselorProfile, VictimCounselorAssignment


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom login form with styling
    """
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email Address',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
    }))
    
    class Meta:
        model = User
        fields = ['email', 'password']


class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration
    """
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email Address',
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password',
    }))
    phone_number = forms.CharField(
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number',
        }),
        required=False
    )
    
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'phone_number']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'user'
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """
    Form for user profile information
    """
    full_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Full Name',
    }))
    gender = forms.ChoiceField(
        choices=UserProfile.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    age = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Age',
    }), required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Address',
        'rows': 3,
    }), required=False)
    emergency_contact = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Emergency Contact Number',
    }), required=False)
    
    class Meta:
        model = UserProfile
        fields = ['full_name', 'gender', 'age', 'address', 'emergency_contact']


class CounselorRegistrationForm(UserCreationForm):
    """
    Form for counselor registration
    """
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email Address',
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password',
    }))
    phone_number = forms.CharField(
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number',
        }),
        required=False
    )
    
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'phone_number']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'counselor'
        if commit:
            user.save()
        return user


class CounselorProfileForm(forms.ModelForm):
    """
    Form for counselor profile information
    """
    full_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Full Name',
    }))
    specialization = forms.ChoiceField(
        choices=CounselorProfile.SPECIALIZATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    qualification = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Qualifications',
    }))
    experience_years = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Years of Experience',
    }))
    bio = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Professional Bio',
        'rows': 4,
    }))
    verification_document = forms.FileField(widget=forms.FileInput(attrs={
        'class': 'form-control',
    }), required=False)
    
    class Meta:
        model = CounselorProfile
        fields = ['full_name', 'specialization', 'qualification', 'experience_years', 'bio', 'verification_document']
        
        
# Add these forms to core/forms.py

class CounselorVerificationForm(forms.ModelForm):
    """
    Form for admin to verify counselor accounts
    """
    VERIFICATION_CHOICES = (
        ('verified', 'Verify'),
        ('rejected', 'Reject'),
    )
    
    verification_status = forms.ChoiceField(
        choices=VERIFICATION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    verification_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Notes regarding verification decision',
            'rows': 3,
        }),
        required=False
    )
    
    class Meta:
        model = CounselorProfile
        fields = ['verification_status', 'verification_notes']


class CounselorAvailabilityForm(forms.ModelForm):
    """
    Form for counselors to set their availability
    """
    day = forms.ChoiceField(
        choices=CounselorAvailability.DAY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    is_available = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = CounselorAvailability
        fields = ['day', 'start_time', 'end_time', 'is_available']
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be later than start time")
        
        return cleaned_data


class CounselingSessionForm(forms.ModelForm):
    """
    Form for scheduling counseling sessions
    """
    scheduled_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    duration_minutes = forms.ChoiceField(
        choices=[(30, '30 minutes'), (45, '45 minutes'), (60, '1 hour'), (90, '1.5 hours'), (120, '2 hours')],
        initial=60,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Additional notes for the session',
            'rows': 3
        }),
        required=False
    )
    
    class Meta:
        model = CounselingSession
        fields = ['scheduled_time', 'duration_minutes', 'notes']
    
    def __init__(self, *args, **kwargs):
        self.counselor = kwargs.pop('counselor', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
    def clean_scheduled_time(self):
        scheduled_time = self.cleaned_data.get('scheduled_time')
        
        # Check if the scheduled time is in the future
        if scheduled_time and scheduled_time <= timezone.now():
            raise forms.ValidationError("Scheduled time must be in the future")
            
        # If counselor is provided, check availability
        if self.counselor and scheduled_time:
            # Get day of week as lowercase string
            day_of_week = scheduled_time.strftime('%A').lower()
            time_of_day = scheduled_time.time()
            
            # Check if counselor is available at this time
            availability_exists = CounselorAvailability.objects.filter(
                counselor=self.counselor,
                day=day_of_week,
                start_time__lte=time_of_day,
                end_time__gte=time_of_day,
                is_available=True
            ).exists()
            
            if not availability_exists:
                raise forms.ValidationError("The counselor is not available at this time")
            
            # Check if counselor already has a session at this time
            duration = self.cleaned_data.get('duration_minutes', 60)
            session_end_time = scheduled_time + timezone.timedelta(minutes=int(duration))
            
            counselor_assignments = CounselorAssignment.objects.filter(counselor=self.counselor, status='active')
            conflicting_sessions = CounselingSession.objects.filter(
                assignment__in=counselor_assignments,
                status='scheduled',
                scheduled_time__lt=session_end_time,
                scheduled_time__gte=scheduled_time
            )
            
            if conflicting_sessions.exists():
                raise forms.ValidationError("The counselor already has a session scheduled at this time")
        
        return scheduled_time


class UserCounselorAssignmentForm(forms.ModelForm):
    """
    Form for assigning users to counselors
    """
    status = forms.ChoiceField(
        choices=CounselorAssignment.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Notes about this assignment',
            'rows': 3
        }),
        required=False
    )
    
    class Meta:
        model = CounselorAssignment
        fields = ['counselor', 'user', 'status', 'notes']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show verified counselors in the dropdown
        self.fields['counselor'].queryset = User.objects.filter(
            user_type='counselor',
            counselor_profile__verification_status='verified'
        )
        # Only show regular users in the dropdown
        self.fields['user'].queryset = User.objects.filter(user_type='user')
        
        # Add Bootstrap classes
        self.fields['counselor'].widget.attrs.update({'class': 'form-control'})
        self.fields['user'].widget.attrs.update({'class': 'form-control'})
        
        


class VictimCounselorAssignmentForm(forms.ModelForm):
    class Meta:
        model = VictimCounselorAssignment
        fields = ['victim', 'counselor']