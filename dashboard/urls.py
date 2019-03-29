from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^success/(?P<next>[\s\S]*?)/$', views.SuccessView.as_view(), name="success"),
    url(r'^error/(?P<next>[\s\S]*?)/(?P<msgs>[\u4e00-\u9fa5_a-zA-Z0-9\S\s]*?)/$', views.ErrorView.as_view(), name="error"),
]
