from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.homeView.as_view(), name="home"),
    path("user/<int:pk>", views.UserDetailView.as_view(), name="user_detail"),
    
    path("admin/", admin.site.urls, name="admin"),

    path("login", views.loginView.as_view(), name="login"),
    path("logout", views.logoutView.as_view(), name="logout"),
    path("app/add", views.thingAddView.as_view(), name="add_thing"),
    path("app/list", views.thingListView.as_view(), name="list"),
    path("app/lookup", views.thingLookupView.as_view(), name="lookup_thing"),
    path("app/<int:id>", views.thingDetailView.as_view(), name="get_thing"),

    path("api", include("rest_framework.urls"))
]