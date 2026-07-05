"""
배포 설정 모델
"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class DeploymentConfig:
    """배포 설정"""
    name: str
    context_path: Optional[str] = None
    doc_base: Optional[str] = None
    enabled: bool = True
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            'name': self.name,
            'context_path': self.context_path,
            'doc_base': self.doc_base,
            'enabled': self.enabled
        }
