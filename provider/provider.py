from typing import Any

from dify_plugin import ToolProvider


class ComfyuiGenerateProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # 不检测 ComfyUI 是否可用，仅保留空方法
        pass
