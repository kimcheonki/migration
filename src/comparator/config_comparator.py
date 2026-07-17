"""
설정 파일 비교 모듈
AS-IS 파일과 TO-BE 샘플 파일을 비교하여 차이점을 분석
"""
import json
import re
from typing import Dict, List, Any
from pathlib import Path


class ConfigComparator:
    """설정 파일 비교 클래스"""
    
    def __init__(self, keywords_file: str):
        """
        초기화
        
        Args:
            keywords_file: 키워드 JSON 파일 경로
        """
        self.keywords = self._load_keywords(keywords_file)
    
    def _load_keywords(self, keywords_file: str) -> Dict[str, Any]:
        """키워드 JSON 파일 로드"""
        try:
            with open(keywords_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"키워드 파일을 찾을 수 없습니다: {keywords_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"키워드 파일 JSON 파싱 오류: {e}")
    
    def compare(self, as_is_content: str, to_be_content: str) -> Dict[str, Any]:
        """
        AS-IS와 TO-BE 설정 비교
        
        Args:
            as_is_content: AS-IS 설정 파일 내용
            to_be_content: TO-BE 샘플 설정 파일 내용
            
        Returns:
            비교 결과 딕셔너리
        """
        comparison_result = {
            'server': self.keywords.get('server', 'unknown'),
            'differences': [],
            'summary': {
                'total_keywords': len(self.keywords.get('keywords', {})),
                'analyzed_keywords': 0,
                'differences_found': 0,
                'missing_in_as_is': 0,
                'missing_in_to_be': 0,
                'mismatched': 0
            }
        }
        
        for keyword_name, keyword_config in self.keywords.get('keywords', {}).items():
            comparison_result['summary']['analyzed_keywords'] += 1
            
            # 키워드별 비교
            keyword_diff = self._compare_keyword(
                keyword_name,
                keyword_config,
                as_is_content,
                to_be_content
            )
            
            if keyword_diff['has_differences']:
                comparison_result['differences'].append(keyword_diff)
                comparison_result['summary']['differences_found'] += 1
                
                if keyword_diff['missing_in_as_is']:
                    comparison_result['summary']['missing_in_as_is'] += 1
                if keyword_diff['missing_in_to_be']:
                    comparison_result['summary']['missing_in_to_be'] += 1
                if keyword_diff['mismatched']:
                    comparison_result['summary']['mismatched'] += 1
        
        # 우선순위별 정렬
        comparison_result['differences'].sort(
            key=lambda x: x['priority'],
            reverse=True
        )
        
        return comparison_result
    
    def _compare_keyword(self, keyword_name: str, keyword_config: Dict[str, Any],
                       as_is_content: str, to_be_content: str) -> Dict[str, Any]:
        """
        특정 키워드 비교
        
        Args:
            keyword_name: 키워드 이름
            keyword_config: 키워드 설정
            as_is_content: AS-IS 내용
            to_be_content: TO-BE 내용
            
        Returns:
            키워드별 비교 결과
        """
        result = {
            'keyword': keyword_name,
            'description': keyword_config.get('description', ''),
            'priority': self._get_priority_value(keyword_config.get('priority', 'low')),
            'has_differences': False,
            'missing_in_as_is': False,
            'missing_in_to_be': False,
            'mismatched': False,
            'as_is_values': [],
            'to_be_values': [],
            'differences_detail': []
        }
        
        # 서버 타입에 따라 다른 비교 방식 사용
        server = self.keywords.get('server', '')
        
        if server == 'wildfly':
            self._compare_wildfly_keyword(keyword_name, keyword_config, as_is_content, to_be_content, result)
        elif server == 'apache':
            self._compare_apache_keyword(keyword_name, keyword_config, as_is_content, to_be_content, result)
        elif server == 'tomcat':
            self._compare_tomcat_keyword(keyword_name, keyword_config, as_is_content, to_be_content, result)
        
        return result
    
    def _compare_wildfly_keyword(self, keyword_name: str, keyword_config: Dict[str, Any],
                                as_is_content: str, to_be_content: str, result: Dict[str, Any]):
        """Wildfly 키워드 비교"""
        xpath = keyword_config.get('xpath', '')
        attributes = keyword_config.get('attributes', [])
        elements = keyword_config.get('elements', [])
        
        # XPath 패턴을 정규식으로 변환하여 검색
        pattern = self._xpath_to_regex(xpath)
        
        # AS-IS에서 추출
        as_is_matches = re.findall(pattern, as_is_content, re.DOTALL | re.IGNORECASE)
        result['as_is_values'] = as_is_matches
        
        # TO-BE에서 추출
        to_be_matches = re.findall(pattern, to_be_content, re.DOTALL | re.IGNORECASE)
        result['to_be_values'] = to_be_matches
        
        # 비교
        if not as_is_matches and to_be_matches:
            result['missing_in_as_is'] = True
            result['has_differences'] = True
            result['differences_detail'].append({
                'type': 'missing_in_as_is',
                'message': f'AS-IS 파일에 {keyword_name} 설정이 없습니다. TO-BE 샘플에 있습니다.'
            })
        elif as_is_matches and not to_be_matches:
            result['missing_in_to_be'] = True
            result['has_differences'] = True
            result['differences_detail'].append({
                'type': 'missing_in_to_be',
                'message': f'TO-BE 샘플에 {keyword_name} 설정이 없습니다. AS-IS 파일에 있습니다.'
            })
        elif as_is_matches != to_be_matches:
            result['mismatched'] = True
            result['has_differences'] = True
            result['differences_detail'].append({
                'type': 'mismatched',
                'message': f'{keyword_name} 설정이 다릅니다.',
                'as_is_count': len(as_is_matches),
                'to_be_count': len(to_be_matches)
            })
    
    def _compare_apache_keyword(self, keyword_name: str, keyword_config: Dict[str, Any],
                               as_is_content: str, to_be_content: str, result: Dict[str, Any]):
        """Apache 키워드 비교"""
        directives = keyword_config.get('directives', [])
        
        for directive in directives:
            # AS-IS에서 디렉티브 추출
            as_is_pattern = rf'{directive}\s+(.+)'
            as_is_matches = re.findall(as_is_pattern, as_is_content, re.IGNORECASE)
            
            # TO-BE에서 디렉티브 추출
            to_be_matches = re.findall(as_is_pattern, to_be_content, re.IGNORECASE)
            
            if as_is_matches:
                result['as_is_values'].extend(as_is_matches)
            if to_be_matches:
                result['to_be_values'].extend(to_be_matches)
            
            # 비교
            if not as_is_matches and to_be_matches:
                result['missing_in_as_is'] = True
                result['has_differences'] = True
                result['differences_detail'].append({
                    'type': 'missing_in_as_is',
                    'message': f'AS-IS 파일에 {directive} 디렉티브가 없습니다.'
                })
            elif as_is_matches and not to_be_matches:
                result['missing_in_to_be'] = True
                result['has_differences'] = True
                result['differences_detail'].append({
                    'type': 'missing_in_to_be',
                    'message': f'TO-BE 샘플에 {directive} 디렉티브가 없습니다.'
                })
            elif as_is_matches != to_be_matches:
                result['mismatched'] = True
                result['has_differences'] = True
                result['differences_detail'].append({
                    'type': 'mismatched',
                    'message': f'{directive} 디렉티브 설정이 다릅니다.',
                    'as_is_count': len(as_is_matches),
                    'to_be_count': len(to_be_matches)
                })
    
    def _compare_tomcat_keyword(self, keyword_name: str, keyword_config: Dict[str, Any],
                               as_is_content: str, to_be_content: str, result: Dict[str, Any]):
        """Tomcat 키워드 비교"""
        elements = keyword_config.get('elements', [])
        attributes = keyword_config.get('attributes', [])
        
        for element in elements:
            # AS-IS에서 요소 추출
            element_pattern = rf'<{element}[^>]*>(.*?)</{element}>'
            as_is_matches = re.findall(element_pattern, as_is_content, re.DOTALL)
            
            # TO-BE에서 요소 추출
            to_be_matches = re.findall(element_pattern, to_be_content, re.DOTALL)
            
            if as_is_matches:
                result['as_is_values'].extend(as_is_matches)
            if to_be_matches:
                result['to_be_values'].extend(to_be_matches)
            
            # 비교
            if not as_is_matches and to_be_matches:
                result['missing_in_as_is'] = True
                result['has_differences'] = True
                result['differences_detail'].append({
                    'type': 'missing_in_as_is',
                    'message': f'AS-IS 파일에 {element} 요소가 없습니다.'
                })
            elif as_is_matches and not to_be_matches:
                result['missing_in_to_be'] = True
                result['has_differences'] = True
                result['differences_detail'].append({
                    'type': 'missing_in_to_be',
                    'message': f'TO-BE 샘플에 {element} 요소가 없습니다.'
                })
            elif as_is_matches != to_be_matches:
                result['mismatched'] = True
                result['has_differences'] = True
                result['differences_detail'].append({
                    'type': 'mismatched',
                    'message': f'{element} 요소 설정이 다릅니다.',
                    'as_is_count': len(as_is_matches),
                    'to_be_count': len(to_be_matches)
                })
    
    def _xpath_to_regex(self, xpath: str) -> str:
        """
        XPath 패턴을 정규식으로 변환
        
        Args:
            xpath: XPath 패턴
            
        Returns:
            정규식 패턴
        """
        # 간단한 XPath를 정규식으로 변환
        # 예: //datasources/datasource -> <datasources>.*?<datasource>.*?</datasource>
        regex = xpath
        
        # //를 <로 변환
        regex = regex.replace('//', '<')
        # /를 >.*?<로 변환
        regex = regex.replace('/', '>.*?<')
        # [@...] 속성 선택자 제거
        regex = re.sub(r'\[@[^]]+\]', '', regex)
        
        return regex
    
    def _get_priority_value(self, priority: str) -> int:
        """
        우선순위 문자열을 숫자로 변환
        
        Args:
            priority: 우선순위 문자열 (high, medium, low)
            
        Returns:
            우선순위 숫자 (3=high, 2=medium, 1=low)
        """
        priority_map = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return priority_map.get(priority.lower(), 1)
    
    def get_high_priority_differences(self, comparison_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        우선순위가 높은 차이점만 반환
        
        Args:
            comparison_result: 비교 결과
            
        Returns:
            우선순위가 높은 차이점 목록
        """
        return [diff for diff in comparison_result['differences'] if diff['priority'] == 3]
    
    def format_comparison_report(self, comparison_result: Dict[str, Any]) -> str:
        """
        비교 결과를 보고서 형식으로 변환
        
        Args:
            comparison_result: 비교 결과
            
        Returns:
            보고서 문자열
        """
        report = []
        report.append(f"=== {comparison_result['server'].upper()} 설정 비교 보고서 ===\n")
        
        summary = comparison_result['summary']
        report.append(f"분석된 키워드: {summary['analyzed_keywords']}/{summary['total_keywords']}")
        report.append(f"차이점 발견: {summary['differences_found']}")
        report.append(f"  - AS-IS 누락: {summary['missing_in_as_is']}")
        report.append(f"  - TO-BE 누락: {summary['missing_in_to_be']}")
        report.append(f"  - 설정 불일치: {summary['mismatched']}")
        report.append("")
        
        if comparison_result['differences']:
            report.append("=== 차이점 상세 ===\n")
            
            for diff in comparison_result['differences']:
                priority_str = {3: '높음', 2: '중간', 1: '낮음'}[diff['priority']]
                report.append(f"키워드: {diff['keyword']} (우선순위: {priority_str})")
                report.append(f"설명: {diff['description']}")
                
                for detail in diff['differences_detail']:
                    report.append(f"  - {detail['message']}")
                
                report.append("")
        else:
            report.append("차이점이 없습니다. AS-IS 파일이 TO-BE 샘플과 일치합니다.")
        
        return "\n".join(report)
