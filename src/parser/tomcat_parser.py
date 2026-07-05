"""
Tomcat 설정파일 파서
"""
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from src.utils.xml_utils import XMLUtils


class TomcatParser:
    """Tomcat 설정파일 파서"""
    
    def __init__(self):
        pass
    
    def parse_xml(self, content: str) -> Dict:
        """Tomcat XML 설정파일 파싱"""
        root = XMLUtils.parse_xml(content)
        
        if root is None:
            return {
                'error': 'XML 파싱 실패',
                'raw_content': content
            }
        
        return {
            'root': root,
            'attributes': XMLUtils.get_attributes(root),
            'raw_content': content,
            'structure': XMLUtils.element_to_dict(root)
        }
    
    def parse_properties(self, content: str) -> Dict:
        """Tomcat properties 파일 파싱"""
        properties = {}
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                properties[key.strip()] = value.strip()
        
        return {
            'properties': properties,
            'raw_content': content
        }
    
    def parse(self, content: str, file_type: str = 'xml') -> Dict:
        """파일 타입에 따라 파싱"""
        if file_type == 'xml':
            return self.parse_xml(content)
        elif file_type == 'properties':
            return self.parse_properties(content)
        else:
            return {
                'error': f'지원하지 않는 파일 타입: {file_type}',
                'raw_content': content
            }
    
    def extract_connector_config(self, parsed: Dict) -> List[Dict]:
        """Connector 설정 추출"""
        if 'root' not in parsed:
            return []
        
        connectors = []
        connector_elements = XMLUtils.find_elements(parsed['root'], 'Connector')
        
        for connector in connector_elements:
            config = XMLUtils.get_attributes(connector)
            connectors.append(config)
        
        return connectors
    
    def extract_thread_pool_config(self, parsed: Dict) -> Dict:
        """스레드 풀 설정 추출"""
        if 'root' not in parsed:
            return {}
        
        thread_pool = {}
        executor_elements = XMLUtils.find_elements(parsed['root'], 'Executor')
        
        if executor_elements:
            executor = executor_elements[0]
            thread_pool = XMLUtils.get_attributes(executor)
        
        return thread_pool
    
    def extract_datasource_config(self, parsed: Dict) -> List[Dict]:
        """데이터소스 설정 추출"""
        if 'root' not in parsed:
            return []
        
        datasources = []
        resource_elements = XMLUtils.find_elements(parsed['root'], 'Resource')
        
        for resource in resource_elements:
            attrs = XMLUtils.get_attributes(resource)
            if attrs.get('type', '').startswith('javax.sql.'):
                datasources.append(attrs)
        
        return datasources
