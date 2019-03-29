from django.contrib.auth.models import Permission
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import PermissionRequiredMinxin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect
from django.db.models import Q
from accounts.forms import CreatePermissionForm
import json

class PermissionListView(LoginRequiredMixin, PermissionRequiredMinxin, ListView):
    permission_required = "auth.add_permission"
    model = Permission
    template_name = "user/permission.html"
    paginate_by = 10
    ordering = "id"

    def get_queryset(self):
        queryset = super(PermissionListView, self).get_queryset()
        permission_reg = self.request.GET.get("permission_reg", "")
        if permission_reg:
            queryset = Permission.objects.filter(Q(content_type__app_label__icontains=permission_reg) | Q(content_type__model__icontains=permission_reg))
        return queryset
    def get_context_data(self, **kwargs):
        context = super(PermissionListView, self).get_context_data(**kwargs)
        permission_reg_url = self.request.GET.copy()
        if permission_reg_url.get("permission_reg", ""):
            try:
                permission_reg_url.pop("page")
            except Exception as e:
                pass
            context["permission_reg"] = permission_reg_url.get("permission_reg")
            context["search_name"] = "&" + permission_reg_url.urlencode()
        return context

class PermissionAddView(LoginRequiredMixin, PermissionRequiredMinxin, TemplateView):
    permission_required = "auth.add_permission"
    template_name = "user/permission_add.html"

    def get_context_data(self, **kwargs):
        context = super(PermissionAddView, self).get_context_data(**kwargs)
        context["contenttype"] = ContentType.objects.all()
        return context
    def post(self, request):
        """
        content_type_id = self.request.POST.get("content_type_id", "")
        codename = self.request.POST.get("codename", "")
        name = self.request.POST.get("name", "")
        if not codename or codename.find(" ") >=1:
            return redirect("error", next="permission_add", msgs="codename不合法")
        try:
            content_type = ContentType.objects.get(id=content_type_id)
        except ContentType.DoesNotExist:
            return redirect("error", next="permission_add", msgs="模型不存在")
        try:
            Permission.objects.create(codename=codename, name=name, content_type=content_type)
        except Exception as e:
            return redirect("error", next="permission_add", msgs=e.args)
        return redirect("success", next="permission_list")
        """
        permissionform = CreatePermissionForm(request.POST)
        if permissionform.is_valid():
            try:
                Permission.objects.create(**permissionform.cleaned_data)
                return redirect("success", next="permission_list")
            except Exception as e:
                return redirect("error", next="permission_list", msgs=e.args)
        else:
            return redirect("error", next="permission_list", msgs=json.dumps(json.loads(permissionform.errors.as_json()), ensure_ascii=False))

class ModifyDisplayName(LoginRequiredMixin, PermissionRequiredMinxin, View):
    permission_required = "auth.change_permission"
    def post(self,request):
        permission_id = request.POST.get("permission_id", "")
        displayname = request.POST.get("name", "")
        if not displayname:
            return redirect("error", next="permission_list", msgs="权限显示名为空")
        try:
            permission_obj = Permission.objects.get(id=permission_id)
            permission_obj.name = displayname
            permission_obj.save()
            return redirect("success", next="permission_list")
        except Exception as e:
            return redirect("error", next="permission_list", msgs=e.args)