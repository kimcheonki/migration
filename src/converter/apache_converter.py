"""
Apache 설정 변환기
"""
import re
from typing import Dict, List
from src.model.result import ConfigChange, MigrationIssue, FileMigrationResult, MigrationStatus


class ApacheConverter:
    """Apache 설정 변환기"""
    
    def __init__(self, from_version: str, to_version: str, rules: Dict):
        self.from_version = from_version
        self.to_version = to_version
        self.rules = rules
    
    def convert(self, parsed: Dict) -> FileMigrationResult:
        """Apache 설정 변환"""
        changes = []
        issues = []
        applicable = True
        
        directives = parsed['directives']
        raw_content = parsed['raw_content']
        
        # 버전 키 생성
        version_key = f"{self.from_version}_to_{self.to_version}"
        
        # 마이그레이션 규칙 적용
        if 'apache' in self.rules and version_key in self.rules['apache']:
            rule_set = self.rules['apache'][version_key]
            
            for rule in rule_set.get('rules', []):
                pattern = rule.get('old_pattern', '')
                action = rule.get('action', '')
                
                for directive_info in directives:
                    directive = directive_info['directive']
                    value = directive_info['value']
                    
                    match = re.match(pattern, value)
                    if match:
                        if action == 'keep':
                            changes.append(ConfigChange(
                                key=directive,
                                old_value=value,
                                new_value=value,
                                change_type='keep',
                                reason=rule.get('description', ''),
                                line_number=directive_info['line_number']
                            ))
                        elif action == 'check_module_exists':
                            issues.append(MigrationIssue(
                                severity='warning',
                                message=f"모듈 존재 여부 확인 필요: {directive}",
                                suggestion=rule.get('description', ''),
                                line_number=directive_info['line_number']
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
            file_type='conf',
            original_content=raw_content,
            migrated_content=raw_content,
            status=status,
            changes=changes,
            issues=issues,
            applicable=applicable
        )
    
    def apply_changes(self, original_content: str, changes: List[ConfigChange]) -> str:
        """변경사항 적용"""
        lines = original_content.split('\n')
        
        for change in changes:
            if change.line_number and change.line_number <= len(lines):
                # 실제 변환 로직 구현 필요
                pass
        
        return '\n'.join(lines)
