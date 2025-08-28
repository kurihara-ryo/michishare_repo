# apps/plans/forms.py
# apps/plans/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Plan, Spot, Photo

class PlanForm(forms.ModelForm):
    # 画面表示用の非モデル項目（保存しない）
    total_minutes = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={"readonly": "readonly"})
    )

    class Meta:
        model = Plan
        fields = ["title", "tags", "description"]   # ← total_minutes を外す

# 既存のフォームセット（例）
SpotFormSet = inlineformset_factory(
    Plan, Spot,
    fields=["order", "name", "lat", "lng", "stay_minutes", "note"],
    extra=1, can_delete=True
)

PhotoFormSet = inlineformset_factory(
    Plan, Photo,
    fields=["image", "caption"],
    extra=1, can_delete=True
)
