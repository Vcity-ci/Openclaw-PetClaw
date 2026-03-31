import os
import socket
from modules.logger_manager import LoggerManager

class PortManager:
    def __init__(self):
        self.logger = LoggerManager()
        # 官方 Onboard 完成的标志：通常是生成了 .env 或 data 目录下的配置文件
        self.onboard_flag = ".env" 

    def check_onboard_status(self, root_path):
        """
        状态灯 A 逻辑：检测 Onboard 是否完成
        原理：官方执行完 onboard 后，根目录下必然会存在有效的 .env 文件
        """
        if not root_path or not os.path.isdir(root_path):
            return False
            
        env_path = os.path.join(root_path, self.onboard_flag)
        if os.path.exists(env_path):
            # 简单检查文件大小，防止是个空文件
            if os.path.getsize(env_path) > 10:
                return True
        return False

    def check_port_active(self, port, host='127.0.0.1'):
        """
        状态灯 B 逻辑：检测 Gateway 是否在线
        原理：尝试建立 TCP 连接，如果成功则说明网关已成功 bind 端口
        """
        try:
            # 使用 socket 探测端口，超时设短一点以保证 GUI 不卡顿
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    def scan_for_config(self, root_path):
        """
        保留原有的扫描功能，用于在 UI 上确认目录合法性
        """
        env_path = os.path.join(root_path, ".env")
        if os.path.exists(env_path):
            return env_path
        return None

    def get_local_ip(self):
        """
        辅助功能：获取本地 IP，用于日志审计
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"