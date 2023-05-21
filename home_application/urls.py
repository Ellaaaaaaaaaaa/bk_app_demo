# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.conf.urls import url

from . import views

urlpatterns = (
    url(r"^$", views.home),
    url(r"^search_business/$", views.search_business, name="业务信息"),
    url(r"^search_module/$", views.search_module, name="查询业务实例拓扑"),
    url(r"^search_biz_inst_topo/$", views.search_biz_inst_topo, name="查询业务实例拓扑"),
    url(r"^list_biz_hosts/$", views.list_biz_hosts, name="业务下的主机"),

    #### 主机操作
    url(r"^get_host_base_info/$", views.get_host_base_info, name="主机信息"),

    #url(r"^clone_host_property/$", views.clone_host_property, name="克隆属性"),

    url(r"^transfer_host_module/$", views.transfer_host_module, name="转移模块"),


    # 操作记录
    url(r"^record_page/$", views.record_page, name="操作记录页面"),
    url(r"^record_lists/$", views.record_lists, name="操作记录日志"),

    # 发布
    url(r"^deploy_page/$", views.deploy_page, name="发布页面"),
    url(r"^get_job_plan_list/$", views.get_job_plan_list, name="查询执行方案列表"),
    url(r"^get_job_plan_detail/$", views.get_job_plan_detail, name="查询执行方案详情"),
    url(r"^execute_job_plan/$", views.execute_job_plan, name="执行作业执行方案"),
    url(r"^get_job_execute_history_list/$", views.get_job_execute_history_list, name="查询作业执行历史"),
    url(r"^refresh_alert_data/", views.refresh_alert_data, name="刷新告警数据"),
    url(r"^get_alert_monitor/", views.get_alert_monitor, name="告警数据"),
    url(r"^get_alert_monitor_group_data/", views.get_alert_monitor_group_data, name="可视化告警数据"),
)
