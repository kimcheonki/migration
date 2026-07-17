"""
대화형 마이그레이션 모드
"""
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, List

# 현재 디렉토리를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils.logger import get_logger
from src.utils.file_utils import FileUtils
from src.utils.detector import ConfigFileDetector
from src.config import Config
from src.model.result import ServerType
from src.comparator.config_comparator import ConfigComparator
from src.comparator.comparison_reporter import ComparisonReporter
from src.converter.template_based_converter import TemplateBasedConverter


class InteractiveMode:
    """대화형 마이그레이션 모드"""
    
    def __init__(self):
        self.logger = get_logger()
        self.config = Config()
    
    def run(self):
        """대화형 모드 실행"""
        print("=" * 60)
        print("WEB/WAS 마이그레이션 툴 - 대화형 모드")
        print("=" * 60)
        print()
        
        # 1. 입력 파일 선택 (먼저 선택하여 자동 감지)
        input_path = self._select_input_file()
        
        # 2. 서버 자동 감지 또는 수동 선택
        server_name = self._select_or_detect_server(input_path)
        
        # 3. 버전 선택
        from_version, to_version = self._select_versions(server_name)
        
        # 4. TO-BE 샘플 파일 로드 및 비교
        comparison_result = self._compare_with_template(server_name, to_version, input_path)
        
        # 5. 비교 결과 표시
        self._display_comparison_result(comparison_result)
        
        # 6. 변환 여부 확인
        proceed = input("\n변환을 계속 진행하시겠습니까? (y/n): ").strip().lower()
        if proceed != 'y':
            print("마이그레이션이 취소되었습니다.")
            return
        
        # 7. 출력 디렉토리 선택
        output_dir = self._select_output_dir()
        
        # 8. 레포트 형식 선택
        report_types = self._select_report_types()
        
        # 9. 확인 및 실행
        self._confirm_and_execute(server_name, from_version, to_version, 
                                  input_path, output_dir, report_types, comparison_result)
    
    def _select_or_detect_server(self, input_path: str) -> str:
        """서버 자동 감지 또는 수동 선택"""
        # 자동 감지 시도
        detected_server = ConfigFileDetector.detect_server(input_path)
        
        if detected_server:
            print(f"자동 감지된 서버: {detected_server.upper()}")
            use_detected = input("감지된 서버를 사용하시겠습니까? (y/n): ").strip().lower()
            
            if use_detected == 'y':
                return detected_server
        
        # 수동 선택
        print("\n지원하는 서버:")
        print("1. Apache")
        print("2. Tomcat")
        print("3. Wildfly")
        print("4. Nginx")
        print()
        
        while True:
            choice = input("서버를 선택하세요 (1-4): ").strip()
            if choice == '1':
                return 'apache'
            elif choice == '2':
                return 'tomcat'
            elif choice == '3':
                return 'wildfly'
            elif choice == '4':
                return 'nginx'
            else:
                print("잘못된 선택입니다. 다시 선택해주세요.")
    
    def _compare_with_template(self, server_name: str, to_version: str, input_path: str) -> dict:
        """TO-BE 샘플 파일과 비교"""
        print(f"\nTO-BE 샘플 파일과 비교 중...")
        
        # 키워드 파일 경로
        keywords_file = os.path.join(
            parent_dir, 'samples', server_name, 'keywords', f'{server_name}-keywords.json'
        )
        
        # 템플릿 파일 경로
        template_file = os.path.join(
            parent_dir, 'samples', server_name, f'{server_name}{to_version}.xml'
        )
        
        # 템플릿 파일이 없으면 기본 템플릿 사용
        if not os.path.exists(template_file):
            template_file = os.path.join(
                parent_dir, 'samples', server_name, f'{server_name}-template.xml'
            )
        
        # AS-IS 파일 내용 로드
        with open(input_path, 'r', encoding='utf-8') as f:
            as_is_content = f.read()
        
        # TO-BE 템플릿 파일 내용 로드
        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                to_be_content = f.read()
        else:
            print(f"경고: TO-BE 템플릿 파일을 찾을 수 없습니다: {template_file}")
            to_be_content = ""
        
        # 비교 수행
        if os.path.exists(keywords_file):
            comparator = ConfigComparator(keywords_file)
            comparison_result = comparator.compare(as_is_content, to_be_content)
            
            # 비교 레포트 생성
            reporter = ComparisonReporter()
            report = reporter.generate_text_report(comparison_result)
            print(report)
            
            return comparison_result
        else:
            print(f"경고: 키워드 파일을 찾을 수 없습니다: {keywords_file}")
            return None
    
    def _display_comparison_result(self, comparison_result: dict):
        """비교 결과 표시"""
        if not comparison_result:
            print("비교 결과가 없습니다.")
            return
        
        summary = comparison_result['summary']
        print(f"\n비교 요약:")
        print(f"  분석된 키워드: {summary['analyzed_keywords']}/{summary['total_keywords']}")
        print(f"  차이점 발견: {summary['differences_found']}")
        
        if summary['differences_found'] > 0:
            print(f"    - AS-IS 누락: {summary['missing_in_as_is']}")
            print(f"    - TO-BE 누락: {summary['missing_in_to_be']}")
            print(f"    - 설정 불일치: {summary['mismatched']}")
            
            # 우선순위가 높은 차이점 표시
            high_priority_diffs = [d for d in comparison_result['differences'] if d['priority'] == 3]
            if high_priority_diffs:
                print(f"\n우선순위가 높은 차이점 ({len(high_priority_diffs)}개):")
                for diff in high_priority_diffs[:5]:  # 상위 5개만 표시
                    print(f"  - {diff['keyword']}: {diff['description']}")
        else:
            print("  차이점이 없습니다.")
    
    def _select_versions(self, server_name: str) -> tuple:
        """버전 선택"""
        print(f"\n{server_name.upper()} 버전 선택")
        print("버전 번호만 입력하세요 (예: 22, 38)")
        print()
        
        from_version = input("AS-IS 버전을 입력하세요 (예: 22): ").strip()
        to_version = input("TO-BE 버전을 입력하세요 (예: 38): ").strip()
        
        # 버전에서 숫자만 추출
        from_version = ''.join(c for c in from_version if c.isdigit())
        to_version = ''.join(c for c in to_version if c.isdigit())
        
        if not from_version or not to_version:
            print("유효한 버전 번호를 입력해주세요.")
            return self._select_versions(server_name)
        
        return from_version, to_version
    
    def _select_input_file(self) -> str:
        """입력 파일 선택 (GUI 대화상자)"""
        print("\n설정파일 선택")
        
        # tkinter 루트 생성 (숨김)
        root = tk.Tk()
        root.withdraw()
        
        # 파일 선택 대화상자
        file_path = filedialog.askopenfilename(
            title="설정파일 선택",
            filetypes=[
                ("모든 설정파일", "*.conf;*.xml;*.properties"),
                ("Apache 설정", "*.conf"),
                ("XML 파일", "*.xml"),
                ("Properties 파일", "*.properties"),
                ("모든 파일", "*.*")
            ],
            initialdir=os.getcwd()
        )
        
        root.destroy()
        
        if not file_path:
            print("파일 선택이 취소되었습니다.")
            return self._select_input_file()  # 다시 선택 요청
        
        if not os.path.exists(file_path):
            print(f"파일을 찾을 수 없습니다: {file_path}")
            return self._select_input_file()
        
        print(f"선택된 파일: {file_path}")
        return file_path
    
    def _select_output_dir(self) -> str:
        """출력 디렉토리 선택 (GUI 대화상자)"""
        print(f"\n출력 디렉토리 선택")
        
        # tkinter 루트 생성 (숨김)
        root = tk.Tk()
        root.withdraw()
        
        # 디렉토리 선택 대화상자
        output_dir = filedialog.askdirectory(
            title="출력 디렉토리 선택",
            initialdir=os.path.join(os.getcwd(), "output")
        )
        
        root.destroy()
        
        if not output_dir:
            print("디렉토리 선택이 취소되었습니다. 기본값 'output'을 사용합니다.")
            output_dir = "output"
        
        print(f"선택된 출력 디렉토리: {output_dir}")
        return output_dir
    
    def _select_report_types(self) -> List[str]:
        """레포트 형식 선택"""
        print(f"\n레포트 형식 선택")
        print("1. HTML만")
        print("2. Excel만")
        print("3. 둘 다")
        print()
        
        while True:
            choice = input("레포트 형식을 선택하세요 (1-3): ").strip()
            if choice == '1':
                return ['html']
            elif choice == '2':
                return ['excel']
            elif choice == '3':
                return ['html', 'excel']
            else:
                print("잘못된 선택입니다. 다시 선택해주세요.")
    
    def _confirm_and_execute(self, server_name: str, from_version: str, 
                           to_version: str, input_path: str, 
                           output_dir: str, report_types: List[str], 
                           comparison_result: dict = None):
        """확인 및 실행"""
        print()
        print("=" * 60)
        print("마이그레이션 설정 확인")
        print("=" * 60)
        print(f"서버: {server_name}")
        print(f"AS-IS 버전: {from_version}")
        print(f"TO-BE 버전: {to_version}")
        print(f"입력 경로: {input_path}")
        print(f"출력 디렉토리: {output_dir}")
        print(f"레포트 형식: {', '.join(report_types)}")
        print("=" * 60)
        print()
        
        confirm = input("마이그레이션을 시작하시겠습니까? (y/n): ").strip().lower()
        
        if confirm == 'y':
            print()
            print("마이그레이션을 시작합니다...")
            print()
            
            try:
                # 템플릿 기반 변환 사용
                keywords_file = os.path.join(
                    parent_dir, 'samples', server_name, 'keywords', f'{server_name}-keywords.json'
                )
                template_file = os.path.join(
                    parent_dir, 'samples', server_name, f'{server_name}{to_version}.xml'
                )
                
                # 템플릿 파일이 없으면 기본 템플릿 사용
                if not os.path.exists(template_file):
                    template_file = os.path.join(
                        parent_dir, 'samples', server_name, f'{server_name}-template.xml'
                    )
                
                # AS-IS 파일 내용 로드
                with open(input_path, 'r', encoding='utf-8') as f:
                    as_is_content = f.read()
                
                # 템플릿 기반 변환 수행
                if os.path.exists(keywords_file) and os.path.exists(template_file):
                    converter = TemplateBasedConverter(keywords_file, template_file)
                    converted_content = converter.convert(as_is_content, comparison_result)
                    
                    # 변환된 파일 저장
                    os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f'{server_name}_converted.xml')
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(converted_content)
                    
                    print(f"변환된 파일 저장: {output_file}")
                else:
                    # 기존 마이그레이션 툴 사용
                    from src.main import MigrationTool
                    tool = MigrationTool()
                    results, summary = tool.migrate(
                        server_name, from_version, to_version,
                        input_path, output_dir, recursive=False
                    )
                    tool.generate_reports(summary, results, output_dir, report_types)
                
                # 비교 레포트 생성
                if comparison_result:
                    reporter = ComparisonReporter()
                    comparison_report_path = os.path.join(output_dir, 'comparison_report.html')
                    reporter.generate_html_report(comparison_result, comparison_report_path)
                    print(f"비교 레포트 저장: {comparison_report_path}")
                
                print()
                print("=" * 60)
                print("마이그레이션 완료!")
                print("=" * 60)
                print(f"결과 파일: {output_dir}")
                print()
                
                if report_types:
                    print("생성된 레포트:")
                    if 'html' in report_types:
                        print(f"  - {os.path.join(output_dir, 'migration_report.html')}")
                    if 'excel' in report_types:
                        print(f"  - {os.path.join(output_dir, 'migration_report.xlsx')}")
                
            except Exception as e:
                print()
                print(f"오류 발생: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("마이그레이션이 취소되었습니다.")


def main():
    """대화형 모드 메인 함수"""
    interactive = InteractiveMode()
    interactive.run()


if __name__ == '__main__':
    main()
