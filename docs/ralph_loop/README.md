# Ralph Loop 운영 가이드

Ralph Loop은 **작업 단위(Task) → 실행 → 검증 → 개선 → 재검증**을 반복해
품질을 끌어올리는 운영 방식입니다. 본 가이드는 정기 점검/컴플라이언스 시나리오에
Ralph Loop를 적용하는 표준 절차를 제공합니다.

## 핵심 원칙

- 작은 작업 단위로 쪼갠다.
- 각 작업에 **명확한 Pass/Fail 기준**을 둔다.
- 실패 시 개선 후 동일 작업을 반복한다.
- 반복 결과와 증거를 남긴다.

## 폴더 구조

```text
docs/ralph_loop/
  README.md
  task_template.yaml
  run_log_template.md
  summary_template.md
scripts/
  ralph_loop.py
  periodic_review.py
  aws_evidence_collect.py
```

## 빠른 시작

### 1. 작업 템플릿 작성

`docs/ralph_loop/task_template.yaml`을 복사해 작업 정의를 작성합니다.

### 2. 실행 폴더 생성

```bash
python3 scripts/ralph_loop.py init --run-id run-YYYY-MM-DD
```

### 3. 작업 정의 검증

```bash
python3 scripts/ralph_loop.py validate --tasks docs/ralph_loop/task_template.yaml
```

### 4. 요약 리포트 생성

```bash
python3 scripts/ralph_loop.py summary \
  --tasks docs/ralph_loop/task_template.yaml \
  --out reports/ralph_loop/run-YYYY-MM-DD/summary.md
```

### 5. 상세 리포트 생성 (템플릿 기반)

```bash
python3 scripts/ralph_loop.py report \
  --tasks docs/ralph_loop/task_template.yaml \
  --out reports/ralph_loop/run-YYYY-MM-DD/report.md
```

### 6. 정기 점검 플랜 자동 생성

```bash
python3 scripts/periodic_review.py plan \
  --config config/ralph_loop.yaml \
  --year 2026 \
  --create-runs
```

### 7. AWS 증거 수집 자동화 (읽기 전용)

```bash
python3 scripts/aws_evidence_collect.py \
  --discover-log-groups \
  --discover-out reports/ralph_loop/run-YYYY-MM-DD/discovered_log_groups.json \
  --cloudtrail \
  --start 2026-02-01 \
  --end 2026-02-02 \
  --s3-bucket com.sungmin.networks.talkcrm \
  --config config/ralph_loop.yaml
```

환경 분류 규칙과 필터는 `config/ralph_loop.yaml`의 `env_classification`, `env_filter`를 사용합니다.
운영 로그 포함이 필요하면 `--env-filter prod`를 명시하세요.

## 권장 운영 기준 (기본값)

- 반복 횟수: 최대 3회
- 반복 간 변경 기록: `run_log.md`
- 증거 패키지: `compliance-evidence/` 구조 사용
