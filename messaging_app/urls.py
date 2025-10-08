from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # You can add your chats app URLs here later
    # path('api/', include('chats.urls')),
]
