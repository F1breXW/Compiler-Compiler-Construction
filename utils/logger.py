"""
日志工具类
"""

from datetime import datetime


class Logger:
    """简单的日志工具类"""
    
    @staticmethod
    def info(message: str):
        """输出信息日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [INFO] {message}")
    
    @staticmethod
    def warning(message: str):
        """输出警告日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [WARNING] {message}")
    
    @staticmethod
    def error(message: str):
        """输出错误日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [ERROR] {message}")
    
    @staticmethod
    def debug(message: str):
        """输出调试日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [DEBUG] {message}")
