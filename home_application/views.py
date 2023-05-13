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
import datetime
import jsonschema
import json
import logging
from blueking.component.shortcuts import get_client_by_request
from django.core.paginator import Paginator
from django.shortcuts import render
from django.template.defaulttags import register
from django.http import JsonResponse, HttpResponseNotAllowed
from .models import Records, JobExecuteHistory

from home_application.schema import (
    CLONE_HOST_PROPERTY_PARAMS,
)
from django.conf import settings

logger = logging.getLogger('auditLogger')

"""
    配置平台接口信息
    https://apigw.ce.bktencent.com/docs/component-api/default/CC/intro
"""
OS_TYPE = {"1": "Linux", "2": "Windows", "3": "AIX"}
PLATFORMS = dict([
    ("cmdb", "配置平台"),
    ("jobs", "作业平台"),
    ("monitor", "监控平台"),
    ("sops", "运维平台")
])
OPER_METHOD = dict([
    ("POST", "新增"),
    ("DELETE", "删除"),
    ("PATCH", "修改")
])


# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
def home(request):
    """
    首页  配置页
    """
    if request.GET.get("is_vue") == "1":
        return render(request, "home_application/index_vue.html")
    return render(request, "home_application/index_home.html", {"os_type": json.dumps(OS_TYPE)})


def search_business(request):
    """
    # 查询业务
    """
    kwargs = {"condition": {
        "bk_biz_id": settings.BK_BIZ_ID
    }}
    response = get_client_by_request(request, **kwargs).cc.search_business()
    return JsonResponse(response)


def list_biz_hosts_topo(request):
    # 查询业务下的主机和拓扑信息
    pramas = json.loads(request.body)
    bk_biz_id = pramas.get("bk_biz_id", None)
    bk_biz_name = pramas.get("bk_biz_name", "业务名称")
    start = pramas.get("start", 0)
    length = pramas.get("length", 100)
    resp = get_client_by_request(request, **{
        "page": {
            "start": start,
            "limit": length
        },
        "bk_biz_id": bk_biz_id,
        "fields": [
            "bk_host_id",
            "bk_cloud_id",
            "bk_host_innerip",
            "bk_os_type",
            "bk_mac"
        ]
    }).cc.list_biz_hosts_topo()
    res = resp["data"]["info"]
    children = []
    for item in res:
        sub_children = []
        for item2 in item["topo"]:
            subsub_children = []
            for item3 in item2["module"]:
                subsub_children.append({
                    "name": f'模：[{item3["bk_module_id"]}] {item3["bk_module_name"]}',
                    # "value": 1
                })
            sub_children.append({
                "name": f'集：[{item2["bk_set_id"]}] {item2["bk_set_name"]}',
                "children": subsub_children
            })
        children.append({
            # item["bk_mac"] item["bk_os_type"]
            "name": f'主机：[{item["host"]["bk_host_id"]}] {item["host"]["bk_host_innerip"]}',
            "children": sub_children
        })

    data = {
        "name": f"业：{bk_biz_name}",
        "children": children
    }
    return JsonResponse(data)


def list_biz_hosts(request):
    # 查询业务下的主机，获取当前业务的主机列表
    params = json.loads(request.body)
    bk_biz_id = settings.BK_BIZ_ID
    bk_set_id = params.get("bk_set_id")
    bk_module_id = params.get("bk_module_id")
    client = get_client_by_request(request)
    data = {
        "recordsTotal": 0,
        "free_nums": 0,  # 空闲机池数
        "resource_nums": 0,  # 资源池主机数
        "data": []
    }
    request_data = {
        "page": {"start": params.get("start", 0), "limit": params.get("length", 20), "sort": "bk_host_id"},
        "bk_biz_id": bk_biz_id,
        "fields": ["bk_host_id", "bk_cloud_id", "bk_host_innerip", "bk_os_type", "bk_mac", "bk_host_name"]
    }
    if bk_set_id:
        request_data["bk_set_ids"] = [int(bk_set_id)]

    if bk_module_id:
        request_data["bk_module_ids"] = [int(bk_module_id)]

    biz_hosts = client.cc.list_biz_hosts(request_data)
    if biz_hosts.get("result", False):
        data["recordsTotal"] = biz_hosts["data"]["count"]
        data["recordsFiltered"] = biz_hosts["data"]["count"]
        data["data"] = biz_hosts["data"]["info"]
    return JsonResponse(data)


def get_host_base_info(request):
    """
    获取主机详情
    """
    bk_host_id = request.GET.get("bk_host_id", 0)
    client = get_client_by_request(request)

    response = client.cc.get_host_base_info({"bk_host_id": bk_host_id})
    # 渲染模板返回
    if request.GET.get("data_type") == "json":
        return JsonResponse(response)
    host_properties = response.get("data") if response.get("result", False) else []

    return render(request, "home_application/host_detail.html", {"data": host_properties,
                                                                 "os_type": OS_TYPE,
                                                                 "fields": settings.HOST_PROPERTIE_FIELDS
                                                                 })


def clone_host_property(request):
    """
    机器属性管理 克隆主机属性
    """
    if not request.method.lower() == "post":
        return HttpResponseNotAllowed(permitted_methods=["POST"])
    params = json.loads(request.body)
    try:
        jsonschema.validate(params, CLONE_HOST_PROPERTY_PARAMS)
        bk_biz_id = settings.BK_BIZ_ID
        ip_kwargs = dict(
            bk_biz_id=bk_biz_id,
            bk_org_ip=params.get("bk_org_ip", None),
            bk_dst_ip=params.get("bk_dst_ip", None))
        client = get_client_by_request(request)
        results = client.cc.clone_host_property(ip_kwargs)
        Records.objects.create(**{
            "operator": request.user.username,
            "operate_time": datetime.datetime.now(),
            "operate_action": "克隆主机属性",
            "operate_status": "SUCCESS" if results.get("result") else "FAILED",
            "input_params": params,
            "output_params": results
        })
        return JsonResponse(results)
    except jsonschema.ValidationError as e:
        response = {"result": False, "code": 1306406, "data": {},
                    "message": f"Validate Params error, detail: {e.message}"}
        return JsonResponse(response)


def transfer_host_module(request):
    """
    # 业务内的主机转移模块
    """
    if not request.method.lower() == "post":
        return HttpResponseNotAllowed(permitted_methods=["POST"])

    req_params = json.loads(request.body)
    if isinstance(req_params, dict):
        req_params = {
            "bk_biz_id": settings.BK_BIZ_ID,
            "bk_host_id": [req_params.get("bk_host_id")],
            "bk_module_id": req_params.get("bk_module_id", []),
            "is_increment": bool(int(req_params.get("is_increment", 0))),
            #  覆盖或者追加,会删除原有关系. true是更新，false是覆盖
        }
        client = get_client_by_request(request)
        results = client.cc.transfer_host_module(req_params)
        # 执行结果记录
        Records.objects.create(**{
            "operator": request.user.username,
            "operate_time": datetime.datetime.now(),
            "operate_action": "转移主机模块",
            "operate_status": "SUCCESS" if results.get("result") else "FAILED",
            "input_params": req_params,
            "output_params": results
        })
        return JsonResponse(results)


def search_module(request):
    client = get_client_by_request(request)
    params = {
        "fields": [
            "bk_module_name",
            "bk_module_id",
            "bk_set_id",
            "bk_set_name"
        ],
        "bk_biz_id": settings.BK_BIZ_ID,
        "page": {
            "start": 0,
            "limit": 1000
        }
    }

    modules = {"info": [], "count": client.cc.search_module(params)["data"]["count"]}

    for module in client.cc.search_module(params)["data"]["info"]:
        module["bk_module_name"] = f"{module.get('bk_set_name', '默认')}-{module['bk_module_name']}"
        modules["info"].append(module)
    return JsonResponse(modules)


def search_biz_inst_topo(request):
    # 查询业务实例拓扑
    biz_data = {}
    client = get_client_by_request(request)
    req_data = {"bk_biz_id": settings.BK_BIZ_ID}
    response = client.cc.search_biz_inst_topo(req_data)
    if response.get("result"):
        biz_data = response["data"][0]
        set_children = []
        decode_biz_topo(biz_data, set_children)
        biz_data.update({"child": set_children})
    return JsonResponse(biz_data)


def decode_biz_topo(topo, set_children=None):
    """
    解析业务数据
    """
    for topo_child in topo["child"]:
        if topo_child["bk_obj_id"] == "set":
            biz_set = topo_child
            sub_children = []
            for module in biz_set["child"]:
                sub_children.append({
                    "bk_inst_name": f'{module["bk_inst_name"]}({module["bk_inst_id"]})',
                    "bk_inst_id": module["bk_inst_id"]
                })
            set_children.append({
                "bk_inst_id": biz_set["bk_inst_id"],
                "bk_inst_name": biz_set["bk_inst_name"],
                "child": sub_children
            })
        else:
            decode_biz_topo(topo_child, set_children)


def record_page(request):
    """
    操作记录页面
    """
    return render(request, "home_application/record.html")


def record_lists(request):
    """
    操作记录日志内容
    """
    start, length = 0, 30
    try:
        params = json.loads(request.body)
        start = params.get("start", 0)
        length = params.get("length", 30)
    except:
        pass
    records = Records.objects.all().order_by('-create_time')
    paginator = Paginator(records, length)
    data = []

    for item in paginator.get_page(start):
        data.append({"id": item.id,
                     "operator": item.operator,
                     "operate_time": item.operate_time,
                     "operate_action": item.operate_action,
                     "operate_status": item.operate_status,
                     "create_time": item.create_time,
                     "update_time": item.update_time,
                     "input_params": json.dumps(item.input_params),
                     "output_params": json.dumps(item.output_params)})
    return JsonResponse({
        "result": True,
        "message": "",
        "code": 200,
        "data": {
            "total": records.count(),
            "results": data
        }
    })


# 编写自定义模板过滤
@register.filter
def get_item(dict: dict, key):
    return dict.get(key, key)


def deploy_page(request):
    """
    操作记录页面
    """
    return render(request, "home_application/deploy.html")


def get_job_plan_list(request):
    """
    查询执行方案列表
    """
    bk_biz_id = request.GET.get("bk_biz_id")
    start = request.GET.get("start", 0)
    length = request.GET.get("length", 20)

    if not bk_biz_id:
        return JsonResponse({
            "result": True,
            "message": "",
            "code": 200,
            "data": {
                "total": 0,
                "results": [],
            }
        })

    client = get_client_by_request(request)

    kwargs = {
        "bk_biz_id": bk_biz_id,
        "start": start,
        "length": length,
    }
    result = client.jobv3.get_job_plan_list(kwargs)

    if not result["result"]:
        return JsonResponse({
            "result": False,
            "message": result["message"],
            "code": result["code"],
            "data": {
                "total": 0,
                "results": [],
            }
        })

    for plan in result["data"]["data"]:
        plan["create_time"] = datetime.datetime.fromtimestamp(plan["create_time"]).strftime("%Y-%m-%d %H:%M:%S")
        plan["last_modify_time"] = datetime.datetime.fromtimestamp(plan["last_modify_time"]).strftime("%Y-%m-%d %H:%M:%S")

    return JsonResponse({
        "result": True,
        "message": "",
        "code": 200,
        "data": {
            "total": result["data"]["total"],
            "results": result["data"]["data"],
        }
    })


def get_job_plan_detail(request):
    """
    查询执行方案详情
    """
    bk_biz_id = request.GET.get("bk_biz_id")
    job_plan_id = request.GET.get("job_plan_id")

    client = get_client_by_request(request)

    kwargs = {
        "bk_biz_id": bk_biz_id,
        "job_plan_id": job_plan_id,
    }

    result = client.jobv3.get_job_plan_detail(kwargs)
    return JsonResponse({
        "result": True,
        "message": "",
        "code": 200,
        "data": result["data"],
    })


def execute_job_plan(request):
    """
    执行作业执行方案
    """
    params = json.loads(request.body)

    bk_biz_id = params["bk_biz_id"]
    job_plan_id = params["job_plan_id"]
    global_var_list = params["global_var_list"]

    client = get_client_by_request(request)

    cleaned_global_var_list = []

    for global_var in global_var_list:
        if global_var["type"] == 3:
            cleaned_global_var_list.append({
                "id": global_var["id"],
                "server": {"ip_list": [{"ip": global_var["value"], "bk_cloud_id": 0}]}
            })
        else:
            cleaned_global_var_list.append({
                "id": global_var["id"],
                "value": global_var["value"],
            })

    kwargs = {
        "bk_biz_id": bk_biz_id,
        "job_plan_id": job_plan_id,
        "global_var_list": cleaned_global_var_list,
    }

    result = client.jobv3.execute_job_plan(kwargs)

    # 执行结果记录
    Records.objects.create(**{
        "operator": request.user.username,
        "operate_time": datetime.datetime.now(),
        "operate_action": "执行作业执行方案",
        "operate_status": "SUCCESS" if result.get("result") else "FAILED",
        "input_params": kwargs,
        "output_params": result
    })

    if not result["result"]:
        return JsonResponse({
            "result": False,
            "message": result["message"],
            "code": result["code"],
            "data": None,
        })

    JobExecuteHistory.objects.create(
        bk_biz_id=bk_biz_id,
        job_plan_id=job_plan_id,
        job_instance_id=result["data"]["job_instance_id"],
        job_instance_name=result["data"]["job_instance_name"],
    )

    return JsonResponse({
        "result": True,
        "message": "",
        "code": 200,
        "data": result["data"],
    })


def get_job_execute_history_list(request):
    """
    查询作业执行历史
    """
    bk_biz_id = request.GET.get("bk_biz_id", 0)

    histories = JobExecuteHistory.objects.filter(bk_biz_id=bk_biz_id).order_by("-job_instance_id")

    results = []

    client = get_client_by_request(request)

    for history in histories:
        if not history.is_finished:
            # 组件API请求参数
            kwargs = {
                "bk_biz_id": bk_biz_id,
                "job_instance_id": history.job_instance_id,
            }
            result = client.jobv3.get_job_instance_status(kwargs)
            if result["result"]:
                history.is_finished = result["data"]["finished"]
                history.status = result["data"]["job_instance"]["status"]
                history.create_time = result["data"]["job_instance"]["create_time"]
                history.start_time = result["data"]["job_instance"]["start_time"]
                history.end_time = result["data"]["job_instance"]["end_time"]
                history.total_time = result["data"]["job_instance"]["total_time"]
                history.save()

        results.append({
            "job_plan_id": history.job_plan_id,
            "job_instance_id": history.job_instance_id,
            "job_instance_name": history.job_instance_name,
            "status": history.get_status_display(),
            "create_time": datetime.datetime.fromtimestamp(history.create_time/1000).strftime("%Y-%m-%d %H:%M:%S") if history.create_time else None,
            "start_time": datetime.datetime.fromtimestamp(history.start_time/1000).strftime("%Y-%m-%d %H:%M:%S") if history.start_time else None,
            "end_time": datetime.datetime.fromtimestamp(history.end_time/1000).strftime("%Y-%m-%d %H:%M:%S") if history.end_time else None,
            "total_time": history.total_time,
        })

    return JsonResponse({
        "result": True,
        "message": "",
        "code": 200,
        "data": results,
    })
