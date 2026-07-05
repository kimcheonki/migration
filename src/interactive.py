"""
대화형 마이그레이션 모드
"""
import os
from typing import Optional, List
from src.utils.logger import get_logger
from src.utils.file_utils import FileUtils
from src.utils.detector import ConfigFileDetector
from src.config import Config
from src.model.result import ServerType


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
        
        # 4. 출력 디렉토리 선택
        output_dir = self._select_output_dir()
        
        # 5. 레포트 형식 선택
        report_types = self._select_report_types()
        
        # 6. 확인 및 실행
        self._confirm_and_execute(server_name, from_version, to_version, 
                                  input_path, output_dir, report_types)
    
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
        print()
        
        while True:
            choice = input("서버를 선택하세요 (1-3): ").strip()
            if choice == '1':
                return 'apache'
            elif choice == '2':
                return 'tomcat'
            elif choice == '3':
                return 'wildfly'
            else:
                print("잘못된 선택입니다. 다시 선택해주세요.")
    
    def _select_versions(self, server_name: str) -> tuple:
        """버전 선택"""
        print(f"\n{server_name.upper()} 버전 선택")
        print()
        
        from_version = input("AS-IS 버전을 입력하세요 (예: 2.4.39): ").strip()
        to_version = input("TO-BE 버전을 입력하세요 (예: 2.4.57): ").strip()
        
        return from_version, to_version
    
    def _select_input_file(self) -> str:
        """입력 파일 선택"""
        print("\n설정파일 선택")
        print("파일 경로 또는 디렉토리 경로를 입력하세요.")
        print("드래그 앤 드롭으로 파일 경로를 붙여넣을 수 있습니다.")
        print()
        
        while True:
            input_path = input("입력 경로: ").strip().strip('"')
            
            if not input_path:
                print("경로를 입력해주세요.")
                continue
            
            if not os.path.exists(input_path):
                print(f"파일을 찾을 수 없습니다: {input_path}")
                continue
            
            return input_path
    
    def _select_output_dir(self) -> str:
        """출력 디렉토리 선택"""
        print(f"\n출력 디렉토리 선택")
        print()
        
        default_output = "output"
        output_dir = input(f"출력 디렉토리 (기본값: {default_output}): ").strip()
        
        if not output_dir:
            output_dir = default_output
        
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
                           output_dir: str, report_types: List[str]):
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
            
            # 마이그레이션 실행
            from src.main import MigrationTool
            tool = MigrationTool()
            
            try:
                results, summary = tool.migrate(
                    server_name, from_version, to_version,
                    input_path, output_dir, recursive=False
                )
                
                tool.generate_reports(summary, results, output_dir, report_types)
                
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
        else:
            print("마이그레이션이 취소되었습니다.")


def main():
    """대화형 모드 메인 함수"""
    interactive = InteractiveMode()
    interactive.run()


if __name__ == '__main__':
    main()
