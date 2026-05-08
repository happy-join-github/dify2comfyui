import json
import urllib.parse
from typing import Any, Generator

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from .comfyui_client import ComfyUIClient


class ComfyuiTxt2ImgTool(Tool):
    """ComfyUI 文生图工具"""

    def _prepare_workflow(self, positive_prompt: str, negative_prompt: str, workflow_template: str) -> dict:
        """准备文生图工作流"""
        workflow = json.loads(workflow_template)
        workflow['85']['inputs']['text'] = negative_prompt
        workflow['92']['inputs']['text'] = positive_prompt
        return workflow

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        api_url = tool_parameters.get("api_url", "").strip()
        positive_prompt = tool_parameters.get("positive_prompt", "").strip()
        negative_prompt = tool_parameters.get("negative_prompt", "").strip()
        workflow = tool_parameters.get("workflow", "")
        # 默认超时时间为10分钟
        timeout = tool_parameters.get("timeout", 600)
        node_id = tool_parameters.get("nodeID", "9")
        resource_type = tool_parameters.get("resourceType", "image")

        if not api_url:
            return self.create_json_message({"status": "error","message": "缺少 ComfyUI api_url","url": ""})
            
        if not positive_prompt:
            return self.create_json_message({"status": "error","message": "缺少正向提示词","url": ""})
        
        if not negative_prompt:
            return self.create_json_message({"status": "error","message": "缺少负向提示词","url": ""})
        
        if not workflow:
            return self.create_json_message({"status": "error","message": "缺少工作流模板","url": ""})
            
        try:
            client = ComfyUIClient(api_url)
            wf = self._prepare_workflow(positive_prompt, negative_prompt, workflow)
            prompt_id = client.submit_prompt(wf)
            result = client.wait_for_result(prompt_id, node_id, resource_type, timeout)

            if result["status"] == "error":
                return self.create_json_message(result)
                

            info = result["url"]
            if isinstance(info, dict):
                filename = info.get("filename", "")
                
                img_url = f"{api_url}/view?{urllib.parse.urlencode({'filename': filename, 'type': info.get('type', 'output')})}"
                result["url"] = img_url
                
                return self.create_json_message(result)
            else:
                return self.create_json_message(result)

        except TimeoutError as e:
            return self.create_json_message({
                "status": "error",
                "message": f"生成超时：{str(e)}",
                "url": ""
            })
        except Exception as e:
            err_msg = str(e)[:120]
            return self.create_json_message({
                "status": "error",
                "message": f"生成失败：{err_msg}",
                "url": ""
            })
