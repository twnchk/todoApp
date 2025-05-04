from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import register, user_login, user_logout, user_profile

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='user_login'),
    path('logout/', user_logout, name='user_logout'),
    path('changePassword/', auth_views.PasswordChangeView.as_view(template_name="change_password.html"),
         name='password_change'),
    path('changePassword/done', auth_views.PasswordChangeDoneView.as_view(template_name="change_password_done.html"),
         name='password_change_done'),
    path('resetPassword/', auth_views.PasswordResetView.as_view(template_name="reset_password.html"),
         name='password_reset'),
    path('resetPassword/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='confirm_reset_password.html'),
         name='password_reset_confirm'),
    path('resetPassword/done/', auth_views.PasswordResetDoneView.as_view(template_name="reset_password_done.html"),
         name='password_reset_done'),
    path('resetPassword/complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="reset_password_complete.html"),
         name='password_reset_complete'),
    path('profile/<int:id>', user_profile, name='user_profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
