from django.contrib import admin
from django.urls import path
from bsvapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name='home'),
    path("home", views.home, name='home'),
    path("music_modes", views.music_modes, name='music_modes'),
    path("color_modes", views.color_modes, name='color_modes'),
    path("color_programs", views.color_programs, name='color_programs'),    
    path("off", views.off, name='off'),
]
