from django.urls import path
from . import views

app_name = 'dashboard'
urlpatterns = [
    path('<str:session_key>/', views.dashboard, name="dashboard"),
    path('<str:session_key>/filters/<str:params>', views.filters, name="filters"),
    path('<str:session_key>/groups', views.groups, name="groups"),
    path('<str:session_key>/new_meeting/<str:params>', views.new_meeting, name="new_meeting"),
    path('<str:session_key>/new_task/<str:params>', views.new_task, name="new_meeting")
]