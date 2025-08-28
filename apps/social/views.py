from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Follow

User = get_user_model()

@login_required
def follow_toggle(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({"ok": False, "error": "cannot_follow_self"}, status=400)

    rel, created = Follow.objects.get_or_create(follower=request.user, followed=target)
    following = True if created else (rel.delete() or False)

    followers_count = Follow.objects.filter(followed=target).count()
    return JsonResponse({"ok": True, "following": following, "followers_count": followers_count})
