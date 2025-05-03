from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from .models import User, UserProfile, CounselorProfile


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