# apps/plans/views.py
# apps/plans/views.py
import json
from django import forms
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Prefetch
from django.forms import inlineformset_factory
from django.contrib import messages
from django.db.models import Q, Prefetch

from .models import Plan, Spot, Photo, TRANSPORT_CHOICES

# ------------ フィード ------------
def feed(request):
    q = (request.GET.get("q") or "").strip()

    plans = (
        Plan.objects.order_by("-created_at")
        .select_related("author")
        .prefetch_related(
            Prefetch("photos", queryset=Photo.objects.order_by("order", "id")),
            "spots",
        )
    )

    if q:
        qs = plans
        # @username 完全一致（前方の @ を剥がして iexact）
        if q.startswith("@"):
            username = q[1:]
            qs = qs.filter(author__username__iexact=username)

        # #tag → tags 内部検索（スペース/カンマ区切りタグを想定）
        elif q.startswith("#"):
            tag = q[1:]
            qs = qs.filter(tags__icontains=tag)

        # それ以外は汎用フリーワード（タイトル/本文/タグ/スポット名）
        else:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(tags__icontains=q)
                | Q(spots__name__icontains=q)
            ).distinct()

        plans = qs

    return render(request, "plans/feed.html", {"plans": plans, "q": q})

# ------------ 詳細 ------------
def plan_detail(request, pk):
    plan = get_object_or_404(
        Plan.objects.select_related('author').prefetch_related('spots', 'photos'),
        pk=pk
    )
    spots = [{
        "name": s.name, "lat": s.lat, "lng": s.lng,
        "stay": s.stay_minutes, "mode": s.transport_to_next, "order": s.order
    } for s in plan.spots.all()]
    route_latlng = []
    if plan.route_geojson and plan.route_geojson.get("type") == "LineString":
        route_latlng = [[lng, lat] for (lng, lat) in plan.route_geojson.get("coordinates", [])]
    ctx = {
        "plan": plan,
        "spots": json.dumps(spots, ensure_ascii=False),
        "route_json": json.dumps(route_latlng),
        "transport_labels": dict(TRANSPORT_CHOICES),
    }
    return render(request, 'plans/plan_detail.html', ctx)

# ------------ GPSルート保存 ------------
@require_POST
@login_required
def plan_track_save(request, pk):
    plan = get_object_or_404(Plan, pk=pk, author=request.user)
    try:
        data = json.loads(request.body or "{}")
        coords = data.get("coordinates") or []   # [[lng,lat], ...]
        if not isinstance(coords, list):
            return HttpResponseBadRequest("coordinates must be a list")
        plan.route_geojson = {"type": "LineString", "coordinates": coords}
        plan.started_at = data.get("started_at") or plan.started_at
        plan.ended_at   = data.get("ended_at")   or plan.ended_at
        plan.save(update_fields=["route_geojson", "started_at", "ended_at"])
        return JsonResponse({"ok": True, "count": len(coords)})
    except Exception as e:
        return HttpResponseBadRequest(str(e))


# ------------ フォーム定義 ------------
class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ["title", "tags", "description"]

class SpotForm(forms.ModelForm):
    class Meta:
        model = Spot
        fields = ["order", "name", "lat", "lng", "stay_minutes", "transport_to_next", "note"]
        widgets = {"lat": forms.HiddenInput(), "lng": forms.HiddenInput()}

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ["order", "image", "caption"]

# フォームセット（ここが “公式名”）
SpotFS  = inlineformset_factory(Plan, Spot,  form=SpotForm,  extra=1, can_delete=True)
PhotoFS = inlineformset_factory(Plan, Photo, form=PhotoForm, extra=1, can_delete=True)

# ------------ 新規作成 ------------
# 新規
@login_required
def plan_create(request):
    plan = Plan(author=request.user)
    if request.method == "POST":
        form = PlanForm(request.POST, request.FILES, instance=plan)
        sfs  = SpotFS(request.POST, instance=plan, prefix="spots")
        pfs  = PhotoFS(request.POST, request.FILES, instance=plan, prefix="photos")
        if form.is_valid() and sfs.is_valid() and pfs.is_valid():
            plan = form.save()
            sfs.instance = plan; pfs.instance = plan
            sfs.save(); pfs.save()
            return redirect("plans:plan_detail", pk=plan.pk)
    else:
        form = PlanForm(instance=plan)
        sfs  = SpotFS(instance=plan, prefix="spots")
        pfs  = PhotoFS(instance=plan, prefix="photos")

    return render(request, "plans/plan_form.html", {
        "form": form,
        "spot_formset": sfs,     # ← ここに合わせる
        "photo_formset": pfs,    # ← ここに合わせる
    })

# ------------ 編集 ------------
@login_required
def plan_update(request, pk):
    plan = get_object_or_404(Plan, pk=pk, author=request.user)
    if request.method == "POST":
        form = PlanForm(request.POST, request.FILES, instance=plan)
        spot_formset  = SpotFS(request.POST, instance=plan, prefix="spots")
        photo_formset = PhotoFS(request.POST, request.FILES, instance=plan, prefix="photos")
        if form.is_valid() and spot_formset.is_valid() and photo_formset.is_valid():
            form.save()
            spot_formset.save()
            photo_formset.save()
            return redirect("plans:plan_detail", pk=plan.pk)
    else:
        form = PlanForm(instance=plan)
        spot_formset  = SpotFS(instance=plan, prefix="spots")
        photo_formset = PhotoFS(instance=plan, prefix="photos")

    return render(request, "plans/plan_form.html", {
        "form": form,
        "spot_formset": spot_formset,
        "photo_formset": photo_formset,
        "mode": "edit",
        "plan": plan,
    })

@login_required
def plan_delete(request, pk):
    plan = get_object_or_404(Plan, pk=pk, author=request.user)
    if request.method != "POST":
        messages.error(request, "不正なリクエストです。")
        return redirect("plans:plan_detail", pk=plan.pk)

    title = plan.title
    plan.delete()  # Photo は on_delete=CASCADE で一緒に消えます（物理ファイルは後述）
    messages.success(request, f"「{title}」を削除しました。")

    # 戻り先（クエリ ?next=/accounts/xxx/ を優先）
    next_url = request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("plans:feed")
