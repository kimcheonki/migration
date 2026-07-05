"""
파일 유틸리티
"""
import os
from pathlib import Path
from typing import List, Optional


class FileUtils:
    """파일 유틸리티 클래스"""
    
    @staticmethod
    def read_file(file_path: str, encoding: str = 'utf-8') -> str:
        """파일 읽기"""
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    
    @staticmethod
    def write_file(file_path: str, content: str, encoding: str = 'utf-8'):
        """파일 쓰기"""
        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """파일 확장자 반환"""
        return Path(file_path).suffix.lower()
    
    @staticmethod
    def get_file_type(file_path: str) -> str:
        """파일 타입 반환"""
        ext = FileUtils.get_file_extension(file_path)
        
        type_map = {
            '.conf': 'conf',
            '.xml': 'xml',
            '.properties': 'properties',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.htaccess': 'conf'
        }
        
        return type_map.get(ext, 'unknown')
    
    @staticmethod
    def find_config_files(directory: str, extensions: List[str], 
                         recursive: bool = True) -> List[str]:
        """디렉토리 내 설정파일 찾기"""
        config_files = []
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        config_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    if any(file.endswith(ext) for ext in extensions):
                        config_files.append(file_path)
        
        return config_files
    
    @staticmethod
    def ensure_directory(directory: str):
        """디렉토리 생성"""
        os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def get_file_name(file_path: str) -> str:
        """파일명 반환"""
        return os.path.basename(file_path)
