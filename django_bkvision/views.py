# -*- coding:utf-8 -*-
import json

import requests
from blueapps.account.decorators import login_exempt
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from django_bkvision.settings import PRE_PROCESS_FUNC, BKVISION_APIGW_URL
from django_bkvision.utils import normalize_request_headers


def build_headers(request):
    request_headers = normalize_request_headers(request)
    request_headers.update({
        "X-Bkapi-Authorization": json.dumps({
            "bk_app_code": settings.APP_CODE,
            "bk_app_secret": settings.SECRET_KEY,
        })
    })
    return request_headers


def proxy_request(request, path):
    headers = build_headers(request)
    params = request.GET.copy()
    proxy_response = requests.request(
        method=request.method,
        url=f"https://apps.ce.bktencent.com/bk-vision{path}",
        params=params,
        data=request.body,
        headers=headers,
        verify=False
    )
    return HttpResponse(
        proxy_response.content,
        status=proxy_response.status_code,
        content_type=proxy_response.headers.get('Content-Type')
    )


@login_exempt
@csrf_exempt
@require_http_methods(["POST"])
def query_variable(request):
    """获取变量数据"""

    try:
        return proxy_request(request, '/openapi/v1/data/query_variable/')
    except Exception as e:
        return JsonResponse({"result": False, "message": "query_variable exception: {}".format(e), "code": 400})


@login_exempt
@csrf_exempt
@require_http_methods(["POST"])
def query_data(request):
    """获取数据"""

    try:
        # 转发前的预处理hook
        request = PRE_PROCESS_FUNC(request)
        return proxy_request(request, '/openapi/v1/data/query/')
    except Exception as e:
        return JsonResponse({"result": False, "message": "query_data exception: {}".format(e), "code": 400})


@login_exempt
@require_http_methods(["GET"])
def query_meta(request):
    """
    获取配置
        curl -X GET -H 'content-type: application/json' \
            'http://127.0.0.1:8001/bkvision/api/v1/meta/query/?share_uid=FwchfLZSsoaBSzjpW7WBa7'
    """
    try:
        return proxy_request(request, '/openapi/v1/meta/query/')
    except Exception as e:
        return JsonResponse({"result": False, "message": "query_meta exception: {}".format(e), "code": 400})


@login_exempt
@csrf_exempt
@require_http_methods(["GET"])
def get_panel(request):
    """获取图表配置"""

    try:
        return proxy_request(request, '/openapi/v1/data/get_panel/')
    except Exception as e:
        return JsonResponse({"result": False, "message": "get_panel exception: {}".format(e), "code": 400})


@login_exempt
@csrf_exempt
@require_http_methods(["GET"])
def get_child_panels(request):
    """获取子图列表"""

    try:
        return proxy_request(request, '/openapi/v1/data/get_child_panels/')
    except Exception as e:
        return JsonResponse({"result": False, "message": "get_child_panels exception: {}".format(e), "code": 400})
