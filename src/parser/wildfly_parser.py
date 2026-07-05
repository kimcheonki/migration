"""
Wildfly 설정파일 파서
"""
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from src.utils.xml_utils import XMLUtils


class WildflyParser:
    """Wildfly 설정파일 파서"""
    
    def __init__(self):
        pass
    
    def parse_xml(self, content: str) -> Dict:
        """Wildfly XML 설정파일 파싱"""
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
        """Wildfly properties 파일 파싱"""
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
    
    def extract_datasource_config(self, parsed: Dict) -> List[Dict]:
        """데이터소스 설정 추출"""
        if 'root' not in parsed:
            return []
        
        datasources = []
        datasource_elements = XMLUtils.find_elements(parsed['root'], 'datasource')
        
        for ds in datasource_elements:
            config = {
                'jndi_name': XMLUtils.get_attribute(ds, 'jndi-name'),
                'connection_url': None,
                'driver_class': None,
                'username': None,
                'pool_config': {}
            }
            
            # connection-url 추출
            connection_url = XMLUtils.find_element(ds, 'connection-url')
            if connection_url is not None and connection_url.text:
                config['connection_url'] = connection_url.text
            
            # driver-class 추출
            driver_class = XMLUtils.find_element(ds, 'driver-class')
            if driver_class is not None and driver_class.text:
                config['driver_class'] = driver_class.text
            
            # user-name 추출
            user_name = XMLUtils.find_element(ds, 'user-name')
            if user_name is not None and user_name.text:
                config['username'] = user_name.text
            
            # pool 설정 추출
            pool = XMLUtils.find_element(ds, 'pool')
            if pool is not None:
                config['pool_config'] = XMLUtils.get_attributes(pool)
            
            datasources.append(config)
        
        return datasources
    
    def extract_thread_pool_config(self, parsed: Dict) -> Dict:
        """스레드 풀 설정 추출"""
        if 'root' not in parsed:
            return {}
        
        thread_pool = {}
        
        # io-subsystem에서 스레드 설정 추출
        subsystems = XMLUtils.find_elements(parsed['root'], 'subsystem')
        for subsystem in subsystems:
            if 'io' in XMLUtils.get_attribute(subsystem, 'xmlns', ''):
                worker_elements = XMLUtils.find_elements(subsystem, 'worker')
                for worker in worker_elements:
                    thread_pool.update(XMLUtils.get_attributes(worker))
        
        return thread_pool
    
    def extract_ssl_config(self, parsed: Dict) -> Dict:
        """SSL 설정 추출"""
        if 'root' not in parsed:
            return {}
        
        ssl_config = {
            'enabled': False,
            'certificate_file': None,
            'certificate_key_file': None,
            'protocol': None
        }
        
        # SSL 관련 설정 추출
        subsystems = XMLUtils.find_elements(parsed['root'], 'subsystem')
        for subsystem in subsystems:
            if 'undertow' in XMLUtils.get_attribute(subsystem, 'xmlns', ''):
                ssl_elements = XMLUtils.find_elements(subsystem, 'ssl')
                if ssl_elements:
                    ssl_config['enabled'] = True
                    ssl_config.update(XMLUtils.get_attributes(ssl_elements[0]))
        
        return ssl_config
