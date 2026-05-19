from django.urls import path

from . import views


urlpatterns = [
    path("api/projects/", views.create_project, name="api_create_project"),
    path("api/projects/all/", views.get_projects, name="api_get_projects"),
    path("api/bid/", views.place_bid, name="api_place_bid"),
    path("api/bids/<int:project_id>/", views.get_bids, name="api_get_bids"),
    path("", views.landing, name="landing"),
    path("signup/<str:role>/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("client/", views.client_dashboard, name="client_dashboard"),
    path("freelancer/", views.freelancer_dashboard, name="freelancer_dashboard"),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),
    path("bid-form/<int:project_id>/", views.place_bid_form, name="place_bid_form"),
    path("bids/<int:bid_id>/accept/", views.accept_bid, name="accept_bid"),
    path("projects/<int:project_id>/complete/", views.complete_project, name="complete_project"),
    path("projects/<int:project_id>/save/", views.toggle_saved_project, name="toggle_saved_project"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/<str:username>/", views.profile_view, name="public_profile"),
    path("notifications/", views.notifications_view, name="notifications"),
    path(
        "notifications/<int:notification_id>/read/",
        views.mark_notification_read,
        name="mark_notification_read",
    ),
    path("messages/", views.inbox, name="inbox"),
    path("messages/<int:thread_id>/", views.chat_thread, name="chat_thread"),
    path("projects/<int:project_id>/chat/<int:user_id>/", views.start_chat, name="start_chat"),
    path("projects/<int:project_id>/review/<int:user_id>/", views.submit_review, name="submit_review"),
]
