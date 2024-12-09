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
from django.views.decorators.cache import cache_page
import requests
import json
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings


@cache_page(60*15)
def cached(request):
    all_users = User.objects.all()
    return HttpResponse('<html><body><h1>{0} users... cached</h1></body></html>', format(len(all_users)))

def cacheless(request):
    all_users = User.objects.all()
    return HttpResponse('<html><body><h1>{0} users... cacheless</h1></body></html>', format(len(all_users)))


class LoginPage(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = CustomLoginForm()
        return render(request, 'newtemplate/login.html', {'form': form})

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
        return render(request, 'newtemplate/login.html', {'form': form})
    
def logoutUser(request):
    logout(request)
    return redirect('landing')


class RegisterPage(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = RegisterForm()
        return render(request, 'newtemplate/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect after successful registration
        return render(request, 'newtemplate/register.html', {'form': form})
    

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



class LangingPage(View):
    template_name = "newtemplate/landing.html"
    page_name = 'Air Quality Dashboard'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            print('redirecting user to dashboard')
            return redirect('dashboard')  
        context = {'page_name': self.page_name}
        return render(request, self.template_name, context)



class Dashboard(LoginRequiredMixin, View):
    login_url = 'login'
    template_name = 'newtemplate/dashboard.html'
    page_name = "Dashboard"

    def get(self, request, *args, **kwargs):
        API_TOKEN = settings.WAQI_API_KEY
        user = request.user

        q = request.GET.get('q') if request.GET.get('q') != None else ''
        search_query = request.GET.get('q', '')
        if search_query:
            city = search_query
        else:
            city = user.profile.city

        url = f"https://api.waqi.info/feed/{city}/?token={API_TOKEN}"
        response = requests.get(url)
        data = response.json()

        if data["status"] == "ok":

            aqi_trends = data["data"]["forecast"].get("daily", {}).get("pm25", [])
            trend_labels = [entry["day"] for entry in aqi_trends]
            trend_values = [entry["avg"] for entry in aqi_trends]
            
            context = {
                'page_name': self.page_name,
                "user": user,
                "city_name": data["data"]["city"]["name"],
                "aqi": data["data"]["aqi"],
                "dominant_pollutant": data["data"].get("dominentpol", "Not Provided"),
                "iaqi": data["data"].get("iaqi", {}),
                "update_time": data["data"]["time"].get("s", "Not Available"),
                "pollutant_source": data["data"]["attributions"][0]["name"] if data["data"]["attributions"] else "Unknown Source",
                "standard": data["data"]["iaqi"].get("pm25", {}).get("standard", "Not Provided"),
                "impact": data["data"]["iaqi"].get("pm25", {}).get("impact", "Not Available"),
                "pm25": data["data"]["iaqi"].get("pm25", {}).get("v", "N/A"),
                "pm10": data["data"]["forecast"].get("daily", {}).get("pm10", [{}])[0].get("avg", "N/A"),
                "o3": data["data"]["forecast"].get("daily", {}).get("o3", [{}])[0].get("avg", "N/A"),
                "aqi_trend_labels": json.dumps(trend_labels), 
                "aqi_trend_values": json.dumps(trend_values),
            }

        else:
            context = {"error": "Unable to fetch data"}
        

        return render(request, 'newtemplate/dashboard.html', context)
    

class Weather(View):
    login_url = 'weather'
    template_name = 'newtemplate/weather.html'
    page_name = "Weather"

    def opencage(self, city):
        API = settings.OPENCAGE_API_KEY
        url = f'https://api.opencagedata.com/geocode/v1/json?q={city}&key={API}'
        response = requests.get(url)
        data = response.json()

        if data['results']:
            lat = data['results'][0]['geometry']['lat']
            lng = data['results'][0]['geometry']['lng']
            return lat, lng
        else:
            return None, None

    def fetch_weather_data(self, lat, lng, city):
        API_TOKEN = settings.WEATHER_API_KEY
        url = 'http://api.weatherapi.com/v1/forecast.json'
        params = {
            'key': API_TOKEN,
            'q': f'{lat},{lng}', 
            'days': 7, 
            'aqi': 'no', 
            'alerts': 'no',
        }

        context = {'page_name': self.page_name, 'city_name': city}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status() 
            data = response.json()

            forecast_with_weekdays = []
            for day in data['forecast']['forecastday']:
                date_obj = datetime.strptime(day['date'], "%Y-%m-%d")
                weekday_name = date_obj.strftime('%A')  # Get full weekday name (e.g., Monday)

                forecast_with_weekdays.append({
                    'date': day['date'], 
                    'weekday': weekday_name,  
                    'day': day['day'],  
                    'icon': day['day']['condition']['icon'], 
                })

            context['forecast'] = forecast_with_weekdays
            context['current_weather'] = {
                'temperature': data['current']['temp_c'], 
                'condition': data['current']['condition']['text'],
                'icon': data['current']['condition']['icon'],
                'updated': data['current']['last_updated'],
            }
        except requests.exceptions.RequestException as e:
            context['error'] = f"Unable to fetch weather data: {str(e)}"

        return context

class WeatherCelsius(Weather):
    def get(self, request, *args, **kwargs):
        user = request.user
        search_query = request.GET.get('q', '')
        city = search_query if search_query else user.profile.city

        lat, lng = self.opencage(city)

        if lat is None or lng is None:
            context = {'page_name': self.page_name, 'error': f"Could not find coordinates for {city}"}
            return render(request, self.template_name, context)

        context = self.fetch_weather_data(lat, lng, city)

        return render(request, self.template_name, context)  
    

class WeatherFahrenheit(Weather):
    def convert_to_fahrenheit(self, celsius):
        fahrenheit = (celsius * 9/5) + 32
        return round(fahrenheit, 2) 

    def get(self, request, *args, **kwargs):
        user = request.user
        search_query = request.GET.get('q', '')
        city = search_query if search_query else user.profile.city

        lat, lng = self.opencage(city)

        if lat is None or lng is None:
            context = {'page_name': self.page_name, 'error': f"Could not find coordinates for {city}"}
            return render(request, self.template_name, context)

        context = self.fetch_weather_data(lat, lng, city)

        if 'current_weather' in context:
            context['current_weather']['temperature'] = self.convert_to_fahrenheit(context['current_weather']['temperature'])

        if 'forecast' in context:
            for day in context['forecast']:
                day['day']['maxtemp_f'] = self.convert_to_fahrenheit(day['day']['maxtemp_c'])
                day['day']['mintemp_f'] = self.convert_to_fahrenheit(day['day']['mintemp_c'])

        return render(request, self.template_name, context)


class Profile(LoginRequiredMixin, View):
    login_url = 'login'
    template_name = 'newtemplate/profile.html'
    page_name = "Profile"

    def get(self, request, *args, **kwargs):
        user = request.user
        country_form = CountryForm(instance=user.profile)
        context = {'user': user, 'page_name': self.page_name, 'country_form': country_form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = request.user

        # Extract general user data
        bio = request.POST.get('bio', '').strip()
        if bio:
            user.profile.bio = bio

        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email

        user.save()

        # Extract profile data
        country = request.POST.get('country', '').strip()
        city = request.POST.get('city', '').strip()

        if country:
            country_form = CountryForm(request.POST or None, instance=user.profile)
            if country_form.is_valid():
                user.profile.country = country

        if city:
            user.profile.city = city
        user.profile.save()

        if request.method == 'POST':
            air_quality_alert = request.POST.get('air_quality_alert') == 'on'
            weather_alert = request.POST.get('weather_alert') == 'on'
            health_advice_alert = request.POST.get('health_advice_alert') == 'on'

            # Update the user profile with new preferences
            user.profile.air_quality_alert = air_quality_alert
            user.profile.weather_alert = weather_alert
            user.profile.health_advice_alert = health_advice_alert

            user.profile.save()  
        

        return redirect('profile')

    




class LocationsPage(View):
    template_name = 'newtemplate/locations.html'
    page_name = "Locations"

    def get(self, request, *args, **kwargs):
        context = {
            'page_name': self.page_name,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
            lat = request.POST.get('lat')
            lng = request.POST.get('lng')

            if not lat or not lng:
                return JsonResponse({'error': 'Coordinates not provided'}, status=400)

            # WAQI API request URL
            API_KEY = '7d192ca63cae02017579faf8c94e08c355de2830'
            url = f'https://api.waqi.info/feed/geo:{lat};{lng}/?token={API_KEY}'

            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()

                # Extract AQI data
                if data.get('status') == 'ok':
                    aqi = data['data'].get('aqi', 'N/A')
                    iaqi = data['data'].get('iaqi', {})
                    # Send AQI and IAQI details back to the frontend
                    return JsonResponse({'aqi': aqi, 'iaqi': iaqi})
                else:
                    return JsonResponse({'error': 'Failed to retrieve data from WAQI'}, status=500)
            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': str(e)}, status=500)


class HistoricalPage(View):
    template_name = 'newtemplate/historical.html'
    page_name = "Historical Data"

    def get(self, request, *args, **kwargs):
        context = {'page_name': self.page_name}
        return render(request, self.template_name, context)
    
class HealthAdvicePage(View):
    template_name = 'newtemplate/health_advice.html'
    page_name = "Health Advice"

    def get(self, request, *args, **kwargs):
        context = {'page_name': self.page_name}
        return render(request, self.template_name, context)


class Contact(View):
    pass

class About(View):
    pass

class Faq(View):
    pass

class Settings(View):
    pass

class Documentation(View):
    pass

class UpgradeToPro(View):
    pass

class NotificationsPage(View):
    pass


def send_email_view(request):
    users = UserProfile.objects.filter(weather_alert=True)

    for user in users:
        weather_url = f'http://api.weatherapi.com/v1/current.json?key={settings.WEATHER_API_KEY}&q={user.city}'
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()
        temperature = weather_data['current']['temp_c']
        condition = weather_data['current']['condition']['text']
        humidity = weather_data['current']['humidity']
        wind_speed = weather_data['current']['wind_kph']
        weather_message = f"""
        Weather in {user.city}:
        Temperature: {temperature}°C
        Condition: {condition}
        Humidity: {humidity}%
        Wind Speed: {wind_speed} km/h
        """
        subject = 'Air Quality Alert'
        recipient = user.user.email
        message = weather_message

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # Sender's email
            [recipient],  # List of recipients
            fail_silently=False,
        )

    return redirect('profile')
