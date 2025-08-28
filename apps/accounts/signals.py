# apps/accounts/signals.py
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile

@receiver(
    post_save,
    sender=settings.AUTH_USER_MODEL,
    dispatch_uid="accounts.profile.create",   # ← 二重接続防止
)
def ensure_profile_exists(sender, instance, created, **kwargs):
    # 作成時のみ & 何度呼ばれても安全
    if created:
        Profile.objects.get_or_create(user=instance)
