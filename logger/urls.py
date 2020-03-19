from django.urls import path

from . import views

app_name = 'logger'
urlpatterns = [
    path('', views.login, name='login'),
    path('setup/', views.setup, name='setup'),
    path('verify/<str:username>/<str:password>', views.verify, name='verify')
]