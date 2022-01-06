from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add/", views.add_listing, name="add_listing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("inactive/<int:listing_id>", views.inactive, name="inactive"),
]
