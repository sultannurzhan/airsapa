import json
import re
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, resolve, reverse_lazy
from django.views import View
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import os
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse, HttpResponseBadRequest
from django.db import transaction
from .models import *
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.db.models.functions import TruncDate
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import permission_required
from django.views.generic.edit import CreateView


class LoginPage(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = CustomLoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  
            else:
                form.add_error('password', 'Invalid username or password')
        return render(request, 'base/login.html', {'form': form})
    
def logoutUser(request):
    logout(request)
    return redirect('default')

class RegisterPage(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

    @csrf_exempt
    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.set_password(form.cleaned_data['password'])
            user.save()

            country = form.cleaned_data['country']
            city = form.cleaned_data['city']
            userprofile = UserProfile.objects.create(user=user, country=country, city=city)
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Error occurred during registration')
            return render(request, 'register.html', {'form': form})



class DefaultPage(View):
    template_name = "default.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            print('redirecting user to dashboard')
            return redirect('dashboard')  
        return render(request, self.template_name)


class Dashboard(LoginRequiredMixin, View):
    login_url = 'login'
    template_name = 'dashboard.html' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        air_quality_data = {
            'temperature': 22.5,  # Example temperature in °C
            'humidity': 60,       # Example humidity in %
            'pm2_5': 15,          # Example PM2.5 in µg/m³
            'pm10': 20,           # Example PM10 in µg/m³
            'nox': 30,            # Example NOx in ppb
            'nh3': 10,            # Example NH3 in ppb
            'co2': 350,           # Example CO2 in ppm
            'so2': 5,             # Example SO2 in ppb
            'voc': 50,            # Example VOC in ppb
        }
        context['air_quality_data'] = air_quality_data
        return context
    
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard.html')


class Profile(LoginRequiredMixin, View):
    login_url = 'login'
    template_name = 'profile.html' 
    def  get(self, request, *args, **kwargs):
        user = request.user
        context = {'user': user}
        return render(request, 'profile.html', context)

