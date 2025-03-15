from django.urls import path

from .views import (
    RegisterView,
    UserLoginView,
    UserLogoutView,
    UserEmailRecoveryPasswordView,
    UserPasswordResetView,
    UserPasswordResetDoneView,
    UserAccountView,
    UserProfileView,
    UserProfileUpdateView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('password-reset/', UserEmailRecoveryPasswordView.as_view(), name='password_reset'),
    path('password-reset-done/', UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', UserPasswordResetView.as_view(), name='password_reset_confirm'),
    path('account/', UserAccountView.as_view(), name='user_account_view'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='user_profile_update_view'),
    path('profile/', UserProfileView.as_view(), name='user_profile_view'),
]