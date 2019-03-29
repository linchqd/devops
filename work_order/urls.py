from django.conf.urls import url, include
from work_order import views

urlpatterns = [
    url(r'^apply/$', views.WorkOrderApplyView.as_view(), name="work_order_apply"),
    url(r'^list/$', views.WorkOrderListView.as_view(), name="work_order_list"),
    url(r'^detail/$', views.WorkOrderDetailView.as_view(), name="work_order_detail"),
    url(r'^history/$', views.WorkOrderHistoryView.as_view(), name="work_order_history"),
]
