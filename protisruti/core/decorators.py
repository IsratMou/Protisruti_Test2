from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def user_type_required(user_type, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user is of the specified type,
    redirecting to the login page if necessary.
    """
    def check_user_type(user):
        if user.is_authenticated and user.user_type == user_type:
            return True
        raise PermissionDenied
    
    return user_passes_test(check_user_type, login_url=login_url, redirect_field_name=redirect_field_name)


def user_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the logged in user is a regular user,
    redirects to the login page if necessary.
    """
    actual_decorator = user_type_required(
        user_type='user',
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def counselor_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the logged in user is a counselor,
    redirects to the login page if necessary.
    """
    actual_decorator = user_type_required(
        user_type='counselor',
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def verified_counselor_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the logged in user is a verified counselor,
    redirects to the login page if necessary.
    """
    def check_verified_counselor(user):
        if user.is_authenticated and user.user_type == 'counselor':
            try:
                if user.counselor_profile.verification_status == 'verified':
                    return True
            except:
                pass
        raise PermissionDenied
    
    actual_decorator = user_passes_test(
        check_verified_counselor,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    
    if function:
        return actual_decorator(function)
    return actual_decorator


def admin_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the logged in user is an admin,
    redirects to the login page if necessary.
    """
    actual_decorator = user_type_required(
        user_type='admin',
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator