"""
SSL 설정 모델
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SSLConfig:
    """SSL 설정"""
    certificate_file: Optional[str] = None
    certificate_key_file: Optional[str] = None
    certificate_chain_file: Optional[str] = None
    protocol: Optional[str] = None
    cipher_suite: Optional[str] = None
    enabled: bool = False
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            'certificate_file': self.certificate_file,
            'certificate_key_file': self.certificate_key_file,
            'certificate_chain_file': self.certificate_chain_file,
            'protocol': self.protocol,
            'cipher_suite': self.cipher_suite,
            'enabled': self.enabled
        }
