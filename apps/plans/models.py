# apps/plans/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete
from django.dispatch import receiver
User = get_user_model()

class Plan(models.Model):
    title = models.CharField(max_length=200)
    tags = models.CharField(max_length=200, blank=True, default="")
    description = models.TextField(blank=True, default="")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="plans")
    created_at = models.DateTimeField(auto_now_add=True)

    # GPSで保存する実走ルート（GeoJSON LineString: [[lng,lat], ...]）
    route_geojson = models.JSONField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at   = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

TRANSPORT_CHOICES = [
    ("walk", "徒歩"),
    ("train","電車"),
    ("bus",  "バス"),
    ("car",  "車"),
    ("bike", "自転車"),
    ("boat", "船"),
    ("other","その他"),
]

class Spot(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="spots")
    order = models.PositiveIntegerField(default=1)
    name = models.CharField(max_length=200)
    lat = models.FloatField()
    lng = models.FloatField()
    stay_minutes = models.PositiveIntegerField(default=0)
    transport_to_next = models.CharField(max_length=10, choices=TRANSPORT_CHOICES, default="walk")
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.order}. {self.name}"

class Photo(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="photos")
    order = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="plan_photos/%Y/%m/%d/")
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Photo({self.plan_id})-{self.order}"

@receiver(post_delete, sender=Photo)
def delete_photo_file(sender, instance, **kwargs):
    # ストレージから物理削除（存在チェック付き）
    if instance.image:
        instance.image.storage.delete(instance.image.name)
