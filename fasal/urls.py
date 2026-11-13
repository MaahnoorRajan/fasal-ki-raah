from django.urls import path
from django.contrib.auth import views as auth_views

from .views import driver_signup, driver_trips, planner, withdraw_trip

urlpatterns = [
    path("", planner, name="planner"),
    path("drivers/signup/", driver_signup, name="driver-signup"),
    path("drivers/login/", auth_views.LoginView.as_view(
        template_name="fasal/driver_auth.html", next_page="driver-trips",
    ), name="driver-login"),
    path("drivers/logout/", auth_views.LogoutView.as_view(next_page="planner"), name="driver-logout"),
    path("drivers/trips/", driver_trips, name="driver-trips"),
    path("drivers/trips/<int:pk>/withdraw/", withdraw_trip, name="withdraw-trip"),
]
