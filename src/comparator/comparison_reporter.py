"""
비교 결과 보고서 생성 모듈
HTML, 텍스트 형식의 비교 보고서 생성
"""
import json
from typing import Dict, Any
from pathlib import Path


class ComparisonReporter:
    """비교 결과 보고서 생성 클래스"""
    
    def __init__(self):
        """초기화"""
        pass
    
    def generate_html_report(self, comparison_result: Dict[str, Any], 
                           output_path: str) -> str:
        """
        HTML 형식의 비교 보고서 생성
        
        Args:
            comparison_result: 비교 결과
            output_path: 출력 파일 경로
            
        Returns:
            생성된 HTML 파일 경로
        """
        html_content = self._generate_html_content(comparison_result)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _generate_html_content(self, comparison_result: Dict[str, Any]) -> str:
        """HTML 콘텐츠 생성"""
        html = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>설정 파일 비교 보고서</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }
        .summary {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }
        .summary-item {
            margin: 10px 0;
            font-size: 16px;
        }
        .summary-item strong {
            color: #555;
        }
        .differences {
            margin-top: 30px;
        }
        .difference-card {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 20px;
            background-color: white;
        }
        .difference-card.high {
            border-left: 5px solid #f44336;
        }
        .difference-card.medium {
            border-left: 5px solid #ff9800;
        }
        .difference-card.low {
            border-left: 5px solid #4CAF50;
        }
        .keyword-name {
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .keyword-description {
            color: #666;
            font-style: italic;
            margin-bottom: 15px;
        }
        .priority-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            color: white;
            margin-left: 10px;
        }
        .priority-high {
            background-color: #f44336;
        }
        .priority-medium {
            background-color: #ff9800;
        }
        .priority-low {
            background-color: #4CAF50;
        }
        .detail-item {
            padding: 10px;
            margin: 5px 0;
            background-color: #f5f5f5;
            border-radius: 3px;
        }
        .detail-item.missing-in-as-is {
            background-color: #ffebee;
            border-left: 3px solid #f44336;
        }
        .detail-item.missing-in-to-be {
            background-color: #fff3e0;
            border-left: 3px solid #ff9800;
        }
        .detail-item.mismatched {
            background-color: #e8f5e9;
            border-left: 3px solid #4CAF50;
        }
        .no-differences {
            text-align: center;
            padding: 40px;
            color: #4CAF50;
            font-size: 18px;
        }
        .values-section {
            margin-top: 15px;
            padding: 10px;
            background-color: #fafafa;
            border-radius: 3px;
        }
        .values-title {
            font-weight: bold;
            color: #555;
            margin-bottom: 5px;
        }
        .values-content {
            font-family: 'Courier New', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            word-break: break-all;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 설정 파일 비교 보고서</h1>
        
        <div class="summary">
            <h2>📋 요약</h2>
            <div class="summary-item">
                <strong>서버:</strong> {server}
            </div>
            <div class="summary-item">
                <strong>분석된 키워드:</strong> {analyzed}/{total}
            </div>
            <div class="summary-item">
                <strong>차이점 발견:</strong> {differences}
            </div>
            <div class="summary-item" style="margin-left: 20px;">
                <strong>AS-IS 누락:</strong> {missing_as_is}
            </div>
            <div class="summary-item" style="margin-left: 20px;">
                <strong>TO-BE 누락:</strong> {missing_to_be}
            </div>
            <div class="summary-item" style="margin-left: 20px;">
                <strong>설정 불일치:</strong> {mismatched}
            </div>
        </div>
        
        <div class="differences">
            <h2>🔍 차이점 상세</h2>
            {differences_html}
        </div>
    </div>
</body>
</html>"""
        
        summary = comparison_result['summary']
        server = comparison_result['server'].upper()
        
        # 차이점 HTML 생성
        if comparison_result['differences']:
            differences_html = ""
            for diff in comparison_result['differences']:
                priority_class = diff['priority']  # 3=high, 2=medium, 1=low
                priority_str = {3: '높음', 2: '중간', 1: '낮음'}[diff['priority']]
                priority_badge = {3: 'high', 2: 'medium', 1: 'low'}[diff['priority']]
                
                details_html = ""
                for detail in diff['differences_detail']:
                    detail_type = detail.get('type', '')
                    detail_class = detail_type.replace('_', '-')
                    details_html += f"""
                    <div class="detail-item {detail_class}">
                        {detail['message']}
                    </div>"""
                
                # 값 섹션
                values_html = ""
                if diff['as_is_values'] or diff['to_be_values']:
                    values_html += """
                    <div class="values-section">
                        <div class="values-title">AS-IS 값:</div>
                        <div class="values-content">{}</div>
                        <div class="values-title">TO-BE 값:</div>
                        <div class="values-content">{}</div>
                    </div>""".format(
                        json.dumps(diff['as_is_values'], indent=2, ensure_ascii=False) if diff['as_is_values'] else '없음',
                        json.dumps(diff['to_be_values'], indent=2, ensure_ascii=False) if diff['to_be_values'] else '없음'
                    )
                
                differences_html += f"""
                <div class="difference-card {priority_class}">
                    <div class="keyword-name">
                        {diff['keyword']}
                        <span class="priority-badge priority-{priority_badge}">우선순위: {priority_str}</span>
                    </div>
                    <div class="keyword-description">{diff['description']}</div>
                    {details_html}
                    {values_html}
                </div>"""
        else:
            differences_html = """
            <div class="no-differences">
                ✅ 차이점이 없습니다. AS-IS 파일이 TO-BE 샘플과 일치합니다.
            </div>"""
        
        html = html.format(
            server=server,
            analyzed=summary['analyzed_keywords'],
            total=summary['total_keywords'],
            differences=summary['differences_found'],
            missing_as_is=summary['missing_in_as_is'],
            missing_to_be=summary['missing_in_to_be'],
            mismatched=summary['mismatched'],
            differences_html=differences_html
        )
        
        return html
    
    def generate_text_report(self, comparison_result: Dict[str, Any]) -> str:
        """
        텍스트 형식의 비교 보고서 생성
        
        Args:
            comparison_result: 비교 결과
            
        Returns:
            텍스트 보고서
        """
        report = []
        report.append("=" * 60)
        report.append(f"설정 파일 비교 보고서 - {comparison_result['server'].upper()}")
        report.append("=" * 60)
        report.append("")
        
        summary = comparison_result['summary']
        report.append("📋 요약")
        report.append("-" * 40)
        report.append(f"분석된 키워드: {summary['analyzed_keywords']}/{summary['total_keywords']}")
        report.append(f"차이점 발견: {summary['differences_found']}")
        report.append(f"  - AS-IS 누락: {summary['missing_in_as_is']}")
        report.append(f"  - TO-BE 누락: {summary['missing_in_to_be']}")
        report.append(f"  - 설정 불일치: {summary['mismatched']}")
        report.append("")
        
        if comparison_result['differences']:
            report.append("🔍 차이점 상세")
            report.append("-" * 40)
            
            for diff in comparison_result['differences']:
                priority_str = {3: '높음', 2: '중간', 1: '낮음'}[diff['priority']]
                report.append(f"\n키워드: {diff['keyword']} (우선순위: {priority_str})")
                report.append(f"설명: {diff['description']}")
                
                for detail in diff['differences_detail']:
                    report.append(f"  - {detail['message']}")
                
                if diff['as_is_values']:
                    report.append(f"  AS-IS 값: {json.dumps(diff['as_is_values'], ensure_ascii=False)}")
                if diff['to_be_values']:
                    report.append(f"  TO-BE 값: {json.dumps(diff['to_be_values'], ensure_ascii=False)}")
        else:
            report.append("✅ 차이점이 없습니다. AS-IS 파일이 TO-BE 샘플과 일치합니다.")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
