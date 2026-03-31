import shutil
from pathlib import Path


class SecurityManager:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.compose_file = self.base_dir / "docker-compose.yml"
        self.backup_file = self.base_dir / "docker-compose.backup.yml"

    def ensure_backup(self):
        if not self.compose_file.exists():
            raise FileNotFoundError("docker-compose.yml 不存在")

        if not self.backup_file.exists():
            shutil.copy2(self.compose_file, self.backup_file)
            return True
        return False

    def harden_gateway(self):
        if not self.compose_file.exists():
            raise FileNotFoundError("docker-compose.yml 不存在")

        with open(self.compose_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        modified = False

        for line in lines:
            # 1. 识别特征：这一行是列表项 (-)，且包含官方的端口变量或默认端口
            if ' - "' in line and (":18789" in line or ":18790" in line):
                # 2. 检查是否已经加固过，避免重复叠加
                if "127.0.0.1:" not in line:
                    # 3. 核心替换逻辑：
                    # 寻找第一个双引号 '"'，并在其后插入 '127.0.0.1:'
                    # 这样无论中间是变量还是数字，都能成功锁定本地
                    line = line.replace('"', '"127.0.0.1:', 1) 
                    modified = True

            new_lines.append(line)

        if modified:
            with open(self.compose_file, "w", encoding="utf-8", newline='\n') as f:
                f.writelines(new_lines)
        
        return modified

    def restore_backup(self):
        if not self.backup_file.exists():
            raise FileNotFoundError("备份文件不存在")

        shutil.copy2(self.backup_file, self.compose_file)
        return True

    def is_hardened(self):
        if not self.compose_file.exists():
            return False

        try:
            with open(self.compose_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 只要检测到引号内紧跟 127.0.0.1，且包含关键变量或端口
            # 这种匹配方式比死等特定字符串更健壮
            return '"127.0.0.1:${OPENCLAW_GATEWAY_PORT' in content or '"127.0.0.1:18789' in content
        except:
            return False