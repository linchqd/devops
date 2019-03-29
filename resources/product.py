from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import PermissionRequiredMinxin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlquote_plus
from resources.models import Product, Server
from django.contrib.auth.models import User
from resources.forms import CreatProductForm
import json

class ProductAddView(LoginRequiredMixin, PermissionRequiredMinxin, TemplateView):
    permission_required = "resources.add_product"
    template_name = "resources/product_add.html"

    def get_context_data(self, **kwargs):
        context = super(ProductAddView, self).get_context_data(**kwargs)
        context["userlist"] = User.objects.filter(is_superuser=False)
        context["products"] = Product.objects.filter(pid__exact=0)
        return context

    def post(self, request):
        productform = CreatProductForm(request.POST)
        next_url = request.GET.get("next") if request.GET.get("next", "") else "product_manage"
        if productform.is_valid():
            product_obj = Product(**productform.cleaned_data)
            try:
                product_obj.save()
                return redirect(reverse("success", kwargs={"next": urlquote_plus(next_url)}))
            except Exception as e:
                return redirect(reverse("error", kwargs={"next": urlquote_plus(next_url), "msgs": e.args}))
        else:
            return redirect(reverse("error", kwargs={"next": urlquote_plus(next_url), "msgs": json.dumps(json.loads(productform.errors.as_json()), ensure_ascii=False)}))

class GetProductView(LoginRequiredMixin, PermissionRequiredMinxin, View):
    permission_required = "resources.add_product"
    def get(self, request):
        ret = {"status": 0}
        pid = request.GET.get("pid", "")
        if pid:
            ret["data"] = list(Product.objects.filter(pid__exact=pid).values())
            return JsonResponse(ret)

        return JsonResponse(ret)

class ProductManageView(LoginRequiredMixin, PermissionRequiredMinxin, TemplateView):
    permission_required = "resources.change_product"
    template_name = "resources/product_manage.html"
    def get_context_data(self, **kwargs):
        context = super(ProductManageView, self).get_context_data(**kwargs)
        product_id = self.request.GET.get("pid", "")
        if product_id:
            try:
                context["products"] = Product.objects.filter(pid__exact=product_id)
                try:
                    context["parent"] = Product.objects.get(id__exact=product_id).service_name
                except Product.DoesNotExist:
                    pass
                return context
            except Exception as e:
                return context
        else:
            context["products"] = Product.objects.filter(pid__exact=0)
            return context

    def post(self, request):
        product_id = request.POST.get("product_id", "")
        next_url = request.POST.get("next") if request.POST.get("next", "") else "product_manage"
        if product_id:
            try:
                product_obj = Product.objects.get(pk__exact=product_id)
            except Product.DoesNotExist:
                return redirect(reverse("error", kwargs={"next": urlquote_plus(next_url), "msgs": "业务线不存在"}))
            if product_obj.pid == 0:
                if len(Product.objects.filter(pid__exact=product_id)) > 0:
                    return redirect(reverse("error", kwargs={"next": urlquote_plus(next_url), "msgs": "业务线存在二级业务线，不能删除"}))
                if len(Server.objects.filter(server_id__exact=product_id)) > 0:
                    return redirect(reverse("error", kwargs={"next": urlquote_plus(next_url), "msgs": "业务线存在服务器，不能删除"}))
            else:
                if len(Server.objects.filter(server_purpose__exact=product_id)) > 0:
                    return redirect(reverse("error", kwargs={"next": urlquote_plus(next_url), "msgs": "业务线存在服务器，不能删除"}))
            product_obj.delete()
            return redirect(reverse("success", kwargs={"next": urlquote_plus(next_url)}))
        else:
            return HttpResponse("")


