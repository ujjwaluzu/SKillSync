from django.urls import path
from . import views

urlpatterns = [
    # 🔹 API routes (keep these)
    path('api/projects/', views.create_project),
    path('api/projects/all/', views.get_projects),
    path('api/bid/', views.place_bid),
    path('api/bids/<int:project_id>/', views.get_bids),

    # 🔹 Frontend routes
    path('', views.landing),
    path('signup/<str:role>/', views.signup),
    path('login/', views.login_view),

    path('client/', views.client_dashboard),        # ✅ FIXED
    path('freelancer/', views.freelancer_dashboard),# ✅ FIXED
    path('bid-form/<int:project_id>/', views.place_bid_form),
]