"""
Apache 설정파일 파서
"""
import re
from typing import Dict, List, Optional
from src.utils.xml_utils import XMLUtils


class ApacheParser:
    """Apache 설정파일 파서"""
    
    def __init__(self):
        self.directives = []
    
    def parse(self, content: str) -> Dict:
        """Apache 설정파일 파싱"""
        lines = content.split('\n')
        directives = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # 주석 및 빈 라인 무시
            if not line or line.startswith('#'):
                continue
            
            # 기본 디렉티브 파싱
            if ' ' in line:
                parts = line.split(None, 1)
                directive = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ""
                
                directives.append({
                    'line_number': line_num,
                    'directive': directive,
                    'value': value,
                    'raw_line': line
                })
        
        return {
            'directives': directives,
            'raw_content': content
        }
    
    def extract_directive(self, parsed: Dict, directive_name: str) -> List[Dict]:
        """특정 디렉티브 추출"""
        return [d for d in parsed['directives'] if d['directive'] == directive_name]
    
    def extract_ssl_config(self, parsed: Dict) -> Dict:
        """SSL 설정 추출"""
        ssl_config = {
            'certificate_file': None,
            'certificate_key_file': None,
            'certificate_chain_file': None,
            'protocol': None,
            'enabled': False
        }
        
        ssl_directives = self.extract_directive(parsed, 'SSLEngine')
        if ssl_directives and ssl_directives[0]['value'].lower() == 'on':
            ssl_config['enabled'] = True
        
        cert_file = self.extract_directive(parsed, 'SSLCertificateFile')
        if cert_file:
            ssl_config['certificate_file'] = cert_file[0]['value']
        
        key_file = self.extract_directive(parsed, 'SSLCertificateKeyFile')
        if key_file:
            ssl_config['certificate_key_file'] = key_file[0]['value']
        
        chain_file = self.extract_directive(parsed, 'SSLCertificateChainFile')
        if chain_file:
            ssl_config['certificate_chain_file'] = chain_file[0]['value']
        
        protocol = self.extract_directive(parsed, 'SSLProtocol')
        if protocol:
            ssl_config['protocol'] = protocol[0]['value']
        
        return ssl_config
    
    def extract_worker_config(self, parsed: Dict) -> Dict:
        """Worker 설정 추출"""
        worker_config = {
            'max_request_workers': None,
            'threads_per_child': None,
            'server_limit': None
        }
        
        for directive in parsed['directives']:
            if directive['directive'] == 'MaxRequestWorkers':
                worker_config['max_request_workers'] = directive['value']
            elif directive['directive'] == 'ThreadsPerChild':
                worker_config['threads_per_child'] = directive['value']
            elif directive['directive'] == 'ServerLimit':
                worker_config['server_limit'] = directive['value']
        
        return worker_config
