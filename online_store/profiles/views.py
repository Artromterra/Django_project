from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetDoneView
)
from django.core import management
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, TemplateView, UpdateView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin

from shop.models.order import Order
from .forms import (
    RegisterForm,
    LoginForm,
    UserEmailRecoveryPasswordForm,
    UserSetNewPasswordForm,
    ProfileUserUpdateForm,
    ProfileAccountUpdateForm,
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
    success_url = reverse_lazy('profiles:user_profile_update_view')

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = Order.objects.filter(user=self.request.user).order_by('-created_at').first()
        context['order'] = order
        return context


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "profile.html"

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    View для редактирования профиля
    """
    model = User
    template_name = 'profile.html'
    form_class = ProfileUserUpdateForm
    http_method_names = ['get', 'post', 'put', 'patch']

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование профиля пользователя: {self.request.user.username}'

        if self.request.POST:
            context['account_form'] = ProfileAccountUpdateForm(self.request.POST, instance=self.request.user.account)
        else:
            context['account_form'] = ProfileAccountUpdateForm(instance=self.request.user.account)

        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        account_form = ProfileAccountUpdateForm(self.request.POST, instance=self.request.user.account)

        print(self.request.POST)
        if account_form.is_valid():
            print("Форма аккаунта валидна")
            account_form.save()
        else:
            print(f"Ошибка в форме аккаунта: {account_form.errors.as_json()}")


        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profiles:user_profile_view')
