"""
XML 유틸리티
"""
import xml.etree.ElementTree as ET
from typing import Dict, Optional, List


class XMLUtils:
    """XML 유틸리티 클래스"""
    
    @staticmethod
    def parse_xml(content: str) -> Optional[ET.Element]:
        """XML 파싱"""
        try:
            return ET.fromstring(content)
        except ET.ParseError:
            return None
    
    @staticmethod
    def get_attribute(element: ET.Element, attr_name: str, 
                     default: Optional[str] = None) -> Optional[str]:
        """속성 값 가져오기"""
        return element.attrib.get(attr_name, default)
    
    @staticmethod
    def get_attributes(element: ET.Element) -> Dict[str, str]:
        """모든 속성 가져오기"""
        return dict(element.attrib)
    
    @staticmethod
    def find_elements(element: ET.Element, tag: str) -> List[ET.Element]:
        """태그로 요소 찾기"""
        return element.findall(tag)
    
    @staticmethod
    def find_element(element: ET.Element, tag: str) -> Optional[ET.Element]:
        """태그로 단일 요소 찾기"""
        return element.find(tag)
    
    @staticmethod
    def element_to_dict(element: ET.Element) -> Dict:
        """요소를 딕셔너리로 변환"""
        result = {
            'tag': element.tag,
            'attributes': dict(element.attrib),
            'text': element.text,
            'children': []
        }
        
        for child in element:
            result['children'].append(XMLUtils.element_to_dict(child))
        
        return result
    
    @staticmethod
    def dict_to_element(data: Dict) -> ET.Element:
        """딕셔너리를 요소로 변환"""
        element = ET.Element(data['tag'], attrib=data['attributes'])
        
        if data['text']:
            element.text = data['text']
        
        for child_data in data['children']:
            element.append(XMLUtils.dict_to_element(child_data))
        
        return element
    
    @staticmethod
    def element_to_string(element: ET.Element, encoding: str = 'unicode') -> str:
        """요소를 문자열로 변환"""
        return ET.tostring(element, encoding=encoding)
