from django import forms
from resources.models import Idc
from django.contrib.auth.models import User
from resources.models import Product

class CreateIdcForm(forms.Form):
    name = forms.CharField(error_messages={'required': '机房名称不能为空'})
    module_letter = forms.CharField(error_messages={'required': '机房名称简称不能为空'})
    addr = forms.CharField(required=True, error_messages={'required': '机房地址不能为空'})
    user_name = forms.CharField(required=True ,error_messages={'required': '机房负责人不能为空'})
    user_phone = forms.CharField(required=True ,error_messages={'required': '机房负责人电话不能为空'})
    user_email = forms.EmailField(required=True ,error_messages={'required': '机房负责人邮箱不能为空'})
    remarks = forms.CharField(required=False)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        try:
            idc_obj = Idc.objects.get(name__exact=name)
            raise forms.ValidationError(message="该idc机房已经存在")
        except Idc.DoesNotExist:
            return name
    def clean_module_letter(self):
        module_letter = self.cleaned_data.get("module_letter")
        try:
            idc_obj = Idc.objects.get(module_letter__exact=module_letter)
            raise forms.ValidationError(message="该idc机房名称简称已经存在")
        except Idc.DoesNotExist:
            return module_letter

class CreatProductForm(forms.Form):
    service_name    = forms.CharField(required=True)
    module_letter   = forms.CharField(required=True)
    op_interface    = forms.MultipleChoiceField(choices=((u.email, u.username) for u in User.objects.filter(is_superuser=False)))
    dev_interface   = forms.MultipleChoiceField(choices=((u.email, u.username) for u in User.objects.filter(is_superuser=False)))
    pid             = forms.CharField(required=True)

    def clean_service_name(self):
        service_name = self.cleaned_data["service_name"]
        try:
            product_obj = Product.objects.get(service_name__exact=service_name)
            raise forms.ValidationError(message="业务线已存在")
        except Product.DoesNotExist:
            return service_name

    def clean_module_letter(self):
        module_letter = self.cleaned_data["module_letter"]
        try:
            product_obj = Product.objects.get(service_name__exact=module_letter)
            raise forms.ValidationError(message="业务线简称已存在")
        except Product.DoesNotExist:
            return module_letter

    def clean_pid(self):
        pid = self.cleaned_data['pid']
        if pid.isdigit():
            if int(pid) != 0:
                try:
                    product_obj = Product.objects.get(pk__exact=pid)
                    if product_obj.pid != 0:
                        raise forms.ValidationError(message="请选择正确的上级业务线")
                except Product.DoesNotExist:
                    raise forms.ValidationError(message="请选择正确的上级业务线")
        else:
            raise forms.ValidationError(message="请选择正确的业务线")
        return pid

    def clean_op_interface(self):
        op_interface = self.cleaned_data["op_interface"]
        return ",".join(op_interface)

    def clean_dev_interface(self):
        dev_interface = self.cleaned_data["dev_interface"]
        return ",".join(dev_interface)
