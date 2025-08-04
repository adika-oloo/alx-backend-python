# Add to INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework_simplejwt',
]

# Add REST framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}
