import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QFileDialog, QLabel, QMessageBox, QTextBrowser, QHBoxLayout)
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import Qt, QTimer
from pathlib import Path
from modules.port_manager import PortManager
from modules.logger_manager import LoggerManager
from modules.container_manager import ContainerManager
from modules.security_manager import SecurityManager
from modules.volume_manager import VolumeManager
from modules.env_manager import EnvManager

class PetClawMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pm = PortManager()
        self.log_sys = LoggerManager()
        self.cm = ContainerManager()
        
        self.user_selected_path = ""
        self.em = None 
        self.sm = None
        self.vm = None

        self.input_path = ""
        self.output_path = ""
        self.current_page = 0
        
        self.init_ui()
        
        # 状态监测定时器
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_status_leds)
        self.monitor_timer.start(2000) # 每2秒检查一次

    def init_ui(self):
        self.setWindowTitle("PetClaw v0.8")
        self.setFixedSize(550, 850)
        layout = QVBoxLayout()

        # [1. 目录与路径配置]
        # 在 [1. 基础路径配置] 之前插入 Docker 全局状态
        layout.addWidget(QLabel("<b>[ 0. 系统环境监测 ]</b>"))
        self.docker_alive_led = QLabel("📡 Docker 状态：检测中...")
        self.docker_alive_led.setStyleSheet("padding: 5px; background-color: #333; border-radius: 3px;")
        layout.addWidget(self.docker_alive_led)
        layout.addWidget(QLabel("<b>[ 1. 基础路径配置 ]</b>"))
        self.btn_import = QPushButton("选择 OpenClaw 根目录")
        self.btn_import.clicked.connect(self.import_logic)
        layout.addWidget(self.btn_import)
        self.label_root = QLabel("根目录：未选择")
        layout.addWidget(self.label_root)
        # ================= 安全模块（不影响原逻辑） =================

        layout.addWidget(QLabel("<br><b>[ 安全控制 (Gateway 防暴露) ]</b>"))

        self.security_status = QLabel("⚪ 未检测")
        layout.addWidget(self.security_status)

        h_box_security = QHBoxLayout()

        self.btn_harden_port = QPushButton("🔒 安全加固")
        self.btn_harden_port.setEnabled(False)
        self.btn_harden_port.clicked.connect(self.harden_port_logic)

        # 按钮 2：[新增] 环境路径注入 (仅修改 .env)
        self.btn_inject_env = QPushButton("📝 路径变量注入")
        self.btn_inject_env.clicked.connect(self.inject_env_logic)

        # 按钮 3：[新增] YAML 挂载解耦 (仅修改 docker-compose.yml)
        self.btn_decouple_yml = QPushButton("🔗 YAML 路径解耦")
        self.btn_decouple_yml.clicked.connect(self.decouple_yml_logic)

        self.btn_restore = QPushButton("♻️ 一键还原")
        self.btn_restore.clicked.connect(self.restore_logic)

        h_box_security.addWidget(self.btn_harden_port)
        h_box_security.addWidget(self.btn_inject_env)
        h_box_security.addWidget(self.btn_decouple_yml)
        h_box_security.addWidget(self.btn_restore)
        layout.addLayout(h_box_security)
# ==========================================================

        h_box_paths = QHBoxLayout()
        self.btn_set_in = QPushButton("设置输入源 (RO)")
        self.btn_set_in.clicked.connect(self.select_in_logic)
        self.btn_set_out = QPushButton("设置输出区 (RW)")
        self.btn_set_out.clicked.connect(self.select_out_logic)
        h_box_paths.addWidget(self.btn_set_in)
        h_box_paths.addWidget(self.btn_set_out)
        layout.addLayout(h_box_paths)

        # [2. 初始化阶段]
        layout.addWidget(QLabel("<br><b>[ 2. 交互式初始化 (Onboard) ]</b>"))
        self.onboard_led = QLabel("⚪ 等待初始化")
        layout.addWidget(self.onboard_led)
        
        self.btn_copy_onboard = QPushButton("复制 Onboard 命令并打开 Bash")
        self.btn_copy_onboard.setEnabled(False)
        self.btn_copy_onboard.clicked.connect(self.copy_onboard_cmd)
        layout.addWidget(self.btn_copy_onboard)

        # [3. 网关阶段] 增加销毁控制
        layout.addWidget(QLabel("<br><b>[ 3. 开启网关服务 (Gateway) ]</b>"))
        
        # 状态灯
        self.gateway_led = QLabel("⚪ 网关未就绪")
        layout.addWidget(self.gateway_led)

        # 按钮组
        h_box_gate = QHBoxLayout()
        self.btn_copy_gateway = QPushButton("复制 Gateway 命令")
        self.btn_copy_gateway.setEnabled(False)
        self.btn_copy_gateway.clicked.connect(self.copy_gateway_cmd)
        
        self.btn_destroy = QPushButton("💥 销毁沙箱容器")
        self.btn_destroy.setStyleSheet("background-color: #4a1a1a; color: #ff6666;")
        self.btn_destroy.clicked.connect(self.destroy_logic)
        
        h_box_gate.addWidget(self.btn_copy_gateway)
        h_box_gate.addWidget(self.btn_destroy)
        layout.addLayout(h_box_gate)

        # [4. 审计日志]
        layout.addWidget(QLabel("<br><b>[ 流程审计日志 ]</b>"))
        self.log_box = QTextBrowser()
        self.log_box.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: 'Consolas';")
        layout.addWidget(self.log_box)

        # 底部控制
        ctrl_layout = QHBoxLayout()
        btn_prev = QPushButton("<")
        btn_prev.clicked.connect(lambda: self.change_page(-1))
        btn_next = QPushButton(">")
        btn_next.clicked.connect(lambda: self.change_page(1))
        self.page_label = QLabel("P 1")
        btn_clear = QPushButton("清理")
        btn_clear.clicked.connect(self.clear_logs)
        ctrl_layout.addWidget(btn_prev)
        ctrl_layout.addWidget(self.page_label)
        ctrl_layout.addWidget(btn_next)
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(btn_clear)
        layout.addLayout(ctrl_layout)

        c = QWidget()
        c.setLayout(layout)
        self.setCentralWidget(c)

    # --- 核心逻辑 ---

    def import_logic(self):
        path = QFileDialog.getExistingDirectory(self, "选择 OpenClaw 根目录")
        if path:
            self.user_selected_path = path
            self.label_root.setText(f"根目录：...{path[-30:]}")
            self.btn_copy_onboard.setEnabled(True)
            self.log_sys.write_log(f"锁定根目录: {path}")
            self.refresh_log_view()
            self.init_security()

    def select_in_logic(self):
        path = QFileDialog.getExistingDirectory(self, "选择输入目录 (RO)")
        if path:
            self.input_path = path
            self.log_sys.write_log(f"设置输入挂载: {path}")
            self.refresh_log_view()

    def select_out_logic(self):
        path = QFileDialog.getExistingDirectory(self, "选择输出目录 (RW)")
        if path:
            self.output_path = path
            self.log_sys.write_log(f"设置输出挂载: {path}")
            self.refresh_log_view()

    def copy_onboard_cmd(self):
        """拼接并复制 Step 2 命令"""
        base = os.path.abspath(self.user_selected_path)
        # 构造 CMD 兼容的命令（支持跨盘符 cd）
        drive = base[:2]
        cmd = f"{drive} && cd \"{base}\" && docker compose up -d"
        
        QApplication.clipboard().setText(cmd)
        self.log_sys.write_log(f"已复制 Onboard 指令。请在终端粘贴执行。")
        QMessageBox.information(self, "指令已复制", "已复制 cd 与 Onboard 指令。\n请打开任意终端（如 PowerShell/CMD）粘贴并完成初始化配置。")

    def copy_gateway_cmd(self):
        """拼接并复制 Step 3 命令"""
        base = os.path.abspath(self.user_selected_path)
        drive = base[:2]
        cmd = f"{drive} && cd \"{base}\" && docker compose up -d openclaw-gateway"
        
        QApplication.clipboard().setText(cmd)
        self.log_sys.write_log(f"已复制 Gateway 指令。正在等待端口响应...")

    def update_status_leds(self):
        """状态灯轮询逻辑"""
        # 1. 优先检测 Docker Desktop 存活状态
        alive, msg = self.cm.check_docker_alive()
        if alive:
            if "✅" not in self.docker_alive_led.text():
                self.log_sys.write_log("Docker Desktop 服务连接成功")
            self.docker_alive_led.setText(f"✅ {msg}")
            self.docker_alive_led.setStyleSheet("color: #00ff00; font-weight: bold;")
            self.btn_import.setEnabled(True) # 只有 Docker 开了才允许后续操作
        else:
            self.docker_alive_led.setText(f"❌ {msg}")
            self.docker_alive_led.setStyleSheet("color: #ff4444; font-weight: bold;")
            self.btn_import.setEnabled(False)
            self.log_sys.write_log("等待 Docker Desktop 启动...", force=False)
            return # 如果 Docker 没开，跳过后续所有探测（防止报错刷屏）

        # ... 后续原有的 Onboard 和 Gateway 检测逻辑 ...
        has_runtime, names = self.cm.has_openclaw_containers()
        self.btn_destroy.setEnabled(has_runtime)

        # 1. 检测 Onboard 状态 (检查是否生成了特定的配置文件或容器记录)
        # 这里逻辑交由 pm 处理，pm 检查用户目录下是否存在 .openclaw 文件夹或 env
        onboard_done = self.pm.check_onboard_status(self.user_selected_path)
        if onboard_done:
            self.onboard_led.setText("🟢 Onboard 已完成")
            self.onboard_led.setStyleSheet("color: green; font-weight: bold;")
            self.btn_copy_gateway.setEnabled(True)
        else:
            self.onboard_led.setText("⚪ 等待初始化...")
            self.onboard_led.setStyleSheet("color: gray;")

        # 2. 检测 Gateway 状态 (探测 18789 端口)
        gateway_running = self.pm.check_port_active(18789)
        if gateway_running:
            self.gateway_led.setText("🟢 网关已在线: http://127.0.0.1:18789")
            self.gateway_led.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.gateway_led.setText("⚪ 网关未响应")
            self.gateway_led.setStyleSheet("color: gray;")

    def refresh_log_view(self):
        logs, total = self.log_sys.get_page(self.current_page)
        self.log_box.setPlainText("\n".join(logs))
        self.page_label.setText(f"P {self.current_page + 1}/{total}")
        self.log_box.moveCursor(QTextCursor.MoveOperation.End)

    def change_page(self, step):
        self.current_page = max(0, self.current_page + step)
        self.refresh_log_view()

    def clear_logs(self):
        self.log_sys.clear_logs()
        self.current_page = 0
        self.refresh_log_view()
    def destroy_logic(self):
        """销毁逻辑与二次确认"""
        reply = QMessageBox.question(self, '物理熔断确认', 
                                   "确定要销毁当前容器吗？\n这会停止所有 AI 任务，但会保留你的 .env 和数据挂载。",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            success, msg = self.cm.destroy_gateway_container()
            if success:
                self.log_sys.write_log(f"🔥 {msg}", force=True)
                # 销毁后重置灯光状态（虽然定时器也会更新，但这里手动刷一下交互更好）
                self.gateway_led.setText("⚪ 容器已销毁")
                self.gateway_led.setStyleSheet("color: gray;")
            else:
                self.log_sys.write_log(f"⚠️ {msg}", force=True)
            self.refresh_log_view()
    def init_security(self):
        try:
            root_path = Path(self.user_selected_path)
            self.sm = SecurityManager(root_path)
            self.sm.ensure_backup()
            
            self.vm = VolumeManager(root_path)
            
            # 只有这里才会实例化 EnvManager，此时 user_selected_path 已存在
            self.em = EnvManager(root_path)
            self.em.ensure_backup()

            self.btn_harden_port.setEnabled(True)
            self.btn_harden_vol.setEnabled(True)
            self.btn_restore.setEnabled(True)

            self.update_security_status()
        except Exception as e:
            self.security_status.setText(f"❌ 初始化失败: {e}")


    def harden_port_logic(self):
        """仅执行网关端口锁定"""
        try:
            modified = self.sm.harden_gateway()
            if modified:
                self.log_sys.write_log("🔒 端口加固：已强制绑定至 127.0.0.1", force=True)
            else:
                self.log_sys.write_log("ℹ️ 端口加固：当前已是加固状态", force=True)
        except Exception as e:
            self.log_sys.write_log(f"❌ 端口加固失败: {e}", force=True)
    
        self.update_security_status()
        self.refresh_log_view()

    def inject_env_logic(self):
        """动作 1：将用户选择的物理路径写入 .env 变量"""
        if not self.input_path or not self.output_path:
            QMessageBox.warning(self, "路径缺失", "请先通过上方按钮设置输入(RO)和输出(RW)目录")
            return

        try:
            success, msg = self.em.inject_paths(self.input_path, self.output_path)
            if success:
                self.log_sys.write_log("📝 Env 注入：物理路径变量已存入 .env 文件", force=True)
            else:
                self.log_sys.write_log(f"❌ Env 注入失败: {msg}", force=True)
        except Exception as e:
            self.log_sys.write_log(f"❌ 运行异常: {e}", force=True)
    
        self.refresh_log_view()

    def decouple_yml_logic(self):
        """动作 2：修改 YAML，使其引用变量并应用只读/读写后缀"""
        try:
            # 这里 vm.apply_isolation 不需要传入路径，它内部只负责改写引用结构
            success = self.vm.apply_isolation() 
            if success:
                self.log_sys.write_log("🔗 YAML 解耦：挂载点已重定向至 Env 变量并设置权限", force=True)
            else:
                self.log_sys.write_log("ℹ️ YAML 已处于解耦状态，无需重复操作", force=True)
        except Exception as e:
            self.log_sys.write_log(f"❌ YAML 修改失败: {e}", force=True)

        self.update_security_status()
        self.refresh_log_view()

    def restore_logic(self):
        try:
            self.sm.restore_backup() # 还原 YAML
            if self.em: self.em.restore() # 还原 .env
            self.log_sys.write_log("♻️ 配置已全部还原至原始状态", force=True)
        except Exception as e:
            self.log_sys.write_log(f"❌ 还原失败: {e}", force=True)
        self.update_security_status()
        self.refresh_log_view()



    def update_security_status(self):
        if not self.sm or not self.vm: return
        is_p_safe = self.sm.is_hardened()
        is_v_safe = self.vm.is_isolated()
    
        if is_p_safe and is_v_safe:
            self.security_status.setText("🟢 完全保护：网关与路径均已加固")
            self.security_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        elif is_p_safe or is_v_safe:
            status_text = "🟡 部分保护：" + ("网关已锁" if is_p_safe else "路径已隔离")
            self.security_status.setText(status_text)
            self.security_status.setStyleSheet("color: #ffff00; font-weight: bold;")
        else:
            self.security_status.setText("⚠️ 风险状态：建议执行加固操作")
            self.security_status.setStyleSheet("color: #ffaa00; font-weight: bold;")
        
        # 核心：手动触发 UI 刷新，防止 QLabel 文本变了但颜色没变
        self.security_status.repaint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PetClawMain()
    window.show()
    sys.exit(app.exec())