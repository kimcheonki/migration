"""
GUI 메인 윈도우
tkinter 기반 전체 GUI 애플리케이션
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import Optional
import threading

# 현재 디렉토리를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils.detector import ConfigFileDetector
from src.comparator.config_comparator import ConfigComparator
from src.comparator.comparison_reporter import ComparisonReporter
from src.converter.template_based_converter import TemplateBasedConverter


class MigrationGUI:
    """마이그레이션 GUI 메인 클래스"""
    
    def __init__(self):
        """초기화"""
        self.root = tk.Tk()
        self.root.title("WEB/WAS 마이그레이션 툴")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # 변수
        self.input_file_path = tk.StringVar()
        self.server_name = tk.StringVar()
        self.from_version = tk.StringVar()
        self.to_version = tk.StringVar()
        self.output_dir = tk.StringVar(value="output")
        self.report_html = tk.BooleanVar(value=True)
        self.report_excel = tk.BooleanVar(value=True)
        
        # 비교 결과 저장
        self.comparison_result = None
        
        # 스타일 설정
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # UI 생성
        self._create_ui()
    
    def _create_ui(self):
        """UI 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 제목
        title_label = ttk.Label(
            main_frame, 
            text="WEB/WAS 마이그레이션 툴", 
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 1. 파일 선택 섹션
        self._create_file_selection_section(main_frame, 1)
        
        # 2. 서버 선택 섹션
        self._create_server_selection_section(main_frame, 2)
        
        # 3. 버전 선택 섹션
        self._create_version_selection_section(main_frame, 3)
        
        # 4. 출력 설정 섹션
        self._create_output_section(main_frame, 4)
        
        # 5. 레포트 설정 섹션
        self._create_report_section(main_frame, 5)
        
        # 6. 버튼 섹션
        self._create_button_section(main_frame, 6)
        
        # 7. 로그/결과 섹션
        self._create_log_section(main_frame, 7)
        
        # 진행 상태바
        self._create_progress_bar(main_frame, 8)
    
    def _create_file_selection_section(self, parent, row):
        """파일 선택 섹션"""
        frame = ttk.LabelFrame(parent, text="1. AS-IS 파일 선택", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        frame.columnconfigure(1, weight=1)
        
        ttk.Label(frame, text="설정 파일:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.input_file_path, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5
        )
        ttk.Button(frame, text="찾기...", command=self._select_input_file).grid(
            row=0, column=2, padx=5
        )
    
    def _create_server_selection_section(self, parent, row):
        """서버 선택 섹션"""
        frame = ttk.LabelFrame(parent, text="2. 서버 선택", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(frame, text="서버 타입:").grid(row=0, column=0, sticky=tk.W)
        
        server_combo = ttk.Combobox(
            frame, 
            textvariable=self.server_name,
            values=['Apache', 'Tomcat', 'Wildfly', 'Nginx'],
            state='readonly',
            width=20
        )
        server_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        server_combo.bind('<<ComboboxSelected>>', self._on_server_selected)
    
    def _create_version_selection_section(self, parent, row):
        """버전 선택 섹션"""
        frame = ttk.LabelFrame(parent, text="3. 버전 선택", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(frame, text="AS-IS 버전:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.from_version, width=15).grid(
            row=0, column=1, sticky=tk.W, padx=5
        )
        
        ttk.Label(frame, text="TO-BE 버전:").grid(row=0, column=2, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.to_version, width=15).grid(
            row=0, column=3, sticky=tk.W, padx=5
        )
        
        ttk.Label(frame, text="(예: Wildfly22, Wildfly38)").grid(row=0, column=4, sticky=tk.W, padx=5)
    
    def _create_output_section(self, parent, row):
        """출력 설정 섹션"""
        frame = ttk.LabelFrame(parent, text="4. 출력 설정", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        frame.columnconfigure(1, weight=1)
        
        ttk.Label(frame, text="출력 디렉토리:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.output_dir, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5
        )
        ttk.Button(frame, text="찾기...", command=self._select_output_dir).grid(
            row=0, column=2, padx=5
        )
    
    def _create_report_section(self, parent, row):
        """레포트 설정 섹션"""
        frame = ttk.LabelFrame(parent, text="5. 레포트 설정", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Checkbutton(frame, text="HTML 레포트", variable=self.report_html).grid(
            row=0, column=0, sticky=tk.W, padx=10
        )
        ttk.Checkbutton(frame, text="Excel 레포트", variable=self.report_excel).grid(
            row=0, column=1, sticky=tk.W, padx=10
        )
    
    def _create_button_section(self, parent, row):
        """버튼 섹션"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        ttk.Button(frame, text="비교", command=self._compare_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="변환", command=self._convert_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="비교 후 변환", command=self._compare_and_convert).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="종료", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
    
    def _create_log_section(self, parent, row):
        """로그/결과 섹션"""
        frame = ttk.LabelFrame(parent, text="로그 및 결과", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        parent.rowconfigure(row, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            frame, 
            height=15, 
            width=80,
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 로그 텍스트 스크롤바
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set
    
    def _create_progress_bar(self, parent, row):
        """진행 상태바"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(frame, text="준비됨")
        self.status_label.grid(row=0, column=1, padx=10)
    
    def _select_input_file(self):
        """입력 파일 선택"""
        file_path = filedialog.askopenfilename(
            title="AS-IS 설정 파일 선택",
            filetypes=[
                ("모든 설정파일", "*.conf;*.xml;*.properties"),
                ("Apache 설정", "*.conf"),
                ("XML 파일", "*.xml"),
                ("Properties 파일", "*.properties"),
                ("모든 파일", "*.*")
            ],
            initialdir=os.getcwd()
        )
        
        if file_path:
            self.input_file_path.set(file_path)
            self._log(f"선택된 파일: {file_path}")
            
            # 자동 서버 감지
            detected_server = ConfigFileDetector.detect_server(file_path)
            if detected_server:
                self.server_name.set(detected_server.capitalize())
                self._log(f"자동 감지된 서버: {detected_server.capitalize()}")
    
    def _select_output_dir(self):
        """출력 디렉토리 선택"""
        dir_path = filedialog.askdirectory(
            title="출력 디렉토리 선택",
            initialdir=self.output_dir.get()
        )
        
        if dir_path:
            self.output_dir.set(dir_path)
            self._log(f"선택된 출력 디렉토리: {dir_path}")
    
    def _on_server_selected(self, event):
        """서버 선택 이벤트"""
        server = self.server_name.get()
        self._log(f"선택된 서버: {server}")
    
    def _log(self, message):
        """로그 메시지 추가"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def _set_status(self, message):
        """상태 메시지 설정"""
        self.status_label.config(text=message)
    
    def _start_progress(self):
        """진행 상태 시작"""
        self.progress.start()
        self.root.update_idletasks()
    
    def _stop_progress(self):
        """진행 상태 중지"""
        self.progress.stop()
        self.root.update_idletasks()
    
    def _compare_files(self):
        """파일 비교"""
        # 유효성 검사
        if not self._validate_inputs():
            return
        
        # 백그라운드에서 비교 실행
        thread = threading.Thread(target=self._compare_files_thread)
        thread.daemon = True
        thread.start()
    
    def _compare_files_thread(self):
        """파일 비교 스레드"""
        self._start_progress()
        self._set_status("비교 중...")
        self._log("=" * 60)
        self._log("파일 비교 시작")
        self._log("=" * 60)
        
        try:
            # 파일 경로
            input_path = self.input_file_path.get()
            server_name = self.server_name.get().lower()
            to_version = self.to_version.get()
            
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
                self._log(f"경고: TO-BE 템플릿 파일을 찾을 수 없습니다: {template_file}")
                to_be_content = ""
            
            # 비교 수행
            if os.path.exists(keywords_file):
                comparator = ConfigComparator(keywords_file)
                self.comparison_result = comparator.compare(as_is_content, to_be_content)
                
                # 비교 레포트 생성
                reporter = ComparisonReporter()
                report = reporter.generate_text_report(self.comparison_result)
                self._log(report)
                
                # 요약 표시
                summary = self.comparison_result['summary']
                self._log(f"\n비교 요약:")
                self._log(f"  분석된 키워드: {summary['analyzed_keywords']}/{summary['total_keywords']}")
                self._log(f"  차이점 발견: {summary['differences_found']}")
                
                if summary['differences_found'] > 0:
                    self._log(f"    - AS-IS 누락: {summary['missing_in_as_is']}")
                    self._log(f"    - TO-BE 누락: {summary['missing_in_to_be']}")
                    self._log(f"    - 설정 불일치: {summary['mismatched']}")
                
                self._set_status("비교 완료")
            else:
                self._log(f"경고: 키워드 파일을 찾을 수 없습니다: {keywords_file}")
                self._set_status("비교 실패")
        
        except Exception as e:
            self._log(f"오류 발생: {e}")
            import traceback
            self._log(traceback.format_exc())
            self._set_status("오류 발생")
        
        finally:
            self._stop_progress()
    
    def _convert_files(self):
        """파일 변환"""
        # 유효성 검사
        if not self._validate_inputs():
            return
        
        # 백그라운드에서 변환 실행
        thread = threading.Thread(target=self._convert_files_thread)
        thread.daemon = True
        thread.start()
    
    def _convert_files_thread(self):
        """파일 변환 스레드"""
        self._start_progress()
        self._set_status("변환 중...")
        self._log("=" * 60)
        self._log("파일 변환 시작")
        self._log("=" * 60)
        
        try:
            # 파일 경로
            input_path = self.input_file_path.get()
            server_name = self.server_name.get().lower()
            to_version = self.to_version.get()
            output_dir = self.output_dir.get()
            
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
            
            # 템플릿 기반 변환 수행
            if os.path.exists(keywords_file) and os.path.exists(template_file):
                converter = TemplateBasedConverter(keywords_file, template_file)
                converted_content = converter.convert(as_is_content, self.comparison_result)
                
                # 변환된 파일 저장
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, f'{server_name}_converted.xml')
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(converted_content)
                
                self._log(f"변환된 파일 저장: {output_file}")
                self._set_status("변환 완료")
            else:
                self._log(f"경고: 키워드 또는 템플릿 파일을 찾을 수 없습니다")
                self._set_status("변환 실패")
        
        except Exception as e:
            self._log(f"오류 발생: {e}")
            import traceback
            self._log(traceback.format_exc())
            self._set_status("오류 발생")
        
        finally:
            self._stop_progress()
    
    def _compare_and_convert(self):
        """비교 후 변환"""
        # 먼저 비교
        self._compare_files()
        
        # 비교 완료 후 변환
        self.root.after(100, self._check_compare_and_convert)
    
    def _check_compare_and_convert(self):
        """비교 완료 확인 후 변환"""
        if self.comparison_result:
            # 사용자 확인
            result = messagebox.askyesno(
                "확인",
                "비교가 완료되었습니다. 변환을 진행하시겠습니까?"
            )
            if result:
                self._convert_files()
    
    def _validate_inputs(self):
        """입력 유효성 검사"""
        if not self.input_file_path.get():
            messagebox.showerror("오류", "AS-IS 파일을 선택해주세요.")
            return False
        
        if not self.server_name.get():
            messagebox.showerror("오류", "서버를 선택해주세요.")
            return False
        
        if not self.from_version.get():
            messagebox.showerror("오류", "AS-IS 버전을 입력해주세요.")
            return False
        
        if not self.to_version.get():
            messagebox.showerror("오류", "TO-BE 버전을 입력해주세요.")
            return False
        
        if not self.output_dir.get():
            messagebox.showerror("오류", "출력 디렉토리를 선택해주세요.")
            return False
        
        return True
    
    def run(self):
        """GUI 실행"""
        self.root.mainloop()


def main():
    """GUI 메인 함수"""
    app = MigrationGUI()
    app.run()


if __name__ == '__main__':
    main()
