from django.core import management
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import RegisterForm
# from django.conf import settings

from .models import User

# request User is: settings.AUTH_USER_MODEL
app_name = 'profiles'

class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'register.html'
    success_url = reverse_lazy('shop:check-frontend')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.is_active = True
        user.save()
        management.call_command('customer_permissions', user.id)
        # user = authenticate(
        #     self.request,
        #     email=email,
        #     password=password
        # )
        return response
