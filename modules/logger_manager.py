import os
import datetime

class LoggerManager:
    def __init__(self):
        self.log_file = "petclaw_history.log"
        self.page_size = 15  # 适当增加单页容量
        self.last_message = "" # 用于日志去重

    def write_log(self, message, force=False):
        """
        记录行为。
        force=True 时强制写入，否则会过滤掉与上一条重复的内容，防止轮询日志刷屏。
        """
        if not force and message == self.last_message:
            return
            
        self.last_message = message
        timestamp = datetime.datetime.now().strftime("%H:%M:%S") # 简化时间戳，增强可读性
        log_entry = f"[{timestamp}] {message}\n"
        
        try:
            # 使用 a+ 模式确保文件不存在时自动创建，并保持 UTF-8
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            # 这里的 print 仅作为最后的兜底
            print(f"Log Write Error: {e}")

    def read_all_logs(self):
        """返回所有日志列表"""
        if not os.path.exists(self.log_file):
            return ["尚未产生操作日志"]
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                # 过滤掉可能的空行
                return [line.strip() for line in f.readlines() if line.strip()]
        except Exception:
            return ["日志读取失败"]

    def clear_logs(self):
        """清空本地文件并重置缓存"""
        try:
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
            self.last_message = ""
            return True
        except Exception:
            return False

    def get_page(self, page_index):
        all_logs = self.read_all_logs()
        if not all_logs:
            return ["等待操作中..."], 1
            
        all_logs.reverse() # 最新在前
        
        total_logs = len(all_logs)
        # 确保至少有 1 页
        total_pages = max(1, (total_logs + self.page_size - 1) // self.page_size)
        
        # 防止索引越界
        if page_index >= total_pages:
            page_index = total_pages - 1
            
        start = page_index * self.page_size
        end = start + self.page_size
        return all_logs[start:end], total_pages