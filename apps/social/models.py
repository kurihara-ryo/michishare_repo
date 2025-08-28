from django.conf import settings
from django.db import models
from django.db.models import Q, F

class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='following',
        on_delete=models.CASCADE,
    )
    # ※ データを消さずに進めるため、一時的に null/blank を許可
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='followers',
        on_delete=models.CASCADE,
        null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # 重複フォロー禁止（followed が NULL の行は除外）
            models.UniqueConstraint(
                fields=['follower', 'followed'],
                name='unique_follow',
                condition=Q(followed__isnull=False),
            ),
            # 自分自身はフォローできない
            models.CheckConstraint(
                check=~Q(follower=F('followed')),
                name='no_self_follow',
            ),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.follower} -> {self.followed or "None"}'
