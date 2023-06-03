# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import time
from typing import List, Dict

from blueking.component.shortcuts import get_client_by_user, get_client_by_request
from celery.schedules import crontab
from celery.task import periodic_task


from home_application.models import MonitorAlert, Records

logger = logging.getLogger('auditLogger')


def _get_monitor_alert(request=None):
    """
    获取告警数据
    {
      "id": "168387970514723",
      "alert_name": "测试推送到FlashDuty_copy",
      "status": "ABNORMAL",
      "description": "REAL_TIME(CPU使用率) >= 0.0%, 当前值0.700467%",
      "severity": 1,
      "metric": ["bk_monitor.system.cpu_summary.usage"],
      "bk_biz_id": 3,
      "ip": "10.0.48.18",
      "bk_cloud_id": 0,
      "bk_service_instance_id": null,
      "bk_topo_node": [
        "module|78",
        "set|18",
        "biz|3",
        "environment|3",
        "subsystem|6"
      ],
      "assignee": ["admin"],
      "appointee": null,
      "is_ack": null,
      "is_shielded": false,
      "shield_left_time": "0s",
      "shield_id": null,
      "is_handled": true,
      "strategy_id": 169,
      "create_time": 1683879705,
      "update_time": 1683981142,
      "begin_time": 1683877676,
      "end_time": null,
      "latest_time": 1683981116,
      "first_anomaly_time": 1683877676,
      "target_type": "HOST",
      "target": "10.0.48.18|0",
      "category": "os",
      "tags": [],
      "category_display": "主机&云平台-操作系统",
      "duration": "1d 4h",
      "ack_duration": null,
      "data_type": "time_series",
      "converge_id": "168387970514723",
      "event_id": "424e454d6dc5eda67d717e45821f847b.1683981116.169.169.1",
      "plugin_id": "bkmonitor",
      "stage_display": "已通知",
      "dimensions": [
        {
          "display_value": "10.0.48.18",
          "display_key": "目标IP",
          "value": "10.0.48.18",
          "key": "ip"
        },
        {
          "display_value": 0,
          "display_key": "云区域ID",
          "value": 0,
          "key": "bk_cloud_id"
        }
      ],
      "seq_id": 14723,
      "dedupe_md5": "800b63a023dbf885e6532f14d7024c52",
      "dedupe_keys": [
        "strategy_id",
        "target_type",
        "target",
        "bk_biz_id"
      ],
      "dimension_message": "目标IP(10.0.48.18)",
      "metric_display": [
        {
          "id": "bk_monitor.system.cpu_summary.usage",
          "name": "CPU使用率"
        }
      ],
      "target_key": "主机 10.0.48.18",
      "ack_operator": "",
      "shield_operator": [],
      "strategy_name": "测试推送到FlashDuty_copy",
      "bk_biz_name": "demo体验业务"
    }
    """
    # 获取client
    if request:
        client = get_client_by_request(request)
    else:
        # 需要应用拥有用户认证豁免权限
        client = get_client_by_user("teacher")

    # 获取业务列表
    result = client.cc.search_business()
    if not result["result"]:
        raise Exception("获取业务列表失败：%s" % result["message"])
    bk_biz_ids = [business["bk_biz_id"] for business in result["data"]["info"]]

    # 获取告警数据(最近一天)
    kwargs = {
        "bk_biz_ids": bk_biz_ids,
        "start_time": int(time.time()) - 60 * 60 * 24,
        "end_time": int(time.time()),
        "page": 1,
        "page_size": 10
    }
    result = client.monitor_v3.search_alert(kwargs)
    if not result["result"]:
        raise Exception("获取告警数据失败：%s" % result["message"])
    alerts = result["data"]["alerts"]

    # 获取剩余页数
    for i in range(0, (result["data"]["total"] - 1) // kwargs["page_size"]):
        kwargs["page"] += 1
        result = client.monitor_v3.search_alert(kwargs)
        if not result["result"]:
            raise Exception("获取告警数据失败：%s" % result["message"])
        alerts.extend(result["data"]["alerts"])

    return alerts


def _save_monitor_alert_to_db(alerts: List[Dict]):
    """
    保存告警数据到数据库
    """
    for alert in alerts:
        MonitorAlert.objects.update_or_create(
            alert_id=alert["id"],
            defaults={
                "bk_biz_id": alert["bk_biz_id"],
                "alert_id": alert["id"],
                "name": alert["alert_name"],
                "severity": alert["severity"],
                "category": alert["category"],
                "category_display": alert["category_display"],
                "status": alert["status"],
                "is_shielded": alert["is_shielded"],
                "assignee": alert["assignee"] or [],
                "is_ack": bool(alert["is_ack"]),
                "is_handled": alert["is_handled"],
                "strategy_id": alert["strategy_id"],
                "strategy_name": alert["strategy_name"],
                "ack_operator": alert["ack_operator"]or "",
                "bk_cloud_id": alert["bk_cloud_id"],
                "ip": alert["ip"],
                "create_time": datetime.fromtimestamp(alert["create_time"]),
                "latest_time": datetime.fromtimestamp(alert["latest_time"]),
                "begin_time": datetime.fromtimestamp(alert["begin_time"]),
                "end_time": datetime.fromtimestamp(alert["end_time"]) if alert["end_time"] else None,
                "update_time": datetime.fromtimestamp(alert["update_time"]),
            },
        )


@periodic_task(run_every=crontab(minute='*'))
def sync_monitor_alert_data(request=None):
    """
    同步并保存告警数据
    search_alert数据示例
    """
    alerts = _get_monitor_alert(request)
    _save_monitor_alert_to_db(alerts)


@periodic_task(run_every=crontab())
def get_sops_task_status():
    """
    获取sops标准运维任务执行结果，更新操作日志记录表
    1.查询操作日志中所有任务ID
    2.调用SOPS接口，根据任务ID查询任务执行状态
    3.更新操作日志表数据
    """
    queryset = Records.objects.filter(operate_action="故障机切换", operate_status="RUNNING" )
    for item in queryset:
        task_id = item.input_params.get("task_id")
        bk_biz_id = item.input_params.get("bk_biz_id")
        kwargs = {
            "bk_biz_id": bk_biz_id,
            "task_id": task_id
        }

        client = get_client_by_user("admin")
        api_response = client.sops.get_task_status(kwargs)
        if not api_response ["result"]:
            logger.error(f"[Celery] update record data failed, detail: {api_response['message']}")
            return

        status = api_response['data']["state"]

        # 更新日志管理数据
        Records.objects.filter(pk=item.id).update(**{
            "operator": item.operator ,
            "operate_time": item.operate_time ,
            "operate_action": item.operate_action ,
            "operate_status": status ,
            "input_params": item.input_params ,
            "output_params": item.output_params
        })
        logger.info(f"[Celery] update record data success")
