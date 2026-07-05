"""
Tomcat 파서 및 컨버터 테스트
"""
import unittest
from src.parser.tomcat_parser import TomcatParser
from src.converter.tomcat_converter import TomcatConverter
from src.model.result import MigrationStatus


class TestTomcatParser(unittest.TestCase):
    """Tomcat 파서 테스트"""
    
    def setUp(self):
        self.parser = TomcatParser()
    
    def test_parse_xml(self):
        """XML 파싱 테스트"""
        content = """<?xml version="1.0" encoding="UTF-8"?>
<Server port="8005" shutdown="SHUTDOWN">
    <Service name="Catalina">
        <Connector port="8080" protocol="HTTP/1.1"/>
    </Service>
</Server>"""
        
        result = self.parser.parse_xml(content)
        
        self.assertIn('root', result)
        self.assertEqual(result['attributes']['port'], '8005')
    
    def test_parse_properties(self):
        """Properties 파싱 테스트"""
        content = """
# This is a comment
server.port=8080
server.host=localhost
"""
        
        result = self.parser.parse_properties(content)
        
        self.assertEqual(result['properties']['server.port'], '8080')
        self.assertEqual(result['properties']['server.host'], 'localhost')
    
    def test_extract_connector_config(self):
        """Connector 설정 추출 테스트"""
        content = """<?xml version="1.0" encoding="UTF-8"?>
<Server>
    <Service>
        <Connector port="8080" protocol="HTTP/1.1" maxThreads="200"/>
    </Service>
</Server>"""
        
        result = self.parser.parse_xml(content)
        connectors = self.parser.extract_connector_config(result)
        
        self.assertEqual(len(connectors), 1)
        self.assertEqual(connectors[0]['port'], '8080')
        self.assertEqual(connectors[0]['maxThreads'], '200')


class TestTomcatConverter(unittest.TestCase):
    """Tomcat 컨버터 테스트"""
    
    def setUp(self):
        self.converter = TomcatConverter("8.5", "10.1", {})
    
    def test_convert_xml(self):
        """XML 변환 테스트"""
        parsed = {
            'attributes': {'port': '8080', 'maxThreads': '200'},
            'raw_content': '<Connector port="8080" maxThreads="200"/>'
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
