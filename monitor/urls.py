from django.conf.urls import url, include
from monitor import views

urlpatterns = [
    url(r'^zabbix/', include([
        url(r'^cachehost/$', views.CacheZabbixHost.as_view(), name="cache_host"),
        url(r'^host/', include([
            url(r'^sync/$', views.SyncHostToZabbix.as_view(), name="sync_host"),
            url(r'^linktemplates/$', views.LinkTemplatesView.as_view(), name="link_templates"),
            url(r'^unlinktemplate/$', views.UnlinkTemplateView.as_view(), name="unlink_template"),
        ])),
    ])),
]