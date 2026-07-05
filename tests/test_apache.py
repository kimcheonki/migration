"""
Apache 파서 및 컨버터 테스트
"""
import unittest
from src.parser.apache_parser import ApacheParser
from src.converter.apache_converter import ApacheConverter
from src.model.result import MigrationStatus


class TestApacheParser(unittest.TestCase):
    """Apache 파서 테스트"""
    
    def setUp(self):
        self.parser = ApacheParser()
    
    def test_parse_basic_config(self):
        """기본 설정 파싱 테스트"""
        content = """
ServerName localhost
DocumentRoot "/var/www/html"
Listen 80
"""
        result = self.parser.parse(content)
        
        self.assertEqual(len(result['directives']), 3)
        self.assertEqual(result['directives'][0]['directive'], 'ServerName')
        self.assertEqual(result['directives'][1]['directive'], 'DocumentRoot')
        self.assertEqual(result['directives'][2]['directive'], 'Listen')
    
    def test_parse_with_comments(self):
        """주석 포함 파싱 테스트"""
        content = """
# This is a comment
ServerName localhost
# Another comment
Listen 80
"""
        result = self.parser.parse(content)
        
        self.assertEqual(len(result['directives']), 2)
    
    def test_extract_directive(self):
        """특정 디렉티브 추출 테스트"""
        content = """
Listen 80
Listen 443
ServerName localhost
"""
        result = self.parser.parse(content)
        listen_directives = self.parser.extract_directive(result, 'Listen')
        
        self.assertEqual(len(listen_directives), 2)
    
    def test_extract_ssl_config(self):
        """SSL 설정 추출 테스트"""
        content = """
SSLEngine on
SSLCertificateFile "/etc/ssl/cert.pem"
SSLCertificateKeyFile "/etc/ssl/key.pem"
"""
        result = self.parser.parse(content)
        ssl_config = self.parser.extract_ssl_config(result)
        
        self.assertTrue(ssl_config['enabled'])
        self.assertEqual(ssl_config['certificate_file'], "/etc/ssl/cert.pem")
        self.assertEqual(ssl_config['certificate_key_file'], "/etc/ssl/key.pem")


class TestApacheConverter(unittest.TestCase):
    """Apache 컨버터 테스트"""
    
    def setUp(self):
        self.converter = ApacheConverter("2.4.39", "2.4.57", {})
    
    def test_convert_basic(self):
        """기본 변환 테스트"""
        parsed = {
            'directives': [
                {'directive': 'ServerName', 'value': 'localhost', 'line_number': 1}
            ],
            'raw_content': 'ServerName localhost'
        }
        
        result = self.converter.convert(parsed)
        
        self.assertEqual(result.status, MigrationStatus.SUCCESS)
        self.assertTrue(result.applicable)
    
    def test_convert_with_rules(self):
        """규칙 적용 변환 테스트"""
        rules = {
            'apache': {
                '2.4.39_to_2.4.57': {
                    'rules': [
                        {
                            'old_pattern': 'KeepAliveTimeout\\s+(\\d+)',
                            'action': 'keep',
                            'description': 'KeepAliveTimeout 설정 유지'
                        }
                    ]
                }
            }
        }
        
        converter = ApacheConverter("2.4.39", "2.4.57", rules)
        parsed = {
            'directives': [
                {'directive': 'KeepAliveTimeout', 'value': '5', 'line_number': 1}
            ],
            'raw_content': 'KeepAliveTimeout 5'
        }
        
        result = converter.convert(parsed)
        
        self.assertEqual(len(result.changes), 1)
        self.assertEqual(result.changes[0].key, 'KeepAliveTimeout')


if __name__ == '__main__':
    unittest.main()
