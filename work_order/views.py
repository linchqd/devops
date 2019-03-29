from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.models import User
from django.utils.http import urlquote_plus
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.shortcuts import reverse, redirect
from work_order.models import WorkOrder
from work_order.forms import WorkOrderForms
import json
# Create your views here.

class WorkOrderApplyView(LoginRequiredMixin, TemplateView):
    template_name = "work_order/apply.html"
    def get_context_data(self, **kwargs):
        context = super(WorkOrderApplyView, self).get_context_data(**kwargs)
        context["order_type"] = WorkOrder.ORDER_TYPE
        context["order_assign_to"] = User.objects.all()
        return context
    def post(self, request):
        work_order_data = WorkOrderForms(request.POST)
        if work_order_data.is_valid():
            try:
                work_order_obj = WorkOrder(**work_order_data.cleaned_data)
                work_order_obj.save()
                return redirect(reverse("success", kwargs={"next": "work_order_list"}))
            except Exception as e:
                return redirect(reverse("error", kwargs={"next": "work_order_apply", "msgs": e.args}))
        else:
            print(work_order_data.errors.as_json())
            return redirect(reverse("error", kwargs={"next": "work_order_apply", "msgs": json.dumps(json.loads(work_order_data.errors.as_json()), ensure_ascii=False)}))

class WorkOrderListView(LoginRequiredMixin, ListView):
    template_name = "work_order/list.html"
    paginate_by = 10
    ordering = ['-completed_time']
    model = WorkOrder
    left_page_range = 7
    right_page_range = 7

    def get_queryset(self):
        queryset = super(WorkOrderListView, self).get_queryset()
        queryset = queryset.filter(order_status__lt=2)
        search_keywords = self.request.GET.get("search_keywords", "")
        if search_keywords:
            queryset = queryset.filter(title__icontains=search_keywords)
            return queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super(WorkOrderListView, self).get_context_data(**kwargs)
        context["page_range"] = self.create_page_range(context["page_obj"])
        search_data = self.request.GET.copy()
        try:
            search_data.pop("page")
        except:
            pass
        if search_data:
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
        work_order_id = request.POST.get("id", "")
        ret = {"status": True}
        if work_order_id:
            try:
                work_order_obj = WorkOrder.objects.get(id__exact=work_order_id)
                work_order_obj.order_status = 3
                work_order_obj.save()
                return JsonResponse(ret)
            except WorkOrder.DoesNotExist:
                ret["status"] = False
                ret["msgs"] = "工单不存在"
                return JsonResponse(ret)
            except Exception as e:
                ret["status"] = False
                ret["msgs"] = e.args
                return JsonResponse(ret)
        else:
            ret["status"] = False
            ret["msgs"] = "工单不存在"
            return JsonResponse(ret)

class WorkOrderDetailView(LoginRequiredMixin, View):
    template_name = "work_order/detail.html"
    def get(self, request):
        work_order_id = request.GET.get("id", "")
        next_url = request.GET.get("next") if request.GET.get("next", None) else reverse("work_order_list")
        if not work_order_id:
            return HttpResponseRedirect(Http404)
        try:
            work_order_obj = WorkOrder.objects.get(id__exact=work_order_id)
            if not request.user.is_superuser:
                if not request.user == work_order_obj.order_assign_to:
                    return HttpResponseRedirect(Http404)
            context = {"id": work_order_obj.id, "title": work_order_obj.title,
                       "order_type": work_order_obj.get_order_type_display(),
                       "order_contents": work_order_obj.order_contents,
                       "order_status": work_order_obj.order_status, "next_url": next_url}
            if work_order_obj.order_status > 1:
                context["order_result"] = work_order_obj.order_result
                return render(request, self.template_name, context=context)
            else:
                return render(request, self.template_name, context=context)
        except WorkOrder.DoesNotExist:
            return HttpResponseRedirect(Http404)

    def post(self, request):
        order_id = request.POST.get("order_id", "")
        next_url = request.POST.get("next") if request.POST.get("next", None) else "work_order_list"
        context = {}
        if not order_id:
            return redirect(reverse("error", kwargs={"next": urlquote_plus(next_url), "msgs": "工单不存在"}))
        try:
            work_order_obj = WorkOrder.objects.get(id__exact=order_id)
            if work_order_obj.order_status == 0:
                work_order_obj.order_status = 1
                work_order_obj.save()
                context = {"id": work_order_obj.id, "title": work_order_obj.title,
                           "order_type": work_order_obj.get_order_type_display(), "msg": "1",
                           "order_contents": work_order_obj.order_contents, "order_status": work_order_obj.order_status}
            elif work_order_obj.order_status == 1:
                order_result = request.POST.get("order_result", "")
                if order_result:
                    work_order_obj.order_status = 2
                    work_order_obj.order_result = order_result
                    work_order_obj.save()
                    context = {"id": work_order_obj.id, "title": work_order_obj.title,
                               "order_type": work_order_obj.get_order_type_display(), "msg": "2",
                               "order_contents": work_order_obj.order_contents,
                               "order_status": work_order_obj.order_status, "order_result": work_order_obj.order_result}
                else:
                    return redirect(reverse("error", kwargs={"next": urlquote_plus(next_url), "msgs": "处理结果不能为空"}))
            context["next_url"] = request.GET.get("next") if request.GET.get("next", None) else reverse("work_order_list")
            return render(request, self.template_name, context=context)
        except WorkOrder.DoesNotExist:
            return redirect(reverse("error", kwargs={"next": urlquote_plus(next_url), "msgs": "工单不存在"}))
        except Exception as e:
            return redirect(reverse("error", kwargs={"next": urlquote_plus(next_url), "msgs": e.args}))

class WorkOrderHistoryView(LoginRequiredMixin, ListView):
    template_name = "work_order/history.html"
    paginate_by = 10
    ordering = ['-completed_time']
    model = WorkOrder
    left_page_range = 7
    right_page_range = 7

    def get_queryset(self):
        queryset = super(WorkOrderHistoryView, self).get_queryset()
        queryset = queryset.filter(order_status__gt=1)
        search_keywords = self.request.GET.get("search_keywords", "")
        if search_keywords:
            queryset = queryset.filter(title__icontains=search_keywords)
            return queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super(WorkOrderHistoryView, self).get_context_data(**kwargs)
        context["page_range"] = self.create_page_range(context["page_obj"])
        search_data = self.request.GET.copy()
        try:
            search_data.pop("page")
        except:
            pass
        if search_data:
            context.update(search_data.dict())
            context["search_name"] = "&" + search_data.urlencode()
        return context

    def create_page_range(self, page_obj):
        start = page_obj.number - self.left_page_range
        end = page_obj.number + self.right_page_range
        if start <= 0:
            start = 1
        if end > page_obj.paginator.num_pages:
            end = page_obj.paginator.num_pages
        return range(start, (end + 1))



