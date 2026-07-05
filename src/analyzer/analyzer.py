"""
설정 분석기
"""
from typing import Dict, List
from src.model.result import FileMigrationResult, MigrationSummary, MigrationStatus, ServerType


class ConfigAnalyzer:
    """설정 분석기"""
    
    def __init__(self, server_name: str, server_type: ServerType):
        self.server_name = server_name
        self.server_type = server_type
    
    def analyze_results(self, results: List[FileMigrationResult], 
                       from_version: str, to_version: str) -> MigrationSummary:
        """마이그레이션 결과 분석"""
        total_files = len(results)
        successful_files = 0
        warning_files = 0
        error_files = 0
        manual_review_files = 0
        total_changes = 0
        total_issues = 0
        
        for result in results:
            if result.status == MigrationStatus.SUCCESS:
                successful_files += 1
            elif result.status == MigrationStatus.WARNING:
                warning_files += 1
            elif result.status == MigrationStatus.ERROR:
                error_files += 1
            elif result.status == MigrationStatus.MANUAL_REVIEW:
                manual_review_files += 1
            
            total_changes += len(result.changes)
            total_issues += len(result.issues)
        
        return MigrationSummary(
            server_name=self.server_name,
            server_type=self.server_type,
            from_version=from_version,
            to_version=to_version,
            total_files=total_files,
            successful_files=successful_files,
            warning_files=warning_files,
            error_files=error_files,
            manual_review_files=manual_review_files,
            total_changes=total_changes,
            total_issues=total_issues
        )
    
    def check_compatibility(self, result: FileMigrationResult) -> bool:
        """호환성 검사"""
        return result.applicable
    
    def identify_critical_issues(self, results: List[FileMigrationResult]) -> List[Dict]:
        """치명적 이슈 식별"""
        critical_issues = []
        
        for result in results:
            for issue in result.issues:
                if issue.severity == 'critical':
                    critical_issues.append({
                        'file_path': result.file_path,
                        'issue': issue
                    })
        
        return critical_issues
