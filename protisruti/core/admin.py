from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile, CounselorProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'


class CounselorProfileInline(admin.StackedInline):
    model = CounselorProfile
    can_delete = False
    verbose_name_plural = 'Counselor Profile'


class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'user_type', 'is_active', 'date_joined')
    search_fields = ('email', 'user_type')
    readonly_fields = ('date_joined',)
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
         'fields': ('first_name', 'last_name', 'phone_number')}),
        (_('User type'), {'fields': ('user_type',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type'),
        }),
    )

    def get_inlines(self, request, obj=None):
        if obj:
            if obj.user_type == 'user':
                return [UserProfileInline]
            elif obj.user_type == 'counselor':
                return [CounselorProfileInline]
        return []


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'gender', 'age', 'created_at')
    search_fields = ('full_name', 'user__email')
    list_filter = ('gender', 'created_at')


@admin.register(CounselorProfile)
class CounselorProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'specialization',
                    'experience_years', 'verification_status')
    list_filter = ('specialization', 'verification_status', 'created_at')
    search_fields = ('full_name', 'user__email', 'qualification')
    actions = ['mark_as_verified', 'mark_as_rejected']

    def mark_as_verified(self, request, queryset):
        queryset.update(verification_status='verified')
    mark_as_verified.short_description = "Mark selected counselors as verified"

    def mark_as_rejected(self, request, queryset):
        queryset.update(verification_status='rejected')
    mark_as_rejected.short_description = "Mark selected counselors as rejected"


# Register the User model with the custom admin
admin.site.register(User, CustomUserAdmin)
