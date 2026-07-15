# **ERPNext 자체 구축 및 Claude Code 기반 지능형 자율 개발 환경 통합 아키텍처**

현대의 전사적 자원 관리(ERP) 시스템은 기업의 재무, 인사, 제조, 유통 등 핵심 비즈니스 프로세스를 관장하는 방대한 생태계이다. 이러한 생태계에서 파이썬(Python)과 Node.js 기반의 오픈소스 프레임워크인 Frappe 위에 구축된 ERPNext는 그 유연성과 확장성 덕분에 전 세계적으로 광범위하게 채택되고 있다. 하지만 다중 테넌트(Multi-tenant) 아키텍처, 복잡한 데이터베이스 스키마, 그리고 프레임워크 고유의 ORM(Object-Relational Mapping) 및 메타데이터 주도(Metadata-driven) 개발 방식은 초기 인프라 구축과 맞춤형 모듈(Custom App) 개발에 상당한 학습 곡선을 요구한다.  
이러한 기술적 장벽을 극복하고 개발 생산성을 기하급수적으로 끌어올리기 위해 Anthropic의 Claude Code와 같은 에이전트형 인공지능 코딩 도구를 통합하는 것은 단순한 자동화를 넘어선 패러다임의 전환을 의미한다. 인공지능이 시스템의 디렉토리 구조를 자율적으로 분석하고, 터미널 명령어를 실행하며, 데이터베이스에 직접 접근해 스키마를 쿼리하는 환경을 구축함으로써, 개발자는 아키텍처 설계와 제품 기획이라는 상위 계층의 의사결정에만 집중할 수 있게 된다. 본 보고서는 ERPNext의 자체 호스팅(Self-hosting) 인프라 구성부터 Claude Code를 활용한 코드 취득 전략, 컨텍스트 엔지니어링(CLAUDE.md), 모델 컨텍스트 프로토콜(MCP) 데이터베이스 연동, 그리고 서브에이전트(Agent) 및 슬래시 명령어(Slash Command) 설계까지 전체 패키지를 실제 상용 환경에서 즉시 적용할 수 있는 전문가 수준으로 심층 분석한다.

## **1\. ERPNext 자체 호스팅(Self-Hosting) 인프라 구축 및 코드 취득 전략**

ERPNext를 온프레미스(On-premise) 또는 자체 클라우드 환경에 구축하기 위한 인프라 아키텍처는 역사적으로 단일 서버에 파이썬 가상환경(venv), Node.js, MariaDB, Redis, Supervisor, Nginx를 수동으로 설치하는 베어메탈(Bare-metal) 방식이 주류를 이루었다. 그러나 이러한 방식은 운영체제의 패키지 의존성 충돌, 파이썬 버전 업데이트 시의 호환성 문제, 그리고 마이크로서비스 확장의 한계라는 기술적 부채를 발생시킨다. 따라서 현대의 프로덕션 표준은 도커(Docker) 기반의 컨테이너 오케스트레이션을 활용하는 방향으로 완전히 전환되었다. 소규모 인스턴스라 하더라도 일관된 설치 경로, 자동화된 업데이트, 그리고 데이터 백업의 무결성을 고려할 때 공식 frappe\_docker 리포지토리를 활용하는 것이 압도적으로 유리하다.  
Frappe의 컨테이너 생태계는 백엔드(Gunicorn), 프론트엔드(정적 자산 및 프록시), 웹소켓(Socket.IO), 스케줄러, 백그라운드 큐(Redis 기반), 그리고 관계형 데이터베이스(MariaDB) 등 다수의 독립적인 마이크로서비스로 분리되어 작동한다. 코드를 취득하고 초기 인프라를 구성하는 첫 단계는 깃허브(GitHub) 저장소를 복제하는 것으로 시작된다. 개발자는 터미널에서 git clone https://github.com/frappe/frappe\_docker 명령어를 통해 최신 배포 스크립트와 도커 컴포즈(Docker Compose) 템플릿을 확보해야 한다.  
프로덕션 수준에서 자체 맞춤형 앱(Custom App)을 포함한 ERPNext 인스턴스를 배포하려면 기본 이미지 위에 커스텀 코드를 주입하여 새로운 도커 이미지를 빌드하는 과정이 필수적이다. 프레임워크는 이를 위해 apps.json 파일 기반의 선언적 앱 설치 방식을 제공한다.

| 구성 요소 | 기술 스택 및 버전 사양 | 아키텍처 역할 및 인프라 연동 특성 |
| :---- | :---- | :---- |
| **Backend** | Python 3.14 (최신 안정화) | 비즈니스 로직(Controller) 처리, Gunicorn WSGI 서버 구동, Frappe ORM 쿼리 실행 |
| **Frontend** | Nginx, Node.js 24 | 정적 자산(CSS/JS) 서빙, 역방향 프록시(Reverse Proxy), Rollup 기반 자산 번들링 |
| **Database** | MariaDB | 트랜잭션 데이터 저장, 백엔드 컨테이너와의 핑 지연시간(Low Latency) 최소화 필수 |
| **Cache & Queue** | Redis | 인메모리 캐싱(redis\_cache), RQ 기반 백그라운드 작업(redis\_queue), 실시간 이벤트(redis\_socketio) |
| **Websocket** | Node.js, Socket.IO | 문서 동시 편집 충돌 방지, 시스템 실시간 알림 브로드캐스팅 처리 |

이미지 빌드 시 보안은 가장 중요한 요소이다. apps.json 파일 내에 프라이빗 깃허브 저장소 접근을 위한 개인 액세스 토큰(PAT)이 포함되는 경우, 이를 도커 이미지 레이어에 평문으로 남겨서는 안 된다. 이를 방지하기 위해 Frappe Docker 환경은 BuildKit의 시크릿(Secret) 마운트 기능을 활용한다. 개발자는 터미널에서 export APPS\_JSON\_BASE64=$(base64 \-w 0 apps.json) 명령을 통해 JSON 파일을 Base64로 인코딩한 후, \--build-arg APPS\_JSON\_BASE64=$APPS\_JSON\_BASE64 플래그를 통해 빌드 프로세스에 안전하게 주입해야 한다. 이후 compose.yaml 파일과 환경에 맞는 오버라이드 파일(예: overrides/compose.mariadb.yaml)을 결합하여 컨테이너 네트워크를 기동한다. 이 전체 배포 파이프라인은 셸 스크립트의 실행을 수반하므로, 후술할 Claude Code의 스킬(Skill) 메커니즘을 통해 완벽하게 자동화될 수 있다.

## **2\. Frappe 프레임워크 아키텍처 및 코드 가이드**

에이전트 기반 인공지능에게 ERPNext 개발을 위임하기 위해서는 대상 프레임워크의 고유한 디렉토리 구조와 파일 명명 규칙, 그리고 프레임워크 동작 원리를 AI가 명확히 인지하고 있어야 한다. Frappe 프레임워크는 애플리케이션(App)과 사이트(Site)라는 두 가지 축을 중심으로 구성된다. 애플리케이션은 파이썬과 자바스크립트 코드의 모음이며, 사이트는 데이터베이스와 설정 정보가 담긴 격리된 테넌트이다.  
작업 공간의 중심이 되는 frappe-b\[span\_22\](start\_span)\[span\_22\](end\_span)ench 디렉토리 내부는 크게 apps, sites, config, logs 로 나뉜다. 새로운 기능을 개발할 때 코어 프레임워크(예: /apps/frappe 또는 /apps/erpnext)를 직접 수정하는 것은 프레임워크 업데이트 시 충돌을 유발하므로 절대적으로 금지된다. 모든 개발은 bench new-app 명령어를 통해 생성된 커스텀 앱 내부에서 이루어져야 하며, 해당 앱의 구조적 특징은 다음과 같다.

1. **hooks.py**: Frappe 개발의 심장부이다. 프레임워크 이벤트 가로채기(Intercept), 스케줄러 등록(CRON), 커스텀 API 라우팅 설정, 표준 Doctype 동작 오버라이딩 등 모든 프레임워크 확장이 이 파일에 선언된다.  
2. **개발 모드 활성화(developer\_mode: 1\)**: 커스텀 앱에서 새로운 Doctype(데이터베이스 테이블 및 화면 UI 구조)을 생성할 때, 이 설정이 활성화되어 있어야 변경사항이 데이터베이스뿐만 아니라 파일 시스템의 JSON 파일로 저장되어 깃(Git) 형상 관리가 가능해진다.  
3. **patches.txt**: 데이터베이스 마이그레이션 스크립트를 관리한다. 시스템 배포 시 bench migrate 명령어가 호출되면 이 파일에 기록된 순서대로 패치 코드가 1회만 실행되어 스키마 변경을 안전하게 처리한다.  
4. **Fixtures**: 기존 표준 앱(ERPNext)의 화면에 커스텀 필드(Custom Field)를 추가하거나 출력 양식(Print Format)을 수정하는 경우, 이 변경사항은 시스템 데이터베이스에만 기록된다. 이를 커스텀 앱의 코드베이스로 가져오기 위해서는 hooks.py에 fixtures 배열을 선언하고 bench export-fixtures를 실행하여 JSON 파일 형태로 덤프해야 한다.

이러한 지식은 일반적인 파이썬 장고(Django)나 패스트API(FastAPI) 개발과는 완전히 다른 궤도에 있다. 따라서 언어 모델이 일반적인 파이썬 코드 생성 지식에 의존하여 코드를 짜는 것을 방지하고, Frappe 프레임워크의 메타데이터 주도 방식을 따르도록 강제하는 지침 주입 메커니즘이 필수적으로 요구된다.

## **3\. Claude Code 컨텍스트 엔지니어링: CLAUDE.md 최적화 및 점진적 정보 공개**

Claude Code는 Anthropic이 개발한 로컬 터미널 상주형 AI 에이전트로, 개발자가 평문으로 목표를 제시하면 코드베이스를 자율적으로 탐색하고 툴체인을 실행하여 소프트웨어를 구축하는 도구이다. 이 에이전트의 사고 과정을 ERPNext 환경에 맞게 조정하는 핵심 메커니즘이 바로 CLAUDE.md 파일이다. 일반적인 프로젝트 문서와 달리 이 파일은 매 세션이 시작될 때마다 언어 모델의 컨텍스트 창(Context Window) 최상단에 주입되는 시스템 프롬프트의 연장선으로 기능한다.  
컨텍스트 창의 한계와 토큰 처리 비용, 그리고 긴 지시사항으로 인한 지능 저하(Attention Dilution) 현상을 고려할 때, CLAUDE.md는 200\~300줄 이내로 유지되어야 하며 고도의 정보 밀도를 가져야 한다. 보일러플레이트 코드나 린터(Linter)가 자동으로 잡아내는 사소한 스타일 규칙, 혹은 AI가 이미 방대하게 학습한 언어적 특성(예: "타입스크립트란 무엇인가")을 포함하는 것은 토큰 낭비이다. 대신 프레임워크의 한계, 금지 사항, 아키텍처 맵, 그리고 셸 명령어의 패턴에 집중해야 한다.  
가장 진보된 형태의 컨텍스트 주입은 3계층 아키텍처(Three-layer architecture)와 점진적 정보 공개(Progressive Disclosure) 패턴을 결합하는 것이다.

* **사용자 계층(\~/.claude/CLAUDE.md)**: 개인화된 셸 선호도(예: "터미널에서 Vim 대신 Nano를 사용하라")를 정의한다. 이 파일은 형상 관리 시스템에 커밋되지 않는다.  
* **프로젝트 계층(프로젝트 루트 CLAUDE.md)**: 팀 전체가 공유하는 ERPNext 코어 규칙, bench 명령어 사용법, 인프라 레이아웃을 정의한다.  
* **하위 디렉토리 계층(apps/custom\_app/CLAUDE.md)**: 특정 커스텀 모듈의 비즈니스 도메인 지식, 결제 게이트웨이 연동 규칙 등을 선언한다. 에이전트가 해당 디렉토리 내의 파일을 조작할 때만 메모리에 추가로 로드된다.

추가적으로, 문서가 비대해지는 것을 방지하기 위해 @imports 시스템을 적극 활용해야 한다. 루트 CLAUDE.md를 가볍게 유지하면서, 특정 작업이 발생할 때만 조건부로 참조 파일을 불러오도록 트리거를 설정하는 것이다. 다음은 실제 ERPNext 자체 구축 환경에 맞춤화된 프로덕션 수준의 루트 \[span\_42\](start\_span)\[span\_42\](end\_span)CLAUDE.md 예시이다.

# **Frappe & ERPNext 프로젝트 운영 환경 컨텍스트**

본 시스템은 Python/Node.js 기반의 Frappe 프레임워크와 ERPNext를 활용하는 엔터프라이즈 환경이다. 모든 개발은 메타데이터 주도(Metadata-driven) 방식을 따른다.

## **1\. 아키텍처 및 무결성 규칙 (금지 사항)**

* 코어 조작 금지: /apps/frappe 및 /apps/erpnext 디렉토리 내부의 코드는 절대 직접 수정하지 않는다. 프레임워크 확장은 오직 /apps/custom\_app 내의 hooks.py를 통해서만 이루어진다.  
* 데이터베이스 직접 조작 금지: SQL 쿼리를 직접 작성하여 스키마를 변경하지 않는다. 모든 테이블 스키마 변경은 커스텀 앱 내의 Doctype JSON 파일을 수정하고 bench migrate를 실행하여 처리한다.  
* 환경 파일 열람 주의: /sites/\*/site\_config.json 에는 암호화 키(encryption\_key)와 데이터베이스 루트 비밀번호가 포함되어 있다. 로깅이나 파일 출력 시 해당 데이터를 절대로 포함시키지 않는다.

## **2\. 개발 및 배포 워크플로우**

* 스키마 변경: 새로운 Doctype을 설계할 때는 bench \--site \[사이트명\] set-config developer\_mode 1이 설정되어 있는지 반드시 확인한다.  
* 커스텀 필드 백업: 표준 문서(Sales Invoice 등)에 추가된 커스텀 필드는 hooks.py의 fixtures 배열에 선언 후 bench export-fixtures \--app custom\_app을 통해 앱 내부로 반출한다.  
* 동적 컨텍스트 참조: 프론트엔드 React 연동이나 외부 API 연동 작업이 필요할 경우 @imports .claude/rules/api\_guidelines.md 를 참조하여 해당 규칙을 따른다.

## **3\. 핵심 Bench CLI 명령어**

명령어는 반드시 /home/frappe/frappe-bench 위치에서 실행해야 한다.

* bench \--site \[사이트명\] migrate: 스키마 동기화 및 마이그레이션 적용  
* bench build: 프론트엔드 정적 자산(CSS/JS) 재빌드  
* bench \--site \[사이트명\] install-app \[앱이름\]: 대상 사이트에 커스텀 앱 마운트  
* bench restart: Gunicorn 워커 및 백그라운드 큐 재시작

위의 예시는 금지 사항을 명시적으로 앞에 배치하여 환각(Hallucination)에 의한 시스템 파괴를 방지하고, 에이전트가 bench CLI에 의존하여 시스템 상태를 변화시키도록 명확한 행동 양식을 정의한다.

## **4\. 지능형 서브에이전트(Agent) 구성 및 워크플로우 관리**

복잡한 ERP 환경에서는 단일한 시스템 프롬프트만으로 모든 도메인 로직을 포괄하기 어렵다. 최신 Claude Code 생태계는 agents/\*.md 또는 workflows/\*.js 디렉토리를 활용하여 전문화된 '서브에이전트(Subagents)'를 정의할 수 있는 기능을 지원한다. 에이전트는 특정 맥락(Context)과 허용된 도구(Tools)의 집합을 부여받은 독립적인 실행 단위이다.  
ERPNext 구축 프로젝트에서는 다음과 같은 서브에이전트 구성이 실효적이다.

* **코드 리뷰어 에이전트(code-reviewer.md)**: Frappe 프레임워크의 보안 표준(예: SQL 인젝션 방지를 위한 frappe.db.sql 파라미터화, 접근 권한 체크 has\_permission)만을 전문적으로 검토하는 에이전트.  
* **인프라 데브옵스 에이전트(infra-operator.md)**: 도커 컨테이너 상태 조회, Nginx 프록시 설정, Redis 캐시 모니터링 등 인프라 레이어의 진단만을 수행하는 에이전트.

이러한 서브에이전트는 사용자가 \--agent 플래그를 통해 명시적으로 호출하거나, 스킬 내부에서 context: fork 속성을 사용하여 메인 대화 맥락과 분리된 하위 프로세스로 실행될 수 있다. 서브에이전트를 활용하면 복잡한 마이그레이션 작업 중 주 대화창의 토큰 제한이 소진되는 것을 방지하고, 특정 작업에 비용 효율적인 모델(예: Claude 3.5 Haiku)을 선택적으로 할당하여 API 비용을 최적화할 수 있는 강력한 이점을 제공한다.

## **5\. 모델 컨텍스트 프로토콜(MCP)을 활용한 데이터베이스 심층 연동**

에이전트가 로컬 디렉토리의 파일들을 분석하여 프레임워크의 논리적 구조를 파악하는 것을 넘어, 현재 운영 중인 시스템의 라이브 상태(Live State)와 동적인 데이터를 이해하기 위해서는 외부 자원에 대한 표준화된 접근 프로토콜이 필수적이다. 이를 해결하는 기술적 표준이 모델 컨텍스트 프로토콜(MCP, Model Context Protocol)이다. MCP는 USB-C가 하드웨어 연결을 표준화한 것처럼, 다양한 AI 애플리케이션과 외부 데이터 소스(데이터베이스, 웹 검색, 파일 시스템 등) 간의 통신을 JSON-RPC 기반의 클라이언트-서버 아키텍처로 통일한 오픈소스 프로토콜이다.  
ERPNext는 수백 개의 테이블이 동적으로 생성되고 얽혀 있는 거대한 관계형 데이터베이스 스키마를 동반한다. 개발 중 에러를 디버깅하거나 복잡한 ORM 스크립트를 작성하기 위해, 에이전트는 외래 키(Foreign Key) 관계와 테이블 메타데이터를 직접 조회할 수 있어야 한다. 이를 위해 MariaDB 재단에서 공식적으로 유지보수하는 MariaDB MCP 서버(github.com/MariaDB/mcp)를 Claude Code에 통합하는 것이 가장 이상적인 아키텍처 설계이다.  
MariaDB MCP 서버를 연동하면 Claude Code 클라이언트는 다음과 같은 데이터베이스 심층 분석 도구들을 획득하게 된다.

| MCP 도구 명칭 | 기능적 역할 및 특징 | ERPNext 개발 활용 시나리오 |
| :---- | :---- | :---- |
| list\_databases / list\_tables | 권한이 부여된 데이터베이스 및 테이블 목록 조회 | 사이트 초기화 시 \_ 접두사가 붙은 테넌트 테이블 존재 유무 및 생성 검증 |
| get\_table\_schema | 특정 테이블의 컬럼 타입, 제약조건, 통계 조회 | Doctype JSON 설정이 데이터베이스 실제 스키마에 올바르게 반영되었는지 실시간 대조 검증 |
| execute\_sql | 읽기 전용 쿼리(SELECT, SHOW, DESCRIBE) 실행 | 커스텀 모듈의 비즈니스 로직에 의해 적재된 데이터를 조회하여 테스트 주도 개발(TDD) 수행 |
| search\_vector\_store | 임베딩 기반 의미론적 유사도 검색 (설정 시) | 방대한 ERP 문서(매뉴얼, 규정)를 벡터 기반으로 검색하여 컨텍스트화 (고급 활용) |

이 통합 구성을 활성화하기 위해서는 터미널에서 c\[span\_65\](start\_span)\[span\_65\](end\_span)\[span\_67\](start\_span)\[span\_67\](end\_span)laude mcp add 명령을 실행하거나, 설정 파일(주로 \~/.claude.json 또는 최신 표준인 mcp.json)에 서버의 구동 커맨드와 환경 변수를 선언해야 한다. 이 때 보안의 관점에서 비밀번호와 같은 민감한 자격 증명은 JSON 평문이 아닌 환경 변수 바인딩을 통해 서버로 전달되어야 한다.  
다음은 Claude Code가 ERPNext의 기반 MariaDB에 접속할 수 있도록 구성된 표준 mcp.json (또는 settings.json 내 mcpServers 블록) 설정의 실제 예시이다.  
`{`  
  `"mcpServers": {`  
    `"mariadb-erpnext": {`  
      `"command": "uv",`  
      `"args": [`  
        `"run",`  
        `"--with",`  
        `"mcp-server-mariadb",`  
        `"mcp-server-mariadb"`  
      `],`  
      `"env": {`  
        `"DB_HOST": "127.0.0.1",`  
        `"DB_PORT": "3306",`  
        `"DB_USER": "readonly_ai_user",`  
        `"DB_PASSWORD": "${AI_DB_PASSWORD}",`  
        `"DB_NAME": "_1234567890abcdef",`   
        `"MCP_READ_ONLY": "true"`  
      `}`  
    `}`  
  `}`  
`}`

해당 MCP 연동의 효과는 즉각적이고 폭발적이다. 에러가 발생했을 때 과거처럼 개발자가 별도의 데이터베이스 클라이언트를 열어 쿼리를 날리고 결과를 복사해 AI에게 전달할 필요가 없다. 에이전트 자신이 에러 로그를 읽고, get\_table\_schema를 호출해 누락된 컬럼을 스스로 찾아낸 뒤, 프레임워크 패치 파일을 작성하여 수정을 완료하는 완전한 클로즈드 루프(Closed-loop) 오토메이션이 달성된다. 단, MCP\_READ\_ONLY=true 플래그는 애플리케이션 계층에서의 방어일 뿐이므로, 보안 무결성을 보장하기 위해 데이터베이스 자체에서 SELECT 권한만을 가진 전용 계정(readonly\_ai\_user)을 생성하여 할당하는 것이 기업 환경의 필수 보안 원칙이다.

## **6\. 슬래시 명령어(Slash Command)와 커스텀 스킬(Skill) 생태계 구축**

CLAUDE.md가 에이전트의 기본적인 행동 강령이라면, 스킬(Skill)은 반복적이고 복잡한 다단계 엔지니어링 절차를 캡슐화(Encapsulation)하여 재사용 가능하게 만드는 고도의 오케스트레이션 도구이다. 스킬은 .claude/skills/ 디렉토리 아래에 폴더 단위로 저장되며, 개발자는 터미널에서 슬래시 명령어(예: /scaffold-app) 형태로 이를 즉각적으로 호출할 수 있다.  
스킬 시스템의 구조는 점진적 정보 공개 아키텍처의 정점을 보여준다. 각 스킬 폴더에는 필수적으로 SKILL.md 파일이 존재해야 하며, 이 파일의 최상단에는 YAML 프런트매터(Frontmatter)가 정의된다. 시스템이 구동될 때 에이전트는 전체 스킬 본문을 모두 읽는 것이 아니라, 오직 프런트매터의 name과 description만을 메모리에 적재하여 맵(Map)을 형성한다. 사용자의 프롬프트 의도가 description의 내용과 일치하거나, 사용자가 명시적으로 슬래시 명령어를 타이핑했을 때 비로소 하단의 지시사항과 스크립트 본문이 컨텍스트로 인출된다.  
다음은 ERPNext 운영 환경에서 재해 복구(Disaster Recovery) 또는 마이그레이션을 위한 데이터베이스 백업 프로세스를 완벽히 자동화하는 스킬 설계 예시이다. 파일은 .claude/skills/backup-erpnext/SKILL.md 위치에 저장된다.  
`---`  
`name: backup-erpnext`  
`description: 현재 활성화된 ERPNext 사이트의 데이터베이스와 모든 파일(공용 및 비공개 파일 포함)을 안전하게 백업한다. 사용자가 "백업해줘", "데이터 백업", "사이트 보관해"라고 요청할 때 실행한다.`  
`disable-model-invocation: true`  
`effort: low`  
`argument-hint: 백업을 수행할 특정 사이트 이름이 있다면 입력하고, 없다면 생략 가능.`  
`arguments:`  
  `- name: site_name`  
    `description: 백업할 Frappe 사이트 도메인 이름 (예: erp.example.com)`  
    `required: false`  
`---`

`# ERPNext 시스템 무결성 백업 자동화 워크플로우`

`본 스킬은 Frappe 프레임워크의 내장 백업 도구를 활용하여 시스템의 스냅샷을 생성하는 절차이다. 다음 단계를 순차적으로 수행하라.`

`1. **디렉토리 컨텍스트 확인 및 사이트 식별**:`  
   ``- 현재 경로가 `frappe-bench` 내부인지 `pwd` 명령으로 확인한다.``  
   ``- 인자로 전달받은 `site_name`이 없다면 `cat sites/currentsite.txt` 명령을 실행하여 현재 기본 사이트를 식별한다.``

`2. **전체 백업 실행 (데이터베이스 + 파일)**:`  
   ``- 일반적인 `bench backup`은 데이터베이스만을 백업하므로 파일 유실 위험이 있다. 반드시 사용자 업로드 파일(public/private)을 포함하는 `--with-files` 플래그를 사용해야 한다.``  
   ``- 셸 명령어: `bench --site [식별된_사이트명] backup --with-files` 를 실행한다.``

`3. **결과 검증 및 리포팅**:`  
   ``- 백업이 완료되면 `ls -lh sites/[식별된_사이트명]/private/backups/` 명령을 실행하여 최근 생성된 `.sql.gz` 파일과 `.tar` 파일들의 용량 및 생성 시각을 검증한다.``  
   `- 개발자에게 백업 파일의 경로, 이름, 파일 크기를 요약하여 보고한다.`

이 설계에서 가장 핵심적인 부분은 disable-model-invocation: true 속성이다. 백업이나 복원, 커스텀 앱 배포와 같이 디스크 I/O가 크거나 시스템 상태를 변경하는 파괴적 부작용(Side effect)을 가진 워크플로우는 에이전트가 문맥상 유추하여 임의로 실행해서는 안 된다. 이 옵션을 선언하면 에이전트의 자율 발동이 차단되며, 오직 개발자가 터미널에 명시적으로 /backup-erpnext를 입력했을 때만 실행되도록 통제권을 인간에게 남겨둘 수 있다.  
추가적으로, effort: low 메타데이터를 부여함으로써 복잡한 논리적 추론이 필요 없는 단순 터미널 스크립트 실행 작업에 과도한 토큰 추론 비용이 발생하는 것을 최적화할 수 있다. 더 나아가, hooks 필드를 활용해 깃 커밋(Git Commit) 직후 자동으로 코딩 컨벤션 검사 스킬을 발동시키는 등 이벤트 기반의 워크플로우를 구성하는 것도 가능하다.

## **7\. 권한 통제(Permissions)와 샌드박싱 기반 보안 아키텍처**

AI 에이전트에게 로컬 시스템의 셸(Bash, Zsh 등) 접근 권한을 부여하고 파일 시스템 조작을 위임하는 것은 개발 속도를 비약적으로 높이는 동시에 치명적인 보안 리스크를 유발한다. 특히 ERP 환경에는 .env 파일의 깃허브 토큰이나 site\_config.json의 데이터베이스 마스터 계정 정보 등 유출 시 기업에 심각한 타격을 줄 수 있는 민감 정보가 산재해 있다. 따라서 에이전트의 권한을 정밀하게 제어하는 샌드박싱(Sandboxing) 설정은 선택이 아닌 필수이다.  
Claude Code의 권한 통제 시스템은 계층적(Cascading) 오버라이드 구조를 갖는다. 조직 전체의 보안 정책을 강제하는 관리자 정책(Managed Policy)이 최상위에 위치하며, 그 아래로 명령줄 플래그(Command line), 로컬 설정(.claude/settings.local.json), 프로젝트 설정(.claude/settings.json), 그리고 유저 전역 설정(\~/.claude/settings.json) 순으로 우선순위가 적용된다. 이 중 권한 검사 리스트(allow, ask, deny)는 오버라이드되어 사라지는 것이 아니라 모든 계층의 규칙이 병합(Merge)되며, 그중에서도 **deny 규칙은 다른 어떤 allow 규칙보다 우선하여 무조건적으로 실행을 차단**하는 강력한 거부권을 행사한다.  
다음은 ERPNext 개발 환경의 자율성을 보장하면서도 시스템 붕괴를 원천 차단하는 프로젝트 레벨의 .claude/settings.json 권한 설정 예시이다.  
`{`  
  `"$schema": "https://json.schemastore.org/claude-code-settings.json",`  
  `"permissions": {`  
    `"defaultMode": "acceptEdits",`  
    `"allow": [`  
      `"Bash(bench build)",`  
      `"Bash(bench start)",`  
      `"Bash(bench --site * migrate)",`  
      `"Bash(bench --site * clear-cache)",`  
      `"Bash(npm run lint)",`  
      `"Bash(git status)",`  
      `"Bash(ls)",`  
      `"Read(apps/custom_app/**)"`  
    `],`  
    `"deny": [`  
      `"Bash(bench drop-site *)",`  
      `"Bash(rm -rf *)",`  
      `"Bash(sudo *)",`  
      `"Bash(DROP DATABASE *)",`  
      `"Bash(bench --site * mysql)",`  
      `"Read(sites/*/site_config.json)",`  
      `"Read(sites/*/common_site_config.json)",`  
      `"Read(sites/*/private/**)",`  
      `"Read(config/**)"`  
    `]`  
  `},`  
  `"autoCompactThreshold": 75,`  
  `"notifications": true`  
`}`

이 설정의 메커니즘을 해부해보면 방어적 엔지니어링의 정밀한 설계를 확인할 수 있다. 첫째, defaultMode: "acceptEdits" 설정을 통해 에이전트가 프레임워크 내의 파이썬 또는 자바스크립트 소스 파일을 편집할 때마다 사용자에게 팝업으로 승인을 요구하는 번거로움을 제거하였다. 이를 통해 대규모 리팩토링이나 여러 파일에 걸친 동시 수정 작업이 병목 없이 매끄럽게 진행된다. 둘째, allow 블록에는 반복적이고 파괴적이지 않은 Frappe CLI 명령어를 와일드카드(\*)와 함께 선언하여(bench \--site \* migrate), 에이전트가 스키마 동기화 및 캐시 초기화를 자체 판단하에 대기 시간 없이 즉시 실행하도록 자율성을 부여했다. 셋째, deny 블록은 시스템의 생명선이다. bench drop-site는 테넌트의 데이터베이스를 영구적으로 삭제하는 파괴적 명령이므로 어떤 상황에서도 에이전트의 실행을 불허한다. 또한 Read 거부 규칙을 통해 사이트 설정 파일(site\_config.json)에 대한 열람을 차단함으로써, 에이전트가 분석을 핑계로 데이터베이스 비밀번호나 암호화 키(encryption\_key)를 읽어 외부 클라우드 모델로 전송하는 정보 유출(Data Exfiltration) 사고의 가능성을 원천적으로 봉쇄한다. 넷째, autoCompactThreshold: 75 옵션은 에이전트가 장시간 코드를 분석하여 컨텍스트 창 용량의 75%에 도달했을 때 대화 내용을 자동 압축하도록 지시한다. 이는 메모리 오버플로우로 인한 오류를 예방하고 세션의 안정성을 확보한다. 완료 시 데스크탑 푸시 알림(notifications: true) 기능은 방대한 테스트 스위트 실행 중 개발자의 컨텍스트 스위칭 효율을 향상시킨다.  
만약 기업 환경의 보안 규정 상 최고 성능의 모델(Claude 3.5 Sonnet 이상) 사용이 허가되어 있다면, 정적 규칙 설정 대신 defaultMode: "auto"를 도입할 수 있다. 오토 모드는 모델에 내장된 분류기(Classifier)가 해당 명령의 위험도를 실시간으로 평가하여, 안전한 작업은 자동으로 통과시키고 위험한 작업(rm \-rf 등)은 인간의 승인(Human-in-the-loop)을 요구하도록 설계된 동적 보안 체계이다.

## **8\. 결론**

오픈소스 ERP의 표준인 Frappe 및 ERPNext를 현대적인 도커 기반 인프라 위에 자체 구축하고, 이를 Anthropic Claude Code라는 최첨단 자율 에이전트와 통합하는 것은 소프트웨어 엔지니어링의 생산성 패러다임을 근본적으로 혁신하는 접근이다.  
Frappe 프레임워크는 JSON 메타데이터 중심의 아키텍처와 명확한 디렉토리 분리 원칙을 가지고 있어, AI 에이전트가 패턴을 학습하고 예측 가능한 코드를 생성하기에 가장 이상적인 기반을 제공한다. 본 보고서에서 분석한 아키텍처는 단순한 기술들의 집합이 아니다. CLAUDE.md를 통한 점진적인 시스템 컨텍스트 주입은 에이전트에게 지도를 쥐여주고, MariaDB MCP 서버의 실시간 데이터베이스 연동은 시스템의 내장을 꿰뚫어 보는 엑스레이 시야를 제공한다. 더불어 YAML 프런트매터를 정밀하게 조율한 SKILL.md 슬래시 명령어는 에이전트를 숙련된 시스템 운영자로 변모시키며, 계층화된 settings.json 권한 통제는 이 모든 막강한 자율성이 파국으로 치닫지 않도록 통제하는 완벽한 샌드박스로 기능한다.  
결론적으로, 본 가이드에서 제시한 지능형 개발 환경 통합 패키지를 기업의 프로덕션 파이프라인에 이식함으로써, 소규모 엔지니어링 팀이라 하더라도 수만 줄에 달하는 레거시 ERP 시스템의 마이그레이션이나 복잡한 인시던트 대응 시간을 획기적으로 단축할 수 있는 극대화된 레버리지(Leverage)를 획득할 수 있다. 기술의 발전 속도를 고려할 때, 명확한 가드레일(Guardrails)과 정교한 컨텍스트 주입을 통한 에이전트 협업 체계 구축은 기업의 디지털 트랜스포메이션 속도를 결정짓는 가장 핵심적인 경쟁 우위가 될 것이다.

#### **참고 자료**

1\. Claude Code | Anthropic's agentic coding system, https://www.anthropic.com/product/claude-code 2\. Overview \- Claude Code Docs, https://code.claude.com/docs/en/overview 3\. Self-hosting ERPNext \+ Frappe HR \- bare-metal Ubuntu vs Docker?, https://discuss.frappe.io/t/self-hosting-erpnext-frappe-hr-bare-metal-ubuntu-vs-docker/163162 4\. Manual Installation of Frappe & ERPNext on Ubuntu: A Complete Guide | by rashid pbi, https://medium.com/@rashidpbi111/manual-installation-of-frappe-erpnext-on-ubuntu-a-complete-guide-0223565730c9 5\. GitHub \- frappe/frappe\_docker: Docker environment for developing, deploying, and running Frappe applications (ERPNext and custom apps) in production and development, https://github.com/frappe/frappe\_docker 6\. Directory structure \- Frappe Documentation, https://docs.frappe.io/framework/user/en/basics/directory-structure 7\. \[Tutorial\] ERPNext v16 – Local Docker Setup for Development \- Frappe Forum, https://discuss.frappe.io/t/tutorial-erpnext-v16-local-docker-setup-for-development/159165 8\. How to add custom app to production docker setup? \- ERPNext \- Frappe Forum, https://discuss.frappe.io/t/how-to-add-custom-app-to-production-docker-setup/113283 9\. frappe\_docker/docs/02-setup/02-build-setup.md at main \- GitHub, https://github.com/frappe/frappe\_docker/blob/main/docs/02-setup/02-build-setup.md 10\. Frappe Docker Custom App Guide (Create Docker Image For Your Custom Frappe App), https://discuss.frappe.io/t/frappe-docker-custom-app-guide-create-docker-image-for-your-custom-frappe-app/151315 11\. Apps \- Frappe Documentation, https://docs.frappe.io/framework/user/en/basics/apps 12\. ERPNext Development for beginners \- GitHub Gist, https://gist.github.com/revant/543179ec9b4442674a61c6d760a6d34a 13\. Mastering ERPNext 16: The Complete Guide to Custom App Development \- David Muraya, https://davidmuraya.com/blog/develop-erpnext-custom-app/ 14\. Add “Move Custom Doctype to App” Option in Developer UI · Issue \#38332 \- GitHub, https://github.com/frappe/frappe/issues/38332 15\. The Complete Guide to CLAUDE.md — Make Claude Code Truly Understand Your Project, https://medium.com/@n913239/the-complete-guide-to-claude-md-make-claude-code-truly-understand-your-project-d9d026b808f1 16\. The Developer's Guide to CLAUDE.md \- TurboDocx, https://www.turbodocx.com/resources/claude-md-guide 17\. CLAUDE.md Guide: Configure Claude Code Like a Pro (2026) | Serenities AI, https://serenitiesai.com/articles/claude-md-complete-guide-2026 18\. Explore the .claude directory \- Claude Code Docs, https://code.claude.com/docs/en/claude-directory 19\. 12 Best CLAUDE.md Examples From Real Repos \- AY Automate, https://www.ayautomate.com/blog/best-claude-md-examples 20\. Claude Code settings \- Claude Code Docs, https://code.claude.com/docs/en/settings 21\. SKILL.md Format Specification: Complete YAML Frontmatter Reference \- Agensi, https://www.agensi.io/learn/skill-md-format-reference 22\. What is the Model Context Protocol (MCP)? \- Model Context Protocol, https://modelcontextprotocol.io/docs/getting-started/intro 23\. What is Model Context Protocol? Connect AI to your world | Claude by Anthropic, https://claude.com/blog/what-is-model-context-protocol 24\. Model Context Protocol (MCP) explained: A practical technical overview for developers and architects \- CodiLime, https://codilime.com/blog/model-context-protocol-explained/ 25\. MariaDB Cloud MCP Server, https://mariadb.com/docs/mariadb-cloud/cloud-ai/mcp-server 26\. skills/mariadb-mcp/SKILL.md at main \- GitHub, https://github.com/MariaDB/skills/blob/main/mariadb-mcp/SKILL.md 27\. Unlocking Your MariaDB Data: A Deep Dive into the MariaDB MCP Server for AI Engineers, https://skywork.ai/skypage/en/mariadb-data-mcp-server-ai-engineers/1977651364416512000 28\. Connect Claude Code to tools via MCP, https://code.claude.com/docs/en/mcp 29\. MCP: Model Context Protocol \- Cheatsheet | SFEIR Institute, https://institute.sfeir.com/en/claude-code/claude-code-mcp-model-context-protocol/cheatsheet/ 30\. Proposal: Universal MCP Configuration File Standard \#2218 \- GitHub, https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2218 31\. MCP JSON Configuration FastMCP, https://gofastmcp.com/integrations/mcp-json-configuration 32\. Claude Code Skills — Secure Agent Skills for Developers | Skills Directory, https://www.skillsdirectory.com/claude-code-skills 33\. Directory of Claude Agent Skills \- Awesome Claude, https://awesomeclaude.ai/awesome-claude-skills 34\. Extend Claude with skills \- Claude Code Docs, https://code.claude.com/docs/en/skills 35\. How to create custom skills | Claude Help Center, https://support.claude.com/en/articles/12512198-how-to-create-custom-skills 36\. The Complete Guide to Building Skills for Claude | Anthropic, https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf 37\. Deep Dive SKILL.md (Part 1/2) \- A B Vijay Kumar, https://abvijaykumar.medium.com/deep-dive-skill-md-part-1-2-09fc9a536996 38\. ERPNext Backup & Restore Cheat Sheet: Bench Commands, Files & Migration, https://finbyz.tech/erpnext/wiki/backup-and-restore-erpnext 39\. ERPNext Bench Commands: The Complete Reference with Explanations (2026) \- Managely Cloud ERP, https://managely.cloud/en/blog/erpnext-bench-commands 40\. Claude Code Permissions: A Practical settings.json Guide for Allow, Deny, and Ask Rules, https://www.developersdigest.tech/blog/claude-code-permissions-settings-guide 41\. Configure permissions \- Claude Code Docs, https://code.claude.com/docs/en/agent-sdk/permissions 42\. Choose a permission mode \- Claude Code Docs, https://code.claude.com/docs/en/permission-modes 43\. 12 Claude Code Settings You Should Enable Right Now | MindStudio, https://www.mindstudio.ai/blog/12-claude-code-settings-enable-now