from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse, HttpResponseRedirect, QueryDict
from django.views.generic import TemplateView, View, ListView
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from accounts.mixins import PermissionRequiredMinxin
import logging

logger = logging.getLogger(__name__)

class UserLoginView(TemplateView):
    template_name = "user/login.html"

    def post(self, request, *args, **kwargs):
        ret= {"status": 0, "msgs": ""}
        username = self.request.POST.get("username", "")
        userpass = self.request.POST.get("userpass", "")
        user = authenticate(username=username, password=userpass)
        if user:
            login(request, user)
            ret["next_url"] = self.request.GET.get("next") if self.request.GET.get("next", "") else "/"
            logger.debug("user: {} login success".format(username))
        else:
            ret["status"] = 1
            ret["msgs"] = "用户名或密码错误,请联系管理员!"
            logger.debug("user: {} login faile".format(username))
        return JsonResponse(ret)

class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse("user_login"))

class UserListView(LoginRequiredMixin, PermissionRequiredMinxin, ListView):
    permission_required = "auth.add_user"
    model = User
    template_name = "user/list.html"
    paginate_by = 10
    left_page_range = 7
    right_page_range = 7
    ordering = "id"

    def get_queryset(self):
        queryset = super(UserListView, self).get_queryset()
        queryset = queryset.filter(is_superuser=False)
        username = self.request.GET.get("username", "")
        if username:
            queryset = queryset.filter(username__icontains=username)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context["page_range"] = self.create_page_range(context["page_obj"])
        search_name = self.request.GET.copy()
        if search_name.get("username", ""):
            try:
                search_name.pop("page")
            except:
                pass
            context.update(search_name.dict())
            context["search_name"] = "&" + search_name.urlencode()
        return context

    def create_page_range(self,page_obj):
        start = page_obj.number - self.left_page_range
        end = page_obj.number + self.right_page_range
        if start <=0:
            start = 1
        if end > page_obj.paginator.num_pages:
            end = page_obj.paginator.num_pages
        return range(start,(end + 1))

class UserModifyStatusView(LoginRequiredMixin, View):
    def post(self,request):
        user_id = self.request.POST.get("uid", "")
        ret = {"status": 0}
        try:
            user_obj = User.objects.get(id=user_id)
            user_obj.is_active = False if user_obj.is_active else True
            user_obj.save()
        except User.DoesNotExist:
            ret["msgs"] = "user is does not exist!"
        return JsonResponse(ret)

class UserJoinGroup(LoginRequiredMixin, View):
    def get(self, request):
        uid = request.GET.get("uid", "")
        all_groups = Group.objects.all()
        try:
            user_obj = User.objects.get(id = uid)
        except User.DoesNotExist:
            pass
        else:
            all_groups = all_groups.exclude(id__in=user_obj.groups.values_list("id"))
        return JsonResponse(list(all_groups.values("id", "name")), safe=False)

    def post(self, request):
        data = QueryDict(request.body)
        user_id = data.get("uid", "")
        group_id = data.get("gid", "")
        option = data.get("option", "")
        ret= {"status": 0}
        if option == "join":
            try:
                user_obj = User.objects.get(id=user_id)
                group_obj = Group.objects.get(id=group_id)
                user_obj.groups.add(group_obj)
                user_obj.save()
            except User.DoesNotExist:
                ret["status"] = 1
                ret["msgs"] = "用户不存在!"
            except Group.DoesNotExist:
                ret["status"] = 1
                ret["msgs"] = "用户组不存在!"
            return JsonResponse(ret)




