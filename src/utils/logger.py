"""
로거 유틸리티
"""
import logging
import sys
from datetime import datetime
from pathlib import Path


class Logger:
    """로거 클래스"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """로거 설정"""
        self._logger = logging.getLogger('migration')
        self._logger.setLevel(logging.INFO)
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 포맷터
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        self._logger.addHandler(console_handler)
    
    def info(self, message: str):
        """INFO 레벨 로그"""
        self._logger.info(message)
    
    def warning(self, message: str):
        """WARNING 레벨 로그"""
        self._logger.warning(message)
    
    def error(self, message: str):
        """ERROR 레벨 로그"""
        self._logger.error(message)
    
    def debug(self, message: str):
        """DEBUG 레벨 로그"""
        self._logger.debug(message)


def get_logger() -> Logger:
    """로거 인스턴스 반환"""
    return Logger()
