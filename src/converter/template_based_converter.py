"""
템플릿 기반 변환 모듈
TO-BE 샘플 템플릿을 기반으로 설정 변환 수행
"""
import json
import re
from typing import Dict, Any, List
from pathlib import Path


class TemplateBasedConverter:
    """템플릿 기반 변환 클래스"""
    
    def __init__(self, keywords_file: str, template_file: str):
        """
        초기화
        
        Args:
            keywords_file: 키워드 JSON 파일 경로
            template_file: TO-BE 샘플 템플릿 파일 경로
        """
        self.keywords = self._load_keywords(keywords_file)
        self.template = self._load_template(template_file)
    
    def _load_keywords(self, keywords_file: str) -> Dict[str, Any]:
        """키워드 JSON 파일 로드"""
        try:
            with open(keywords_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"키워드 파일을 찾을 수 없습니다: {keywords_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"키워드 파일 JSON 파싱 오류: {e}")
    
    def _load_template(self, template_file: str) -> str:
        """템플릿 파일 로드"""
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {template_file}")
    
    def convert(self, as_is_content: str, comparison_result: Dict[str, Any] = None) -> str:
        """
        AS-IS 내용을 TO-BE 템플릿 기반으로 변환
        
        Args:
            as_is_content: AS-IS 설정 파일 내용
            comparison_result: 비교 결과 (선택사항)
            
        Returns:
            변환된 TO-BE 형식 내용
        """
        # 템플릿 복사
        converted_content = self.template
        
        # 키워드별로 변환 수행
        for keyword_name, keyword_config in self.keywords.get('keywords', {}).items():
            converted_content = self._convert_keyword(
                keyword_name,
                keyword_config,
                as_is_content,
                converted_content
            )
        
        return converted_content
    
    def _convert_keyword(self, keyword_name: str, keyword_config: Dict[str, Any],
                        as_is_content: str, template_content: str) -> str:
        """
        특정 키워드 변환
        
        Args:
            keyword_name: 키워드 이름
            keyword_config: 키워드 설정
            as_is_content: AS-IS 내용
            template_content: 템플릿 내용
            
        Returns:
            변환된 템플릿 내용
        """
        server = self.keywords.get('server', '')
        
        if server == 'wildfly':
            return self._convert_wildfly_keyword(keyword_name, keyword_config, as_is_content, template_content)
        elif server == 'apache':
            return self._convert_apache_keyword(keyword_name, keyword_config, as_is_content, template_content)
        elif server == 'tomcat':
            return self._convert_tomcat_keyword(keyword_name, keyword_config, as_is_content, template_content)
        
        return template_content
    
    def _convert_wildfly_keyword(self, keyword_name: str, keyword_config: Dict[str, Any],
                                as_is_content: str, template_content: str) -> str:
        """Wildfly 키워드 변환"""
        xpath = keyword_config.get('xpath', '')
        
        # AS-IS에서 키워드 추출
        as_is_values = self._extract_wildfly_values(keyword_name, keyword_config, as_is_content)
        
        if not as_is_values:
            return template_content
        
        # 키워드별 변환 로직
        if keyword_name == 'datasource':
            return self._convert_datasource(as_is_values, template_content)
        elif keyword_name == 'driver':
            return self._convert_driver(as_is_values, template_content)
        elif keyword_name == 'interface':
            return self._convert_interface(as_is_values, template_content)
        elif keyword_name == 'socket-binding':
            return self._convert_socket_binding(as_is_values, template_content)
        elif keyword_name == 'logging':
            return self._convert_logging(as_is_values, template_content)
        elif keyword_name == 'system-property':
            return self._convert_system_property(as_is_values, template_content)
        
        return template_content
    
    def _extract_wildfly_values(self, keyword_name: str, keyword_config: Dict[str, Any],
                               content: str) -> List[str]:
        """Wildfly 값 추출"""
        xpath = keyword_config.get('xpath', '')
        pattern = self._xpath_to_regex(xpath)
        return re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    
    def _convert_datasource(self, as_is_values: List[str], template_content: str) -> str:
        """Datasource 변환"""
        for datasource in as_is_values:
            # ExampleDS 제외
            if 'ExampleDS' in datasource:
                continue
            
            # Wildfly 38 형식으로 변환
            datasource = self._transform_datasource_to_wildfly38(datasource)
            
            # 템플릿에 병합
            datasources_section = re.search(r'<datasources>(.*?)</datasources>', template_content, re.DOTALL)
            if datasources_section:
                old_datasources = datasources_section.group(0)
                new_datasources = old_datasources
                
                drivers_pos = new_datasources.find('<drivers>')
                if drivers_pos > 0:
                    new_datasources = new_datasources[:drivers_pos] + datasource + '\n' + new_datasources[drivers_pos:]
                
                template_content = template_content.replace(old_datasources, new_datasources)
        
        return template_content
    
    def _transform_datasource_to_wildfly38(self, datasource: str) -> str:
        """Datasource를 Wildfly 38 형식으로 변환"""
        # driver-class 제거
        datasource = re.sub(r'\s*<driver-class>[^<]*</driver-class>\s*', '\n                    ', datasource)
        
        # security 구문 변환
        security_pattern = r'<security>\s*<user-name>([^<]*)</user-name>\s*<password>([^<]*)</password>\s*</security>'
        security_match = re.search(security_pattern, datasource, re.DOTALL)
        if security_match:
            username = security_match.group(1)
            password = security_match.group(2)
            new_security = f'<security user-name="{username}">\n                        <credential-reference clear-text="{password}"/>\n                    </security>'
            datasource = re.sub(security_pattern, new_security, datasource, flags=re.DOTALL)
        
        return datasource
    
    def _convert_driver(self, as_is_values: List[str], template_content: str) -> str:
        """Driver 변환"""
        for driver in as_is_values:
            # h2 driver 제외
            if 'h2' in driver.lower():
                continue
            
            # driver-class 제거
            driver = re.sub(r'<driver-class>[^<]*</driver-class>', '', driver)
            
            # 템플릿에 병합
            drivers_section = re.search(r'<drivers>(.*?)</drivers>', template_content, re.DOTALL)
            if drivers_section:
                old_drivers = drivers_section.group(0)
                new_drivers = old_drivers.replace(
                    '</drivers>',
                    driver + '\n                </drivers>'
                )
                template_content = template_content.replace(old_drivers, new_drivers)
        
        return template_content
    
    def _convert_interface(self, as_is_values: List[str], template_content: str) -> str:
        """Interface 변환"""
        for interface in as_is_values:
            # management, public interface 제외 이미 템플릿에 있음
            if 'management' in interface or 'public' in interface:
                continue
            
            # 템플릿에 병합
            interfaces_section = re.search(r'<interfaces>(.*?)</interfaces>', template_content, re.DOTALL)
            if interfaces_section:
                old_interfaces = interfaces_section.group(0)
                new_interfaces = old_interfaces.replace(
                    '</interfaces>',
                    interface + '\n    </interfaces>'
                )
                template_content = template_content.replace(old_interfaces, new_interfaces)
        
        return template_content
    
    def _convert_socket_binding(self, as_is_values: List[str], template_content: str) -> str:
        """Socket binding 변환"""
        for binding in as_is_values:
            # 기본 binding 제외
            if any(x in binding for x in ['ajp', 'http', 'https', 'management-http', 'management-https']):
                continue
            
            # 템플릿에 병합
            socket_binding_group = re.search(r'<socket-binding-group[^>]*>(.*?)</socket-binding-group>', template_content, re.DOTALL)
            if socket_binding_group:
                old_group = socket_binding_group.group(0)
                new_group = old_group.replace(
                    '</socket-binding-group>',
                    binding + '\n    </socket-binding-group>'
                )
                template_content = template_content.replace(old_group, new_group)
        
        return template_content
    
    def _convert_logging(self, as_is_values: List[str], template_content: str) -> str:
        """Logging 변환"""
        for logger in as_is_values:
            # 기본 logger 제외
            if any(x in logger for x in ['com.arjuna', 'com.networknt', 'io.jaegertracing', 'org.jboss.as.config', 'sun.rmi']):
                continue
            
            # 템플릿에 병합
            logging_section = re.search(r'<subsystem xmlns="urn:jboss:domain:logging:8\.0">(.*?)</subsystem>', template_content, re.DOTALL)
            if logging_section:
                old_logging = logging_section.group(0)
                new_logging = old_logging
                
                root_logger_pos = new_logging.find('<root-logger>')
                if root_logger_pos > 0:
                    new_logging = new_logging[:root_logger_pos] + logger + '\n' + new_logging[root_logger_pos:]
                
                template_content = template_content.replace(old_logging, new_logging)
        
        return template_content
    
    def _convert_system_property(self, as_is_values: List[str], template_content: str) -> str:
        """System property 변환"""
        for prop in as_is_values:
            # 템플릿에 병합
            server_tag_pos = template_content.find('<server')
            if server_tag_pos > 0:
                server_end_pos = template_content.find('>', server_tag_pos) + 1
                
                # system-properties 섹션이 있는지 확인
                if '<system-properties>' not in template_content:
                    system_props_section = '\n    <system-properties>\n' + prop + '\n    </system-properties>'
                    template_content = template_content[:server_end_pos] + system_props_section + template_content[server_end_pos:]
                else:
                    # 기존 system-properties 섹션에 추가
                    template_content = template_content.replace(
                        '</system-properties>',
                        prop + '\n    </system-properties>'
                    )
        
        return template_content
    
    def _convert_apache_keyword(self, keyword_name: str, keyword_config: Dict[str, Any],
                               as_is_content: str, template_content: str) -> str:
        """Apache 키워드 변환"""
        directives = keyword_config.get('directives', [])
        
        for directive in directives:
            # AS-IS에서 디렉티브 추출
            pattern = rf'{directive}\s+(.+)'
            matches = re.findall(pattern, as_is_content, re.IGNORECASE)
            
            for match in matches:
                directive_line = f'{directive} {match}'
                
                # 템플릿에 병합
                if keyword_name == 'virtualhost':
                    template_content = self._merge_apache_virtualhost(directive_line, template_content)
                elif keyword_name == 'ssl':
                    template_content = self._merge_apache_ssl(directive_line, template_content)
                elif keyword_name == 'proxy':
                    template_content = self._merge_apache_proxy(directive_line, template_content)
        
        return template_content
    
    def _merge_apache_virtualhost(self, directive_line: str, template_content: str) -> str:
        """Apache VirtualHost 병합"""
        # 간단한 구현: 템플릿 끝에 추가
        return template_content + '\n' + directive_line
    
    def _merge_apache_ssl(self, directive_line: str, template_content: str) -> str:
        """Apache SSL 병합"""
        return template_content + '\n' + directive_line
    
    def _merge_apache_proxy(self, directive_line: str, template_content: str) -> str:
        """Apache Proxy 병합"""
        return template_content + '\n' + directive_line
    
    def _convert_tomcat_keyword(self, keyword_name: str, keyword_config: Dict[str, Any],
                               as_is_content: str, template_content: str) -> str:
        """Tomcat 키워드 변환"""
        elements = keyword_config.get('elements', [])
        
        for element in elements:
            # AS-IS에서 요소 추출
            pattern = rf'<{element}[^>]*>(.*?)</{element}>'
            matches = re.findall(pattern, as_is_content, re.DOTALL)
            
            for match in matches:
                element_content = f'<{element}>{match}</{element}>'
                
                # 템플릿에 병합
                if keyword_name == 'connector':
                    template_content = self._merge_tomcat_connector(element_content, template_content)
                elif keyword_name == 'datasource':
                    template_content = self._merge_tomcat_datasource(element_content, template_content)
        
        return template_content
    
    def _merge_tomcat_connector(self, connector: str, template_content: str) -> str:
        """Tomcat Connector 병합"""
        # Service 태그 내에 병합
        service_section = re.search(r'<Service[^>]*>(.*?)</Service>', template_content, re.DOTALL)
        if service_section:
            old_service = service_section.group(0)
            new_service = old_service.replace('</Service>', connector + '\n    </Service>')
            template_content = template_content.replace(old_service, new_service)
        
        return template_content
    
    def _merge_tomcat_datasource(self, datasource: str, template_content: str) -> str:
        """Tomcat Datasource 병합"""
        # GlobalNamingResources 태그 내에 병합
        naming_section = re.search(r'<GlobalNamingResources>(.*?)</GlobalNamingResources>', template_content, re.DOTALL)
        if naming_section:
            old_naming = naming_section.group(0)
            new_naming = old_naming.replace('</GlobalNamingResources>', datasource + '\n  </GlobalNamingResources>')
            template_content = template_content.replace(old_naming, new_naming)
        
        return template_content
    
    def _xpath_to_regex(self, xpath: str) -> str:
        """XPath 패턴을 정규식으로 변환"""
        regex = xpath
        regex = regex.replace('//', '<')
        regex = regex.replace('/', '>.*?<')
        regex = re.sub(r'\[@[^]]+\]', '', regex)
        return regex
