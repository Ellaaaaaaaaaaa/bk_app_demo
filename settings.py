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

import os

"""
请不要修改该文件
如果你需要对settings里的内容做修改，config/default.py 文件中 添加即可
如有任何疑问，请联系 【蓝鲸助手】
"""
BK_BIZ_ID = 401
# HOST_PROPERTIE_FIELDS 字段格式

HOST_PROPERTIE_FIELDS = {
    "bk_host_innerip": "内网IP",
    "bk_host_outerip": "外网IP",
    "bk_os_type": "操作系统类型",
    "bk_host_name": "主机名称",
    "bk_os_version": "系统版本",
    "bk_os_name": "系统名称",
    "bk_cpu": "CPU核心",
    "bk_os_bit": "系统位数",
    "bk_cpu_module": "CPU型号",
    "bk_mem": "内存大小",
    "bk_disk": "磁盘大小",
    "bk_mac": "MAC地址",
    "create_time": "创建时间",
    "bk_cpu_architecture": "CPU架构",
    "bk_host_innerip_v6": "内网IPv6",
    "bk_host_outerip_v6": "外网IPv6",
    "bk_agent_id": "GSE Agent ID",
    "bk_outer_mac": "外网MAC地址",
    "bk_cloud_vendor": "云厂商",
    "bk_cloud_host_status": "云主机状态",
    "bk_cloud_inst_id": "云实例ID",
    "bk_state": "状态",
    "import_from": "来源",
    "bk_province_name": "省份名称",
    "bk_cloud_id": "云区域ID",
    "bk_sn": "序列号"
}
# V3判断环境的环境变量为BKPAAS_ENVIRONMENT
if "BKPAAS_ENVIRONMENT" in os.environ:
    ENVIRONMENT = os.getenv("BKPAAS_ENVIRONMENT", "dev")
# V2判断环境的环境变量为BK_ENV
else:
    PAAS_V2_ENVIRONMENT = os.environ.get("BK_ENV", "development")
    ENVIRONMENT = {"development": "dev", "testing": "stag", "production": "prod"}.get(
        PAAS_V2_ENVIRONMENT
    )
DJANGO_CONF_MODULE = "config.{env}".format(env=ENVIRONMENT)

try:
    _module = __import__(DJANGO_CONF_MODULE, globals(), locals(), ["*"])
except ImportError as err:
    raise ImportError(
        "Could not import config '%s' (Is it on sys.path?): %s"
        % (DJANGO_CONF_MODULE, err)
    )

for _setting in dir(_module):
    if _setting == _setting.upper():
        locals()[_setting] = getattr(_module, _setting)

# Celery 消息队列设置 Redis
BROKER_URL = "redis://localhost:6379/0"
