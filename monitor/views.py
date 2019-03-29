from django.shortcuts import render

# Create your views here.
from django.views.generic import View, TemplateView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from monitor.zabbix import cache_host, Zabbix, create_host, get_templates, link_templates
from resources.models import Product, Server
import logging

logger = logging.getLogger(__name__)

class CacheZabbixHost(LoginRequiredMixin, View):
    def get(self,request):
        ret = {"status": 0}
        logger.debug("开始同步zabbix缓存表,用户: {}".format(request.user.username))
        try:
            cache_host()
        except Exception as e:
            logger.error("同步失败, {}".format(e.args))
            ret['status'] = 1
            ret['msgs'] = e.args
        logger.debug("同步zabbix缓存表完成")
        return JsonResponse(ret)

class SyncHostToZabbix(LoginRequiredMixin, TemplateView):
    template_name = "monitor/sync_host_to_zabbix.html"
    def get_context_data(self, **kwargs):
        context = super(SyncHostToZabbix, self).get_context_data(**kwargs)
        context['products'] = Product.objects.filter(pid__exact=0)
        context['groups'] = Zabbix().get_groups()
        return context
    def post(self, request):
        ret = {"status": 0}
        logger.debug("开始同步主机到zabbix,用户:{}".format(request.user.username))
        group_id = request.POST.get("group_id", "")
        serverids = request.POST.getlist("host_id[]", [])
        logger.debug("获取post请求参数, group_id: {} , serverids: {}".format(group_id, serverids))
        ret_data = create_host(serverids, group_id)
        ret["data"] = ret_data
        logger.debug("同步主机到zabbix完成")
        return JsonResponse(ret)

class LinkTemplatesView(LoginRequiredMixin, TemplateView):
    template_name = "monitor/link_templates.html"
    def get_context_data(self, **kwargs):
        context = super(LinkTemplatesView, self).get_context_data(**kwargs)
        context["products"] = Product.objects.filter(pid__exact=0)
        context["templates"] = get_templates()
        return context

    def post(self, request):
        ret = {"status": 0}
        logger.debug("开始绑定模版，用户:{}".format(request.user.username))
        template_ids = request.POST.getlist("template_ids[]", [])
        server_ids = request.POST.getlist("server_ids[]", [])
        logger.debug("post提交的参数,模版id:{}, serverid:{}".format(template_ids, server_ids))
        if not template_ids:
            ret["status"] = 1
            ret["msgs"] = "没有选择模板"
            return JsonResponse(ret)
        if not server_ids:
            ret["status"] = 1
            ret["msgs"] = "没有选择服务器"
            return JsonResponse(ret)
        ret["data"] = link_templates(server_ids, template_ids)
        return JsonResponse(ret)

class UnlinkTemplateView(LoginRequiredMixin, View):
    def post(self, request):
        logger.debug("开始删除模版,user: {}".format(request.user.username))
        ret = {"status":True}
        data = request.POST.get("data", "")
        if data:
            serverid = eval(data)["hostid"]
            templateid = eval(data)["templateid"]
            logger.debug("serverid: {}, templateid: {}".format(serverid, templateid))
        else:
            ret["status"] = False
            ret["msgs"] = "提交数据为空"
            return JsonResponse(ret)
        if not serverid:
            ret["status"] = False
            ret["msgs"] = "没有提交服务器"
            return JsonResponse(ret)
        if not templateid:
            ret["status"] = False
            ret["msgs"] = "没有提交模版"
            return JsonResponse(ret)
        try:
            server = Server.objects.get(pk__exact=serverid)
            hostid = server.zabbixhosts.hostid
            logger.debug("hostid: {}, templateid: {}".format(hostid, templateid))
            ret_data = Zabbix().unlink_template(hostid, templateid)
            logger.debug("删除模版{}, return: {}".format(templateid, ret_data))
            if "hostids" not in ret_data:
                ret["status"] = False
                ret["msgs"] = ret_data
                return JsonResponse(ret)
        except Server.DoesNotExist:
            ret["status"] = False
            ret["msgs"] = "服务器不存在"
            return JsonResponse(ret)
        except AttributeError:
            ret["status"] = False
            ret["msgs"] = "请先同步zabbix缓存表"
            return JsonResponse(ret)
        except Exception as e:
            ret["status"] = False
            ret["msgs"] = e.args
            return JsonResponse(ret)
        logger.debug("删除模版{}完成".format(templateid))
        return JsonResponse(ret)