"""
Wildfly 설정 변환기
"""
import re
from typing import Dict, List
from src.model.result import ConfigChange, MigrationIssue, FileMigrationResult, MigrationStatus


class WildflyConverter:
    """Wildfly 설정 변환기"""
    
    def __init__(self, from_version: str, to_version: str, rules: Dict):
        self.from_version = from_version
        self.to_version = to_version
        self.rules = rules
    
    def convert(self, parsed: Dict, file_type: str = 'xml') -> FileMigrationResult:
        """Wildfly 설정 변환"""
        changes = []
        issues = []
        applicable = True
        
        raw_content = parsed['raw_content']
        
        # 버전 키 생성
        version_key = f"{self.from_version}_to_{self.to_version}"
        
        # 마이그레이션 규칙 적용 및 실제 변환
        if 'wildfly' in self.rules and version_key in self.rules['wildfly']:
            rule_set = self.rules['wildfly'][version_key]
            
            for rule in rule_set.get('rules', []):
                pattern = rule.get('old_pattern', '')
                action = rule.get('action', '')
                new_pattern = rule.get('new_pattern', '')
                
                if file_type == 'xml':
                    attributes = parsed.get('attributes', {})
                    for attr_name, attr_value in attributes.items():
                        match = re.match(pattern, f'{attr_name}="{attr_value}"')
                        if match:
                            if action == 'keep':
                                changes.append(ConfigChange(
                                    key=attr_name,
                                    old_value=attr_value,
                                    new_value=attr_value,
                                    change_type='keep',
                                    reason=rule.get('description', '')
                                ))
                            elif action == 'modify' and new_pattern:
                                new_value = new_pattern.format(value=attr_value)
                                # XML 속성 변환
                                raw_content = raw_content.replace(
                                    f'{attr_name}="{attr_value}"',
                                    f'{attr_name}="{new_value}"'
                                )
                                changes.append(ConfigChange(
                                    key=attr_name,
                                    old_value=attr_value,
                                    new_value=new_value,
                                    change_type='modify',
                                    reason=rule.get('description', '')
                                ))
                elif file_type == 'properties':
                    properties = parsed.get('properties', {})
                    for prop_name, prop_value in properties.items():
                        match = re.match(pattern, f'{prop_name}={prop_value}')
                        if match:
                            if action == 'keep':
                                changes.append(ConfigChange(
                                    key=prop_name,
                                    old_value=prop_value,
                                    new_value=prop_value,
                                    change_type='keep',
                                    reason=rule.get('description', '')
                                ))
                            elif action == 'modify' and new_pattern:
                                new_value = new_pattern.format(value=prop_value)
                                # Properties 변환
                                raw_content = raw_content.replace(
                                    f'{prop_name}={prop_value}',
                                    f'{prop_name}={new_value}'
                                )
                                changes.append(ConfigChange(
                                    key=prop_name,
                                    old_value=prop_value,
                                    new_value=new_value,
                                    change_type='modify',
                                    reason=rule.get('description', '')
                                ))
        
        # 버전별 특정 변환 로직
        migrated_content = self._apply_version_specific_transforms(raw_content, file_type, self.from_version, self.to_version)
        
        # 상태 결정
        status = MigrationStatus.SUCCESS
        if any(issue.severity == 'critical' for issue in issues):
            status = MigrationStatus.ERROR
            applicable = False
        elif any(issue.severity == 'warning' for issue in issues):
            status = MigrationStatus.WARNING
        
        return FileMigrationResult(
            file_path='',
            file_type=file_type,
            original_content=parsed['raw_content'],
            migrated_content=migrated_content,
            status=status,
            changes=changes,
            issues=issues,
            applicable=applicable
        )
    
    def _apply_version_specific_transforms(self, content: str, file_type: str, 
                                         from_version: str, to_version: str) -> str:
        """버전별 특정 변환 적용"""
        transformed_content = content
        
        # Wildfly 네임스페이스 버전 매핑
        namespace_mapping = {
            '7': '1.0',      # JBoss AS 7
            '8': '2.0',
            '9': '3.0',
            '10': '4.0',
            '11': '5.0',
            '12': '6.0',
            '13': '7.0',
            '14': '8.0',
            '15': '9.0',
            '16': '10.0',
            '17': '11.0',
            '18': '12.0',
            '19': '13.0',
            '20': '14.0',
            '21': '15.0',
            '22': '16.0',
            '23': '17.0',
            '24': '18.0',
            '25': '19.0',
            '26': '20.0',
            '27': '21.0',
            '28': '22.0',
            '29': '23.0',
            '30': '24.0',
            '31': '25.0',
            '32': '26.0',
            '33': '27.0',
            '34': '28.0',
            '35': '29.0',
            '36': '30.0',
            '37': '31.0',
            '38': '20.0',    # Wildfly 38 uses community:20.0
        }
        
        if file_type == 'xml':
            # Wildfly 38 구조 변환
            if to_version.startswith('38'):
                transformed_content = self._transform_to_wildfly38_with_template(transformed_content, from_version)
        
        return transformed_content
    
    def _transform_to_wildfly38_with_template(self, content: str, from_version: str) -> str:
        """Wildfly 38 템플릿 기반 변환"""
        import re
        import os
        
        # Wildfly 38 템플릿 로드
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'wildfly38.xml')
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        else:
            # 템플릿이 없으면 기본 변환 사용
            return self._transform_to_wildfly38_structure(content)
        
        # 사용자 커스텀 설정 추출
        custom_settings = self._extract_custom_settings(content, from_version)
        
        # 템플릿에 커스텀 설정 병합
        merged_content = self._merge_custom_settings(template_content, custom_settings)
        
        return merged_content
    
    def _extract_custom_settings(self, content: str, from_version: str) -> dict:
        """사용자 커스텀 설정 추출"""
        import re
        
        custom_settings = {
            'datasources': [],
            'drivers': [],
            'socket_bindings': {},
            'interfaces': {},
            'socket_binding_group': {},
            'loggers': [],
            'deployments': [],
            'system_properties': {},
            'custom_properties': {}
        }
        
        # Custom datasource 추출 (ExampleDS 제외)
        datasource_pattern = r'<datasource[^>]*>(.*?)</datasource>'
        for match in re.finditer(datasource_pattern, content, re.DOTALL):
            datasource_content = match.group(1)  # 내용만 추출
            datasource_full = match.group(0)  # 전체 요소
            jndi_name_match = re.search(r'jndi-name="([^"]*)"', datasource_full)
            if jndi_name_match:
                jndi_name = jndi_name_match.group(1)
                if 'ExampleDS' not in jndi_name:
                    # Wildfly 38 형식으로 변환
                    transformed_content = self._transform_datasource_to_wildfly38(datasource_content)
                    # 속성 추출
                    pool_name_match = re.search(r'pool-name="([^"]*)"', datasource_full)
                    pool_name = pool_name_match.group(1) if pool_name_match else jndi_name.split('/')[-1]
                    
                    custom_settings['datasources'].append({
                        'jndi_name': jndi_name,
                        'pool_name': pool_name,
                        'content': transformed_content
                    })
        
        # Custom driver 추출
        driver_pattern = r'<driver name="([^"]*)"[^>]*>(.*?)</driver>'
        for match in re.finditer(driver_pattern, content, re.DOTALL):
            driver_name = match.group(1)
            if driver_name != 'h2':
                driver_content = match.group(2)
                # driver-class 제거
                driver_content = re.sub(r'<driver-class>[^<]*</driver-class>', '', driver_content)
                custom_settings['drivers'].append({
                    'name': driver_name,
                    'content': driver_content
                })
        
        # Custom interface 추출
        interface_pattern = r'<interface name="([^"]*)"[^>]*>(.*?)</interface>'
        for match in re.finditer(interface_pattern, content, re.DOTALL):
            interface_name = match.group(1)
            if interface_name not in ['management', 'public']:
                interface_content = match.group(2)
                custom_settings['interfaces'][interface_name] = interface_content
        
        # Custom socket-binding 추출
        socket_binding_pattern = r'<socket-binding name="([^"]*)"[^>]*>(.*?)</socket-binding>'
        for match in re.finditer(socket_binding_pattern, content, re.DOTALL):
            binding_name = match.group(1)
            binding_content = match.group(2)
            # 기본 binding이 아닌 경우만 추출
            if binding_name not in ['ajp', 'http', 'https', 'management-http', 'management-https', 'txn-recovery-environment', 'txn-status-manager']:
                custom_settings['socket_bindings'][binding_name] = binding_content
        
        # Custom socket-binding-group 설정 추출 (port-offset 등)
        socket_binding_group_pattern = r'<socket-binding-group name="([^"]*)"[^>]*>(.*?)</socket-binding-group>'
        socket_binding_group_match = re.search(socket_binding_group_pattern, content, re.DOTALL)
        if socket_binding_group_match:
            group_attrs = re.search(r'<socket-binding-group name="[^"]*"(.*?)>', socket_binding_group_match.group(0))
            if group_attrs:
                attrs = group_attrs.group(1)
                # port-offset 추출
                port_offset_match = re.search(r'port-offset="([^"]*)"', attrs)
                if port_offset_match and port_offset_match.group(1) != '${jboss.socket.binding.port-offset:0}':
                    custom_settings['socket_binding_group']['port-offset'] = port_offset_match.group(1)
        
        # Custom logger 추출
        logger_pattern = r'<logger category="([^"]*)"[^>]*>(.*?)</logger>'
        for match in re.finditer(logger_pattern, content, re.DOTALL):
            logger_category = match.group(1)
            # 기본 logger가 아닌 경우만 추출
            if logger_category not in ['com.arjuna', 'com.networknt.schema', 'io.jaegertracing.Configuration', 'org.jboss.as.config', 'sun.rmi']:
                logger_content = match.group(0)
                custom_settings['loggers'].append(logger_content)
        
        # Custom deployment 추출
        deployment_pattern = r'<deployment[^>]*>(.*?)</deployment>'
        for match in re.finditer(deployment_pattern, content, re.DOTALL):
            deployment_content = match.group(0)
            custom_settings['deployments'].append(deployment_content)
        
        # Custom system property 추출
        system_property_pattern = r'<system-property name="([^"]*)"[^>]*value="([^"]*)"[^>]*/>'
        for match in re.finditer(system_property_pattern, content):
            prop_name = match.group(1)
            prop_value = match.group(2)
            custom_settings['system_properties'][prop_name] = prop_value
        
        return custom_settings
    
    def _transform_datasource_to_wildfly38(self, content: str) -> str:
        """Datasource를 Wildfly 38 형식으로 변환"""
        import re
        
        # driver-class 요소 제거
        content = re.sub(r'\s*<driver-class>[^<]*</driver-class>\s*', '\n                    ', content)
        
        # security 구문 변환
        # <security><user-name>tmaxedu</user-name><password>tmaxedu</password></security>
        # → <security user-name="tmaxedu"><credential-reference clear-text="tmaxedu"/></security>
        security_pattern = r'<security>\s*<user-name>([^<]*)</user-name>\s*<password>([^<]*)</password>\s*</security>'
        security_match = re.search(security_pattern, content, re.DOTALL)
        if security_match:
            username = security_match.group(1)
            password = security_match.group(2)
            new_security = f'<security user-name="{username}">\n                        <credential-reference clear-text="{password}"/>\n                    </security>'
            content = re.sub(security_pattern, new_security, content, flags=re.DOTALL)
        
        # 이미 Wildfly 38 형식인 경우 (credential-reference가 있는 경우) 유지
        if '<credential-reference' in content:
            return content
        
        return content
    
    def _merge_custom_settings(self, template: str, custom_settings: dict) -> str:
        """템플릿에 커스텀 설정 병합"""
        import re
        
        # Custom datasource 병합
        if custom_settings['datasources']:
            datasources_section = re.search(r'<datasources>(.*?)</datasources>', template, re.DOTALL)
            if datasources_section:
                old_datasources = datasources_section.group(0)
                new_datasources = old_datasources
                
                # drivers 태그 앞에 custom datasource 추가
                drivers_pos = new_datasources.find('<drivers>')
                if drivers_pos > 0:
                    for ds in custom_settings['datasources']:
                        pool_name = ds.get('pool_name', ds['jndi_name'].split('/')[-1])
                        
                        ds_entry = f'                <datasource jndi-name="{ds["jndi_name"]}" pool-name="{pool_name}" enabled="true" use-java-context="true">{ds["content"]}</datasource>\n'
                        new_datasources = new_datasources[:drivers_pos] + ds_entry + new_datasources[drivers_pos:]
                
                template = template.replace(old_datasources, new_datasources)
        
        # Custom driver 병합
        if custom_settings['drivers']:
            drivers_section = re.search(r'<drivers>(.*?)</drivers>', template, re.DOTALL)
            if drivers_section:
                old_drivers = drivers_section.group(0)
                new_drivers = old_drivers
                
                for driver in custom_settings['drivers']:
                    driver_name = driver["name"]
                    driver_content = driver["content"]
                    driver_entry = f'                    <driver name="{driver_name}">{driver_content}</driver>'
                    new_drivers = new_drivers.replace(
                        '</drivers>',
                        driver_entry + '\n                </drivers>'
                    )
                
                template = template.replace(old_drivers, new_drivers)
        
        # Custom interface 병합
        if custom_settings['interfaces']:
            interfaces_section = re.search(r'<interfaces>(.*?)</interfaces>', template, re.DOTALL)
            if interfaces_section:
                old_interfaces = interfaces_section.group(0)
                new_interfaces = old_interfaces
                
                for interface_name, interface_content in custom_settings['interfaces'].items():
                    interface_entry = f'        <interface name="{interface_name}">{interface_content}</interface>\n'
                    new_interfaces = new_interfaces.replace('</interfaces>', interface_entry + '    </interfaces>')
                
                template = template.replace(old_interfaces, new_interfaces)
        
        # Custom socket-binding 병합
        if custom_settings['socket_bindings']:
            socket_binding_group_section = re.search(r'<socket-binding-group[^>]*>(.*?)</socket-binding-group>', template, re.DOTALL)
            if socket_binding_group_section:
                old_group = socket_binding_group_section.group(0)
                new_group = old_group
                
                for binding_name, binding_content in custom_settings['socket_bindings'].items():
                    binding_entry = f'        <socket-binding name="{binding_name}">{binding_content}</socket-binding>\n'
                    new_group = new_group.replace('</socket-binding-group>', binding_entry + '    </socket-binding-group>')
                
                template = template.replace(old_group, new_group)
        
        # Custom socket-binding-group 설정 병합 (port-offset 등)
        if custom_settings['socket_binding_group']:
            for attr_name, attr_value in custom_settings['socket_binding_group'].items():
                if attr_name == 'port-offset':
                    template = re.sub(
                        r'port-offset="\$\{jboss\.socket\.binding\.port-offset:0\}"',
                        f'port-offset="{attr_value}"',
                        template
                    )
        
        # Custom logger 병합
        if custom_settings['loggers']:
            logging_section = re.search(r'<subsystem xmlns="urn:jboss:domain:logging:8\.0">(.*?)</subsystem>', template, re.DOTALL)
            if logging_section:
                old_logging = logging_section.group(0)
                new_logging = old_logging
                
                # root-logger 태그 앞에 custom logger 추가
                root_logger_pos = new_logging.find('<root-logger>')
                if root_logger_pos > 0:
                    for logger in custom_settings['loggers']:
                        new_logging = new_logging[:root_logger_pos] + f'            {logger}\n' + new_logging[root_logger_pos:]
                
                template = template.replace(old_logging, new_logging)
        
        # Custom deployment 병합
        if custom_settings['deployments']:
            # </server> 태그 앞에 deployments 섹션 추가
            deployments_section = '    <deployments>\n'
            for deployment in custom_settings['deployments']:
                deployments_section += f'        {deployment}\n'
            deployments_section += '    </deployments>\n'
            
            template = template.replace('</server>', deployments_section + '</server>')
        
        # Custom system property 병합
        if custom_settings['system_properties']:
            # <server> 태그 다음에 system properties 추가
            server_tag_pos = template.find('<server')
            if server_tag_pos > 0:
                server_end_pos = template.find('>', server_tag_pos) + 1
                system_props_section = '\n    <system-properties>\n'
                for prop_name, prop_value in custom_settings['system_properties'].items():
                    system_props_section += f'        <system-property name="{prop_name}" value="{prop_value}"/>\n'
                system_props_section += '    </system-properties>'
                
                template = template[:server_end_pos] + system_props_section + template[server_end_pos:]
        
        return template
    
    def _transform_to_wildfly38_structure(self, content: str) -> str:
        """Wildfly 38 구조로 변환"""
        import re
        
        # 1. 메인 네임스페이스 업데이트
        content = re.sub(
            r'xmlns="urn:jboss:domain:15.0"',
            'xmlns="urn:jboss:domain:community:20.0"',
            content
        )
        
        # 2. Management 섹션 변환
        # security-realms 제거
        content = re.sub(
            r'<security-realms>.*?</security-realms>',
            '',
            content,
            flags=re.DOTALL
        )
        
        # http-interface 변환
        content = re.sub(
            r'<http-interface security-realm="ManagementRealm">',
            '<http-interface http-authentication-factory="management-http-authentication" console-enabled="true">',
            content
        )
        # http-upgrade에 sasl-authentication-factory 추가
        content = re.sub(
            r'<http-upgrade enabled="true"/>',
            '<http-upgrade enabled="true" sasl-authentication-factory="management-sasl-authentication"/>',
            content
        )
        
        # 3. Extension 모듈 변경
        # org.jboss.as.security 제거
        content = re.sub(
            r'<extension module="org.jboss.as.security"/>',
            '',
            content
        )
        # org.wildfly.extension.clustering.ejb 추가 (없는 경우)
        if 'org.wildfly.extension.clustering.ejb' not in content:
            content = re.sub(
                r'<extension module="org.wildfly.extension.clustering.web"/>',
                '<extension module="org.wildfly.extension.clustering.web"/>\n        <extension module="org.wildfly.extension.clustering.ejb"/>',
                content
            )
        # org.wildfly.extension.elytron-oidc-client 추가 (없는 경우)
        if 'org.wildfly.extension.elytron-oidc-client' not in content:
            content = re.sub(
                r'<extension module="org.wildfly.extension.elytron"/>',
                '<extension module="org.wildfly.extension.elytron"/>\n        <extension module="org.wildfly.extension.elytron-oidc-client"/>',
                content
            )
        
        # 4. Subsystem 네임스페이스 업데이트
        subsystem_updates = {
            'batch-jberet': ('2.0', '3.0'),
            'datasources': ('6.0', '7.2'),
            'ee': ('5.0', '6.0'),
            'ejb3': ('8.0', '10.0'),
            'elytron': ('12.0', 'community:18.0'),
            'infinispan': ('11.0', '15.0'),
            'io': ('3.0', '4.0'),
            'jaxrs': ('2.0', '4.0'),
            'jca': ('5.0', '6.0'),
            'transactions': ('5.0', '6.0'),
            'undertow': ('11.0', 'community:14.0'),
            'weld': ('4.0', '5.0'),
        }
        
        for subsystem, (old_ver, new_ver) in subsystem_updates.items():
            if subsystem == 'elytron':
                old_pattern = f'<subsystem xmlns="urn:wildfly:elytron:{old_ver}"'
                new_pattern = f'<subsystem xmlns="urn:wildfly:elytron:{new_ver}"'
            elif subsystem == 'undertow':
                old_pattern = f'<subsystem xmlns="urn:jboss:domain:undertow:{old_ver}"'
                new_pattern = f'<subsystem xmlns="urn:jboss:domain:undertow:{new_ver}"'
            else:
                old_pattern = f'<subsystem xmlns="urn:jboss:domain:{subsystem}:{old_ver}"'
                new_pattern = f'<subsystem xmlns="urn:jboss:domain:{subsystem}:{new_ver}"'
            content = re.sub(old_pattern, new_pattern, content)
        
        # 5. Distributable-web → Distributable-ejb + Distributable-web 분리
        # 기존 distributable-web 제거
        content = re.sub(
            r'<subsystem xmlns="urn:jboss:domain:distributable-web:2.0">.*?</subsystem>',
            '''        <subsystem xmlns="urn:jboss:domain:distributable-ejb:2.0">
            <bean-management default="default">
                <infinispan-bean-management name="default" max-active-beans="10000" cache-container="ejb" cache="passivation"/>
            </bean-management>
            <local-client-mappings-registry/>
            <infinispan-timer-management name="persistent" cache-container="ejb" cache="persistent" max-active-timers="10000"/>
            <infinispan-timer-management name="transient" cache-container="ejb" cache="transient" max-active-timers="10000"/>
        </subsystem>
        <subsystem xmlns="urn:jboss:domain:distributable-web:5.0">
            <session-management default="default">
                <infinispan-session-management name="default" cache-container="web" granularity="SESSION">
                    <local-affinity/>
                </infinispan-session-management>
            </session-management>
            <single-sign-on-management default="default">
                <infinispan-single-sign-on-management name="default" cache-container="web" cache="sso"/>
            </single-sign-on-management>
            <local-routing/>
        </subsystem>''',
            content,
            flags=re.DOTALL
        )
        
        # 6. Security subsystem 제거
        content = re.sub(
            r'<subsystem xmlns="urn:jboss:domain:security:2.0">.*?</subsystem>',
            '',
            content,
            flags=re.DOTALL
        )
        
        # 7. Microprofile-opentracing 제거
        content = re.sub(
            r'<subsystem xmlns="urn:wildfly:microprofile-opentracing-smallrye:3.0">.*?</subsystem>',
            '',
            content,
            flags=re.DOTALL
        )
        
        # 8. Datasource 구조 변환
        # 각 datasource 요소를 개별적으로 처리
        datasource_pattern = r'<datasource([^>]*?)>(.*?)</datasource>'
        
        def transform_datasource(match):
            attrs = match.group(1)
            content = match.group(2)
            
            # driver-class 요소 제거
            content = re.sub(r'<driver-class>[^<]*</driver-class>', '', content)
            
            # security 구문 변환
            # <security><user-name>sa</user-name><password>sa</password></security>
            # → <security user-name="sa" password="sa"/>
            content = re.sub(
                r'<security>\s*<user-name>([^<]*)</user-name>\s*<password>([^<]*)</password>\s*</security>',
                r'<security user-name="\1" password="\2"/>',
                content,
                flags=re.DOTALL
            )
            
            return f'<datasource{attrs}>{content}</datasource>'
        
        content = re.sub(datasource_pattern, transform_datasource, content, flags=re.DOTALL)
        
        # 9. EJB3 cache 구조 변환
        # cache → simple-cache, passivation-stores 제거
        content = re.sub(
            r'<cache name="simple"/>',
            '<simple-cache name="simple"/>',
            content
        )
        content = re.sub(
            r'<cache name="distributable"[^>]*>',
            '<distributable-cache name="distributable"/>',
            content
        )
        content = re.sub(
            r'<passivation-stores>.*?</passivation-stores>',
            '',
            content,
            flags=re.DOTALL
        )
        
        # 10. EJB3 application-security-domains 추가
        if '<application-security-domains>' not in content:
            content = re.sub(
                r'(<default-security-domain value="other"/>)',
                r'\1\n            <application-security-domains>\n                <application-security-domain name="other" security-domain="ApplicationDomain"/>\n            </application-security-domains>',
                content
            )
        
        # 11. Infinispan 구조 변환
        # cache-container에 marshaller 추가
        content = re.sub(
            r'<cache-container name="ejb"([^>]*)>',
            r'<cache-container name="ejb"\1 modules="org.wildfly.clustering.ejb.infinispan" marshaller="PROTOSTREAM">',
            content
        )
        content = re.sub(
            r'<cache-container name="web"([^>]*)>',
            r'<cache-container name="web"\1 modules="org.wildfly.clustering.web.infinispan" marshaller="PROTOSTREAM">',
            content
        )
        content = re.sub(
            r'<cache-container name="hibernate"([^>]*)>',
            r'<cache-container name="hibernate"\1 modules="org.infinispan.hibernate-cache" marshaller="JBOSS">',
            content
        )
        
        # ejb cache-container에 persistent, transient cache 추가
        ejb_cache_pattern = r'<cache-container name="ejb"[^>]*>.*?</cache-container>'
        ejb_cache_match = re.search(ejb_cache_pattern, content, re.DOTALL)
        if ejb_cache_match:
            old_ejb_cache = ejb_cache_match.group(0)
            if '<local-cache name="persistent">' not in old_ejb_cache:
                new_ejb_cache = old_ejb_cache.replace(
                    '</cache-container>',
                    '''                <local-cache name="persistent">
                    <locking isolation="REPEATABLE_READ"/>
                    <transaction mode="BATCH"/>
                    <expiration interval="0"/>
                    <file-store preload="true"/>
                </local-cache>
                <local-cache name="transient">
                    <locking isolation="REPEATABLE_READ"/>
                    <transaction mode="BATCH"/>
                    <expiration interval="0"/>
                    <file-store passivation="true" purge="true"/>
                </local-cache>
            </cache-container>'''
                )
                content = content.replace(old_ejb_cache, new_ejb_cache)
        
        # 12. Undertow 구조 변환
        # security-realm → ssl-context
        content = re.sub(
            r'<https-listener([^>]*?)security-realm="([^"]*)"([^>]*?)>',
            r'<https-listener\1ssl-context="applicationSSC"\3>',
            content
        )
        # http-invoker security-realm → http-authentication-factory
        content = re.sub(
            r'<http-invoker security-realm="([^"]*)"/>',
            r'<http-invoker http-authentication-factory="application-http-authentication"/>',
            content
        )
        # byte-buffer-pool 추가
        if '<byte-buffer-pool' not in content:
            content = re.sub(
                r'<subsystem xmlns="urn:jboss:domain:undertow:community:14.0"([^>]*?)>',
                r'<subsystem xmlns="urn:jboss:domain:undertow:community:14.0"\1>\n            <byte-buffer-pool name="default"/>',
                content
            )
        # application-security-domains 추가
        undertow_app_sec_pattern = r'<subsystem xmlns="urn:jboss:domain:undertow:community:14.0"[^>]*>.*?</subsystem>'
        undertow_app_sec_match = re.search(undertow_app_sec_pattern, content, re.DOTALL)
        if undertow_app_sec_match:
            old_undertow = undertow_app_sec_match.group(0)
            if '<application-security-domains>' not in old_undertow:
                new_undertow = old_undertow.replace(
                    '</subsystem>',
                    '''            <application-security-domains>
                <application-security-domain name="other" security-domain="ApplicationDomain"/>
            </application-security-domains>
        </subsystem>'''
                )
                content = content.replace(old_undertow, new_undertow)
        
        # 13. Remoting 구조 변환
        # security-realm → sasl-authentication-factory
        content = re.sub(
            r'<http-connector([^>]*?)security-realm="([^"]*)"([^>]*?)>',
            r'<http-connector\1sasl-authentication-factory="application-sasl-authentication"\3>',
            content
        )
        # endpoint 요소 추가
        remoting_pattern = r'<subsystem xmlns="urn:jboss:domain:remoting:8.0">'
        if remoting_pattern in content:
            content = re.sub(
                remoting_pattern,
                remoting_pattern + '\n            <endpoint worker="default"/>',
                content
            )
        
        # 14. Batch-jberet security-domain 추가
        content = re.sub(
            r'<subsystem xmlns="urn:jboss:domain:batch-jberet:3.0">',
            '<subsystem xmlns="urn:jboss:domain:batch-jberet:3.0">\n            <default-job-repository name="in-memory"/>\n            <default-thread-pool name="batch"/>\n            <security-domain name="ApplicationDomain"/>',
            content
        )
        
        # 15. Elytron http에 application-http-authentication 추가
        elytron_http_pattern = r'<http>(.*?)</http>'
        elytron_http_match = re.search(elytron_http_pattern, content, re.DOTALL)
        if elytron_http_match:
            old_http = elytron_http_match.group(0)
            if 'application-http-authentication' not in old_http:
                new_http = old_http.replace(
                    '</http>',
                    '''                <http-authentication-factory name="application-http-authentication" security-domain="ApplicationDomain" http-server-mechanism-factory="global">
                    <mechanism-configuration>
                        <mechanism mechanism-name="BASIC">
                            <mechanism-realm realm-name="ApplicationRealm"/>
                        </mechanism>
                    </mechanism-configuration>
                </http-authentication-factory>
            </http>'''
                )
                content = content.replace(old_http, new_http)
        
        # 16. Elytron sasl에 challenge-path 추가
        content = re.sub(
            r'<property name="wildfly.sasl.local-user.default-user" value="\$local"/>',
            r'<property name="wildfly.sasl.local-user.default-user" value="$local"/>\n                        <property name="wildfly.sasl.local-user.challenge-path" value="${jboss.server.temp.dir}/auth"/>',
            content
        )
        
        # 17. Elytron policy 추가
        elytron_pattern = r'<subsystem xmlns="urn:wildfly:elytron:community:18.0"[^>]*>.*?</subsystem>'
        elytron_match = re.search(elytron_pattern, content, re.DOTALL)
        if elytron_match:
            old_elytron = elytron_match.group(0)
            if '<policy' not in old_elytron:
                new_elytron = old_elytron.replace(
                    '</subsystem>',
                    '''            <policy name="jacc">
                <jacc-policy/>
            </policy>
        </subsystem>'''
                )
                content = content.replace(old_elytron, new_elytron)
        
        # 18. EE concurrent use-transaction-setup-provider 제거
        content = re.sub(
            r' use-transaction-setup-provider="true"',
            '',
            content
        )
        
        # 19. EE concurrent managed-executor-service에 hung-task-termination-period 추가
        content = re.sub(
            r'<managed-executor-service name="default"([^>]*?)>',
            r'<managed-executor-service name="default"\1 hung-task-termination-period="0">',
            content
        )
        content = re.sub(
            r'<managed-scheduled-executor-service name="default"([^>]*?)>',
            r'<managed-scheduled-executor-service name="default"\1 hung-task-termination-period="0">',
            content
        )
        
        # 20. JPA default-datasource 제거
        content = re.sub(
            r' default-datasource=""',
            '',
            content
        )
        
        # 21. Deployments 섹션 제거
        content = re.sub(
            r'<deployments>.*?</deployments>',
            '',
            content,
            flags=re.DOTALL
        )
        
        # 22. IO subsystem에 default-worker 추가
        content = re.sub(
            r'<subsystem xmlns="urn:jboss:domain:io:4.0">',
            '<subsystem xmlns="urn:jboss:domain:io:4.0" default-worker="default">',
            content
        )
        
        # 23. Resource-adapters 버전 업데이트
        content = re.sub(
            r'<subsystem xmlns="urn:jboss:domain:resource-adapters:6.0"/>',
            '<subsystem xmlns="urn:jboss:domain:resource-adapters:7.1"/>',
            content
        )
        
        # 24. Microprofile-config 버전 업데이트
        content = re.sub(
            r'<subsystem xmlns="urn:wildfly:microprofile-config-smallrye:1.0"/>',
            '<subsystem xmlns="urn:wildfly:microprofile-config-smallrye:2.0"/>',
            content
        )
        
        # 25. Datasource H2 connection-url에 MODE 추가
        content = re.sub(
            r'<connection-url>jdbc:h2:mem:test;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE</connection-url>',
            r'<connection-url>jdbc:h2:mem:test;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE;MODE=${wildfly.h2.compatibility.mode:REGULAR}</connection-url>',
            content
        )
        
        return content
    
    def _convert_datasource_to_agroal(self, content: str) -> str:
        """Legacy datasource subsystem을 Agroal로 변환"""
        import re
        
        # legacy datasource subsystem 제거
        legacy_datasource_pattern = r'<subsystem xmlns="urn:jboss:domain:datasources:[^"]*">.*?</subsystem>'
        
        # Agroal datasource subsystem 추가
        agroal_subsystem = '''        <subsystem xmlns="urn:jboss:domain:datasources-agroal:4.0">
            <datasources>
                <!-- Datasource configurations need to be manually converted to Agroal format -->
                <!-- Legacy datasource configurations have been removed -->
                <!-- Please convert your datasources to Agroal format -->
            </datasources>
        </subsystem>'''
        
        # legacy datasource subsystem 찾기
        if re.search(legacy_datasource_pattern, content, re.DOTALL):
            # 변환 메시지 추가
            content = re.sub(
                legacy_datasource_pattern,
                agroal_subsystem,
                content,
                flags=re.DOTALL
            )
            # 주석 추가
            content = content.replace(
                agroal_subsystem,
                '''        <!-- Legacy datasource subsystem converted to Agroal -->
        <!-- Manual conversion required for datasource configurations -->
''' + agroal_subsystem
            )
        
        return content
