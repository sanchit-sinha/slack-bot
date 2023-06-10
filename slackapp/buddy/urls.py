from django.urls import include, path
from . import views

urlpatterns = [
    path('event/', views.event, name='event'),
    path('command/add', views.add, name='add'),
    path('command/delete', views.delete, name='delete'),
]