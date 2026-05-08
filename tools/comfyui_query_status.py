import time
from typing import Any, Generator

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from .comfyui_client import ComfyUIClient


class ComfyuiQueryStatusTool(Tool):
    """ComfyUI 查询任务状态工具"""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        api_url = tool_parameters.get("api_url", "").strip()
        prompt_id = tool_parameters.get("prompt_id", "").strip()
        node_id = tool_parameters.get("nodeID", "9")
        resource_type = tool_parameters.get("resourceType", "image")

        if not api_url:
            yield self.create_json_message({
                "status": "error",
                "message": "缺少 ComfyUI api_url",
                "url": ""
            })
            return

        if not prompt_id:
            yield self.create_json_message({
                "status": "error",
                "message": "缺少 prompt_id",
                "url": ""
            })
            return

        try:
            client = ComfyUIClient(api_url)
            result = client.wait_for_result(prompt_id, node_id, resource_type, timeout=175)

            if result["status"] == "success":
                info = result["url"]
                if isinstance(info, dict):
                    filename = info.get("filename", "")
                    if filename:
                        from urllib.parse import urlencode
                        img_url = f"{api_url}/view?{urlencode({'filename': filename, 'type': info.get('type', 'output')})}"
                        result["url"] = img_url
                yield self.create_json_message(result)
            else:
                yield self.create_json_message(result)

        except Exception as e:
            yield self.create_json_message({
                "status": "error",
                "message": f"查询失败：{str(e)[:120]}",
                "url": ""
            })
