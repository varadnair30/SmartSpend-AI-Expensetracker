from django.contrib import admin
from django.urls import path, include
from .import views
urlpatterns = [
    path('',views.forecast,name="forecast"),
    path('set-budget/', views.set_budget, name='set-budget'),
    

]