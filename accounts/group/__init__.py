from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, User
from django.http import JsonResponse, Http404
from accounts.mixins import PermissionRequiredMinxin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect, reverse

class GroupListView(LoginRequiredMixin, PermissionRequiredMinxin, ListView):
    permission_required = "auth.add_group"
    template_name = "group/list.html"
    model = Group
    paginate_by = 10
    left_page_range = 7
    right_page_range = 7
    ordering = "id"

    def get_context_data(self, **kwargs):
        context = super(GroupListView, self).get_context_data(**kwargs)
        context["page_range"] = self.create_page_range(context["page_obj"])
        return context

    def create_page_range(self, page_obj):
        start = page_obj.number - self.left_page_range
        end = page_obj.number + self.right_page_range
        if start <= 0:
            start = 1
        if end > page_obj.paginator.num_pages:
            end = page_obj.paginator.num_pages
        return range(start, (end + 1))

class CreateGroupView(LoginRequiredMixin, PermissionRequiredMinxin, View):
    permission_required = "auth.add_group"
    def post(self,request):
        ret = {"status": 0}
        group_name = request.POST.get("group_name", "")
        if not group_name:
            ret["status"] = 1
            ret["msgs"] = "组名不能为空!"
            return JsonResponse(ret)
        try:
            g_obj = Group()
            g_obj.name = group_name
            g_obj.save()
        except:
            ret["status"] = 1
            ret["msgs"] = "该组已存在!"
        return JsonResponse(ret)

class GroupUserListView(LoginRequiredMixin, PermissionRequiredMinxin, TemplateView):
    permission_required = "auth.add_group"
    template_name = "group/userlist.html"
    def get_context_data(self, **kwargs):
        context = super(GroupUserListView,self).get_context_data(**kwargs)
        gid = self.request.GET.get("gid", "")
        try:
            group_obj = Group.objects.get(id = gid)
        except Group.DoesNotExist:
            raise Http404
        else:
            context["object_list"] = group_obj.user_set.all()
            context["group_obj"] = group_obj
        return context

    def post(self,request):
        ret = {"status": 0}
        uid = request.POST.get("uid", "")
        gid = request.POST.get("gid", "")
        try:
            user_obj = User.objects.get(id=uid)
            group_obj = Group.objects.get(id=gid)
        except User.DoesNotExist:
            ret["status"] = 1
            ret["msgs"] = "用户不存在！"
            return JsonResponse(ret)
        except Group.DoesNotExist:
            ret["status"] = 1
            ret["msgs"] = "用户组不存在！"
            return JsonResponse(ret)
        else:
            user_obj.groups.remove(group_obj)
        return JsonResponse(ret)

class ModifyGroupPermission(LoginRequiredMixin, PermissionRequiredMinxin, TemplateView):
    permission_required = "auth.change_group"
    template_name = "group/modify_group_permission.html"

    def get_context_data(self, **kwargs):
        context = super(ModifyGroupPermission, self).get_context_data(**kwargs)
        context["contenttype"] = ContentType.objects.all()
        context["group_id"] = self.request.GET.get("gid", "")
        context["permissions"] = self.get_group_permission(context["group_id"])
        return context
    def get_group_permission(self, group_id):
        try:
            group_obj = Group.objects.get(id=group_id)
            return [p.id for p in group_obj.permissions.all()]
        except Group.DoesNotExist:
            return redirect("error", next="group_list", msgs="用户组不存在")
    def post(self,request):
        permissions = request.POST.getlist("permission", [])
        group_id = request.POST.get("group_id", "")
        try:
            group_obj = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return redirect("error", next="group_list", msgs="用户组不存在")
        try:
            if len(permissions) > 0:
                group_obj.permissions.set(permissions)
            else:
                group_obj.permissions.clear()
        except Exception as e:
            return redirect("error", next="group_list", msgs=e.args)
        return redirect("success", next="group_list")

class GroupPermissioinList(LoginRequiredMixin, PermissionRequiredMinxin, View):
    permission_required = "auth.add_group"
    def get(self,request):
        ret = {"status": 0}
        gid = request.GET.get("gid", "")
        try:
            group_obj = Group.objects.get(id=gid)
        except Group.DoesNotExist:
            ret["msgs"] = "用户组不存在"
            return JsonResponse(ret)
        permissions = group_obj.permissions.all()
        ret["data"] = []
        for p in permissions:
            ret["data"].append({"app_label": p.content_type.app_label, "model": p.content_type.model, "codename": p.codename, "name": p.name})
        ret["group_name"] = group_obj.name
        return JsonResponse(ret)

class DeleteGroupView(LoginRequiredMixin, PermissionRequiredMinxin, View):
    permission_required = "auth.delete_group"
    def post(self, request):
        gid = request.POST.get("gid", "")
        ret = {}
        try:
            group_obj = Group.objects.get(id=gid)
        except Group.DoesNotExist:
            ret["next_url"] = reverse("error", kwargs={"next": "group_list", "msgs": "用户组不存在"})
            return JsonResponse(ret)
        if len(group_obj.user_set.all()) > 0:
            ret["next_url"] = reverse("error", kwargs={"next": "group_list", "msgs": "组内还有成员，请先删除成员再删除该组"})
            return JsonResponse(ret)
        if len(group_obj.permissions.all()) > 0:
            ret["next_url"] = reverse("error", kwargs={"next": "group_list", "msgs": "该组关联权限，请先删除权限再删除该组"})
            return JsonResponse(ret)
        try:
            group_obj.delete()
        except Exception as e:
            ret["next_url"] = reverse("error", kwargs={"next": "group_list", "msgs": e.args})
            return JsonResponse(ret)
        ret["next_url"] = reverse("success", kwargs={"next": "group_list"})
        return JsonResponse(ret)