from django.urls import path
from . import views

urlpatterns = [
    path('', views.DefaultPage.as_view(), name='default'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('profile/', views.Profile.as_view(), name='profile'),

    path('login/', views.LoginPage.as_view(), name='login'),
    path('logout', views.logoutUser, name='logout'),
    path('register/', views.RegisterPage.as_view(), name='register'),
]