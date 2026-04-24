from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.create_project),
    path('projects/all/', views.get_projects),
    path('bid/', views.place_bid),
    path('bids/<int:project_id>/', views.get_bids),
]