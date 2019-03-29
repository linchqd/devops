from django.conf.urls import url, include
from resources import views, server, product

urlpatterns = [
    url(r'^idc/', include([
        url(r'^list/$', views.IdcListView.as_view(), name='idc_list'),
        url(r'^add/$', views.IdcAddView.as_view(), name="idc_add"),
    ])),
    url(r'^server/', include([
        url(r'^report/$', server.ServerInfoAutoReport, name="server_report"),
        url(r'^list/$', server.ServerListView.as_view(), name="server_list"),
        url(r'^query/$', server.QueryServerView.as_view(), name="query_server"),
        url(r'^getmonitorstatus/$', server.GetServerMonitorStatusView.as_view(), name="get_server_monitor_status"),
        url(r'^modify/', include([
            url(r'^purpose/$', server.ModifyServerPurpose.as_view(), name="modify_server_purpose")
        ])),
    ])),
    url(r'^product/', include([
        url(r'^add/$', product.ProductAddView.as_view(), name="product_add"),
        url(r'^get/$', product.GetProductView.as_view(), name="product_get"),
        url(r'^manage/$', product.ProductManageView.as_view(), name="product_manage"),
    ])),
]
