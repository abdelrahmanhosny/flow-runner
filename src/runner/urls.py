from django.urls import path
from . import views

urlpatterns = [
    path('start', views.RunnerStartFlow.as_view(), name='start'),
]
