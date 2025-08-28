# apps/accounts/views.py
from apps.social.models import Follow
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Prefetch
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from apps.plans.models import Plan, Photo
from django.contrib.auth import login

from django.db.models import Q, Count
from django.contrib.auth.models import User
User = get_user_model()  # ← 先頭で一度だけ

class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar", "bio"]

@login_required
def profile(request, username):
    target = get_object_or_404(User, username=username)

    follower_count  = Follow.objects.filter(followed=target).count()
    following_count = Follow.objects.filter(follower=target).count()
    is_following = (
        request.user.is_authenticated
        and Follow.objects.filter(follower=request.user, followed=target).exists()
    )

    context = {
        "target": target,
        "follower_count": follower_count,
        "following_count": following_count,
        "is_following": is_following,
        # 必要ならフォーム等も
    }
    return render(request, "accounts/profile.html", context)
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, "ようこそ！アカウントを作成しました。")
            return redirect("plans:feed")
    else:
        form = UserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})

def user_search(request):
    q = request.GET.get("q", "").strip()
    users = []
    if q:
        users = (
            User.objects.filter(
                Q(username__icontains=q) | Q(profile__bio__icontains=q)
            )
            .annotate(
                followers_count=Count("follower_rel"),
                following_count=Count("following_rel"),
            )[:50]
        )
    return render(request, "accounts/search.html", {"q": q, "users": users})
