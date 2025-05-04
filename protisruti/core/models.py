from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models
from django.contrib import admin
from django.conf import settings


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
    email = models.CharField(_('email address'), max_length=255, unique=True)
    user_type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default='user')
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

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='user_profile')
    full_name = models.CharField(max_length=100)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
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

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='counselor_profile')
    full_name = models.CharField(max_length=100)
    specialization = models.CharField(
        max_length=20, choices=SPECIALIZATION_CHOICES)
    qualification = models.CharField(max_length=255)
    experience_years = models.PositiveIntegerField(default=0)
    bio = models.TextField()
    verification_status = models.CharField(
        max_length=10, choices=VERIFICATION_STATUS, default='pending')
    verification_document = models.FileField(
        upload_to='verification_docs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Counselor: {self.full_name}"


# Add these models to core/models.py

class CounselorAvailability(models.Model):
    """
    Model to track counselor availability for sessions
    """
    DAY_CHOICES = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )

    counselor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='availabilities')
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('counselor', 'day', 'start_time', 'end_time')
        verbose_name_plural = 'Counselor Availabilities'

    def __str__(self):
        return f"{self.counselor.counselor_profile.full_name} - {self.get_day_display()} ({self.start_time} - {self.end_time})"


class CounselorAssignment(models.Model):
    """
    Model to track assignment of users to counselors
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('terminated', 'Terminated'),
    )

    counselor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='assigned_users')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='assigned_counselors')
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='active')
    assigned_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    last_session = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('counselor', 'user', 'status')

    def __str__(self):
        return f"{self.user.user_profile.full_name} assigned to {self.counselor.counselor_profile.full_name}"

    def is_active(self):
        return self.status == 'active'


class CounselingSession(models.Model):
    """
    Model to track scheduled and completed counseling sessions
    """
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('missed', 'Missed'),
    )

    assignment = models.ForeignKey(
        CounselorAssignment, on_delete=models.CASCADE, related_name='sessions')
    scheduled_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    status = models.CharField(
        max_length=11, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session: {self.assignment.user.user_profile.full_name} with {self.assignment.counselor.counselor_profile.full_name} on {self.scheduled_time}"

    def is_upcoming(self):
        return self.status == 'scheduled' and self.scheduled_time > timezone.now()


class VictimCounselorAssignment(models.Model):
    victim = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='assignments')
    counselor = models.ForeignKey(
        CounselorProfile, on_delete=models.CASCADE, related_name='assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.victim} assigned to {self.counselor}"


@admin.register(VictimCounselorAssignment)
class VictimCounselorAssignmentAdmin(admin.ModelAdmin):
    list_display = ('victim', 'counselor', 'assigned_at')
    search_fields = ('victim__email', 'counselor__user__email')
    list_filter = ('assigned_at',)


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.email} to {self.receiver.email} at {self.timestamp}"
