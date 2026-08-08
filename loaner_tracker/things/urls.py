from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    
    path("admin/", admin.site.urls, name="admin"),

    path("login/", views.login, name="login"),
    path("things/add/", views.add_thing, name="add_thing"),
    path("things/lookup/", views.lookup, name="lookup"),
    path("things/<int:id>", views.get_thing, name="get_thing")
]