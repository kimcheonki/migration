# 아키텍처 문서

## 시스템 아키텍처

### 전체 구조

```
┌─────────────────────────────────────────────────────────────┐
│                         사용자                                │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      main.py (CLI)                           │
│  - 명령행 인자 파싱                                           │
│  - 마이그레이션 워크플로우 조정                               │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   Config      │ │ FileUtils     │ │  Logger       │
│  (규칙 로드)   │ │ (파일 처리)    │ │ (로깅)        │
└───────────────┘ └───────────────┘ └───────────────┘
          │               │
          └───────┬───────┘
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                     MigrationTool                            │
│  - 마이그레이션 코디네이터                                    │
│  - 파서/컨버터 관리                                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│    Parser     │ │  Converter    │ │  Analyzer     │
│  (설정 파싱)   │ │  (설정 변환)   │ │  (결과 분석)   │
└───────────────┘ └───────────────┘ └───────────────┘
          │               │               │
          └───────────────┼───────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      ReportGenerator                          │
│  - HTML 레포트 생성                                          │
│  - Excel 레포트 생성                                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      출력 파일                               │
│  - 변환된 설정파일                                           │
│  - HTML 레포트                                              │
│  - Excel 레포트                                             │
└─────────────────────────────────────────────────────────────┘
```

## 모듈 상세 설명

### 1. Core 모듈

#### main.py
- CLI 인터페이스 제공
- 전체 마이그레이션 워크플로우 조정
- 사용자 입력 검증

#### config.py
- 마이그레이션 규칙 로드
- 규칙 캐싱
- 버전별 규칙 관리

### 2. Parser 모듈

#### apache_parser.py
- Apache .conf 파일 파싱
- 디렉티브 추출
- SSL/Worker 설정 추출

#### tomcat_parser.py
- Tomcat XML 파일 파싱
- Properties 파일 파싱
- Connector/Executor/Datasource 설정 추출

#### wildfly_parser.py
- Wildfly XML 파일 파싱
- Properties 파일 파싱
- Datasource/Thread Pool/SSL 설정 추출

### 3. Converter 모듈

#### apache_converter.py
- Apache 설정 변환
- 버전별 호환성 규칙 적용
- 변경사항 추적

#### tomcat_converter.py
- Tomcat 설정 변환
- XML/Properties 형식 처리
- 버전별 호환성 규칙 적용

#### wildfly_converter.py
- Wildfly 설정 변환
- XML/Properties 형식 처리
- 버전별 호환성 규칙 적용

### 4. Analyzer 모듈

#### analyzer.py
- 마이그레이션 결과 분석
- 호환성 검사
- 치명적 이슈 식별
- 통계 정보 생성

### 5. Report 모듈

#### excel_report.py
- Excel 형식 레포트 생성
- 요약/상세/이슈 시트 생성
- 스타일링 적용

#### html_report.py
- HTML 형식 레포트 생성
- Jinja2 템플릿 사용
- 반응형 디자인

### 6. Model 모듈

#### result.py
- 마이그레이션 결과 데이터 모델
- ConfigChange, MigrationIssue, FileMigrationResult
- MigrationSummary

#### datasource.py
- 데이터소스 설정 모델
- DatasourceConfig

#### deployment.py
- 배포 설정 모델
- DeploymentConfig

#### ssl_info.py
- SSL 설정 모델
- SSLConfig

### 7. Utils 모듈

#### logger.py
- 로깅 유틸리티
- 싱글톤 패턴
- 콘솔 출력

#### file_utils.py
- 파일 읽기/쓰기
- 파일 타입 식별
- 디렉토리 탐색

#### xml_utils.py
- XML 파싱 유틸리티
- 요소/속성 추출
- XML ↔ 딕셔너리 변환

## 데이터 흐름

```
1. 사용자 입력
   ↓
2. 설정파일 로드 (FileUtils)
   ↓
3. 설정파일 파싱 (Parser)
   ↓
4. 마이그레이션 규칙 로드 (Config)
   ↓
5. 설정 변환 (Converter)
   ↓
6. 결과 분석 (Analyzer)
   ↓
7. 레포트 생성 (ReportGenerator)
   ↓
8. 파일 저장 (FileUtils)
```

## 확장성

### 새로운 서버 추가

1. **Parser 구현**
   ```python
   class NewServerParser:
       def parse(self, content: str) -> Dict:
           # 파싱 로직 구현
           pass
   ```

2. **Converter 구현**
   ```python
   class NewServerConverter:
       def convert(self, parsed: Dict) -> FileMigrationResult:
           # 변환 로직 구현
           pass
   ```

3. **규칙 파일 추가**
   ```yaml
   # src/rules/newserver10.yaml
   server: newserver
   version: "10"
   directives:
     - name: config_key
       pattern: ...
   ```

4. **등록**
   ```python
   # main.py
   self.parsers['newserver'] = NewServerParser()
   self.converters['newserver'] = NewServerConverter
   ```

### 새로운 레포트 형식 추가

1. **ReportGenerator 구현**
   ```python
   class NewReportGenerator:
       def generate(self, summary, results):
           # 레포트 생성 로직
           pass
   ```

2. **등록**
   ```python
   # main.py
   tool.generate_reports(summary, results, output_dir, ['new'])
   ```

## 설계 원칙

1. **단일 책임 원칙**: 각 모듈은 하나의 책임만 가짐
2. **개방-폐쇄 원칙**: 확장에는 열려 있고, 수정에는 닫혀 있음
3. **의존성 역전 원칙**: 추상화에 의존, 구체화에 의존하지 않음
4. **인터페이스 분리 원칙**: 클라이언트가 사용하지 않는 인터페이스에 의존하지 않음

## 성능 고려사항

- 규칙 파일 캐싱으로 반복 로드 방지
- 대용량 파일 처리를 위한 스트리밍 파싱 고려 (향후 개선)
- 병렬 처리 지원 (향후 개선)

## 보안 고려사항

- 민감 정보 (비밀번호 등) 마스킹 처리
- 파일 경로 검증
- 입력 데이터 검증
