# apps/accounts/urls.py
from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("search/", views.user_search, name="search"),                  # ←追加
    path("<str:username>/", views.profile, name="profile"),
]
