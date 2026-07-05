"""
데이터소스 설정 모델
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatasourceConfig:
    """데이터소스 설정"""
    name: str
    jndi_name: Optional[str] = None
    connection_url: Optional[str] = None
    driver_class: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    max_pool_size: Optional[int] = None
    min_pool_size: Optional[int] = None
    validation_query: Optional[str] = None
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            'name': self.name,
            'jndi_name': self.jndi_name,
            'connection_url': self.connection_url,
            'driver_class': self.driver_class,
            'username': self.username,
            'max_pool_size': self.max_pool_size,
            'min_pool_size': self.min_pool_size,
            'validation_query': self.validation_query
        }
