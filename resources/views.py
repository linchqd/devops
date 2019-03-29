from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from resources.models import Idc
from django.shortcuts import redirect
from accounts.mixins import PermissionRequiredMinxin
from resources.forms import CreateIdcForm
import json

class IdcListView(LoginRequiredMixin, ListView):
    template_name = "resources/idc_list.html"
    model = Idc
    ordering = "id"

    def post(self, request):
        idc_id = request.POST.get("id")
        try:
            idc_obj = Idc.objects.get(pk__exact=idc_id)
        except Idc.DoesNotExist:
            return redirect("error", next="idc_list", msgs="该idc机房不存在")
        if len(idc_obj.server_set.all()) > 0:
            return redirect("error", next="idc_list", msgs="该idc机房还有服务器，不能删除")
        else:
            idc_obj.delete()
            return redirect("success", next="idc_list")

class IdcAddView(LoginRequiredMixin, PermissionRequiredMinxin, TemplateView):
    permission_required = "resources.add_idc_list"
    template_name = "resources/idc_add.html"

    def post(self, request):
        data = CreateIdcForm(request.POST)
        if data.is_valid():
            idc_obj = Idc(**data.cleaned_data)
            try:
                idc_obj.save()
                return redirect("success", next="idc_list")
            except Exception as e:
                return redirect("error", next="idc_add", msgs=e.args)
        else:
            return redirect("error", next="idc_add", msgs=json.dumps(json.loads(data.errors.as_json()), ensure_ascii=False))


