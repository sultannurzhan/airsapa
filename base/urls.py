from django.urls import path
from . import views

urlpatterns = [
    path('', views.LangingPage.as_view(), name='landing'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('profile/', views.Profile.as_view(), name='profile'),

    path('login/', views.LoginPage.as_view(), name='login'),
    path('logout', views.logoutUser, name='logout'),
    path('register/', views.RegisterPage.as_view(), name='register'),

    path('contact/', views.Contact.as_view(), name='contact'),
    path('about/', views.About.as_view(), name='about'),
    path('faq/', views.Faq.as_view(), name='faq'),
    path('settings/', views.Settings.as_view(), name='settings'),
    path('documentation/', views.Documentation.as_view(), name='documentation'),
    path('upgrade-to-pro/', views.UpgradeToPro.as_view(), name='upgrade_to_pro'),

    path('weather/', views.WeatherCelsius.as_view(), name='weather'),
    path('weather/fahrenheit', views.WeatherFahrenheit.as_view(), name='fahrenheit'),


    path('historical/', views.HistoricalPage.as_view(), name='historical_page'),
    path('locations/', views.LocationsPage.as_view(), name='locations_page'),
    path('health-advice/', views.HealthAdvicePage.as_view(), name='health_advice_page'),
    path('notifications/', views.NotificationsPage.as_view(), name='notifications_page'),


    path('send-email/', views.send_email_view, name='send_email'),
]