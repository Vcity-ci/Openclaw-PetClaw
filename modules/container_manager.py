import docker
import os
from modules.logger_manager import LoggerManager

class ContainerManager:
    def __init__(self):
        self.logger = LoggerManager()
        self.client = None
        self.reconnect()
        # 官方镜像名称
        self.image_name = "ghcr.io/openclaw/openclaw:latest"
        self.container_prefix = "openclaw" # 对应 compose 中的前缀
    def check_docker_alive(self):
        """
        核心检测：判断 Docker Desktop 服务是否真正可用
        """
        try:
            # 尝试获取版本信息，这是最轻量且能证明 Daemon 存活的操作
            if not self.client:
                self.reconnect()
            if self.client:
                self.client.ping()
                return True, "Docker Desktop 已就绪"
            return False, "Docker 守护进程未连接"
        except Exception:
            return False, "Docker Desktop 尚未启动或正在初始化"

    def reconnect(self):
        """建立或重连 Docker 守护进程"""
        try:
            self.client = docker.from_env()
            self.client.ping()
            return True
        except Exception:
            self.client = None
            return False

    def pull_image_if_needed(self):
        """
        预拉取镜像：对应官方流程的第一部分（拉取镜像）
        在用户点击“启动”或初始化时触发，确保后续 compose 不会因为网络超时失败
        """
        if not self.client and not self.reconnect():
            return False, "Docker 未就绪"
        
        try:
            self.logger.write_log(f"正在检查/拉取镜像: {self.image_name}...")
            self.client.images.pull(self.image_name)
            return True, "镜像已就绪"
        except Exception as e:
            return False, f"镜像拉取失败: {str(e)}"

    def cleanup_conflicts(self):
        """
        清理逻辑：在用户执行新流程前，清理掉可能干扰官方 compose 的旧容器
        """
        if not self.client and not self.reconnect():
            return
        
        try:
            containers = self.client.containers.list(all=True)
            for container in containers:
                if self.container_prefix in container.name:
                    self.logger.write_log(f"清理冲突容器: {container.name}")
                    container.remove(force=True)
        except Exception as e:
            self.logger.write_log(f"清理过程出错: {str(e)}")

    def get_docker_info(self):
        """获取简单的系统信息用于 GUI 显示"""
        if not self.client and not self.reconnect():
            return "Disconnected"
        try:
            return self.client.version().get('Version', 'Unknown')
        except:
            return "Error"

    # 注意：由于现在采用“引导复制官方命令”的逻辑，
    # 具体的 'docker run' 动作被用户的 'docker compose' 取代。
    # 该模块保留 launch 功能作为备用沙箱拉起手段。
    

    def find_openclaw_containers(self):
        """
        检测当前 Docker 中是否存在 OpenClaw 相关容器
        包括运行中和已停止的容器，便于 GUI 提供一键清理入口
        """
        if not self.client and not self.reconnect():
            return []

        try:
            containers = self.client.containers.list(all=True)
            matched = []

            for container in containers:
                if "openclaw-gateway" in container.name or "openclaw_sandbox" in container.name:
                    matched.append(container)

            return matched
        except Exception:
            return []

    def has_openclaw_containers(self):
        containers = self.find_openclaw_containers()
        return len(containers) > 0, [c.name for c in containers]




    def launch_base_sandbox(self, input_dir, output_dir):
        """
        [备用逻辑] 拉起一个只挂载了物理路径的空壳容器
        用于在用户不使用 compose 的情况下强制定义物理边界
        """
        if not self.client and not self.reconnect():
            return False, "Docker 未就绪"

        try:
            self.cleanup_conflicts()
            
            volumes_config = {
                os.path.abspath(input_dir): {'bind': '/mnt/data_input', 'mode': 'ro'},
                os.path.abspath(output_dir): {'bind': '/mnt/data_output', 'mode': 'rw'}
            }

            container = self.client.containers.run(
                image=self.image_name,
                name="petclaw_base_sandbox",
                volumes=volumes_config,
                detach=True,
                tty=True,
                stdin_open=True,
                command="sleep infinity" # 仅作为路径挂载的底座
            )
            return True, f"物理底座已启动: {container.short_id}"
        except Exception as e:
            return False, str(e)
    def destroy_gateway_container(self):
        """
        物理熔断：仅销毁容器实例，不触碰数据卷(Volumes)
        """
        targets = self.find_openclaw_containers()
        if not targets:
            return False, "未发现运行中的 OpenClaw 容器"

        for container in targets:
            self.logger.write_log(f"正在强制销毁容器: {container.name}...")
            container.remove(force=True)

        return True, "沙箱容器已物理销毁，环境已重置"

        