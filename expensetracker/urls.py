"""
URL configuration for expensetracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from userprofile.views import react_test_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('expenses.urls')),
    path('authentication/', include('authentication.urls')),
    path('preferences/', include('userpreferences.urls')),
    path('income/', include('userincome.urls')),
    path('forecast/', include('expense_forecast.urls')),
    path('api/', include('api.urls')),
    path('goals/',include('goals.urls')),
    path('app/', TemplateView.as_view(template_name="index.html")),
    path('account/',include('userprofile.urls')),
    path('react-test/', react_test_view, name='react_test'),
]
    
    

