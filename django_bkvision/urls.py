# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.urls import include

from . import views

urlpatterns = (
    url(r'^api/v1/datasource/query/$', views.query_data),
    url(r'^api/v1/meta/query/$', views.query_meta),
    url(r'^api/v1/variable/query/$', views.query_variable),
    url(r'^api/v1/panel/$', views.get_panel),
    url(r'^api/v1/panel/get_child_panels/$', views.get_child_panels),

)
