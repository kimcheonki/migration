# WEB/WAS 마이그레이션 툴

WEB/WAS 설정파일의 버전 마이그레이션을 지원하는 파이썬 도구입니다. AS-IS 서버와 TO-BE 서버 간의 방화벽이 미오픈된 환경에서 설정파일을 분석하고 호환 가능한 설정으로 변환하며, 적용 가능/불가 항목에 대한 레포트를 생성합니다.

## 지원하는 서버

### WEB 서버
- Apache (2.4.x)
- Nginx (향후 지원 예정)

### WAS 서버
- Tomcat (8.5, 10, 11)
- Wildfly (13, 27, 38)

## 주요 기능

- **설정파일 파싱**: Apache (.conf), Tomcat/Wildfly (.xml, .properties) 파일 파싱
- **버전별 마이그레이션 규칙**: 각 버전별 호환성 규칙 적용
- **자동 변환**: 호환 가능한 설정 자동 변환
- **호환성 검사**: 적용 가능/불가 항목 식별
- **다양한 레포트 형식**: HTML, Excel 형식의 상세 레포트 생성
- **확장 가능한 아키텍처**: 새로운 서버 및 버전 쉽게 추가 가능
- **대화형 모드**: 사용자 친화적인 대화형 인터페이스
- **자동 감지**: 설정파일 자동 감지 및 서버 타입 식별

## 설치

### 요구사항

- Python 3.8 이상
- pip

### 의존성 설치

```bash
pip install -r requirements.txt
```

또는

```bash
pip install pyyaml jinja2 lxml openpyxl
```

## 사용법

### 대화형 모드 (추천)

사용자 친화적인 대화형 모드를 사용하면 복잡한 명령행 인자 없이 쉽게 마이그레이션할 수 있습니다. 설정파일을 자동으로 감지하고 단계별로 안내합니다.

```bash
python src/main.py --interactive
```

또는

```bash
python src/main.py -I
```

대화형 모드에서는 다음 단계를 따르세요:
1. 설정파일 경로 입력 (드래그 앤 드롭 지원)
2. 서버 자동 감지 확인 또는 수동 선택
3. AS-IS 및 TO-BE 버전 입력
4. 출력 디렉토리 선택
5. 레포트 형식 선택
6. 마이그레이션 실행

### 기본 사용법 (명령행 모드)

```bash
# 단일 파일 마이그레이션
python src/main.py --server apache --from-version 2.4.39 --to-version 2.4.57 --input httpd.conf --output-dir output/

# 디렉토리 내 모든 파일 마이그레이션
python src/main.py --server tomcat --from-version 8.5 --to-version 10.1 --input /opt/tomcat/conf/ --output-dir output/ --recursive

# 특정 레포트 형식만 생성
python src/main.py --server wildfly --from-version 13 --to-version 27 --input standalone.xml --output-dir output/ --report html
```

### 명령행 인자

| 인자 | 설명 | 필수 |
|------|------|------|
| `--interactive`, `-I` | 대화형 모드 실행 | X |
| `--server`, `-s` | 서버 이름 (apache, tomcat, wildfly) | X (대화형 모드 시) |
| `--from-version`, `-f` | AS-IS 버전 | X (대화형 모드 시) |
| `--to-version`, `-t` | TO-BE 버전 | X (대화형 모드 시) |
| `--input`, `-i` | 입력 파일 또는 디렉토리 경로 | X (대화형 모드 시) |
| `--output-dir`, `-o` | 출력 디렉토리 경로 (기본값: output) | X |
| `--rules-dir` | 규칙 파일 디렉토리 (기본값: src/rules) | X |
| `--recursive`, `-r` | 디렉토리 재귀적 탐색 | X |
| `--report` | 레포트 타입 (html, excel, both) | X |

## 프로젝트 구조

```
migration/
├── README.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
├── .gitignore
│
├── docs/
│   ├── architecture.md
│   └── user-guide.md
│
├── config/
│   └── migration.yaml
│
├── samples/
│   ├── apache/
│   ├── tomcat/
│   └── wildfly/
│
├── src/
│   ├── main.py
│   ├── config.py
│   │
│   ├── analyzer/
│   │   └── analyzer.py
│   │
│   ├── parser/
│   │   ├── apache_parser.py
│   │   ├── tomcat_parser.py
│   │   └── wildfly_parser.py
│   │
│   ├── converter/
│   │   ├── apache_converter.py
│   │   ├── tomcat_converter.py
│   │   └── wildfly_converter.py
│   │
│   ├── report/
│   │   ├── excel_report.py
│   │   └── html_report.py
│   │
│   ├── rules/
│   │   ├── apache24.yaml
│   │   ├── tomcat10.yaml
│   │   ├── tomcat11.yaml
│   │   ├── wildfly27.yaml
│   │   └── wildfly38.yaml
│   │
│   ├── model/
│   │   ├── datasource.py
│   │   ├── deployment.py
│   │   ├── ssl_info.py
│   │   └── result.py
│   │
│   └── utils/
│       ├── logger.py
│       ├── file_utils.py
│       └── xml_utils.py
│
├── tests/
│   ├── test_apache.py
│   ├── test_tomcat.py
│   └── test_wildfly.py
│
└── output/
```

## 새로운 서버 추가 방법

새로운 WEB/WAS 서버를 추가하려면 다음 파일들을 생성/수정해야 합니다:

1. **파서 생성**: `src/parser/{server}_parser.py`
2. **컨버터 생성**: `src/converter/{server}_converter.py`
3. **규칙 파일 추가**: `src/rules/{server}{version}.yaml`
4. **테스트 파일 추가**: `tests/test_{server}.py`

자세한 내용은 `docs/architecture.md`를 참조하세요.

## 레포트

마이그레이션 완료 후 다음 레포트가 생성됩니다:

- **HTML 레포트**: 브라우저에서 확인 가능한 상세 레포트
- **Excel 레포트**: 요약, 상세, 이슈 시트로 구성된 엑셀 파일

레포트에는 다음 정보가 포함됩니다:

- 마이그레이션 요약 (성공/실패/경고 파일 수)
- 파일별 상세 내역
- 변경사항 목록
- 이슈 및 제안사항
- 호환성 분석 결과

## 테스트

```bash
# 전체 테스트 실행
python -m pytest tests/

# 특정 테스트 실행
python -m pytest tests/test_apache.py

# 특정 테스트 메서드 실행
python -m pytest tests/test_apache.py::TestApacheParser::test_parse_basic_config
```

## 기여

이 프로젝트에 기여하고 싶으시다면:

1. Fork 하세요
2. 기능 브랜치를 생성하세요 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋하세요 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시하세요 (`git push origin feature/AmazingFeature`)
5. Pull Request를 열어주세요

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 문의

문제가 있거나 제안사항이 있으면 Issue를 열어주세요.
