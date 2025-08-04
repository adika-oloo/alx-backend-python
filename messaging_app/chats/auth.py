from rest_framework_simplejwt.authentication import JWTAuthentication

def get_user_from_token(request):
    auth = JWTAuthentication()
    try:
        validated_token = auth.get_validated_token(request.headers.get('Authorization').split()[1])
        user = auth.get_user(validated_token)
        return user
    except Exception:
        return None
