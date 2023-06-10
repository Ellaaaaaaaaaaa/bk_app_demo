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

from django.db import models
from datetime import datetime


# Create your models here.


class Records(models.Model):
    operator = models.CharField(verbose_name="操作人", max_length=128)
    operate_time = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    operate_action = models.CharField(verbose_name="操作内容", max_length=255)
    operate_status = models.CharField(verbose_name="操作结果", max_length=255)
    create_time = models.DateTimeField(verbose_name="日志创建时间", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="日志更新时间", auto_now=True)
    is_deleted = models.BooleanField(verbose_name="逻辑删除", default=False)
    input_params = models.JSONField(null=True, verbose_name="请求参数")
    output_params = models.JSONField(null=True, verbose_name="输出参数")

class JobExecuteHistory(models.Model):
    STATUS_CHOICES = [
        (1, "未执行"),
        (2, "正在执行"),
        (3, "执行成功"),
        (4, "执行失败"),
        (5, "跳过"),
        (6, "忽略错误"),
        (7, "等待用户"),
        (8, "手动结束"),
        (9, "状态异常"),
        (10, "步骤强制终止中"),
        (11, "步骤强制终止成功"),
    ]

    bk_biz_id = models.IntegerField(verbose_name="业务ID")
    job_plan_id = models.IntegerField(verbose_name="作业方案ID")
    job_instance_id = models.BigIntegerField(verbose_name="作业实例ID")
    job_instance_name = models.CharField(verbose_name="作业实例名称", max_length=255)
    is_finished = models.BooleanField(verbose_name="作业是否结束", default=False)
    status = models.IntegerField(verbose_name="作业执行状态", choices=STATUS_CHOICES, default=1)
    create_time = models.BigIntegerField(verbose_name="作业创建时间(毫秒)", null=True)
    start_time = models.BigIntegerField(verbose_name="开始执行时间(毫秒)", null=True)
    end_time = models.BigIntegerField(verbose_name="执行结束时间(毫秒)", null=True)
    total_time = models.IntegerField(verbose_name="总耗时(毫秒)", null=True)


class MonitorAlert(models.Model):
    """
    告警信息表
    """
    SEVERITY_CHOICES = [(1, "致命"), (2, "预警"), (3, "提醒")]
    STATUS_CHOICES = [("ABNORMAL", "未恢复"), ("RECOVERED", "已恢复"), ("CLOSED", "已关闭")]

    bk_biz_id = models.IntegerField(verbose_name="业务ID")
    alert_id = models.CharField(verbose_name="告警ID", max_length=64, unique=True)
    name = models.CharField(verbose_name="告警名称", max_length=255)
    severity = models.IntegerField(verbose_name="告警级别", choices=SEVERITY_CHOICES)
    category = models.CharField(verbose_name="分类", max_length=255)
    category_display = models.CharField(verbose_name="分类名称", max_length=255)
    status = models.CharField(verbose_name="当前状态", choices=STATUS_CHOICES, max_length=16)
    is_shielded = models.BooleanField(verbose_name="是否被屏蔽中", default=False)
    assignee = models.JSONField(verbose_name="负责人", default=list)
    is_ack = models.BooleanField(verbose_name="是否确认", default=False)
    is_handled = models.BooleanField(verbose_name="是否处理", default=False)
    strategy_id = models.IntegerField(verbose_name="策略ID")
    strategy_name = models.CharField(verbose_name="策略名称", max_length=255)
    ack_operator = models.CharField(verbose_name="确认人", max_length=64, default="", blank=True)

    bk_cloud_id = models.IntegerField(verbose_name="云区域ID", null=True)
    ip = models.CharField(verbose_name="目标IP", max_length=128, blank=True, null=True)

    begin_time = models.DateTimeField(verbose_name="告警开始时间")
    create_time = models.DateTimeField(verbose_name="告警生成时间")
    latest_time = models.DateTimeField(verbose_name="最近异常时间")
    end_time = models.DateTimeField(verbose_name="结束时间", null=True)
    update_time = models.DateTimeField(verbose_name="更新时间")