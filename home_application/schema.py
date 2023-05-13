SOPS_GET_TEMPLATE_LIST_PARAMS = {
    "type": "object",
    "required": ["bk_biz_id"],
    "properties": {
        "name": {"type": "string"}
    },
}
SOPS_CREATE_AND_EXECUTE_TASK_PARAMS = {
    "type": "object",
    "required": ["name", "bk_biz_id", "template_id", "host_id"],
    "properties": {
        "name": {"type": "string"},
        "bk_biz_id": {"type": "integer"},
        "template_id": {"type": "integer"},
        "host_id": {"type": "integer"}
    },
}
SOPS_STATUS_TASK_PARAMS = {
    "type": "object",
    "required": ["bk_biz_id", "host_id"],
    "properties": {
        "bk_biz_id": {"type": "integer"},
        "host_id": {"type": "integer"},
    },
}
LIST_FREE_HOSTS_PARAMS = {
    "type": "object",
    "required": ["bk_biz_id", "page", "bk_module_ids"],
    "properties": {
        "bk_biz_id": {"type": "integer"},
        "page": {
            "type": "object",
            "patternProperties": {
                "start": {"type": "integer"},
                "limit": {"type": "integer"},
            }
        },
        "bk_module_ids": {
            "type": "array"
        }
    },
}
LIST_BIZ_HOST_PARAMS = {
    "type": "object",
    "required": ["bk_biz_id", "start", "length"],
    "properties": {
        "bk_biz_id": {"type": "integer"},
        "start": {"type": "integer"},
        "length": {"type": "integer"},
    },
}

LIST_BIZ_HOST_TOPO_PARAMS = {
    "type": "object",
    "required": ["bk_biz_id", "bk_biz_name", "start", "length"],
    "properties": {
        "bk_biz_id": {"type": "integer"},
        "bk_biz_name": {"type": "string"},
        "start": {"type": "integer"},
        "length": {"type": "integer"},
    },
}

GET_HOST_BASE_INFO_PARAMS = {
    "type": "object",
    "required": ["bk_host_id"],
    "properties": {
        "bk_host_id": {"type": "integer"},
    },
}

CLONE_HOST_PROPERTY_PARAMS = {
    "type": "object",
    "required": ["bk_org_ip", "bk_dst_ip"],
    "properties": {
        "bk_org_ip": {"type": "string"},
        "bk_dst_ip": {"type": "string"},
    },
}

TRANSFER_HOST_PARAMS = {
    "type": "object",
    "required": ["bk_biz_id", "bk_host_id", "bk_module_id"],
    "properties": {
        "bk_biz_id": {"type": "integer"},
        "bk_host_id": {"type": "array"},
        "bk_module_id": {"type": "array"},
        "is_increment": {"type": "boolean"},
    },
}

SEARCH_BIZ_INST_TOPO_PARAMS = {
    "type": "object",
    "required": ["bk_biz_id"],
    "properties": {
        "bk_biz_id": {"type": "integer"}
    },
}
