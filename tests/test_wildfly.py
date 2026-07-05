"""
Wildfly 파서 및 컨버터 테스트
"""
import unittest
from src.parser.wildfly_parser import WildflyParser
from src.converter.wildfly_converter import WildflyConverter
from src.model.result import MigrationStatus


class TestWildflyParser(unittest.TestCase):
    """Wildfly 파서 테스트"""
    
    def setUp(self):
        self.parser = WildflyParser()
    
    def test_parse_xml(self):
        """XML 파싱 테스트"""
        content = """<?xml version="1.0" encoding="UTF-8"?>
<server xmlns="urn:jboss:domain:27.0">
    <datasources>
        <datasource jndi-name="java:/MyDS">
            <connection-url>jdbc:mysql://localhost:3306/mydb</connection-url>
            <driver-class>com.mysql.jdbc.Driver</driver-class>
        </datasource>
    </datasources>
</server>"""
        
        result = self.parser.parse_xml(content)
        
        self.assertIn('root', result)
    
    def test_parse_properties(self):
        """Properties 파싱 테스트"""
        content = """
# Database configuration
db.url=jdbc:mysql://localhost:3306/mydb
db.username=root
"""
        
        result = self.parser.parse_properties(content)
        
        self.assertEqual(result['properties']['db.url'], 'jdbc:mysql://localhost:3306/mydb')
        self.assertEqual(result['properties']['db.username'], 'root')
    
    def test_extract_datasource_config(self):
        """데이터소스 설정 추출 테스트"""
        content = """<?xml version="1.0" encoding="UTF-8"?>
<server xmlns="urn:jboss:domain:27.0">
    <datasources>
        <datasource jndi-name="java:/MyDS">
            <connection-url>jdbc:mysql://localhost:3306/mydb</connection-url>
            <driver-class>com.mysql.jdbc.Driver</driver-class>
        </datasource>
    </datasources>
</server>"""
        
        result = self.parser.parse_xml(content)
        datasources = self.parser.extract_datasource_config(result)
        
        self.assertEqual(len(datasources), 1)
        self.assertEqual(datasources[0]['jndi_name'], 'java:/MyDS')
        self.assertEqual(datasources[0]['connection_url'], 'jdbc:mysql://localhost:3306/mydb')


class TestWildflyConverter(unittest.TestCase):
    """Wildfly 컨버터 테스트"""
    
    def setUp(self):
        self.converter = WildflyConverter("13", "27", {})
    
    def test_convert_xml(self):
        """XML 변환 테스트"""
        parsed = {
            'attributes': {'enabled': 'true'},
            'raw_content': '<ssl enabled="true"/>'
        }
        
        result = self.converter.convert(parsed, 'xml')
        
        self.assertEqual(result.status, MigrationStatus.SUCCESS)
        self.assertTrue(result.applicable)
    
    def test_convert_properties(self):
        """Properties 변환 테스트"""
        parsed = {
            'properties': {'server.port': '8080'},
            'raw_content': 'server.port=8080'
        }
        
        result = self.converter.convert(parsed, 'properties')
        
        self.assertEqual(result.status, MigrationStatus.SUCCESS)
        self.assertTrue(result.applicable)


if __name__ == '__main__':
    unittest.main()
