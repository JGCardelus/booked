from django.urls import path
from . import views

app_name = 'dashboard'
urlpatterns = [
    path('<str:session_key>/', views.dashboard, name="dashboard")
]