from django.contrib import admin
from django.urls import path
from bsvapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name='home'),
    path("home", views.home, name='home'),
    path("music_mode", views.music_mode, name='music_mode'),
    path("color_mode", views.color_mode, name='color_mode'),            
]
