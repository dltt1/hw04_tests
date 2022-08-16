from . import views
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import PasswordChangeDoneView, PasswordResetView
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import path

app_name = 'users'

urlpatterns = [
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'justpage/',
        views.JustStaticPage.as_view()
    ),
    path(
        'password_change/',
        PasswordChangeView.as_view(),
        name='password_change_form'
    ),
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        PasswordResetView.as_view(),
        name='password_reset_form'
    ),
    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),
    path(
        'reset/<uid64>/<token>',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(),
        name='password_reset_done'
    ),
]
