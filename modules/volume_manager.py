from pathlib import Path

class VolumeManager:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.compose_file = self.base_dir / "docker-compose.yml"

    def apply_isolation(self):
        """执行 YAML 路径解耦：将原始变量替换为 PetClaw 专属变量并裂变子目录"""
        if not self.compose_file.exists():
            return False

        with open(self.compose_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        modified = False
        # 匹配特征：包含官方工作空间变量和容器内目标路径
        target_sig = "OPENCLAW_WORKSPACE_DIR"
        target_path = ":/home/node/.openclaw/workspace"

        for line in lines:
            # 只有同时满足变量名和容器路径，且不是已经修改过的行
            if target_sig in line and target_path in line and "/input" not in line:
                indent = line[:line.find("- ")]
                
                # 构造裂变后的引用行
                in_line = f'{indent}- "${{PETCLAW_INPUT_DIR}}:/home/node/.openclaw/workspace/input:ro"\n'
                out_line = f'{indent}- "${{PETCLAW_OUTPUT_DIR}}:/home/node/.openclaw/workspace/output:rw"\n'
                
                new_lines.append(in_line)
                new_lines.append(out_line)
                modified = True
            else:
                new_lines.append(line)

        if modified:
            with open(self.compose_file, "w", encoding="utf-8", newline='\n') as f:
                f.writelines(new_lines)
        
        return modified

    def is_isolated(self):
        if not self.compose_file.exists(): return False
        with open(self.compose_file, "r", encoding="utf-8") as f:
            content = f.read()
        return "PETCLAW_INPUT_DIR" in content