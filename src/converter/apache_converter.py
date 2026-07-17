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
        lines = raw_content.split('\n')
        
        # 버전 키 생성
        version_key = f"{self.from_version}_to_{self.to_version}"
        
        # 마이그레이션 규칙 적용 및 실제 변환
        if 'apache' in self.rules and version_key in self.rules['apache']:
            rule_set = self.rules['apache'][version_key]
            
            for rule in rule_set.get('rules', []):
                pattern = rule.get('old_pattern', '')
                action = rule.get('action', '')
                new_pattern = rule.get('new_pattern', '')
                
                for directive_info in directives:
                    directive = directive_info['directive']
                    value = directive_info['value']
                    line_number = directive_info['line_number']
                    
                    match = re.match(pattern, value)
                    if match:
                        if action == 'keep':
                            # 설정 유지
                            changes.append(ConfigChange(
                                key=directive,
                                old_value=value,
                                new_value=value,
                                change_type='keep',
                                reason=rule.get('description', ''),
                                line_number=line_number
                            ))
                        elif action == 'modify':
                            # 설정 수정
                            if new_pattern:
                                new_value = new_pattern.format(value=match.group(1) if match.groups() else value)
                                # 실제 라인 수정
                                if line_number <= len(lines):
                                    old_line = lines[line_number - 1]
                                    new_line = re.sub(pattern, new_value, old_line)
                                    lines[line_number - 1] = new_line
                                
                                changes.append(ConfigChange(
                                    key=directive,
                                    old_value=value,
                                    new_value=new_value,
                                    change_type='modify',
                                    reason=rule.get('description', ''),
                                    line_number=line_number
                                ))
                        elif action == 'check_module_exists':
                            issues.append(MigrationIssue(
                                severity='warning',
                                message=f"모듈 존재 여부 확인 필요: {directive}",
                                suggestion=rule.get('description', ''),
                                line_number=line_number
                            ))
        
        # 버전별 특정 변환 로직
        migrated_lines = self._apply_version_specific_transforms(lines, self.from_version, self.to_version)
        
        migrated_content = '\n'.join(migrated_lines)
        
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
            migrated_content=migrated_content,
            status=status,
            changes=changes,
            issues=issues,
            applicable=applicable
        )
    
    def _apply_version_specific_transforms(self, lines: List[str], from_version: str, to_version: str) -> List[str]:
        """버전별 특정 변환 적용"""
        transformed_lines = lines.copy()
        
        # Apache 2.4.x 버전 간 일반적인 변환
        if from_version.startswith('2.4') and to_version.startswith('2.4'):
            # KeepAlive 설정 최적화
            for i, line in enumerate(transformed_lines):
                if line.strip().startswith('KeepAliveTimeout'):
                    # 최신 버전에서는 더 작은 값이 권장될 수 있음
                    match = re.search(r'KeepAliveTimeout\s+(\d+)', line)
                    if match:
                        timeout = int(match.group(1))
                        if timeout > 10:
                            transformed_lines[i] = re.sub(
                                r'KeepAliveTimeout\s+\d+',
                                f'KeepAliveTimeout 5  # 자동 조정: {timeout} -> 5',
                                line
                            )
        
        return transformed_lines
    
    def apply_changes(self, original_content: str, changes: List[ConfigChange]) -> str:
        """변경사항 적용"""
        lines = original_content.split('\n')
        
        for change in changes:
            if change.line_number and change.line_number <= len(lines):
                # 실제 변환 로직 구현 필요
                pass
        
        return '\n'.join(lines)
