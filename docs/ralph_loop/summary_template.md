# Ralph Loop 점검 요약 보고서

- Run ID: {{ run_id }}
- Generated: {{ generated_at }}
- Owner: {{ owner }}
- Environment: {{ environment }}

## 개요

- 목적: 정기 점검 및 컴플라이언스 검증
- 기준: HIPAA Security Rule + OWASP LLM Top 10(v1.1)
- 반복 방식: Ralph Loop (Task → Execute → Verify → Improve → Re-Verify)

## 요약

- 총 작업 수: {{ task_count }}
- 최대 반복 횟수(기본값): {{ max_iterations_default }}

## 작업 목록

| ID | Objective | Max Iterations | Evidence |
|---|---|---|---|
{% for task in tasks -%}
| {{ task.id }} | {{ task.objective }} | {{ task.max_iterations }} | {{ task.evidence }} |
{% endfor %}

## HIPAA 위험분석 매핑 (요약)

- 위험등록부 업데이트:
- 개선 조치:
- 재검증 결과:

## OWASP LLM Top 10 매핑 (요약)

- LLM01:
- LLM02:
- LLM03:
- LLM04:
- LLM05:
- LLM06:
- LLM07:
- LLM08:
- LLM09:
- LLM10:

## 증거 패키지

- 위치:
- 해시/무결성:

## 부록

- 관련 로그:
- 변경 이력:
