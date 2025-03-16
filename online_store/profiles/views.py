from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetDoneView
)
from django.core import management
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404


from .forms import (
    RegisterForm,
    LoginForm,
    UserEmailRecoveryPasswordForm,
    UserSetNewPasswordForm, ProfileForm,
)
from .models import Account, User
from shop.models.cart import Cart

app_name = 'profiles'

class RegisterView(FormView):
    """
     представление для регистрации нового пользователя
    """
    form_class = RegisterForm
    template_name = 'register.html'
    success_url = reverse_lazy('profiles:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.is_active = True
        user.username = username
        user.email = email
        user.save()

        Account.objects.create(user=user)

        management.call_command('customer_permissions', user.id)

        return response


class UserLoginView(FormView):
    """
    представление для логина зарегистрированного пользователя
    """
    template_name = 'login.html'
    form_class = LoginForm

    def get_success_url(self):
        if Cart.objects.filter(user=self.request.user).exists():
            return reverse_lazy('shop:order')
        return reverse_lazy('homepage')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(
            email=email,
            password=password,
        )
        if user is not None and user.is_active:
            login(self.request, user)

        return super().form_valid(form)


class UserLogoutView(LogoutView):
    http_method_names = ['get', 'post', 'options']
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class UserEmailRecoveryPasswordView(PasswordResetView):
    """
    представление по сбросу пароля по почте
    """
    template_name = 'email.html'
    form_class = UserEmailRecoveryPasswordForm
    success_url = reverse_lazy('profiles:password_reset_done')
    subject_template_name = 'email/password_reset_subject.txt'
    email_template_name = 'email/password_reset_email.html'


class UserPasswordResetView(PasswordResetConfirmView):
    """
    представление для ввода нового пароля
    """
    template_name = 'password.html'
    form_class = UserSetNewPasswordForm
    success_url = reverse_lazy('profiles:login')


class UserPasswordResetDoneView(PasswordResetDoneView):
    """
    промежуточное представление для отображения процесса смены пароля
    """
    template_name = 'password_reset_done.html'


class UserAccountView(LoginRequiredMixin, TemplateView):
    template_name = "account.html"


class ProfileUpdateView(LoginRequiredMixin, FormView):
    template_name = 'profile.html'
    form_class = ProfileForm
    success_url = reverse_lazy('profiles:profile')

    def get_initial(self):
        user = self.request.user
        account = get_object_or_404(Account, user=user)  # Получаем аккаунт пользователя
        return {
            'email': user.email,
            'phone': user.phone,
            'avatar': user.avatar,
            'first_name': account.first_name,
            'last_name': account.last_name,
            'patronymic': account.patronymic,
        }

    def form_valid(self, form):
        user = self.request.user
        user.email = form.cleaned_data['email']
        user.phone = form.cleaned_data['phone']
        if form.cleaned_data['avatar']:
            user.avatar = form.cleaned_data['avatar']
        user.save()

        account = get_object_or_404(Account, user=user)
        account.first_name = form.cleaned_data['first_name']
        account.last_name = form.cleaned_data['last_name']
        account.patronymic = form.cleaned_data['patronymic']
        account.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
