from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    accept_space_request, booking_detail, driver_signup, driver_trips, edit_trip, my_requests,
    planner, request_space, withdraw_trip,
)

urlpatterns = [
    path("", planner, name="planner"),
    path("requests/", my_requests, name="my-requests"),
    path("bookings/<int:pk>/", booking_detail, name="booking-detail"),
    path("trips/<int:pk>/request/", request_space, name="request-space"),
    path("drivers/signup/", driver_signup, name="driver-signup"),
    path("drivers/login/", auth_views.LoginView.as_view(
        template_name="fasal/driver_auth.html", next_page="driver-trips",
    ), name="driver-login"),
    path("drivers/logout/", auth_views.LogoutView.as_view(next_page="planner"), name="driver-logout"),
    path("drivers/trips/", driver_trips, name="driver-trips"),
    path("drivers/trips/<int:pk>/edit/", edit_trip, name="edit-trip"),
    path("drivers/trips/<int:pk>/withdraw/", withdraw_trip, name="withdraw-trip"),
    path("drivers/trips/<int:pk>/requests/<int:request_id>/accept/", accept_space_request, name="accept-space-request"),
]
