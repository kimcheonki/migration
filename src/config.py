"""
설정 관리
"""
import yaml
import os
from typing import Dict, Optional
from src.utils.logger import get_logger


class Config:
    """설정 클래스"""
    
    def __init__(self, rules_dir: str = 'src/rules'):
        self.rules_dir = rules_dir
        self.logger = get_logger()
        self._rules_cache = {}
    
    def load_rules(self, server_name: str, version: str) -> Dict:
        """서버별 마이그레이션 규칙 로드"""
        # 버전에서 숫자만 추출
        version = ''.join(c for c in version if c.isdigit())
        
        cache_key = f"{server_name}_{version}"
        
        if cache_key in self._rules_cache:
            return self._rules_cache[cache_key]
        
        rule_file = os.path.join(self.rules_dir, f"{server_name}{version}.yaml")
        
        if not os.path.exists(rule_file):
            self.logger.warning(f"규칙 파일을 찾을 수 없습니다: {rule_file}")
            return {}
        
        try:
            with open(rule_file, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
                self._rules_cache[cache_key] = rules
                return rules
        except yaml.YAMLError as e:
            self.logger.error(f"규칙 파일 파싱 오류: {e}")
            return {}
    
    def get_migration_rules(self, server_name: str, from_version: str, 
                           to_version: str) -> Dict:
        """마이그레이션 규칙 가져오기"""
        from_rules = self.load_rules(server_name, from_version)
        to_rules = self.load_rules(server_name, to_version)
        
        return {
            'from': from_rules,
            'to': to_rules
        }
