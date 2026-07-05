"""
HTML 레포트 생성기
"""
from datetime import datetime
from typing import List
from jinja2 import Template
from src.model.result import FileMigrationResult, MigrationSummary


class HTMLReportGenerator:
    """HTML 레포트 생성기"""
    
    def __init__(self):
        self.template = self._get_template()
    
    def _get_template(self) -> Template:
        """HTML 템플릿"""
        template_str = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WEB/WAS 마이그레이션 레포트</title>
    <style>
        body {
            font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        h2 {
            color: #555;
            margin-top: 30px;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .summary-card {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
        }
        .summary-card .value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #007bff;
            color: white;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .status-success {
            color: #28a745;
            font-weight: bold;
        }
        .status-warning {
            color: #ffc107;
            font-weight: bold;
        }
        .status-error {
            color: #dc3545;
            font-weight: bold;
        }
        .severity-critical {
            color: #dc3545;
            font-weight: bold;
        }
        .severity-warning {
            color: #ffc107;
            font-weight: bold;
        }
        .severity-info {
            color: #17a2b8;
        }
        .file-section {
            margin: 30px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 6px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>WEB/WAS 마이그레이션 레포트</h1>
        
        <p><strong>생성일시:</strong> {{ report_date }}</p>
        <p><strong>서버:</strong> {{ server_name }} ({{ server_type }})</p>
        <p><strong>버전:</strong> {{ from_version }} → {{ to_version }}</p>
        
        <h2>요약</h2>
        <div class="summary">
            <div class="summary-card">
                <h3>총 파일 수</h3>
                <div class="value">{{ total_files }}</div>
            </div>
            <div class="summary-card">
                <h3>성공</h3>
                <div class="value" style="color: #28a745;">{{ successful_files }}</div>
            </div>
            <div class="summary-card">
                <h3>경고</h3>
                <div class="value" style="color: #ffc107;">{{ warning_files }}</div>
            </div>
            <div class="summary-card">
                <h3>실패</h3>
                <div class="value" style="color: #dc3545;">{{ error_files }}</div>
            </div>
            <div class="summary-card">
                <h3>수동 검토</h3>
                <div class="value" style="color: #6c757d;">{{ manual_review_files }}</div>
            </div>
            <div class="summary-card">
                <h3>총 변경사항</h3>
                <div class="value">{{ total_changes }}</div>
            </div>
            <div class="summary-card">
                <h3>총 이슈</h3>
                <div class="value">{{ total_issues }}</div>
            </div>
        </div>
        
        <h2>파일별 상세</h2>
        <table>
            <thead>
                <tr>
                    <th>파일 경로</th>
                    <th>타입</th>
                    <th>상태</th>
                    <th>적용 가능</th>
                    <th>변경사항</th>
                    <th>이슈</th>
                </tr>
            </thead>
            <tbody>
                {% for result in results %}
                <tr>
                    <td>{{ result.file_path }}</td>
                    <td>{{ result.file_type }}</td>
                    <td class="status-{{ result.status.value }}">{{ result.status.value }}</td>
                    <td>{{ "O" if result.applicable else "X" }}</td>
                    <td>{{ result.changes|length }}</td>
                    <td>{{ result.issues|length }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <h2>상세 내역</h2>
        {% for result in results %}
        <div class="file-section">
            <h3>{{ result.file_path }}</h3>
            <p><strong>파일 타입:</strong> {{ result.file_type }}</p>
            <p><strong>상태:</strong> <span class="status-{{ result.status.value }}">{{ result.status.value }}</span></p>
            <p><strong>적용 가능:</strong> {{ "예" if result.applicable else "아니오" }}</p>
            
            {% if result.changes %}
            <h4>변경사항 ({{ result.changes|length }}개)</h4>
            <table>
                <thead>
                    <tr>
                        <th>키</th>
                        <th>이전 값</th>
                        <th>새 값</th>
                        <th>유형</th>
                        <th>이유</th>
                    </tr>
                </thead>
                <tbody>
                    {% for change in result.changes %}
                    <tr>
                        <td>{{ change.key }}</td>
                        <td>{{ change.old_value }}</td>
                        <td>{{ change.new_value }}</td>
                        <td>{{ change.change_type }}</td>
                        <td>{{ change.reason }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% endif %}
            
            {% if result.issues %}
            <h4>이슈 ({{ result.issues|length }}개)</h4>
            <table>
                <thead>
                    <tr>
                        <th>심각도</th>
                        <th>메시지</th>
                        <th>제안</th>
                        <th>행 번호</th>
                    </tr>
                </thead>
                <tbody>
                    {% for issue in result.issues %}
                    <tr>
                        <td class="severity-{{ issue.severity }}">{{ issue.severity }}</td>
                        <td>{{ issue.message }}</td>
                        <td>{{ issue.suggestion or "" }}</td>
                        <td>{{ issue.line_number or "" }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
        """
        return Template(template_str)
    
    def generate(self, summary: MigrationSummary, results: List[FileMigrationResult]) -> str:
        """HTML 레포트 생성"""
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return self.template.render(
            report_date=report_date,
            server_name=summary.server_name,
            server_type=summary.server_type.value,
            from_version=summary.from_version,
            to_version=summary.to_version,
            total_files=summary.total_files,
            successful_files=summary.successful_files,
            warning_files=summary.warning_files,
            error_files=summary.error_files,
            manual_review_files=summary.manual_review_files,
            total_changes=summary.total_changes,
            total_issues=summary.total_issues,
            results=results
        )
    
    def save(self, summary: MigrationSummary, results: List[FileMigrationResult], output_path: str):
        """HTML 파일 저장"""
        html_content = self.generate(summary, results)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
