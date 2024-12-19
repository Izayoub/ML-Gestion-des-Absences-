from Ml_gestionABS_app import views


from django.contrib.auth import admin
from django.urls import path
from django.views.generic import RedirectView

app_name = 'Ml_gestionABS_app'
urlpatterns = [


    path('', views.home, name='home'),
    path('take/<int:class_group_id>/', views.take_attendance, name='take_attendance'),
    path('attendance/process/<int:class_group_id>/', views.process_attendance, name='process_attendance'),

]
