import time
import requests
from typing import Dict, Any


class ComfyUIClient:
    """ComfyUI API 客户端"""

    def __init__(self, server_address: str):
        self.base_url = server_address.rstrip('/')

    def submit_prompt(self, workflow: Dict) -> str:
        """提交工作流任务"""
        resp = requests.post(f"{self.base_url}/prompt", json={"prompt": workflow}, timeout=10)
        resp.raise_for_status()
        prompt_id = resp.json().get("prompt_id")
        if not prompt_id:
            raise ValueError("未获得 prompt_id")
        return prompt_id

    def wait_for_result(
        self,
        prompt_id: str,
        output_node: str,
        resolution_type: str = "image",
        timeout: int = 175
    ) -> Dict[str, Any]:
        """等待生成结果"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                hist = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=10)
                if hist.status_code == 200:
                    data = hist.json()
                    if prompt_id in data:
                        outputs = data[prompt_id].get("outputs", {})
                        output = outputs.get(output_node, {})
                        res_list = output.get(resolution_type, [])
                        if res_list:
                            return {
                                "status": "success",
                                "message": "生成成功",
                                "url": res_list[0]
                            }
            except requests.RequestException:
                pass
            time.sleep(1.2)

        return {
            "status": "error",
            "message": f"生成超时 ({timeout}s)",
            "url": ""
        }

