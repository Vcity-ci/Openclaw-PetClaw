import subprocess
import webbrowser
import time
from pathlib import Path

class OperationManager:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.gateway_url = "http://127.0.0.1:18789"

    def run_one_click_startup(self):
        """一键启动核心逻辑"""
        if not self.root_path.exists():
            return False, "根目录路径无效"

        try:
            # 1. 执行 docker-compose 指令
            # 使用 shell=True 兼容 Windows 的命令环境
            cmd = f"cd /d \"{self.root_path}\" && docker compose up -d && docker compose up -d openclaw-gateway"
            
            # 运行并等待指令下发完成
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
            
            if process.returncode != 0:
                return False, f"Docker 指令执行失败: {process.stderr}"

            # 2. 自动打开浏览器 (异步逻辑，建议主程序里判断端口后再开更稳，这里直接尝试)
            # 也可以在这里稍微 sleep 1-2秒等待容器网络就绪
            webbrowser.open(self.gateway_url)
            
            return True, "服务启动指令已发送，正在打开 Web UI..."
            
        except Exception as e:
            return False, f"启动异常: {str(e)}"