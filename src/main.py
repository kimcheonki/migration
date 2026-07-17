"""
WEB/WAS 마이그레이션 툴 메인 프로그램
"""
import argparse
import sys
import os
from typing import Dict, List

# 현재 디렉토리를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.config import Config
from src.utils.logger import get_logger
from src.utils.file_utils import FileUtils
from src.model.result import ServerType
from src.parser.apache_parser import ApacheParser
from src.parser.tomcat_parser import TomcatParser
from src.parser.wildfly_parser import WildflyParser
from src.converter.apache_converter import ApacheConverter
from src.converter.tomcat_converter import TomcatConverter
from src.converter.wildfly_converter import WildflyConverter
from src.analyzer.analyzer import ConfigAnalyzer
from src.report.excel_report import ExcelReportGenerator
from src.report.html_report import HTMLReportGenerator


class MigrationTool:
    """마이그레이션 툴 메인 클래스"""
    
    def __init__(self, rules_dir: str = 'src/rules'):
        self.config = Config(rules_dir)
        self.logger = get_logger()
        
        # 파서 등록
        self.parsers = {
            'apache': ApacheParser(),
            'tomcat': TomcatParser(),
            'wildfly': WildflyParser()
        }
        
        # 컨버터 등록
        self.converters = {
            'apache': ApacheConverter,
            'tomcat': TomcatConverter,
            'wildfly': WildflyConverter
        }
    
    def migrate(self, server_name: str, from_version: str, to_version: str,
               input_path: str, output_dir: str = None, recursive: bool = False) -> List:
        """마이그레이션 수행"""
        self.logger.info(f"마이그레이션 시작: {server_name} {from_version} → {to_version}")
        
        # 서버 타입 결정
        server_type = self._get_server_type(server_name)
        
        # 마이그레이션 규칙 로드
        rules = self.config.get_migration_rules(server_name, from_version, to_version)
        
        # 설정파일 로드
        config_files = self._load_config_files(input_path, server_name, recursive)
        self.logger.info(f"총 {len(config_files)}개의 설정파일을 로드했습니다.")
        
        # 마이그레이션 수행
        results = []
        for file_path, file_type, content in config_files:
            result = self._migrate_file(
                server_name, from_version, to_version,
                file_path, file_type, content, rules
            )
            results.append(result)
            
            # 마이그레이션된 파일 저장
            if output_dir and result.applicable:
                self._save_migrated_file(file_path, result.migrated_content, output_dir)
        
        # 분석
        analyzer = ConfigAnalyzer(server_name, server_type)
        summary = analyzer.analyze_results(results, from_version, to_version)
        
        # 요약 출력
        self._print_summary(summary)
        
        return results, summary
    
    def _get_server_type(self, server_name: str) -> ServerType:
        """서버 타입 반환"""
        web_servers = ['apache', 'nginx']
        if server_name.lower() in web_servers:
            return ServerType.WEB
        return ServerType.WAS
    
    def _load_config_files(self, input_path: str, server_name: str, 
                          recursive: bool) -> List[tuple]:
        """설정파일 로드"""
        config_files = []
        
        if os.path.isdir(input_path):
            # 디렉토리인 경우
            extensions = self._get_supported_extensions(server_name)
            file_paths = FileUtils.find_config_files(input_path, extensions, recursive)
            
            for file_path in file_paths:
                try:
                    content = FileUtils.read_file(file_path)
                    file_type = FileUtils.get_file_type(file_path)
                    config_files.append((file_path, file_type, content))
                except Exception as e:
                    self.logger.error(f"파일 로드 실패: {file_path} - {e}")
        else:
            # 파일인 경우
            try:
                content = FileUtils.read_file(input_path)
                file_type = FileUtils.get_file_type(input_path)
                config_files.append((input_path, file_type, content))
            except Exception as e:
                self.logger.error(f"파일 로드 실패: {input_path} - {e}")
        
        return config_files
    
    def _get_supported_extensions(self, server_name: str) -> List[str]:
        """지원하는 파일 확장자 반환"""
        extensions_map = {
            'apache': ['.conf', '.htaccess'],
            'nginx': ['.conf'],
            'tomcat': ['.xml', '.properties'],
            'wildfly': ['.xml', '.properties']
        }
        return extensions_map.get(server_name.lower(), [])
    
    def _migrate_file(self, server_name: str, from_version: str, to_version: str,
                     file_path: str, file_type: str, content: str, rules: Dict):
        """단일 파일 마이그레이션"""
        parser = self.parsers.get(server_name.lower())
        if not parser:
            raise ValueError(f"지원하지 않는 서버: {server_name}")
        
        # 파싱
        if server_name.lower() == 'apache':
            parsed = parser.parse(content)
        else:
            parsed = parser.parse(content, file_type)
        
        # 변환
        converter_class = self.converters.get(server_name.lower())
        converter = converter_class(from_version, to_version, rules)
        
        if server_name.lower() == 'apache':
            result = converter.convert(parsed)
        else:
            result = converter.convert(parsed, file_type)
        
        # 파일 경로 설정
        result.file_path = file_path
        
        return result
    
    def _save_migrated_file(self, original_path: str, content: str, output_dir: str):
        """마이그레이션된 파일 저장"""
        FileUtils.ensure_directory(output_dir)
        filename = os.path.basename(original_path)
        output_path = os.path.join(output_dir, filename)
        FileUtils.write_file(output_path, content)
        self.logger.info(f"파일 저장: {output_path}")
    
    def _print_summary(self, summary):
        """요약 출력"""
        self.logger.info("=" * 50)
        self.logger.info("마이그레이션 요약")
        self.logger.info("=" * 50)
        self.logger.info(f"서버: {summary.server_name}")
        self.logger.info(f"버전: {summary.from_version} → {summary.to_version}")
        self.logger.info(f"총 파일: {summary.total_files}")
        self.logger.info(f"성공: {summary.successful_files}")
        self.logger.info(f"경고: {summary.warning_files}")
        self.logger.info(f"실패: {summary.error_files}")
        self.logger.info(f"수동 검토: {summary.manual_review_files}")
        self.logger.info(f"총 변경사항: {summary.total_changes}")
        self.logger.info(f"총 이슈: {summary.total_issues}")
        self.logger.info("=" * 50)
    
    def generate_reports(self, summary, results, output_dir: str, 
                        report_types: List[str] = None):
        """레포트 생성"""
        if report_types is None:
            report_types = ['html', 'excel']
        
        FileUtils.ensure_directory(output_dir)
        
        if 'html' in report_types:
            html_generator = HTMLReportGenerator()
            html_path = os.path.join(output_dir, 'migration_report.html')
            html_generator.save(summary, results, html_path)
            self.logger.info(f"HTML 레포트 저장: {html_path}")
        
        if 'excel' in report_types:
            excel_generator = ExcelReportGenerator()
            wb = excel_generator.generate(summary, results)
            excel_path = os.path.join(output_dir, 'migration_report.xlsx')
            excel_generator.save(excel_path)
            self.logger.info(f"Excel 레포트 저장: {excel_path}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='WEB/WAS 설정파일 마이그레이션 툴',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
사용 예시:
  # 단일 파일 마이그레이션
  python src/main.py --server apache --from-version 2.4.39 --to-version 2.4.57 --input httpd.conf --output-dir output/

  # 디렉토리 마이그레이션
  python src/main.py --server tomcat --from-version 8.5 --to-version 10.1 --input /opt/tomcat/conf/ --output-dir output/ --recursive

  # 레포트만 HTML 생성
  python src/main.py --server wildfly --from-version 13 --to-version 27 --input standalone.xml --output-dir output/ --report html

지원하는 서버:
  WEB: Apache
  WAS: Tomcat, Wildfly
        '''
    )
    
    parser.add_argument('--server', '-s', type=str,
                       help='서버 이름 (apache, tomcat, wildfly)')
    parser.add_argument('--from-version', '-f', type=str,
                       help='AS-IS 버전')
    parser.add_argument('--to-version', '-t', type=str,
                       help='TO-BE 버전')
    parser.add_argument('--input', '-i', type=str,
                       help='입력 파일 또는 디렉토리 경로')
    parser.add_argument('--output-dir', '-o', type=str, default='output',
                       help='출력 디렉토리 경로 (기본값: output)')
    parser.add_argument('--rules-dir', type=str, default='src/rules',
                       help='규칙 파일 디렉토리 (기본값: src/rules)')
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='디렉토리 재귀적 탐색')
    parser.add_argument('--report', type=str, nargs='+', 
                       choices=['html', 'excel', 'both'],
                       default=['both'],
                       help='레포트 타입 (html, excel, both)')
    parser.add_argument('--interactive', '-I', action='store_true',
                       help='대화형 모드 실행 (커맨드라인 기반)')
    parser.add_argument('--gui', '-G', action='store_true',
                       help='GUI 모드 실행')
    
    args = parser.parse_args()
    
    # GUI 모드 실행
    if args.gui:
        from src.gui.main_window import main as gui_main
        gui_main()
        return
    
    # 대화형 모드 실행
    if args.interactive:
        from src.interactive import main as interactive_main
        interactive_main()
        return
    
    # 명령행 모드에서는 필수 인자 검사
    if not args.server:
        parser.error("--server/-s 인자가 필요합니다")
    if not args.from_version:
        parser.error("--from-version/-f 인자가 필요합니다")
    if not args.to_version:
        parser.error("--to-version/-t 인자가 필요합니다")
    if not args.input:
        parser.error("--input/-i 인자가 필요합니다")
    
    # 마이그레이션 툴 초기화
    tool = MigrationTool(args.rules_dir)
    
    # 마이그레이션 수행
    results, summary = tool.migrate(
        args.server, args.from_version, args.to_version,
        args.input, args.output_dir, args.recursive
    )
    
    # 레포트 생성
    report_types = []
    if 'both' in args.report or 'html' in args.report:
        report_types.append('html')
    if 'both' in args.report or 'excel' in args.report:
        report_types.append('excel')
    
    tool.generate_reports(summary, results, args.output_dir, report_types)


if __name__ == '__main__':
    main()
