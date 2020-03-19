from django.urls import path
from . import views

app_name = 'samples'
urlpatterns = [
    path('', views.index, name='index'),
    path('messages', views.messages, name='messages')
]