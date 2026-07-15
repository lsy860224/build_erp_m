# 로컬 개발 환경 (Docker + bench)

2026.07.15 구축. Windows(WSL2 + Docker Desktop) 위에서 Frappe/ERPNext bench를 컨테이너로
띄우는 방법과, 이 프로젝트에서만 필요했던 우회 조치를 기록한다.

## 위치

- `frappe_docker`(공식 리포지토리, MIT 라이선스)는 이 저장소 밖의 **sibling 디렉토리**
  `E:\03. Job\00. Claude Code\frappe_docker`에 클론돼 있다 — `build_erp_m` git 이력에는
  포함되지 않는다(빌드 도구이지 우리 저작물이 아님).
- 실제 커스텀 앱 소스는 이 저장소의 [`apps/babipa_erp/`](../apps/babipa_erp/)에 있다 —
  `docs/app-directory-structure.md` 참조.

## 아키텍처: 왜 볼륨을 분리했는가

`frappe_docker/devcontainer-example/docker-compose.yml`의 기본 설정은 리포지토리 전체를
`..:/workspace`로 컨테이너에 바인드 마운트한다. 이 프로젝트에서는 그 원본을
`frappe_docker/.devcontainer/docker-compose.yml`로 복사한 뒤 아래 두 가지를 바꿨다:

```yaml
volumes:
  - ..:/workspace:cached
  - frappe-bench-data:/workspace/development/frappe-bench
  - E:/03. Job/00. Claude Code/build_erp_m/apps/babipa_erp:/workspace/development/frappe-bench/apps/babipa_erp
```

이유 — Windows 호스트 경로를 그대로 바인드 마운트하면 Docker Desktop의 Windows↔WSL2 파일
공유 계층이 두 가지를 지원하지 않는다:

1. **심볼릭 링크 생성 실패** — `bench init`의 `uv venv`가 파이썬 venv를 심볼릭 링크로 만드는데
   `Operation not permitted`로 실패.
2. **chmod 실패** — 새 앱을 `git init`할 때 `core.filemode` 설정을 위해 chmod가 필요한데
   동일하게 `Operation not permitted`로 실패.

그래서 `frappe-bench`(venv·코어 앱 `frappe`/`erpnext`·사이트 데이터)는 **네이티브 Docker
볼륨**에 두어 심볼릭 링크·chmod가 정상 동작하게 하고, 우리가 실제로 편집해야 하는
`apps/babipa_erp`만 별도로 Windows 경로에 바인드 마운트했다. `babipa_erp`는
`bench new-app --no-git`으로 생성해 자체 git init(=chmod 필요) 자체를 건너뛰었다.

부작용: 컨테이너 최초 기동 시 Docker가 마운트 지점(`frappe-bench/`, `frappe-bench/apps/`)을
`root` 소유로 자동 생성하므로, `bench init` 전에 `frappe` 유저로 소유권을 바꿔줘야 한다(아래
"컨테이너 최초 기동" 참조). 그리고 `bench init`이 nested bind mount 때문에 생긴 빈
`apps/babipa_erp/` 디렉토리를 "이미 존재하는 bench"로 오인하므로 `--ignore-exist` 플래그가
필요하다.

## Frappe/ERPNext 버전

`bench init`에 `--frappe-branch`를 지정하지 않으면 `develop`(당시 버전 17, 미출시 개발
브랜치)로 초기화된다 — ERPNext를 설치하려 하면 "not supported and will result in broken
install" 에러가 난다. 반드시 **안정 브랜치**를 명시할 것. 2026.07.15 기준 최신 안정 브랜치는
`version-16`(`git ls-remote --heads https://github.com/frappe/frappe.git`으로 확인 가능,
`version-17`은 아직 없음). frappe와 erpnext는 반드시 같은 `version-N` 브랜치여야 한다.

## Windows(Git Bash)에서 docker exec 쓸 때 주의

Git Bash(MSYS)는 `/`로 시작하는 인자를 자동으로 Windows 경로로 변환한다. `docker exec -w
/workspace/development ...`처럼 컨테이너 내부 절대경로를 넘길 때 이 변환이 걸리면
`OCI runtime exec failed: exec failed: Cwd must be an absolute path` 에러가 난다. 반드시
`MSYS_NO_PATHCONV=1`을 명령 앞에 붙일 것:

```bash
MSYS_NO_PATHCONV=1 docker exec -u frappe -w /workspace/development/frappe-bench <container> bash -c "..."
```

## 컨테이너 기동/재기동

```bash
cd "E:\03. Job\00. Claude Code\frappe_docker"
docker compose -f .devcontainer/docker-compose.yml up -d
```

컨테이너: `devcontainer-frappe-1`(bench), `devcontainer-mariadb-1`, `devcontainer-redis-cache-1`,
`devcontainer-redis-queue-1`. 최초 기동 시(named volume이 비어있을 때)만 소유권 수정 필요:

```bash
docker exec -u root devcontainer-frappe-1 bash -c "chown -R frappe:frappe /workspace/development/frappe-bench"
```

## bench 서버 실행

```bash
MSYS_NO_PATHCONV=1 docker exec -d -u frappe -w /workspace/development/frappe-bench devcontainer-frappe-1 bash -c "bench start > logs/bench-start.log 2>&1"
```

브라우저에서 `http://development.localhost:8000` 접속(`*.localhost`는 hosts 파일 수정 없이
자동으로 `127.0.0.1`로 풀린다). 로그인: `Administrator` / `admin`(로컬 개발 전용 — 인트라넷
외부에 노출되지 않음. 운영 배포 시 반드시 변경).

## 사이트/앱 현황

- 사이트: `development.localhost`
- 설치된 앱: `frappe` 16.27.0, `erpnext` 16.28.0, `babipa_erp` 0.0.1 (모두 `version-16`)
- `developer_mode: 1` 활성화됨 — 새 DocType 생성 시 파일시스템(JSON)에도 반영되어 git 추적 가능
