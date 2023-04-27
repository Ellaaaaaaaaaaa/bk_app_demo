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
