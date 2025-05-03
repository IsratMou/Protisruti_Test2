from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """
    Custom user manager with email as the unique identifier
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model with email as the primary identifier instead of username
    """
    USER_TYPE_CHOICES = (
        ('user', 'User'),
        ('counselor', 'Counselor'),
        ('admin', 'Admin'),
    )
    
    username = None
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """
    Profile for users seeking counseling
    """
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile of {self.full_name}"


class CounselorProfile(models.Model):
    """
    Profile for counselors providing support
    """
    SPECIALIZATION_CHOICES = (
        ('domestic_violence', 'Domestic Violence'),
        ('sexual_assault', 'Sexual Assault'),
        ('child_abuse', 'Child Abuse'),
        ('trauma', 'Trauma'),
        ('general', 'General Support'),
    )
    
    VERIFICATION_STATUS = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='counselor_profile')
    full_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES)
    qualification = models.CharField(max_length=255)
    experience_years = models.PositiveIntegerField(default=0)
    bio = models.TextField()
    verification_status = models.CharField(max_length=10, choices=VERIFICATION_STATUS, default='pending')
    verification_document = models.FileField(upload_to='verification_docs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Counselor: {self.full_name}"