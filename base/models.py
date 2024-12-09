from django.contrib.auth.models import User
from django.db import models
from django_countries.fields import CountryField

class UserProfile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, related_name='profile')
    country = CountryField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    air_quality_alert = models.BooleanField(default=False)
    weather_alert = models.BooleanField(default=False)
    health_advice_alert = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    theme = models.CharField(max_length=20, choices=[('light', 'Light'), ('dark', 'Dark')], default='light')
    notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"

class HistoricalData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='historical_data')
    timestamp = models.DateTimeField(auto_now_add=True)
    temperature = models.FloatField()
    humidity = models.FloatField()
    pm25 = models.FloatField()  # PM2.5
    pm10 = models.FloatField()  # PM10
    nox = models.FloatField()   # NOx
    nh3 = models.FloatField()   # NH3
    co2 = models.FloatField()   # CO2
    so2 = models.FloatField()   # SO2
    voc = models.FloatField()   # VOC
    
    def __str__(self):
        return f"Data for {self.user.username} at {self.timestamp}"