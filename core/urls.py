from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.upload_view, name='upload'),
    path('mapping/', views.mapping_view, name='mapping'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('export/', views.export_csv_view, name='export_csv'),
    path('clear/', views.clear_session_view, name='clear_session'),
]
