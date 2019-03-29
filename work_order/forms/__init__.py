from django import forms
from work_order.models import WorkOrder
from django.contrib.auth.models import User

class WorkOrderForms(forms.Form):
    title = forms.CharField(error_messages={'required': '工单标题不能为空'})
    order_type = forms.CharField(error_messages={'required': '工单类型不能为空'})
    order_contents = forms.CharField(error_messages={'required': '工单内容不能为空'})
    order_applicant = forms.CharField(error_messages={'required': '申请人不能为空'})
    order_assign_to = forms.CharField(error_messages={'required': '指派人不能为空'})

    def clean_order_type(self):
        order_type = self.cleaned_data["order_type"]
        try:
            order_type = int(order_type)
            for ot in WorkOrder.ORDER_TYPE:
                if order_type in ot:
                    return order_type
            else:
                raise forms.ValidationError(message="工单类型不正确")
        except Exception as e:
            raise forms.ValidationError(message="工单类型不正确")

    def clean_order_applicant(self):
        order_applicant = self.cleaned_data["order_applicant"]
        try:
            order_applicant = User.objects.get(pk__exact=order_applicant)
            return order_applicant
        except User.DoesNotExist:
            raise forms.ValidationError(message="申请人不存在")

    def clean_order_assign_to(self):
        order_assign_to = self.cleaned_data["order_assign_to"]
        try:
            order_assign_to = User.objects.get(pk__exact=order_assign_to)
            return order_assign_to
        except User.DoesNotExist:
            raise forms.ValidationError(message="申请人不存在")