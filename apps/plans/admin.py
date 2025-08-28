# apps/plans/admin.py
from django.contrib import admin
from .models import Plan, Spot

class SpotInline(admin.TabularInline):
    model = Spot
    extra = 1

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    inlines = [SpotInline]
    list_display = ("title", "author", "created_at")  # ← is_published を外す
