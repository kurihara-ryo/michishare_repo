# apps/plans/urls.py
from django.urls import path
from . import views

app_name = "plans"
urlpatterns = [
    path("", views.feed, name="feed"),
    path("plans/new/", views.plan_create, name="plan_create"),
    path("plans/<int:pk>/", views.plan_detail, name="plan_detail"),
    path("plans/<int:pk>/edit/", views.plan_update, name="plan_update"),
    path("plans/<int:pk>/track/save/", views.plan_track_save, name="track_save"),
    #削除
    path("plans/<int:pk>/delete/", views.plan_delete, name="plan_delete"),
]




