"""
마이그레이션 결과 모델
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class ServerType(Enum):
    WEB = "web"
    WAS = "was"


class MigrationStatus(Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    MANUAL_REVIEW = "manual_review"


@dataclass
class ConfigChange:
    """설정 변경사항"""
    key: str
    old_value: str
    new_value: str
    change_type: str  # keep, modify, remove, add
    reason: str
    line_number: Optional[int] = None


@dataclass
class MigrationIssue:
    """마이그레이션 이슈"""
    severity: str  # critical, warning, info
    message: str
    suggestion: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class FileMigrationResult:
    """파일별 마이그레이션 결과"""
    file_path: str
    file_type: str
    original_content: str
    migrated_content: str
    status: MigrationStatus
    changes: List[ConfigChange] = field(default_factory=list)
    issues: List[MigrationIssue] = field(default_factory=list)
    applicable: bool = True


@dataclass
class MigrationSummary:
    """마이그레이션 요약"""
    server_name: str
    server_type: ServerType
    from_version: str
    to_version: str
    total_files: int
    successful_files: int
    warning_files: int
    error_files: int
    manual_review_files: int
    total_changes: int
    total_issues: int
