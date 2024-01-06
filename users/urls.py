from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import register, user_login, user_logout

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='user_login'),
    path('logout/', user_logout, name='user_logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
