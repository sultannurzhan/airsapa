from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile
import requests

@shared_task
def send_weather_alert():
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

    return 'Daily alerts sent successfully.'




@shared_task
def send_aqi_alert():
    users = UserProfile.objects.filter(air_quality_alert=True)

    for user in users:
        city = user.city
        API_TOKEN = settings.WAQI_API_KEY
        aqi_url = f'https://api.waqi.info/feed/{city}/?token={API_TOKEN}'
        response = requests.get(aqi_url)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'aqi' in data['data']:
                aqi = data['data']['aqi']
                air_quality_message = f"""
                Air Quality Alert for {city}:
                AQI Level: {aqi}
                {"Unhealthy" if aqi > 100 else "Moderate" if aqi > 50 else "Good"}
                """
                subject = 'Air Quality Alert'
                recipient = user.user.email

                send_mail(
                    subject,
                    air_quality_message,
                    settings.EMAIL_HOST_USER, 
                    [recipient], 
                    fail_silently=False,
                )
    return 'AQI alerts sent successfully.'


@shared_task
def health_advice_mail():
    #It should be done manually by company employers
    users = UserProfile.objects.filter(health_advice_alert=True)

    for user in users:
        subject = "Health Advice for Better Living"
        message = f"""
        Dear {user.user.first_name},

        Here is your personalized health advice for this month:
        - Stay hydrated and drink at least 2 liters of water daily.
        - Get at least 7-8 hours of sleep to maintain good mental and physical health.
        - Exercise regularly, even light activity like walking 30 minutes a day.

        Best regards,
        Your Company Health Team
        """
        recipient = user.user.email

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [recipient],
            fail_silently=False,
        )

    return "Health advice emails sent successfully."