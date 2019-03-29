from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import Q
from django.utils.http import urlquote_plus
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import PermissionRequiredMinxin
from resources.models import Server, Product, Idc
from monitor.zabbix import get_templates
import datetime
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def ServerInfoAutoReport(request):
    if request.method == "POST":
        data = request.POST.dict()
        if data:
            try:
                s_obj = Server.objects.get(uuid__exact=data["uuid"])
                data["check_update_time"] = datetime.datetime.now()
                if data['hostname'] != s_obj.hostname:
                    data = autoaddproduct(data)
                    s_obj.hostname = data['hostname']
                    s_obj.idc = data['idc']
                    s_obj.server_id = data['server_id']
                    s_obj.server_purpose = data['server_purpose']
                    s_obj.inner_ip = data['inner_ip']
                    s_obj.save(update_fields=['hostname', 'server_id', 'inner_ip', 'server_purpose', 'check_update_time'])
                elif s_obj.inner_ip != data['inner_ip']:
                    s_obj.inner_ip = data['inner_ip']
                    s_obj.save(update_fields=['inner_ip'])
                else:
                    s_obj.save(update_fields=['check_update_time'])
            except Server.DoesNotExist:
                data = autoaddproduct(data)
                server_obj = Server(**data)
                server_obj.save()
    return HttpResponse("")
def autoaddproduct(data):
    rs = parse_hostname(data["hostname"])
    try:
        idc_name = rs[0]
        idc_obj = Idc.objects.get(module_letter__exact=idc_name)
        data["idc"] = idc_obj
    except Idc.DoesNotExist:
        data["idc"] = ""
    try:
        server_id = rs[1]
        product_obj = Product.objects.get(module_letter__exact=server_id)
        data["server_id"] = product_obj.id
    except Product.DoesNotExist:
        return data
    try:
        server_purpose = rs[2]
        purpose_obj = Product.objects.get(module_letter__exact=server_purpose)
        data["server_purpose"] = purpose_obj.id
    except Product.DoesNotExist:
        return data
    return data

def parse_hostname(hostname):
    return hostname.split("-")


class ServerListView(LoginRequiredMixin, PermissionRequiredMinxin, ListView):
    permission_required = "resource.add_server"
    template_name = "resources/server_list.html"
    paginate_by = 10
    model = Server
    left_page_range = 7
    right_page_range = 7
    ordering = "id"

    def get_queryset(self):
        queryset = super(ServerListView, self).get_queryset()
        product_id = self.request.GET.get("id", "")
        hostname = self.request.GET.get("hostname", "")
        if product_id:
            queryset = queryset.filter(Q(server_purpose__exact=product_id) | Q(server_id__exact=product_id))
            return queryset
        if hostname:
            queryset = queryset.filter(hostname__icontains=hostname)
            return queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ServerListView, self).get_context_data(**kwargs)
        context["page_range"] = self.create_page_range(context["page_obj"])
        search_data = self.request.GET.copy()
        if search_data:
            try:
                search_data.pop("page")
            except:
                pass
            context.update(search_data.dict())
            context["search_name"] = "&" + search_data.urlencode()
        return context

    def create_page_range(self,page_obj):
        start = page_obj.number - self.left_page_range
        end = page_obj.number + self.right_page_range
        if start <=0:
            start = 1
        if end > page_obj.paginator.num_pages:
            end = page_obj.paginator.num_pages
        return range(start,(end + 1))

    def post(self, request):
        server_id = request.POST.get("server_id", "")
        next_url = request.POST.get("next") if request.POST.get("next", "") else "server_list"
        if server_id:
            try:
                server_obj = Server.objects.get(pk__exact=server_id)
                server_obj.delete()
                return redirect(reverse("success", kwargs={"next": urlquote_plus(next_url)}))
            except Server.DoesNotExist:
                return redirect(reverse("error", kwargs={"next": urlquote_plus(next_url), "msgs": "服务器不存在"}))
        else:
            return HttpResponse("")

class QueryServerView(LoginRequiredMixin, PermissionRequiredMinxin, View):
    permission_required = "resource.add_server"
    def get(self, request):
        ret = {"status": 0}
        product_id = request.GET.get("id", "")
        if product_id:
            ret["data"] = list(Server.objects.filter(server_purpose__exact=product_id).values())
            return JsonResponse(ret)
        else:
            ret["status"] = 1
            return JsonResponse(ret)

class GetServerMonitorStatusView(LoginRequiredMixin, PermissionRequiredMinxin, View):
    permission_required = "resource.add_server"
    def get(self, request):
        ret = []
        server_purpose = request.GET.get("id", "")
        logger.debug("开始获取产品线id: {} 下的server监控信息".format(server_purpose))
        if server_purpose:
            servers = Server.objects.filter(server_purpose__exact=server_purpose)
            logger.debug("产品线下所有的server列表: {}".format(servers))
            for server in servers:
                ret_data = {}
                ret_data["hostname"] = server.hostname
                ret_data["id"] = server.id
                if hasattr(server, "zabbixhosts"):
                    ret_data["monitor"] = True
                    try:
                        templates = get_templates(server.zabbixhosts.hostid)
                        if templates:
                            ret_data["template_tag"] = True
                            ret_data["templates"] = templates
                        else:
                            ret_data["template_tag"] = False
                    except Exception as e:
                        logger.error("获取server: {} 绑定的模板失败, {}".format(server.hostname, e.args))
                else:
                    ret_data["monitor"] = False
                ret.append(ret_data)
        return JsonResponse(ret, safe=False)

class ModifyServerPurpose(LoginRequiredMixin, PermissionRequiredMinxin, TemplateView):
    permission_required = "resources.change_server"
    template_name = "resources/modify_server_purpose.html"

    def get_context_data(self, **kwargs):
        context = super(ModifyServerPurpose, self).get_context_data(**kwargs)
        server_pk = self.request.GET.get("id", "")
        try:
            server_obj = Server.objects.get(pk__exact=server_pk)
        except Server.DoesNotExist:
            return redirect("error", next="server_list", msgs="服务器不存在")
        products = Product.objects.all()
        context["server"] = server_obj
        context["products"] = products
        return context

    def post(self, request):
        next_url = request.GET.get("next") if request.GET.get("next", None) else "server_list"
        s_id = request.POST.get("id", "")
        server_id = request.POST.get("server_id", "")
        server_purpose = request.POST.get("server_purpose", "")

        try:
            server_obj = Server.objects.get(pk__exact=s_id)
        except Server.DoesNotExist:
            return redirect(reverse("error", kwargs={"next": urlquote_plus(next_url), "msgs": "服务器不存在"}))
        if server_id:
            try:
                product_server_id = Product.objects.get(pk__exact=server_id)
            except Product.DoesNotExist:
                return redirect(reverse("error", kwargs={"next": urlquote_plus(next_url), "msgs": "一级业务线不存在"}))
        else:
            return redirect(reverse("error", kwargs={"next": urlquote_plus(next_url), "msgs": "请选择一级业务线"}))

        if server_purpose:
            try:
                product_server_purpose = Product.objects.get(pk__exact=server_purpose)
            except Product.DoesNotExist:
                return redirect(reverse("error", kwargs={"next": urlquote_plus(next_url), "msgs": "二级业务线不存在"}))
        else:
            return redirect(reverse("error", kwargs={"next": urlquote_plus(next_url), "msgs": "请选择二级业务线"}))

        if product_server_purpose.pid != product_server_id.id:
            return Http404
        server_obj.server_id = product_server_id.id
        server_obj.server_purpose = product_server_purpose.id
        server_obj.save()
        return redirect(reverse("success", kwargs={"next": urlquote_plus(next_url)}))
