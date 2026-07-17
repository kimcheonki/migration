"""
Tomcat 설정 변환기
"""
import re
from typing import Dict, List
from src.model.result import ConfigChange, MigrationIssue, FileMigrationResult, MigrationStatus


class TomcatConverter:
    """Tomcat 설정 변환기"""
    
    def __init__(self, from_version: str, to_version: str, rules: Dict):
        self.from_version = from_version
        self.to_version = to_version
        self.rules = rules
    
    def convert(self, parsed: Dict, file_type: str = 'xml') -> FileMigrationResult:
        """Tomcat 설정 변환"""
        changes = []
        issues = []
        applicable = True
        
        raw_content = parsed['raw_content']
        
        # 버전 키 생성
        version_key = f"{self.from_version}_to_{self.to_version}"
        
        # 마이그레이션 규칙 적용 및 실제 변환
        if 'tomcat' in self.rules and version_key in self.rules['tomcat']:
            rule_set = self.rules['tomcat'][version_key]
            
            for rule in rule_set.get('rules', []):
                pattern = rule.get('old_pattern', '')
                action = rule.get('action', '')
                new_pattern = rule.get('new_pattern', '')
                
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
                            elif action == 'modify' and new_pattern:
                                new_value = new_pattern.format(value=attr_value)
                                # XML 속성 변환
                                raw_content = raw_content.replace(
                                    f'{attr_name}="{attr_value}"',
                                    f'{attr_name}="{new_value}"'
                                )
                                changes.append(ConfigChange(
                                    key=attr_name,
                                    old_value=attr_value,
                                    new_value=new_value,
                                    change_type='modify',
                                    reason=rule.get('description', '')
                                ))
                            elif action == 'deprecated':
                                issues.append(MigrationIssue(
                                    severity='warning',
                                    message=f"속성이 deprecated됨: {attr_name}",
                                    suggestion=rule.get('replacement', ''),
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
                            elif action == 'modify' and new_pattern:
                                new_value = new_pattern.format(value=prop_value)
                                # Properties 변환
                                raw_content = raw_content.replace(
                                    f'{prop_name}={prop_value}',
                                    f'{prop_name}={new_value}'
                                )
                                changes.append(ConfigChange(
                                    key=prop_name,
                                    old_value=prop_value,
                                    new_value=new_value,
                                    change_type='modify',
                                    reason=rule.get('description', '')
                                ))
        
        # 버전별 특정 변환 로직
        migrated_content = self._apply_version_specific_transforms(raw_content, file_type, self.from_version, self.to_version)
        
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
            original_content=parsed['raw_content'],
            migrated_content=migrated_content,
            status=status,
            changes=changes,
            issues=issues,
            applicable=applicable
        )
    
    def _apply_version_specific_transforms(self, content: str, file_type: str, 
                                         from_version: str, to_version: str) -> str:
        """버전별 특정 변환 적용"""
        transformed_content = content
        
        # Tomcat 8.5 → 10.x 변환
        if from_version.startswith('8.5') and to_version.startswith('10'):
            if file_type == 'xml':
                # URIEncoding 속성이 deprecated됨
                if 'URIEncoding' in transformed_content:
                    transformed_content = transformed_content.replace(
                        'URIEncoding="UTF-8"',
                        'URIEncoding="UTF-8"  # Tomcat 10+에서는 기본값이 UTF-8'
                    )
        
        # Tomcat 10.x → 11.x 변환
        if from_version.startswith('10') and to_version.startswith('11'):
            if file_type == 'xml':
                # 추가적인 Tomcat 11 특정 변환
                pass
        
        return transformed_content
