<div align="center">

<img src="docs/logo.svg" alt="Guardian Logo" width="200" />

# 🔐 Guardian

### AI 기반 침투 테스트 자동화 플랫폼

[한국어](README.md) | [English](README_EN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Guardian**은 여러 AI 제공자(OpenAI GPT-4, Claude, Google Gemini, OpenRouter)와 검증된 보안 도구들을 결합해 지능적이고 적응적인 보안 점검을 수행하는 엔터프라이즈급 침투 테스트 자동화 프레임워크입니다. 모든 결과는 증거 기반으로 체계적으로 기록됩니다.

[기능](#-기능) • [설치](#-설치) • [빠른 시작](#-빠른-시작) • [문서](#-문서) • [기여](#-기여)

</div>

---

## ⚠️ 법적 고지

**Guardian은 허가받은 보안 테스트 및 교육 목적에만 사용하도록 설계되었습니다.**

- ✅ **합법적 사용**: 승인된 침투 테스트, 보안 연구, 교육 환경
- ❌ **불법적 사용**: 무단 접근, 악성 행위, 모든 형태의 사이버 공격

**테스트 대상에 대해 명시적 서면 허가가 있는지 확인할 책임은 전적으로 사용자에게 있습니다.** 무단 시스템 접근은 CFAA, GDPR 및 각국의 관련 법률에 의해 불법입니다.

**Guardian을 사용하는 경우, 본인이 소유했거나 명시적으로 테스트 허가를 받은 시스템에서만 사용해야 합니다.**

---

## ✨ 기능

### 🤖 멀티 제공자 AI 인텔리전스

- **4개 AI 제공자 지원**: OpenAI (GPT-4o), Anthropic (Claude), Google (Gemini), OpenRouter
- **유연한 제공자 선택**: 설정 또는 커맨드라인에서 제공자 전환
- **멀티 에이전트 아키텍처**: Planner, Tool Selector, Analyst, Reporter 에이전트 협업
- **전략적 의사 결정**: AI가 결과를 분석해 최적의 다음 단계를 결정
- **적응형 테스트**: 발견된 취약점과 반응에 맞춰 전술 자동 조정
- **오탐 필터링**: 지능형 분석으로 노이즈 감소 및 실제 취약점 집중

### 🛠️ 방대한 도구 통합

**19개 보안 도구 통합:**
- **네트워크**: Nmap (정밀 스캔), Masscan (초고속 스캔)
- **웹 정찰**: httpx (HTTP 탐지), WhatWeb (기술 스택 식별), Wafw00f (WAF 탐지)
- **서브도메인 발견**: Subfinder (패시브 열거), Amass (액티브/패시브 매핑), DNSRecon (DNS 분석)
- **취약점 스캐닝**: Nuclei (템플릿 기반), Nikto (웹 취약점), SQLMap (SQL 인젝션), WPScan (WordPress)
- **SSL/TLS 테스트**: TestSSL (암호 스위트 분석), SSLyze (고급 설정 분석)
- **콘텐츠 탐색**: Gobuster (디렉터리 브루트), FFuf (웹 퍼징), Arjun (파라미터 탐색)
- **보안 분석**: XSStrike (XSS 탐지), GitLeaks (시크릿 스캔), CMSeeK (CMS 탐지)

### 📊 증거 기반 기록 강화

- **실행 추적**: 모든 발견 사항을 도구 실행 기록과 연결
- **명령 이력 보존**: 각 실행의 전체 출력 기록
- **원본 증거 저장**: 도구 출력의 2000자 스니펫 저장
- **세션 재현성**: 특정 스캔의 명령과 출력 완전 재구성 가능

### 🔄 스마트 워크플로 시스템

- **파라미터 우선순위**: 워크플로 파라미터가 설정값보다 우선
- **자급형 워크플로**: 워크플로 내에서 도구 파라미터 정의
- **퍼지 매칭**: 워크플로 파일 자동 탐색 및 로딩
- **다중 보고서 형식**: Markdown, HTML, JSON 지원 (증거 포함)

### 🔒 보안 및 컴플라이언스

- **스코프 검증**: 사설망 및 미허가 대상 자동 차단
- **감사 로깅**: AI 의사결정 및 작업 로그 완전 기록
- **Human-in-the-Loop**: 민감 작업 시 확인 프롬프트 설정 가능
- **Safe Mode**: 기본값으로 파괴적 동작 방지

### 📋 전문 보고서

- **다중 형식 지원**: Markdown, HTML, JSON
- **요약 리포트**: 비기술 이해관계자용 요약
- **기술 상세 보고**: 취약점, 증거, 개선 방안 포함
- **증거 섹션**: 원본 도구 출력 포함
- **AI 판단 기록**: AI 분석 과정 투명화

### ⚡ 성능 및 효율

- **비동기 실행**: 도구 병렬 실행으로 속도 향상
- **워크플로 자동화**: 사전 정의된 Recon, Web, Network, Autonomous
- **확장성**: YAML/Python으로 커스텀 도구와 워크플로 제작

---

## 📋 사전 요구사항

### 필수

- **Python 3.11 이상** ([Download](https://www.python.org/downloads/))
- **AI 제공자 API 키** (중 택 1):
  - OpenAI API Key ([Get it here](https://platform.openai.com/api-keys))
  - Anthropic API Key ([Get it here](https://console.anthropic.com/))
  - Google AI Studio API Key ([Get it here](https://makersuite.google.com/app/apikey))
  - OpenRouter API Key ([Get it here](https://openrouter.ai/keys))
- **Git** (레포 클론)

### 선택 (전체 기능 사용 시 권장)

Guardian은 아래 도구가 설치되어 있으면 더 많은 작업을 수행할 수 있습니다:

| Tool | 목적 | 설치 |
|------|------|------|
| **nmap** | 포트 스캐닝 | `apt install nmap` / `choco install nmap` |
| **masscan** | 초고속 스캔 | `apt install masscan` / 소스 빌드 |
| **httpx** | HTTP 탐지 | `go install github.com/projectdiscovery/httpx/cmd/httpx@latest` |
| **subfinder** | 서브도메인 열거 | `go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest` |
| **amass** | 네트워크 매핑 | `go install github.com/owasp-amass/amass/v4/...@master` |
| **nuclei** | 취약점 스캔 | `go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest` |
| **whatweb** | 기술 스택 식별 | `gem install whatweb` / `apt install whatweb` |
| **wafw00f** | WAF 탐지 | `pip install wafw00f` |
| **nikto** | 웹 취약점 스캔 | `apt install nikto` |
| **sqlmap** | SQL 인젝션 | `pip install sqlmap` / `apt install sqlmap` |
| **wpscan** | WordPress 스캔 | `gem install wpscan` |
| **testssl** | SSL/TLS 테스트 | [testssl.sh](https://testssl.sh/)에서 다운로드 |
| **sslyze** | SSL/TLS 분석 | `pip install sslyze` |
| **gobuster** | 디렉터리 브루트 | `go install github.com/OJ/gobuster/v3@latest` |
| **ffuf** | 웹 퍼징 | `go install github.com/ffuf/ffuf/v2@latest` |
| **arjun** | 파라미터 탐색 | `pip install arjun` |
| **xsstrike** | 고급 XSS 탐지 | `git clone https://github.com/s0md3v/XSStrike` |
| **gitleaks** | 시크릿 스캔 | `go install github.com/zricethezav/gitleaks/v8@latest` |
| **cmseek** | CMS 탐지 | `pip install cmseek` |
| **dnsrecon** | DNS 열거 | `pip install dnsrecon` |

> **참고**: Guardian은 외부 도구 없이도 작동하지만 스캔 기능이 제한됩니다. AI는 사용 가능한 도구에 따라 전략을 조정합니다.

---

## 🚀 설치

### 1단계: 레포 클론

```bash
git clone https://github.com/zakirkun/guardian-cli.git
cd guardian-cli
```

### 2단계: Python 환경 구성

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -e .
```

### 3단계: AI 제공자 설정

Guardian은 여러 AI 제공자를 지원합니다. `config/guardian.yaml`에서 선호 제공자를 설정하세요:

```yaml
# config/guardian.yaml
ai:
  # 제공자 선택: openai, claude, gemini, openrouter
  provider: openai

  # OpenAI 설정 (권장)
  openai:
    model: gpt-4o
    api_key: sk-your-api-key-here  # 또는 OPENAI_API_KEY env var 사용

  # Claude 설정
  claude:
    model: claude-3-5-sonnet-20241022
    api_key: null  # 또는 ANTHROPIC_API_KEY env var 사용

  # Gemini 설정
  gemini:
    model: gemini-2.5-pro
    api_key: null  # 또는 GOOGLE_API_KEY env var 사용

  # OpenRouter 설정
  openrouter:
    model: anthropic/claude-3.5-sonnet
    api_key: null  # 또는 OPENROUTER_API_KEY env var 사용
```

**또는 환경 변수로 설정:**

```bash
# Linux/macOS
export OPENAI_API_KEY="sk-your-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
export GOOGLE_API_KEY="your-gemini-key"
export OPENROUTER_API_KEY="your-router-key"

# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key-here"
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### 4단계: 설정 초기화

```bash
# 설치 확인
python -m cli.main --help

# AI 제공자 상태 확인
python -m cli.main models
```

---

## 🎯 빠른 시작

### 기본 명령어

```bash
# 워크플로 목록 확인
python -m cli.main workflow list

# AI 제공자와 모델 확인
python -m cli.main models

# 특정 제공자로 실행
python -m cli.main workflow run --name web_pentest --target example.com --provider openai
```

### 예시 시나리오

#### 1. 웹 애플리케이션 빠른 점검
```bash
# 증거 기록 포함 빠른 점검
python -m cli.main workflow run --name web_pentest --target https://dvwa.csalab.app
```

**예상 결과:**
- ✅ httpx로 HTTP 탐지
- ✅ nuclei로 취약점 스캔
- ✅ 실행 증거 링크 (명령 + 출력)
- ✅ Markdown 보고서 생성

#### 2. 네트워크 종합 평가
```bash
# 전체 네트워크 침투 테스트
python -m cli.main workflow run --name network --target 192.168.1.0/24
```

#### 3. 파라미터 포함 커스텀 워크플로
```bash
# 워크플로 파라미터로 실행
# 워크플로 YAML 파라미터가 설정값보다 우선
python -m cli.main workflow run --name web_pentest --target example.com
```

**워크플로 파라미터 우선순위:**
1. 워크플로 YAML 파라미터 (최우선)
2. 설정 파일 파라미터
3. 도구 기본값 (최하위)

#### 4. 세션 기반 보고서 생성
```bash
# 증거 포함 HTML 보고서 생성
python -m cli.main report --session 20260203_175905 --format html
```

#### 5. AI 제공자 전환
```bash
# OpenAI GPT-4 사용
python -m cli.main workflow run --name web_pentest --target example.com --provider openai

# Claude 사용
python -m cli.main workflow run --name web_pentest --target example.com --provider claude

# Gemini 사용
python -m cli.main workflow run --name web_pentest --target example.com --provider gemini
```

> **Windows 사용자**: `guardian` 대신 `python -m cli.main`을 사용하세요.

---

## 🔧 설정

### 전체 설정 참고

`config/guardian.yaml`을 편집해 Guardian 동작을 커스터마이징할 수 있습니다:

```yaml
# AI 설정
ai:
  provider: openai  # openai, claude, gemini, openrouter

  openai:
    model: gpt-4o
    api_key: sk-your-key  # 또는 OPENAI_API_KEY env var 사용

  claude:
    model: claude-3-5-sonnet-20241022
    api_key: null

  gemini:
    model: gemini-2.5-pro
    api_key: null

  temperature: 0.2
  max_tokens: 8000

# 침투 테스트 설정
pentest:
  safe_mode: true              # 파괴적 동작 방지
  require_confirmation: true   # 각 단계 실행 전 확인
  max_parallel_tools: 3        # 동시 도구 실행 수
  max_depth: 3                 # 최대 스캔 깊이
  tool_timeout: 300            # 도구 타임아웃 (초)

# 출력 설정
output:
  format: markdown             # markdown, html, json
  save_path: ./reports
  include_reasoning: true
  verbosity: normal            # quiet, normal, verbose, debug

# 스코프 검증
scope:
  blacklist:                   # 절대 스캔하지 않음
    - 127.0.0.0/8
    - 10.0.0.0/8
    - 172.16.0.0/12
    - 192.168.0.0/16
  require_scope_file: false
  max_targets: 100

# 도구 기본 설정
tools:
  httpx:
    threads: 50
    timeout: 10
    tech_detect: true

  nuclei:
    severity: ["critical", "high", "medium"]
    templates_path: ~/nuclei-templates

  nmap:
    default_args: "-sV -sC"
    timing: T4
```

### 워크플로 파라미터

`workflows/` 디렉터리에 커스텀 워크플로를 만들 수 있습니다:

```yaml
# workflows/custom_web.yaml
name: custom_web_assessment
description: Custom web security testing

steps:
  - name: http_discovery
    type: tool
    tool: httpx
    parameters:
      threads: 100        # 설정 기본값(50) override
      timeout: 15         # 설정 기본값(10) override
      tech_detect: true

  - name: vulnerability_scan
    type: tool
    tool: nuclei
    parameters:
      severity: ["critical", "high"]  # 설정값 override
      templates_path: ".shared/nuclei/templates/"

  - name: generate_report
    type: report
    # format은 설정 기본값(markdown) 사용
```

**파라미터 우선순위:**
- 워크플로 파라미터 **우선**
- 설정 파라미터
- 도구 기본값

---

## 📖 문서

### 사용자 가이드
- **[한국어 빠른 시작](docs/QUICKSTART_KO.md)** - 한국어 빠른 시작 가이드
- **[빠른 시작 가이드](QUICKSTART.md)** - 영문 빠른 시작
- **[명령어 참고](docs/)** - 모든 명령에 대한 상세 문서
- **[설정 가이드](config/guardian.yaml)** - 전체 설정 참고
- **[워크플로 가이드](docs/WORKFLOW_GUIDE.md)** - 커스텀 워크플로 제작

### 개발자 가이드
- **[커스텀 도구 만들기](docs/TOOLS_DEVELOPMENT_GUIDE.md)** - 도구 통합 제작
- **[워크플로 개발](docs/WORKFLOW_GUIDE.md)** - 워크플로 제작 가이드
- **[도구 목록](tools/README.md)** - 통합 도구 개요

### 아키텍처 개요

```
Guardian Architecture:
┌─────────────────────────────────────────┐
│         AI Provider Layer               │
│  (OpenAI, Claude, Gemini, OpenRouter)   │
└─────────────────────────────────────────┘
                 │
┌─────────────────────────────────────────┐
│       Multi-Agent System                │
│  Planner → Tool Agent → Analyst →      │
│            Reporter                      │
└─────────────────────────────────────────┘
                 │
┌─────────────────────────────────────────┐
│      Workflow Engine                    │
│  - Parameter Priority                   │
│  - Evidence Capture                     │
│  - Session Management                   │
└─────────────────────────────────────────┘
                 │
┌─────────────────────────────────────────┐
│      Tool Integration Layer             │
│  (19 Security Tools)                    │
└─────────────────────────────────────────┘
```

---

## 🏗️ 프로젝트 구조

```
guardian-cli/
├── ai/                    # AI 통합
│   └── providers/         # 멀티 제공자 지원
│       ├── base_provider.py
│       ├── openai_provider.py
│       ├── claude_provider.py
│       ├── gemini_provider.py
│       └── openrouter_provider.py
├── cli/                   # CLI
│   └── commands/         # CLI 명령 (init, scan, recon 등)
├── core/                  # 코어 에이전트 시스템
│   ├── agent.py          # 에이전트 베이스
│   ├── planner.py        # 플래너 에이전트
│   ├── tool_agent.py     # 도구 선택 에이전트
│   ├── analyst_agent.py  # 분석 에이전트
│   ├── reporter_agent.py # 보고서 에이전트
│   ├── memory.py         # 상태 관리
│   └── workflow.py       # 워크플로 오케스트레이션
├── tools/                 # 펜테스트 도구 래퍼
│   ├── nmap.py           # Nmap 통합
│   ├── masscan.py        # Masscan 통합
│   ├── httpx.py          # httpx 통합
│   ├── subfinder.py      # Subfinder 통합
│   ├── amass.py          # Amass 통합
│   ├── nuclei.py         # Nuclei 통합
│   ├── sqlmap.py         # SQLMap 통합
│   ├── wpscan.py         # WPScan 통합
│   ├── whatweb.py        # WhatWeb 통합
│   ├── wafw00f.py        # Wafw00f 통합
│   ├── nikto.py          # Nikto 통합
│   ├── testssl.py        # TestSSL 통합
│   ├── sslyze.py         # SSLyze 통합
│   ├── gobuster.py       # Gobuster 통합
│   ├── ffuf.py           # FFuf 통합
│   └── ...               # 총 15개 도구
├── workflows/             # 워크플로 정의 (YAML)
├── utils/                 # 유틸리티 (로깅, 검증)
├── config/                # 설정 파일
├── docs/                  # 문서
└── reports/               # 생성된 보고서
```

---

## 🆕 최신 업데이트

### Version 2.0.0 - Major Release

#### ✨ 멀티 제공자 AI 지원
- **4개 AI 제공자**: OpenAI, Claude, Gemini, OpenRouter
- **간편 전환**: `config/guardian.yaml` 또는 CLI 플래그
- **추상화 레이어**: 제공자 통합 인터페이스

#### 📊 증거 기록 시스템
- **실행 링크**: 모든 발견 사항을 도구 실행과 연결
- **원본 증거**: 전체 명령 출력 보존 (2000자 스니펫)
- **추적성**: 세션 단위로 전체 실행 재현 가능

#### 🔄 스마트 워크플로 파라미터
- **우선순위**: 워크플로 > 설정 > 기본값
- **자급형**: 워크플로 자체 설정 포함
- **충돌 없음**: 서로 다른 워크플로가 다른 파라미터 사용 가능

#### 🐛 버그 수정
- 워크플로 퍼지 매칭 로직 수정
- 보고서 포맷 처리 수정
- YAML 파싱 에러 메시지 개선

---

## 🤝 기여

기여를 환영합니다. 아래 절차를 따라주세요:

### 개발 환경 설정

```bash
# Fork & Clone
git clone https://github.com/zakirkun/guardian-cli.git
cd guardian-cli

# 개발 의존성 설치
pip install -e ".[dev]"

# 테스트 실행
pytest tests/

# 코드 포맷
black .
```

### 기여 분야

- 🤖 **AI 제공자 통합** - 더 많은 모델 지원
- 🛠️ **신규 도구 통합** - 추가 보안 도구 지원
- 🔄 **커스텀 워크플로** - 워크플로 템플릿 공유
- 🐛 **버그 수정** - 이슈 리포트 및 수정
- 📚 **문서 개선** - 가이드 및 예제 보강
- 🧪 **테스트** - 테스트 커버리지 확장

자세한 내용은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.

---

## 📊 로드맵

- [x] 멀티 제공자 AI 지원 (OpenAI, Claude, Gemini, OpenRouter)
- [x] 증거 기록 및 실행 링크
- [x] 워크플로 파라미터 우선순위
- [ ] 웹 대시보드
- [ ] PostgreSQL 기반 멀티 세션 추적
- [ ] MITRE ATT&CK 매핑
- [ ] 커스텀 모듈 플러그인 시스템
- [ ] CI/CD 파이프라인 통합
- [ ] 추가 AI 모델 (Llama, Mistral)
- [ ] 실시간 협업 기능

---

## 🐛 문제 해결

### 일반적인 이슈

**Import 오류**
```bash
# 의존성 재설치
pip install -e . --force-reinstall
```

**AI 제공자 오류**
```bash
# API 키 확인
python -m cli.main models

# 제공자 설정 확인
cat config/guardian.yaml | grep -A 5 "ai:"
```

**도구를 찾을 수 없음**
```bash
# 도구 설치 여부 확인
which nmap
which httpx

# 누락된 도구 설치 (사전 요구사항 참고)
```

**워크플로가 로딩되지 않음**
```bash
# 워크플로 파일 존재 확인
ls workflows/web_pentest.yaml

# YAML 문법 확인
python -c "import yaml; yaml.safe_load(open('workflows/web_pentest.yaml'))"
```

**Windows에서 명령어 인식 오류**
```powershell
# 전체 명령 사용
python -m cli.main --help
```

추가 도움이 필요하면 이슈를 등록하세요.

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스입니다. 자세한 내용은 [LICENSE](LICENSE)를 참고하세요.

---

## 🙏 감사의 말

- **OpenAI** - GPT-4 기능 지원
- **Anthropic** - Claude AI
- **Google** - Gemini AI
- **LangChain** - AI 오케스트레이션 프레임워크
- **ProjectDiscovery** - 오픈소스 보안 도구 (httpx, subfinder, nuclei)
- **Nmap** - 네트워크 탐색 및 보안 감사
- **Security Community** - 도구 개발자 및 연구자

---

## 📞 지원 및 문의

- **GitHub Issues**: [버그/기능 요청](https://github.com/zakirkun/guardian-cli/issues)
- **Discussions**: [커뮤니티 토론](https://github.com/zakirkun/guardian-cli/discussions)
- **문서**: [docs](docs/)
- **보안 제보**: security@example.com

---

## ⭐ Star History

Guardian이 도움이 되었다면 Star 부탁드립니다.

---

<div align="center">

**Guardian** - 지능적이고 윤리적이며 자동화된 침투 테스트

Made with ❤️ by the Security Community

[⬆ Back to Top](#-guardian)

</div>
