import os
import shutil
from pathlib import Path

class EnvManager:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.env_file = self.base_dir / ".env"
        self.env_bak = self.base_dir / ".env.bak"

    def ensure_backup(self):
        """独立备份 .env"""
        if self.env_file.exists() and not self.env_bak.exists():
            shutil.copy2(self.env_file, self.env_bak)
            return True
        return False

    def inject_paths(self, input_path: str, output_path: str):
        """将物理路径作为变量注入 .env"""
        if not self.env_file.exists():
            return False, "未找到 .env 文件，请先执行 Onboard"

        self.ensure_backup()
        
        with open(self.env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # 过滤掉旧的 PetClaw 变量，防止重复追加
        new_lines = [line for line in lines if "PETCLAW_" not in line]

        # 追加新的环境变量定义
        new_lines.append("\n# --- PetClaw Isolated Volumes ---\n")
        new_lines.append(f"PETCLAW_INPUT_DIR=\"{input_path}\"\n")
        new_lines.append(f"PETCLAW_OUTPUT_DIR=\"{output_path}\"\n")

        with open(self.env_file, "w", encoding="utf-8", newline='\n') as f:
            f.writelines(new_lines)
        return True, "环境变量已写入 .env"

    def restore(self):
        if self.env_bak.exists():
            shutil.copy2(self.env_bak, self.env_file)
            return True
        return False