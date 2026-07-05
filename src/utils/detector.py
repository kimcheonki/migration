"""
설정파일 자동 감지 유틸리티
"""
import re
from typing import Optional, Tuple
from src.utils.file_utils import FileUtils


class ConfigFileDetector:
    """설정파일 자동 감지 클래스"""
    
    # Apache 특정 패턴
    APACHE_PATTERNS = [
        r'ServerRoot\s+',
        r'ServerName\s+',
        r'DocumentRoot\s+',
        r'Listen\s+\d+',
        r'LoadModule\s+\w+_module',
        r'<Directory\s+',
        r'VirtualHost'
    ]
    
    # Tomcat 특정 패턴
    TOMCAT_PATTERNS = [
        r'<Server\s+',
        r'<Service\s+',
        r'<Connector\s+',
        r'<Host\s+',
        r'<Context\s+',
        r'catalina',
        r'org\.apache\.catalina'
    ]
    
    # Wildfly 특정 패턴
    WILDFLY_PATTERNS = [
        r'<server\s+xmlns="urn:jboss:domain:',
        r'<subsystem\s+xmlns="urn:jboss:domain:',
        r'datasource\s+jndi-name',
        r'urn:jboss:domain',
        r'org\.jboss\.as'
    ]
    
    @staticmethod
    def detect_server(file_path: str, content: str = None) -> Optional[str]:
        """파일에서 서버 타입 자동 감지"""
        if content is None:
            content = FileUtils.read_file(file_path)
        
        # 파일 확장자 확인
        ext = FileUtils.get_file_extension(file_path)
        
        # 확장자 기반 초기 추정
        if ext == '.conf':
            # .conf는 주로 Apache
            if ConfigFileDetector._check_patterns(content, ConfigFileDetector.APACHE_PATTERNS):
                return 'apache'
        elif ext in ['.xml']:
            # XML은 Tomcat 또는 Wildfly
            if ConfigFileDetector._check_patterns(content, ConfigFileDetector.TOMCAT_PATTERNS):
                return 'tomcat'
            elif ConfigFileDetector._check_patterns(content, ConfigFileDetector.WILDFLY_PATTERNS):
                return 'wildfly'
        elif ext in ['.properties']:
            # properties는 Tomcat 또는 Wildfly
            # 내용으로 구분 필요
            if 'catalina' in content.lower() or 'tomcat' in content.lower():
                return 'tomcat'
            elif 'jboss' in content.lower() or 'wildfly' in content.lower():
                return 'wildfly'
        
        # 패턴 기반 감지 (확장자와 무관하게)
        if ConfigFileDetector._check_patterns(content, ConfigFileDetector.APACHE_PATTERNS):
            return 'apache'
        elif ConfigFileDetector._check_patterns(content, ConfigFileDetector.TOMCAT_PATTERNS):
            return 'tomcat'
        elif ConfigFileDetector._check_patterns(content, ConfigFileDetector.WILDFLY_PATTERNS):
            return 'wildfly'
        
        return None
    
    @staticmethod
    def _check_patterns(content: str, patterns: list) -> bool:
        """패턴 확인"""
        content_lower = content.lower()
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def detect_version(file_path: str, content: str = None) -> Optional[str]:
        """버전 감지 (파일명이나 내용에서)"""
        if content is None:
            content = FileUtils.read_file(file_path)
        
        # 파일명에서 버전 추출 시도
        filename = FileUtils.get_file_name(file_path).lower()
        
        # Apache 버전 패턴
        apache_version_match = re.search(r'apache[_-]?(\d+\.\d+)', filename)
        if apache_version_match:
            return apache_version_match.group(1)
        
        # Tomcat 버전 패턴
        tomcat_version_match = re.search(r'tomcat[_-]?(\d+\.\d+)', filename)
        if tomcat_version_match:
            return tomcat_version_match.group(1)
        
        # Wildfly 버전 패턴
        wildfly_version_match = re.search(r'wildfly[_-]?(\d+)', filename)
        if wildfly_version_match:
            return wildfly_version_match.group(1)
        
        # 내용에서 버전 추출 시도 (XML에서)
        if '<?xml' in content:
            # Tomcat server.xml에서 버전 추출
            version_match = re.search(r'version="(\d+\.\d+)"', content)
            if version_match:
                return version_match.group(1)
        
        return None
    
    @staticmethod
    def get_file_info(file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """파일 정보 반환 (서버 타입, 버전)"""
        content = FileUtils.read_file(file_path)
        server_type = ConfigFileDetector.detect_server(file_path, content)
        version = ConfigFileDetector.detect_version(file_path, content)
        
        return server_type, version
