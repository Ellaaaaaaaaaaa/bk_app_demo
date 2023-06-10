# -*- coding: utf-8 _*_
from django.utils.deprecation import MiddlewareMixin
from home_application.models import Records


class AccessMiddleware(MiddlewareMixin):
    """
    请求中间件，用于记录用户操作
    """
    def process_view(self, request, view, args, kwargs) :
        meta = request. META
        access_path = str(meta['PATH_INFO'])
        user = str(request.user)

        if access_path.find("search_business") > -1:
            Records.objects.create(**{
                "operator": user,
                "operate_action": "搜索业务",
                "operate_status": ""
            })
        if access_path.find("search_biz_inst_topo") > -1:
            Records.objects.create(**{
                "operator": user,
                "operate_action": "查看业务拓扑",
                "operate_status": ""
            })
        if access_path.find("list_biz_hosts") > -1:
            Records.objects.create(**{
                "operator": user,
                "operate_action": "查看业务主机列表",
                "operate_status": ""
            })
        if access_path.find("get_alert_monitor") > -1:
            Records.objects.create(**{
                "operator": user,
                "operate_action": "查看告警信息页",
                "operate_status": ""
            })
        if access_path.find("get_alert_monitor_group_data") > -1:
            Records.objects.create(**{
                "operator": user,
                "operate_action": "查看告警分析页",
                "operate_status": ""
            })
        return None