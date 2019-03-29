from django.contrib.auth.mixins import PermissionRequiredMixin as PermissionRequired
from django.shortcuts import redirect

class PermissionRequiredMinxin(PermissionRequired):
    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return redirect("error", next="index", msgs="没有权限, 请联系管理员!")
        return super(PermissionRequiredMinxin, self).dispatch(request, *args, **kwargs)