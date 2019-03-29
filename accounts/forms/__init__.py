from django import forms
from django.contrib.contenttypes.models import ContentType

class CreatePermissionForm(forms.Form):
    content_type_id = forms.IntegerField(required=True, error_messages={'required': '模型不能为空'})
    codename = forms.CharField(required=True, error_messages={'required': '权限名不能为空'})
    name = forms.CharField(required=True, error_messages={'required': '显示名不能为空'})

    def clean_codename(self):
        codename = self.cleaned_data.get("codename")
        if codename.find(" ") >=1:
            raise forms.ValidationError(message="codename不合法")
        return codename

    def clean_content_type_id(self):
        content_type_id = self.cleaned_data.get("content_type_id")
        try:
            content_type =  ContentType.objects.get(pk__exact=content_type_id)
        except ContentType.DoesNotExist:
            raise forms.ValidationError(message="模型不存在")
        return content_type_id