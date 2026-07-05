"""
Wildfly 설정 변환기
"""
import re
from typing import Dict, List
from src.model.result import ConfigChange, MigrationIssue, FileMigrationResult, MigrationStatus


class WildflyConverter:
    """Wildfly 설정 변환기"""
    
    def __init__(self, from_version: str, to_version: str, rules: Dict):
        self.from_version = from_version
        self.to_version = to_version
        self.rules = rules
    
    def convert(self, parsed: Dict, file_type: str = 'xml') -> FileMigrationResult:
        """Wildfly 설정 변환"""
        changes = []
        issues = []
        applicable = True
        
        raw_content = parsed['raw_content']
        
        # 버전 키 생성
        version_key = f"{self.from_version}_to_{self.to_version}"
        
        # 마이그레이션 규칙 적용
        if 'wildfly' in self.rules and version_key in self.rules['wildfly']:
            rule_set = self.rules['wildfly'][version_key]
            
            for rule in rule_set.get('rules', []):
                pattern = rule.get('old_pattern', '')
                action = rule.get('action', '')
                
                if file_type == 'xml':
                    attributes = parsed.get('attributes', {})
                    for attr_name, attr_value in attributes.items():
                        match = re.match(pattern, f'{attr_name}="{attr_value}"')
                        if match:
                            if action == 'keep':
                                changes.append(ConfigChange(
                                    key=attr_name,
                                    old_value=attr_value,
                                    new_value=attr_value,
                                    change_type='keep',
                                    reason=rule.get('description', '')
                                ))
                elif file_type == 'properties':
                    properties = parsed.get('properties', {})
                    for prop_name, prop_value in properties.items():
                        match = re.match(pattern, f'{prop_name}={prop_value}')
                        if match:
                            if action == 'keep':
                                changes.append(ConfigChange(
                                    key=prop_name,
                                    old_value=prop_value,
                                    new_value=prop_value,
                                    change_type='keep',
                                    reason=rule.get('description', '')
                                ))
        
        # 상태 결정
        status = MigrationStatus.SUCCESS
        if any(issue.severity == 'critical' for issue in issues):
            status = MigrationStatus.ERROR
            applicable = False
        elif any(issue.severity == 'warning' for issue in issues):
            status = MigrationStatus.WARNING
        
        return FileMigrationResult(
            file_path='',
            file_type=file_type,
            original_content=raw_content,
            migrated_content=raw_content,
            status=status,
            changes=changes,
            issues=issues,
            applicable=applicable
        )
