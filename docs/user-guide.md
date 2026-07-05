# 사용자 가이드

## 시작하기

### 설치

```bash
# 의존성 설치
pip install -r requirements.txt
```

### 기본 사용

```bash
# Apache 설정파일 마이그레이션
python src/main.py --server apache --from-version 2.4.39 --to-version 2.4.57 --input httpd.conf --output-dir output/

# Tomcat 설정파일 마이그레이션
python src/main.py --server tomcat --from-version 8.5 --to-version 10.1 --input server.xml --output-dir output/

# Wildfly 설정파일 마이그레이션
python src/main.py --server wildfly --from-version 13 --to-version 27 --input standalone.xml --output-dir output/
```

## 상세 사용법

### 단일 파일 마이그레이션

단일 설정파일을 마이그레이션하려면:

```bash
python src/main.py \
  --server apache \
  --from-version 2.4.39 \
  --to-version 2.4.57 \
  --input /etc/httpd/conf/httpd.conf \
  --output-dir output/
```

### 디렉토리 마이그레이션

디렉토리 내의 모든 설정파일을 마이그레이션하려면:

```bash
python src/main.py \
  --server tomcat \
  --from-version 8.5 \
  --to-version 10.1 \
  --input /opt/tomcat/conf/ \
  --output-dir output/ \
  --recursive
```

### 레포트 형식 선택

HTML 레포트만 생성:

```bash
python src/main.py \
  --server apache \
  --from-version 2.4.39 \
  --to-version 2.4.57 \
  --input httpd.conf \
  --output-dir output/ \
  --report html
```

Excel 레포트만 생성:

```bash
python src/main.py \
  --server apache \
  --from-version 2.4.39 \
  --to-version 2.4.57 \
  --input httpd.conf \
  --output-dir output/ \
  --report excel
```

두 레포트 모두 생성 (기본값):

```bash
python src/main.py \
  --server apache \
  --from-version 2.4.39 \
  --to-version 2.4.57 \
  --input httpd.conf \
  --output-dir output/ \
  --report both
```

## 지원하는 서버 및 버전

### Apache

| 버전 | 지원 여부 | 비고 |
|------|----------|------|
| 2.4.x | O | 2.4.39 → 2.4.57 등 |

### Tomcat

| 버전 | 지원 여부 | 비고 |
|------|----------|------|
| 8.5 | O | |
| 10.x | O | 10.1 등 |
| 11.x | O | |

### Wildfly

| 버전 | 지원 여부 | 비고 |
|------|----------|------|
| 13 | O | |
| 27 | O | |
| 38 | O | |

## 레포트 해석

### HTML 레포트

HTML 레포트는 다음 섹션으로 구성됩니다:

1. **요약**: 전체 마이그레이션 통계
2. **파일별 상세**: 각 파일의 마이그레이션 결과
3. **상세 내역**: 변경사항 및 이슈 상세

### Excel 레포트

Excel 레포트는 다음 시트로 구성됩니다:

1. **요약**: 전체 마이그레이션 통계
2. **상세**: 파일별 마이그레이션 결과
3. **이슈**: 모든 이슈 목록

### 상태 코드

| 상태 | 의미 | 조치 |
|------|------|------|
| success | 성공적으로 마이그레이션됨 | 그대로 적용 가능 |
| warning | 경고가 있음 | 검토 후 적용 권장 |
| error | 치명적 오류가 있음 | 수동 수정 필요 |
| manual_review | 수동 검토 필요 | 수동 검토 필수 |

## 일반적인 문제 해결

### 파일을 찾을 수 없음

```
오류: 파일을 찾을 수 없습니다: /path/to/file
```

**해결책**: 파일 경로가 올바른지 확인하세요.

### 지원하지 않는 서버

```
오류: 지원하지 않는 서버: unknown
```

**해결책**: `--server` 인자에 올바른 서버 이름을 입력하세요 (apache, tomcat, wildfly).

### 규칙 파일을 찾을 수 없음

```
경고: 규칙 파일을 찾을 수 없습니다: src/rules/apache24.yaml
```

**해결책**: 
- `--rules-dir` 인자로 올바른 규칙 파일 디렉토리를 지정하세요
- 해당 버전의 규칙 파일이 존재하는지 확인하세요

### XML 파싱 오류

```
오류: XML 파싱 실패
```

**해결책**: 
- XML 파일이 올바른 형식인지 확인하세요
- XML 파일의 인코딩이 UTF-8인지 확인하세요

## 팁

### 대용량 디렉토리 처리

대용량 디렉토리를 처리할 때는 `--recursive` 옵션을 사용하여 모든 하위 디렉토리를 포함하세요:

```bash
python src/main.py \
  --server tomcat \
  --from-version 8.5 \
  --to-version 10.1 \
  --input /opt/tomcat/ \
  --output-dir output/ \
  --recursive
```

### 사용자 정의 규칙 사용

사용자 정의 규칙을 사용하려면:

```bash
python src/main.py \
  --server apache \
  --from-version 2.4.39 \
  --to-version 2.4.57 \
  --input httpd.conf \
  --output-dir output/ \
  --rules-dir /path/to/custom/rules/
```

### 출력 디렉토리 구성

출력 디렉을 미리 생성할 필요는 없습니다. 툴이 자동으로 생성합니다:

```bash
python src/main.py \
  --server apache \
  --from-version 2.4.39 \
  --to-version 2.4.57 \
  --input httpd.conf \
  --output-dir /path/to/new/output/
```

## 예제 시나리오

### 시나리오 1: Apache 2.4.39 → 2.4.57

```bash
python src/main.py \
  --server apache \
  --from-version 2.4.39 \
  --to-version 2.4.57 \
  --input /etc/httpd/conf/httpd.conf \
  --output-dir output/apache_upgrade/
```

### 시나리오 2: Tomcat 8.5 → 10.1 (전체 conf 디렉토리)

```bash
python src/main.py \
  --server tomcat \
  --from-version 8.5 \
  --to-version 10.1 \
  --input /opt/tomcat/conf/ \
  --output-dir output/tomcat_upgrade/ \
  --recursive
```

### 시나리오 3: Wildfly 13 → 27 (단일 파일)

```bash
python src/main.py \
  --server wildfly \
  --from-version 13 \
  --to-version 27 \
  --input /opt/wildfly/standalone/configuration/standalone.xml \
  --output-dir output/wildfly_upgrade/
```

## 추가 지원

더 많은 도움이 필요하시면:

- GitHub Issue: 문제 보고 및 기능 요청
- 문서: `docs/architecture.md` - 아키텍처 상세 정보
