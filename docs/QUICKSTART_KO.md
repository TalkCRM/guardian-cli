# Guardian 빠른 시작 가이드 (한국어)

Guardian CLI를 빠르게 설치하고 실행하는 방법을 안내합니다.

## 설치

### 1. 프로젝트 디렉터리로 이동

```bash
cd /path/to/guardian-cli
```

Windows 예시:

```cmd
cd c:\Users\MyUser\workarea\guardian-cli
```

### 2. 가상환경 생성 및 활성화

macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```cmd
python -m venv venv
.\venv\Scripts\activate
```

### 3. Guardian 설치

```bash
pip install -e .
```

### 4. 설정 초기화

```bash
python -m cli.main init
```

### 5. 인증 설정

옵션 A: Antigravity Auth (무료/쿼터)

```bash
python -m cli.main auth login
```

옵션 B: 표준 API 키

`.env` 파일에 키를 저장합니다:

```bash
echo GOOGLE_API_KEY=your_key_here > .env
```

## 주요 명령어

워크플로 목록 확인:

```bash
python -m cli.main workflow list
```

정찰 드라이런 실행:

```bash
python -m cli.main recon --domain example.com --dry-run
```

포트 스캔 실행 (nmap 필요):

```bash
python -m cli.main scan --target scanme.nmap.org
```

전체 워크플로 실행:

```bash
python -m cli.main workflow run --name recon --target example.com
```

특정 모델로 실행:

```bash
python -m cli.main recon --domain example.com --model gemini-3-pro
```

## 설정

다음 파일을 편집해 설정을 변경할 수 있습니다:

- `config/guardian.yaml`
- `~/.guardian/guardian.yaml`

## 도움말

```bash
python -m cli.main --help
python -m cli.main <command> --help
```

## 중요 안내

- Windows에서는 `guardian` 대신 `python -m cli.main` 또는 `.\guardian.bat`을 사용하세요.
- AI 기능을 사용하려면 API 키가 필요합니다.
- 외부 보안 도구(nmap, httpx, subfinder, nuclei)는 선택 사항이지만 권장됩니다.
- 명시적 권한이 있는 시스템만 테스트하세요.

## 문제 해결

명령어를 찾을 수 없음:

- 프로젝트 디렉터리에 있는지 확인하세요.
- 가상환경이 활성화되어 있는지 확인하세요.
- `guardian` 대신 `python -m cli.main`을 사용하세요.

임포트 오류:

- 의존성을 재설치하세요: `pip install -e .`
- Python 버전을 확인하세요: `python --version` (3.11+)

API 오류:

- `.env` 또는 `~/.guardian/.env`의 API 키를 확인하세요.
- 네트워크 연결 상태를 확인하세요.

## 다음 단계

1. 외부 펜테스트 도구를 설치해 기능을 확장하세요.
2. `config/guardian.yaml`에서 설정을 조정하세요.
3. `--dry-run`으로 실행 내용을 확인하세요.
4. `scanme.nmap.org` 같은 안전한 타깃부터 시작하세요.
5. `logs/guardian.log`에서 로그를 확인하세요.
