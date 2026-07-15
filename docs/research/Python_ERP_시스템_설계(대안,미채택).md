> **문서 상태**: 검토 후 미채택된 대안 아키텍처 (2026.07.15 확정). ERPNext를 쓰지 않고 Django+FastAPI로 ERP/MES/POP을 처음부터 직접 구축하는 방향을 제안하지만, 이 프로젝트는 루트 [`CLAUDE.md`](../../CLAUDE.md)에 따라 **ERPNext(Frappe) 기반**으로 진행하기로 확정했다.
> 다만 §6(OPC UA/MQTT 엣지 게이트웨이), §8(ZPL 바코드 라벨 직접 인쇄), §9(OEE·양방향 로트 추적성) 등 MES/POP 현장 데이터 수집·추적성 설계는 ERPNext 커스텀 앱(`babipa_erp`) 내 장비 Endpoint 연동 설계 시 여전히 참고 가치가 있다 — 폐기가 아니라 참고자료로 보존.

# **파이썬 기반 통합 생산 및 자원 관리 시스템(ERP·MES·POP) 아키텍처 및 구현 상세 보고서**

## **1\. 서론 및 시스템 설계의 구조적 배경**

현대의 제조 환경은 급변하는 시장 수요와 다품종 소량 생산의 압박 속에서 데이터 기반의 민첩한 의사결정을 요구하고 있다. 기업의 자금, 회계, 구매, 영업 등 비즈니스 트랜잭션을 총괄하는 전사적 자원 관리(ERP, Enterprise Resource Planning) 시스템과 생산 현장의 작업 지시, 자재 투입, 품질 검사를 통제하는 제조 실행 시스템(MES, Manufacturing Execution System), 그리고 설비와 작업자로부터 데이터를 직접 수집하는 생산 시점 관리(POP, Point of Production) 시스템은 스마트 공장의 핵심 신경망을 구성한다1. 그러나 많은 제조 기업이 이러한 시스템들을 단절된 상태로 운영하거나 물리적인 데이터베이스 연동에만 의존함으로써 심각한 정보의 지연과 데이터 정합성 훼손을 겪고 있다5.  
이러한 단절의 근본적인 원인은 시스템 계층 간의 태생적인 설계 목적과 데이터 처리 주기의 불일치에 있다. 국제 자동화 협회의 ISA-95 참조 모델에 따르면, L4 계층인 ERP는 재무 및 장기 생산 계획을 처리하기 위해 배치(Batch) 위주의 트랜잭션 데이터베이스 환경에서 작동하도록 설계되었다8. 반면 L3 계층인 MES와 L2/L1 계층인 SCADA 및 PLC 시스템은 밀리초(ms) 단위의 상태 변화, 초당 수백 건의 센서 데이터, 즉각적인 품질 이상 알림 등 실시간(Real-time) 이벤트 처리를 목적으로 한다5.  
과거의 모놀리식(Monolithic) 환경에서는 센서 데이터를 PLC에서 SCADA로, 그리고 MES를 거쳐 ERP로 순차적으로 밀어 올리는 경직된 자동화 피라미드 구조를 채택했다9. 그러나 이러한 구조에서 MES가 단순한 실행 시스템의 역할을 넘어 메시지 브로커, 프로토콜 변환기, 분석 플랫폼의 책임을 동시에 떠안게 되면, 결국 통합 계층으로서도 실패하고 실행 시스템으로서의 성능도 크게 저하되는 결과를 초래한다8.  
따라서 본 보고서는 생산 이력 관리, 품질 관리, 자재 관리, 기준서 및 절차서 관리를 모두 아우르는 통합형 ERP/MES/POP 시스템을 파이썬(Python) 기반으로 구축하기 위한 포괄적이고 전문적인 아키텍처를 제안한다. 최대 50명의 동시 접속자를 수용하는 데이터베이스 최적화 전략부터 사내 인트라넷 및 모바일 애플리케이션 환경을 지원하는 백엔드 설계, 그리고 현장의 대규모 IoT 데이터를 유실 없이 수집하기 위한 비동기 이벤트 기반 아키텍처(Event-Driven Architecture)의 상세 설계 사항을 심층적으로 분석한다.

## **2\. 파이썬 기반 백엔드 아키텍처 및 프레임워크 설계**

파이썬(Python)은 데이터 처리 라이브러리가 풍부하고 산업용 프로토콜(OPC UA, Modbus, MQTT 등)과의 연동이 매우 용이하여, 상용 벤더의 로드맵에 종속되지 않는 유연하고 확장 가능한 MES 및 ERP 개발에 최적화된 언어이다11. 시스템의 아키텍처를 설계할 때 가장 먼저 결정해야 할 사항은 어떠한 파이썬 웹 프레임워크를 사용하여 비즈니스 로직과 데이터 입출력을 통제할 것인가이다. 본 아키텍처에서는 강력한 관리자 기능을 제공하는 Django와 고성능 비동기 처리에 특화된 FastAPI를 상호 보완적으로 활용하는 하이브리드(Hybrid) 설계를 제안한다.  
전통적이고 성숙한 프레임워크인 Django는 객체 관계 매핑(ORM), 데이터 검증, 세션 관리, 강력한 보안 매커니즘을 내장하고 있는 'Batteries included(건전지 포함)' 철학을 따른다13. 특히 Django가 기본으로 제공하는 관리자 시스템(Admin Panel)은 단순한 모델 정의만으로 데이터 생성, 수정, 삭제(CRUD)가 가능한 인터페이스를 즉시 생성하므로, 수많은 마스터 데이터(BOM, 자재 마스터, 작업장 정보, 권한 등)를 다루어야 하는 ERP 시스템의 내부 관리 도구를 구축하는 데 소요되는 수백 시간의 프론트엔드 개발 리소스를 절감할 수 있다13. 복잡한 권한 검증이 필요한 재무, 자재 승인 프로세스나 50명 미만의 내부 사용자가 사용하는 사내 인트라넷 환경에서는 Django의 도입이 압도적인 생산성을 보장한다15.  
반면, 공장 현장의 설비가 초당 수천 건의 상태 데이터를 전송하거나, 수십 대의 POP 태블릿이 동시에 실시간 설비종합효율(OEE) 데이터를 지속적으로 요청하는 환경에서는 Django의 동기적(Synchronous) 처리 방식이 병목을 유발할 수 있다. Django의 작업자(Worker) 스레드는 데이터베이스 쓰기나 메시지 큐 푸시 등 I/O 작업이 발생할 때마다 블로킹(Blocking)되어 대기하므로, 동시 접속 요청이 급증하면 스레드 고갈 및 지연 시간(Latency) 급증 현상이 발생한다15. 이러한 고빈도 데이터 수집 및 실시간 API 영역에는 FastAPI가 적합하다. FastAPI는 ASGI(Asynchronous Server Gateway Interface) 서버인 Uvicorn 기반으로 작동하며 파이썬의 네이티브 비동기(async/await) 기능을 활용하여 수만 개의 동시 연결을 병목 없이 처리할 수 있다13.

| 비교 기준 | Django (ERP 및 기준 정보 영역) | FastAPI (MES 데이터 수집 및 실시간 POP 영역) |
| :---- | :---- | :---- |
| **아키텍처 성향** | 모놀리식 (Monolithic), 모델-뷰-템플릿(MVT) | 마이크로서비스 (Microservices), API 중심 |
| **처리 모델** | 동기식 중심 (부분적 비동기 지원) | 네이티브 비동기식 (Asynchronous by default) |
| **성능 및 지연시간** | 평균적인 웹 처리 수준, 무거운 I/O에서 블로킹 발생 | 극도로 빠름, 수천 개의 동시 I/O 작업을 논블로킹으로 처리 |
| **관리자 인터페이스** | 내장된 강력한 Admin Panel 제공 | 처음부터 직접 구축하거나 외부 툴 연동 필요 |
| **API 문서화** | 별도의 라이브러리 추가 설정 필요 | OpenAPI 규격에 맞춘 자동 문서화(Swagger UI) 제공 |
| **최적 활용처** | 복잡한 비즈니스 로직, 권한 관리, 기준서/BOM 마스터 관리 | 설비 IoT 데이터 인제스션, 실시간 OEE 모니터링, 모바일 앱 연동 |

따라서, 사용자 계정, 권한, 회계, 자재 명세서(BOM), 생산 계획 수립 등의 복잡한 비즈니스 관리는 Django 기반의 모놀리식 코어에서 처리하고, 공장 작업자용 태블릿 애플리케이션(POP)과의 통신 및 센서 데이터 수집을 위한 마이크로서비스는 FastAPI로 분리하여 구축하는 2-Tier 백엔드 아키텍처가 시스템의 유연성과 확장성을 극대화한다12.

## **3\. 데이터베이스 선정 및 50명 동시 접속 환경 최적화**

데이터 무결성과 복잡한 트랜잭션 처리가 생명인 제조 ERP/MES 시스템의 데이터베이스로는 ACID 규약을 완벽히 준수하며 대용량 데이터 처리에 강력한 성능을 발휘하는 **PostgreSQL**을 강력히 권장한다11. 다만, 최대 50명의 관리자 및 현장 작업자가 동시에 시스템을 활발히 사용하고, 백그라운드 워커와 수많은 IoT 센서 게이트웨이가 지속적으로 데이터를 기록하는 환경에서는 동시 접속에 대한 데이터베이스의 아키텍처적 대응이 필수적이다.  
PostgreSQL은 기본적으로 '연결 당 프로세스(Process-per-connection)' 모델을 채택하고 있다. 이는 클라이언트 애플리케이션이 데이터베이스에 새로운 연결을 생성할 때마다 운영체제(OS) 수준에서 독립적인 백엔드 프로세스가 포크(Fork)됨을 의미하며, 각 프로세스는 최소 10MB에서 20MB 이상의 메모리 리소스를 점유하게 된다19. 50명의 사용자가 웹과 모바일 앱을 통해 각각 여러 개의 API 요청을 동시에 발생시키고, 수십 대의 장비가 이벤트를 전송하게 되면 순식간에 수백 개의 연결이 형성된다. 이로 인해 데이터베이스 서버는 연결을 유지하기 위해 수 기가바이트(GB)의 메모리를 소모하며 극심한 CPU 컨텍스트 스위칭 오버헤드를 겪게 되어 결국 "FATAL: too many connections" 오류와 함께 시스템 전체가 마비될 위험이 높다19.  
이러한 물리적 한계를 극복하기 위해서는 애플리케이션 프레임워크와 PostgreSQL 사이에 **PgBouncer**와 같은 연결 풀링(Connection Pooling) 미들웨어를 반드시 도입해야 한다20. 연결 풀링은 식당의 주방 시스템과 유사하게 동작한다. 수천 명의 고객(클라이언트 요청)이 밀려들더라도 실제 주방의 요리사(물리적 DB 연결)는 50명으로 제한하여 병목을 방지하는 원리이다20. PgBouncer는 애플리케이션으로부터 들어오는 수많은 논리적 연결을 다중화(Multiplexing)하여 소수의 실제 데이터베이스 연결(Pool)로 라우팅한다23.  
연결 풀링을 구성할 때는 '트랜잭션 풀링 모드(Transaction Pooling Mode)'를 적용하는 것이 가장 효율적이다20. 이 모드에서는 클라이언트가 쿼리를 실행하는 트랜잭션 동안에만 물리적 연결을 할당받고, COMMIT이나 ROLLBACK이 발생하면 즉시 연결을 풀(Pool)로 반환하므로, 사용자 수천 명이 단 50개의 물리적 연결을 공유하여 지연 없이 시스템을 사용할 수 있다20.

| 지표 | 풀링 미적용 (Direct Connections) | 트랜잭션 풀링 적용 (PgBouncer) |
| :---- | :---- | :---- |
| **활성 데이터베이스 연결 수** | 1,000개 이상 (요청 수와 비례) | 50\~100개 내외 고정 (Max Pool Size) |
| **DB 메모리 소비량** | 약 20GB (연결당 10\~20MB 소요) | 약 1GB 이하로 안정적 유지 |
| **세션 상태 유지 여부** | 연결 내내 유지 (SET, 임시 테이블 사용 가능) | 트랜잭션 종료 시 소멸 (상태 비저장 쿼리 설계 필수) |
| **CPU 컨텍스트 스위칭** | 기하급수적으로 증가하여 병목 발생 | 제한된 프로세스로 안정적인 쿼리 스루풋 유지 |

주의할 점은 트랜잭션 풀링 모드 하에서는 연결이 트랜잭션 단위로 끊어지고 섞이므로, 세션 수준의 SET 명령어, 임시 테이블 보존, Prepared Statements 등의 세션 상태(Session State)가 유지되지 않는다는 점이다20. 따라서 시스템 설계 시 이러한 제약을 인지하고 쿼리를 최적화해야 하며, 스키마 마이그레이션(Django Migrations)이나 10분을 초과하는 장기 실행 배치 작업에는 풀러를 거치지 않는 '직접 연결(Direct Connection)'을 병행하여 사용하는 이원화된 데이터베이스 접속 전략을 취해야 한다23.

## **4\. 사용자 인터페이스 및 프론트엔드 배포 전략**

구축된 파이썬 백엔드 위에서 동작하는 프론트엔드 환경은 사용자의 역할과 업무 공간에 따라 '사내 인트라넷 웹'과 '현장 작업용 애플리케이션'으로 이원화되어 설계되어야 한다1. 사무실에서 근무하는 생산 관리자, 자재 관리자, 품질 엔지니어는 고해상도 모니터와 마우스를 통해 수많은 데이터를 분석하고 생산 계획을 수립해야 하므로 복잡한 데이터 그리드(Data Grid)와 차트 기능이 풍부한 웹 애플리케이션 환경이 적합하다25. Django의 템플릿과 HTMX를 결합하거나, Vue.js 기반의 SPA(Single Page Application)를 연동하여 정보의 가시성을 극대화하는 인트라넷을 구성한다.  
반면, 공장 현장에서 직접 쇳물이나 기름을 다루며 작업하는 작업자는 키보드나 마우스를 사용할 수 없으며, 방진 복장이나 장갑을 착용한 상태에서 태블릿 PC나 PDA 화면을 조작해야 한다12. 따라서 POP 및 MES 클라이언트 애플리케이션은 극도로 단순화된 대화형 사용자 경험(UX)을 제공해야 한다. 하나의 화면에는 '작업 시작', '불량 등록', '작업 완료' 등 직관적인 대형 버튼 위주로 배치되어야 하며, 카메라를 활용한 바코드(1D/2D) 스캐닝 기능이 네이티브 수준으로 원활하게 작동해야 한다1.  
이를 구현하기 위해 PWA(Progressive Web App) 기술을 적용하여 사내 인트라넷 웹을 모바일 기기에 앱처럼 설치하거나, React Native나 Flutter를 활용하여 현장용 별도 애플리케이션을 배포하는 방식을 권장한다. 또한, 공장 내부는 무선 네트워크(Wi-Fi) 음영 지역이 발생하기 쉬운 환경적 특성을 지니고 있다. 네트워크 단절로 인해 작업자가 실적을 입력하지 못하는 사태를 방지하기 위해, 오프라인 톨러런트(Offline-tolerant) 아키텍처를 도입해야 한다11. 이는 네트워크가 끊긴 상태에서도 디바이스의 로컬 스토리지에 작업 이력을 캐싱해 두었다가 연결이 복구되면 백엔드(FastAPI) 서버와 자동으로 동기화하는 기능을 필수적으로 포함한다12.

## **5\. 파이썬 기반 오픈소스 ERP 프레임워크 생태계와 맞춤형 개발 전략**

모든 데이터 모델을 처음부터 개발(Scratch)하는 대신, 파이썬 기반으로 이미 전 세계적으로 검증된 오픈소스 ERP 솔루션의 아키텍처를 차용하거나 이를 커스터마이징하는 방안을 적극 고려해야 한다. 대표적인 파이썬 오픈소스 ERP로는 Odoo와 ERPNext가 있으며, 이들의 구조를 이해하는 것은 안정적인 시스템 설계의 밑거름이 된다26.

| 비교 기준 | Odoo | ERPNext |
| :---- | :---- | :---- |
| **기반 프레임워크** | 자체 커스텀 프레임워크 및 ORM | Frappe Framework (Python \+ JS) |
| **아키텍처 사상** | 철저한 앱 기반의 모듈화 (필요한 기능만 설치/확장) | 단일 플랫폼 내 긴밀히 통합된 일체형 아키텍처 |
| **데이터베이스** | PostgreSQL 전용 | MariaDB 기반 |
| **커스터마이징 방식** | 코어 수정 없이 별도 모듈 상속(Inheritance)을 통한 오버라이드 | 코어 확장을 통한 개발 |
| **UI/UX 및 뷰 렌더링** | 데이터 기반의 XML 뷰(View) 런타임 병합 및 렌더링 | Frappe 환경 내 설정 기반 뷰 구성 |

Odoo의 아키텍처는 프레젠테이션, 비즈니스 로직, 데이터 저장소가 완전히 분리된 전형적인 3-Tier 아키텍처를 사용하며, 파이썬 기반의 강력한 ORM 레이어를 통해 복잡한 SQL 쿼리 없이 객체 지향적인 비즈니스 로직 구성을 가능하게 한다28. 특히 눈여겨볼 점은 Odoo의 업그레이드 안전성(Upgrade-safe)을 보장하는 모듈 확장 방식이다30. 시스템에 새로운 기준서 필드를 추가하거나 품질 검사 로직을 변경하고자 할 때, 원본(Core) 코드를 직접 수정하는 것이 아니라 파이썬 상속 메커니즘을 이용한 독립적인 '커스텀 모듈'을 만들어 덮어씌운다30. 또한 화면을 구성하는 프론트엔드 뷰(View) 역시 XML 형태로 데이터베이스에 저장되어 있으며, XPath를 활용해 기존 화면의 특정 부분만을 동적으로 교체할 수 있다29.  
사용자가 요구하는 '생산 이력, 품질, 자재, 기준서를 아우르는 ERP/MES 시스템'을 구축할 때, 이러한 Odoo나 ERPNext의 기본 생산(MRP), 자재(Inventory) 모듈을 베이스라인으로 삼고, 파이썬을 활용해 독자적인 MES 통신 모듈과 POP 인터페이스를 애드온(Add-on) 형태로 개발하여 연동하는 방식이 개발 리스크를 줄이고 도입 기간을 단축하는 매우 현실적이고 강력한 전략이 될 수 있다26.

## **6\. 생산 시점 관리(POP) 및 설비 데이터 수집(MES) 통신 아키텍처**

ERP가 사람에 의한 트랜잭션을 처리한다면, MES와 POP는 기계와 설비, 현장 센서로부터 데이터를 자동으로 그리고 정확하게 수집하는 역할을 담당한다10. 과거에는 PLC(Programmable Logic Controller)나 현장 장비들이 각기 다른 산업용 프로토콜을 사용해 통신했으나, 현대 스마트 팩토리 아키텍처에서는 이를 통일하고 구조화하기 위해 **OPC UA**와 **MQTT**라는 두 가지 프로토콜을 계층적으로 결합하여 사용한다33.

### **6.1. OPC UA를 통한 설비 계층의 시맨틱(Semantic) 데이터 모델링**

OPC UA(Unified Architecture)는 복잡한 제조 설비에서 발생하는 데이터를 안전하고 구조화된 방식으로 수집하기 위한 국제 표준 프로토콜이다34. 단순한 메시징 프로토콜은 기계로부터 '35.5'라는 숫자 값만 던져주어 수신 측에서 그 의미를 유추해야 하는 반면, OPC UA는 객체 지향적인 노드(Node) 구조를 통해 풍부한 시맨틱(의미론적) 메타데이터를 함께 제공한다34.  
예를 들어, 컨베이어 모터의 상태를 나타내는 데이터는 단순한 변수가 아니라 하나의 객체(ObjectNode)로 정의되며, 그 아래에 속도(RPM 단위, Float 타입), 온도(0\~150도 범위), 구동 상태(Running, Stopped 등 Enum 타입)와 같은 속성과 이력을 포함하는 계층적 주소 공간(Address Space)을 형성한다34. 파이썬 환경에서는 asyncua 라이브러리를 통해 고성능의 OPC UA 클라이언트를 구현할 수 있으며38, 폴링(주기적 요청) 방식이 아닌 특정 태그 값의 변화가 발생할 때만 데이터를 수신하는 구독(Subscription) 및 예외 보고(Report-by-exception) 패턴을 적용하여 현장 네트워크 부하를 극단적으로 줄일 수 있다33. 보안 측면에서도 전송 계층의 암호화뿐만 아니라 X.509 인증서를 통한 애플리케이션 계층의 엔드투엔드 보안을 기본 지원하여 현장의 폐쇄망 환경을 보호한다35.

### **6.2. 엣지 게이트웨이 및 MQTT 기반의 이벤트 중심 브로커링**

OPC UA가 클라이언트-서버 모델을 기반으로 기계의 언어를 구조화한다면, 이를 수많은 분석 시스템과 ERP로 가볍게 분배하는 역할은 발행-구독(Publish/Subscribe) 모델 기반의 **MQTT**가 담당한다33.

| 비교 기준 | OPC UA | MQTT (및 Sparkplug B 적용) |
| :---- | :---- | :---- |
| **통신 아키텍처** | 클라이언트 / 서버 기반 (구독 기능 포함) | 브로커 중심의 발행 / 구독 (Pub/Sub) 기반 |
| **주요 역할** | 장비의 상태와 메타데이터에 대한 풍부한 시맨틱 모델링 제공 | 가볍고 신속한 대규모 데이터 전송 및 라우팅 |
| **데이터 모델** | 복잡한 계층적 주소 공간 및 타입 시스템 내장 | 데이터 형식에 무관심(Agnostic), 주제(Topic) 기반 분류 |
| **오버헤드 및 확장성** | 상대적으로 무거움, 연결 관리에 높은 리소스 필요 | 극도로 가벼움(2바이트 헤더), 수만 개의 노드로 확장 용이 |

현장의 PLC 장비와 파이썬 ERP 시스템을 직접 연결하는 것은 설계상 큰 결함(Bottleneck)을 유발한다9. ERP 시스템의 일시적 점검이나 네트워크 지연 시 장비 데이터가 유실되며 양측 모두에 장애가 전파된다. 이를 방지하기 위해 현장 네트워크(L2/L3)에 파이썬 기반의 오프라인 톨러런트 엣지 게이트웨이(Edge Gateway)를 설치해야 한다9.  
이 게이트웨이는 PLC의 OPC UA 서버에 연결하여 데이터를 수집한 후, 불필요한 노이즈를 필터링(예: 초당 센서 데이터를 분당 이동 평균으로 변환)하여 대역폭을 최대 60%까지 절감한다35. 정제된 데이터는 Sparkplug B 규격 또는 표준 JSON 페이로드로 변환되어 중앙의 MQTT 브로커(Mosquitto 등)로 발행(Publish)된다35. 만약 상위 네트워크가 단절되면 엣지 게이트웨이는 데이터를 로컬 버퍼에 임시 저장(Store-and-forward)하고, 연결이 복구되는 즉시 순서대로 재전송하여 데이터의 무결성을 보장한다11.  
이후 파이썬 ERP 서버의 백그라운드 워커(Celery)가 이 MQTT 토픽을 구독하고 있다가 '작업 완료', '자재 소진', '불량 발생' 등의 비즈니스 이벤트가 수신되면 ERP의 회계 원장 및 재고 데이터를 비동기적으로 업데이트하는 느슨한 결합(Decoupling) 아키텍처를 완성한다10.

## **7\. 기준서, 절차서 관리 및 문서 자동화 체계**

제조 시스템의 근간은 마스터 데이터의 정확성과 표준 운영 절차서(SOP, Standard Operating Procedure)의 실시간 배포에 있다.  
기준 정보의 핵심인 자재 명세서(BOM, Bill of Materials)는 데이터베이스 설계 시 단일 계층(Single Level BOM)뿐만 아니라 다중 계층 트리 구조(Indented BOM)를 완벽히 표현할 수 있도록 구현되어야 한다44. 하나의 완제품이 수많은 반제품과 원자재로 분해되는 구조를 저장하기 위해 관계형 데이터베이스 내에 재귀적 참조(Self-referencing) 구조 또는 클로저 테이블(Closure Table) 패턴을 도입하며, 설계 변경(ECO)을 추적하기 위해 BOM의 버전을 엄격히 관리해야 한다44.  
또한 파트에 대한 BOM 정보 외에도, 어떠한 작업장(Work Center)과 설비를 거쳐 제품이 만들어지는지를 정의하는 라우팅(Routing) 기준 정보가 필요하다12. 이러한 기준 정보와 라우팅 데이터는 현장 작업자가 POP 태블릿을 통해 작업 지시를 조회할 때 실시간으로 최신 버전의 작업 절차서 및 조립 도면을 화면에 표시하는 기반 데이터가 된다9.  
생산 현장에서는 종종 제품 출하 시 첨부되어야 하는 품질 검사 성적서, 식별표, 작업 절차서 등의 문서를 동적으로 생성하여 인쇄 및 PDF로 보관해야 하는 요구사항이 발생한다. 이를 위해 파이썬 생태계에서는 **WeasyPrint** 라이브러리의 도입이 강력히 권장된다46. ReportLab과 같이 프로그래밍 방식으로 캔버스에 직접 좌표를 입력해 그림을 그리듯 문서를 생성하는 구식 라이브러리는 테이블 병합이나 복잡한 동적 레이아웃 처리에 매우 취약하다48. 반면 WeasyPrint는 표준 HTML5 템플릿과 CSS3(특히 Flexbox) 기술을 활용하여 웹 페이지를 디자인하듯 문서를 구성하고 이를 고품질의 PDF로 렌더링한다47. 파이썬 백엔드(Django 또는 FastAPI) 내에서 Jinja2 템플릿 엔진과 결합하여 동적인 품질 데이터 리스트를 HTML 템플릿에 주입하고 즉시 PDF 파일로 출력하는 흐름은 개발 생산성과 문서 퀄리티를 동시에 충족시킨다47.

## **8\. 자재 관리 및 바코드(ZPL) 직접 인쇄 아키텍처**

정확한 생산 이력을 관리하기 위해서는 자재의 입고 시점부터 투명한 로트(LOT) 추적 체계가 수립되어야 한다. 협력사로부터 원부자재가 입고되어 창고에 적재되는 순간, 시스템은 해당 묶음을 고유한 배치(Batch)로 인식하고 식별 코드를 부여하여 바코드 라벨을 발행해야 한다50.  
산업 현장에서 주로 사용되는 라벨 프린터(예: Zebra 프린터)를 제어하기 위해 윈도우 OS의 프린터 드라이버나 브라우저의 인쇄 대화 상자를 거치는 방식은 자동화를 저해하고 장애의 주요 원인이 된다. 대신 프로그래머틱하게 라벨을 제어할 수 있는 **ZPL(Zebra Programming Language)** 프로토콜 직접 전송 방식을 사용해야 한다51. ZPL은 캐럿(^)이나 물결표(\~) 문자로 시작하는 텍스트 기반 명령어로 구성되며, 라벨의 시작(^XA)과 종료(^XZ), 좌표(^FO), 바코드 생성(^BC), 텍스트 입력(^FD)을 정의하여 레이아웃을 구성한다51.  
파이썬 백엔드에서는 zpl 또는 zebra\_zpl과 같은 라이브러리를 통해 제품명, 수량, 입고일, 로트 번호 등 동적 데이터가 포함된 ZPL 문자열을 렌더링한다52. 이후 파이썬의 로우 소켓(Raw Socket) 프로그래밍(socket.AF\_INET, socket.SOCK\_STREAM)을 사용하여 공장 네트워크 내 프린터 IP의 9100 포트로 해당 문자열을 직접 전송한다52. 이 아키텍처는 프린터 드라이버 없이 백그라운드 워커를 통해 0.1초 만에 수백 장의 라벨을 병렬로 발행할 수 있게 해준다.  
이렇게 라벨링된 자재가 생산 라인으로 투입될 때, 작업자는 POP 단말기와 블루투스 바코드 스캐너를 이용해 자재의 로트 번호를 스캔한다. 시스템은 스캔된 자재가 현재 생산 중인 제품의 BOM 구성 요소와 일치하는지, 투입 순서가 올바른지 실시간으로 검증(Fool-proof)하여 오투입을 원천 차단한다25. 검증을 통과한 자재는 ERP 상에서 해당 로트의 재고가 즉시 차감(Backflushing)되고 재공품(WIP) 원가로 회계 처리된다10.

## **9\. 생산 이력 관리 및 품질(OEE) 통제**

MES 시스템의 가장 강력한 비즈니스 가치는 투명한 추적성(Traceability) 확보다. 특정 LOT 번호의 완제품에서 치명적인 품질 불량이 보고되었을 때, 해당 완제품을 구성하는 원부자재가 언제, 어느 협력사로부터 납품된 로트인지 역추적(Backward Trace)하는 기능이 제공되어야 한다50. 반대로 협력사에서 리콜 통보를 받은 원자재 로트가 있을 경우, 그 자재가 투입된 모든 재공품과 완제품을 전방 추적(Forward Trace)하여 창고 내 재고를 동결시키고 이미 출하된 제품의 유통 경로를 파악해야 한다50.  
이러한 양방향 추적성을 확보하기 위해서는 작업 지시(Work Order)가 실행될 때 투입된 Material\_Lot과 그 결과로 생성된 Product\_Lot 간의 다대다 맵핑 관계가 데이터베이스 내에서 단 하나의 누락 없이 체인처럼 연결되어 기록되어야 한다55.  
품질 관리 측면에서는 설비종합효율(OEE, Overall Equipment Effectiveness) 모니터링이 핵심이다. OEE는 가동률(Availability), 성능 효율(Performance), 양품률(Quality)의 세 가지 변수를 곱하여 산출된다7. 전통적인 시스템에서는 작업자가 교대근무 종료 시점에 수기로 생산량과 비가동 시간을 입력해왔으나, 이는 데이터 신뢰성이 매우 떨어진다43. 제안하는 시스템 아키텍처에서는 앞서 언급한 MQTT 엣지 게이트웨이를 통해 기계의 RUN, STOP, IDLE 상태 변경 이벤트와 양품/불량 사이클 카운트 이벤트를 시스템으로 실시간 전송한다12. 이벤트 지향 설계(Event-Driven Design) 원칙에 따라 데이터베이스 내 현재 상태 테이블을 덮어쓰는(Update) 것이 아니라, 모든 상태 변경 이벤트를 불변(Immutable)의 로그(Append-only)로 축적한다12. 파이썬 백엔드 워커는 주기적으로 이 시계열 이벤트를 취합하여 OEE 수치를 도출하고, 이를 바탕으로 관리자 대시보드에 정확한 분석 지표를 제공하게 된다.

## **10\. 통합 데이터베이스 스키마 및 ERD 설계**

앞서 설명한 복잡한 기능들을 유기적으로 지원하기 위한 관계형 데이터베이스(PostgreSQL)의 핵심 ERD(Entity-Relationship Diagram) 구조를 다음과 같이 설계한다45. 이 데이터 모델은 3정규형을 기본으로 하되, 시스템 부하가 큰 다단계 이력 추적 및 OEE 시계열 데이터 조회 시에는 조회 성능 극대화를 위해 일부 역정규화를 허용한다.

| 엔티티 (Entity Table) | 주요 속성 (Attributes & Keys) | 기능 및 관계 설명 |
| :---- | :---- | :---- |
| **Products** | product\_id (PK), sku, name, type, uom | 모든 원부자재, 반제품, 완제품의 기준 마스터 데이터. |
| **BOM\_Headers** | bom\_id (PK), product\_id (FK), version | 제품 생산을 위한 자재 명세서의 상위 식별 및 버전 관리 테이블. |
| **BOM\_Items** | bom\_item\_id (PK), bom\_id (FK), component\_id (FK), qty | 각 BOM 내에 소요되는 부품 내역 및 표준 수량 정의. |
| **WorkCenters** | center\_id (PK), name, machine\_ip, opc\_node\_uri | 생산 라인의 작업장 및 물리적 설비 리스트. OPC UA 통신 엔드포인트 포함. |
| **Routing** | routing\_id (PK), product\_id (FK), center\_id (FK), seq | 완제품을 만들기 위해 거쳐야 하는 작업장 순서 및 표준 공수. |
| **WorkOrders** | wo\_id (PK), product\_id (FK), plan\_qty, status | ERP에서 MES로 하달되는 구체적인 작업 지시서 데이터. |
| **InventoryLots** | lot\_id (PK), product\_id (FK), qty, barcode | 입고 및 생산으로 발생한 실물 재고 추적 단위. (바코드 기반 식별) |
| **MaterialConsumptions** | consume\_id (PK), wo\_id (FK), material\_lot\_id (FK), qty | 특정 작업 지시에 실제로 소비된 자재 로트 맵핑 (Backward Trace 핵심). |
| **ProductionResults** | result\_id (PK), wo\_id (FK), center\_id (FK), good\_qty, scrap\_qty, created\_lot\_id (FK) | 작업 지시 실행 후 획득한 양품/불량 수량 및 새로 생성된 로트 이력. |
| **MachineEvents** | event\_id (PK), center\_id (FK), event\_type (e.g., RUN, ERROR), timestamp | 엣지 게이트웨이에서 수신된 기계 단위의 실시간 상태 변화 시계열 로그. |

이 스키마를 바탕으로, Django ORM이나 SQLAlchemy 등의 파이썬 라이브러리를 사용하여 객체 관계로 매핑(Mapping)한다. 데이터 무결성을 유지하기 위해 데이터베이스 엔진 내에 필수적인 외래 키(Foreign Key) 제약 조건과 체크(Check) 제약 조건을 강력하게 설정해야 애플리케이션 레벨의 로직 오류로 인한 데이터 오염을 1차적으로 방어할 수 있다15.

## **11\. 시스템 도입 및 안정화 전략**

ERP, MES, POP, 창고 관리 시스템 등 생산의 전체 주기 데이터를 통합하는 대규모 시스템을 단일 시점(Big-bang)에 전사적으로 오픈하는 것은 현장의 극심한 반발과 데이터 오류를 초래하여 실패할 확률이 높다58. 따라서 조직의 혼란을 방지하고 데이터를 점진적으로 동기화하기 위한 다단계(Phased) 도입 전략이 수반되어야 한다58.

1. **Phase 1: 기준 정보 표준화 및 Core ERP 구축 (약 2\~3개월)** 공장 전반에 흩어져 있는 엑셀 기반의 품목 데이터, BOM, 작업 표준서를 정제하고 코드화하여 파이썬 기반 데이터베이스 마스터에 등재한다59. 이 단계에서는 수주, 발주, 회계 모듈 등 사무 기반 시스템을 우선 안정화하고, 원부자재 창고 입고 시 ZPL 바코드 라벨을 인쇄하여 부착하는 기초 인프라를 확립한다58.  
2. **Phase 2: MES 실행 제어 및 수기 POP 확산 (약 3\~6개월)** 현장 작업 구역에 POP 태블릿과 블루투스 스캐너를 배포한다. ERP에서 승인된 작업 지시서를 바탕으로 현장 작업자가 자재 바코드를 직접 스캔하여 공정에 투입하고 수동으로 실적을 입력하는 과정을 훈련한다7. 이 과정을 통해 시스템 내에서 완벽한 Forward / Backward 로트 추적성(Traceability)이 형성되는지 집중 검증하며, 오류 발생 빈도를 점진적으로 낮춘다.  
3. **Phase 3: IoT 인프라 구축 및 데이터 자동화 (약 6\~9개월)** 마지막으로 수작업 입력을 최소화하기 위해 생산 라인 핵심 설비에 파이썬 엣지 게이트웨이를 설치한다60. 설비의 PLC 태그에서 발생하는 양품/불량 카운터 및 기계 가동 상태 데이터를 OPC UA와 MQTT 브로커를 거쳐 Odoo 기반 등의 ERP 모듈에 직접 결합한다43. 이를 통해 인간의 개입 없이도 정교한 실시간 OEE 산출 및 정확한 원가 배분 등 스마트 팩토리 본연의 가치를 실현하게 된다.

#### **참고 자료**

1. MES/ERP 통합형 생산관리시스템 \- goodstream 2026, [https://goodstream.co.kr/docs/solution/lotus/lotus-mes](https://goodstream.co.kr/docs/solution/lotus/lotus-mes)  
2. MES, 스마트 팩토리, 공장 자동화에 대해 \- 요약 장인 \- 티스토리, [https://namn.tistory.com/145](https://namn.tistory.com/145)  
3. 스마트공장 ERP / MES \- 한국전기, [https://korea-electric.com/smart-factory/smart-factory-erp-mes](https://korea-electric.com/smart-factory/smart-factory-erp-mes)  
4. MES와 QMS는 무슨 뜻? 스마트 팩토리 구축을 위해 꼭 알아야 할 용어 모음 : 기초편 \- SK AX, [https://www.skax.co.kr/insight/trend/2928](https://www.skax.co.kr/insight/trend/2928)  
5. How to Build Seamless MES Integration with ERP: A Practical Guide for Manufacturers, [https://mie-solutions.com/how-to-build-seamless-mes-integration-with-erp-a-practical-guide-for-manufacturers/](https://mie-solutions.com/how-to-build-seamless-mes-integration-with-erp-a-practical-guide-for-manufacturers/)  
6. 제조 Smart Factory MES 구축, [https://www.kolonbenit.com/cmm/fms/FileDown.do?fileId=FILE\_000000000001123\&fileSn=1](https://www.kolonbenit.com/cmm/fms/FileDown.do?fileId=FILE_000000000001123&fileSn=1)  
7. MES, ERP, IoT – 스마트팩토리 용어 정리, [https://smartfactoria.com/content/mes-erp-iot-%EC%8A%A4%EB%A7%88%ED%8A%B8%ED%8C%A9%ED%86%A0%EB%A6%AC-%EC%9A%A9%EC%96%B4-%EC%A0%95%EB%A6%AC-de5c7c91-2bd5-4566-832c-eb53a11e6440](https://smartfactoria.com/content/mes-erp-iot-%EC%8A%A4%EB%A7%88%ED%8A%B8%ED%8C%A9%ED%86%A0%EB%A6%AC-%EC%9A%A9%EC%96%B4-%EC%A0%95%EB%A6%AC-de5c7c91-2bd5-4566-832c-eb53a11e6440)  
8. The ERP–MES–PLC Triangle: A Real-Time Reference Architecture \- iFactory AI, [https://ifactoryapp.com/article/erp-mes-plc-triangle-real-time-architecture](https://ifactoryapp.com/article/erp-mes-plc-triangle-real-time-architecture)  
9. Software Architecture for Industrial Machinery Manufacturers: Integrating ERP, MES, and IoT Platforms, [https://devoxsoftware.com/blog/software-architecture-for-industrial-machinery-manufacturers-integrating-erp-mes-and-iot-platforms/](https://devoxsoftware.com/blog/software-architecture-for-industrial-machinery-manufacturers-integrating-erp-mes-and-iot-platforms/)  
10. Manufacturing ERP & MES Integration | NETLINKS, [https://netlinks.net/blog/manufacturing-mes-erp-integration/](https://netlinks.net/blog/manufacturing-mes-erp-integration/)  
11. MES Development Service | Simplico — Custom Python MES for Manufacturers, [https://simplico.net/mes-development/](https://simplico.net/mes-development/)  
12. How to Develop a Manufacturing Execution System (MES) with Python \- Simplico, [https://simplico.net/2025/12/14/how-to-develop-a-manufacturing-execution-system-mes-with-python/](https://simplico.net/2025/12/14/how-to-develop-a-manufacturing-execution-system-mes-with-python/)  
13. FastAPI vs Django: Which Backend Framework Is the Optimal Choice for Businesses in 2026? \- MERCTECHS | Software Consultancy, [https://www.merctechs.com/en/blog/fastapi-vs-django-2026](https://www.merctechs.com/en/blog/fastapi-vs-django-2026)  
14. Which Is the Best Python Web Framework: Django, Flask, or FastAPI? \- The JetBrains Blog, [https://blog.jetbrains.com/pycharm/2025/02/django-flask-fastapi/](https://blog.jetbrains.com/pycharm/2025/02/django-flask-fastapi/)  
15. FastAPI vs. Django: Choosing the Best Python Framework for Your Application Needs, [https://dev.to/romdevin/fastapi-vs-django-choosing-the-best-python-framework-for-your-application-needs-24gk](https://dev.to/romdevin/fastapi-vs-django-choosing-the-best-python-framework-for-your-application-needs-24gk)  
16. FastAPI vs Django \[Best Choice for Large Projects\] \- Raagz IT, [https://raagz.it/django-fastapi-to-build-large-projects/index.html](https://raagz.it/django-fastapi-to-build-large-projects/index.html)  
17. Concurrency and async / await \- FastAPI, [https://fastapi.tiangolo.com/async/](https://fastapi.tiangolo.com/async/)  
18. Python Application Development | DynamicUnit, [https://dynamicunit.com/python-application-development](https://dynamicunit.com/python-application-development)  
19. Outgrowing Postgres: Handling increased user concurrency \- Tinybird, [https://www.tinybird.co/blog/outgrowing-postgres-handling-increased-user-concurrency](https://www.tinybird.co/blog/outgrowing-postgres-handling-increased-user-concurrency)  
20. PostgreSQL Performance Optimization: Why Connection Pooling Is Critical at Scale, [https://dev.to/abdullahmubin/postgresql-performance-optimization-why-connection-pooling-is-critical-at-scale-27bk](https://dev.to/abdullahmubin/postgresql-performance-optimization-why-connection-pooling-is-critical-at-scale-27bk)  
21. Not all Postgres connection pooling is equal \- Microsoft Community Hub, [https://techcommunity.microsoft.com/blog/adforpostgresql/not-all-postgres-connection-pooling-is-equal/825717](https://techcommunity.microsoft.com/blog/adforpostgresql/not-all-postgres-connection-pooling-is-equal/825717)  
22. How to Manage Connection Limits in PostgreSQL \- OneUptime, [https://oneuptime.com/blog/post/2026-01-25-manage-connection-limits-postgresql/view](https://oneuptime.com/blog/post/2026-01-25-manage-connection-limits-postgresql/view)  
23. Connection pooling in Prisma Postgres, [https://www.prisma.io/docs/postgres/database/connection-pooling](https://www.prisma.io/docs/postgres/database/connection-pooling)  
24. Managed Connection Pooling overview | Cloud SQL for PostgreSQL, [https://docs.cloud.google.com/sql/docs/postgres/managed-connection-pooling](https://docs.cloud.google.com/sql/docs/postgres/managed-connection-pooling)  
25. MES (Manufacturing Execution System, 공장정보화시스템) \- Romantic Deer Project, [https://romanticdeer.tistory.com/entry/MES-Manufacturing-Execution-System-%EA%B3%B5%EC%9E%A5%EC%A0%95%EB%B3%B4%ED%99%94%EC%8B%9C%EC%8A%A4%ED%85%9C](https://romanticdeer.tistory.com/entry/MES-Manufacturing-Execution-System-%EA%B3%B5%EC%9E%A5%EC%A0%95%EB%B3%B4%ED%99%94%EC%8B%9C%EC%8A%A4%ED%85%9C)  
26. Odoo vs ERPNext: 8 Best ERP Differences for Businesses \- NerithonX Technologies, [https://nerithonx.com/blog/open-source-erp-odoo-vs-erpnext/](https://nerithonx.com/blog/open-source-erp-odoo-vs-erpnext/)  
27. Top Open Source ERP Python for Your Business | Mobilunity, [https://mobilunity.com/blog/list-of-open-source-erps-fueled-by-python/](https://mobilunity.com/blog/list-of-open-source-erps-fueled-by-python/)  
28. Chapter 1: Architecture Overview — Odoo 19.0 documentation, [https://www.odoo.com/documentation/19.0/developer/tutorials/server\_framework\_101/01\_architecture.html](https://www.odoo.com/documentation/19.0/developer/tutorials/server_framework_101/01_architecture.html)  
29. Building a Module — Odoo 19.0 documentation, [https://www.odoo.com/documentation/19.0/developer/tutorials/backend.html](https://www.odoo.com/documentation/19.0/developer/tutorials/backend.html)  
30. Odoo Customization Using Python Explained \- NerithonX Technologies, [https://nerithonx.com/blog/odoo-customization-using-python-explained/](https://nerithonx.com/blog/odoo-customization-using-python-explained/)  
31. How Python Driven Odoo Customizations Can Unlock Business Potential in 2025, [https://www.odooprogrammer.com/blog/how-python-driven-odoo-customizations-can-unlock-business-potential](https://www.odooprogrammer.com/blog/how-python-driven-odoo-customizations-can-unlock-business-potential)  
32. View architectures — Odoo 19.0 documentation, [https://www.odoo.com/documentation/19.0/developer/reference/user\_interface/view\_architectures.html](https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html)  
33. OPC UA and MQTT: How to Bridge OT Protocols for Scalable Industrial Data \- HiveMQ, [https://www.hivemq.com/blog/opc-ua-mqtt-bridge-ot-protocols-industrial-data/](https://www.hivemq.com/blog/opc-ua-mqtt-bridge-ot-protocols-industrial-data/)  
34. MQTT vs OPC UA: Why This Question Never Has a Straight Answer \- FlowFuse, [https://flowfuse.com/blog/2026/01/opcua-vs-mqtt/](https://flowfuse.com/blog/2026/01/opcua-vs-mqtt/)  
35. OPC-UA & MQTT Protocol Integration for Smart Factory Greenfield Builds \- iFactory AI, [https://ifactoryapp.com/greenfield-consulting/opc-ua-mqtt-protocol-integration-smart-factory-greenfield](https://ifactoryapp.com/greenfield-consulting/opc-ua-mqtt-protocol-integration-smart-factory-greenfield)  
36. OPC UA vs MQTT: Which Protocol Should You Use for IIoT Data Integration?, [https://vnodeautomation.com/opc-ua-vs-mqtt/](https://vnodeautomation.com/opc-ua-vs-mqtt/)  
37. A Practical Guide to OPC UA with Python: Client, Server, Containerization, and Telegraf, [https://akpolatcem.medium.com/getting-started-with-opc-ua-building-your-first-client-server-application-in-python-6107fb4cafec](https://akpolatcem.medium.com/getting-started-with-opc-ua-building-your-first-client-server-application-in-python-6107fb4cafec)  
38. asyncua.client package \- opcua-asyncio documentation, [https://opcua-asyncio.readthedocs.io/en/latest/api/asyncua.client.html](https://opcua-asyncio.readthedocs.io/en/latest/api/asyncua.client.html)  
39. asyncua \- PyPI, [https://pypi.org/project/asyncua/](https://pypi.org/project/asyncua/)  
40. A Minimal OPC-UA Client \- opcua-asyncio documentation, [https://opcua-asyncio.readthedocs.io/en/latest/usage/get-started/minimal-client.html](https://opcua-asyncio.readthedocs.io/en/latest/usage/get-started/minimal-client.html)  
41. MQTT vs. OPC UA in Modern IIoT: Which Protocol Should You Choose? | Proxus Blog, [https://proxus.io/blog/mqtt-vs-opc-ua-in-modern-iiot/](https://proxus.io/blog/mqtt-vs-opc-ua-in-modern-iiot/)  
42. Odoo Mqtt \- Autoronics, [https://www.autoronics.com/odoo-mqtt](https://www.autoronics.com/odoo-mqtt)  
43. Machine/PLC IoT Gateway (MQTT/OPC-UA) — Specialized Solutions Module for Odoo, [https://ecosire.com/hi/apps/odoo/odoo-machine-iot-gateway-mqtt-opcua](https://ecosire.com/hi/apps/odoo/odoo-machine-iot-gateway-mqtt-opcua)  
44. BOM: 생산을 체계화하는 핵심 데이터 구조, [https://rupijun.tistory.com/entry/BOM-%EC%83%9D%EC%82%B0%EC%9D%84-%EC%B2%B4%EA%B3%84%ED%99%94%ED%95%98%EB%8A%94-%ED%95%B5%EC%8B%AC-%EB%8D%B0%EC%9D%B4%ED%84%B0-%EA%B5%AC%EC%A1%B0](https://rupijun.tistory.com/entry/BOM-%EC%83%9D%EC%82%B0%EC%9D%84-%EC%B2%B4%EA%B3%84%ED%99%94%ED%95%98%EB%8A%94-%ED%95%B5%EC%8B%AC-%EB%8D%B0%EC%9D%B4%ED%84%B0-%EA%B5%AC%EC%A1%B0)  
45. Open Source Erp Database Structure and Schema Diagram, [https://databasesample.com/database/open-source-erp-database](https://databasesample.com/database/open-source-erp-database)  
46. WeasyPrint, [https://weasyprint.org/](https://weasyprint.org/)  
47. Generate good looking PDFs with WeasyPrint and Jinja2 \- Josh Karamuth, [https://joshkaramuth.com/blog/generate-good-looking-pdfs-weasyprint-jinja2/](https://joshkaramuth.com/blog/generate-good-looking-pdfs-weasyprint-jinja2/)  
48. Top 10 Python PDF generator libraries: Complete guide for developers (2026) \- Nutrient, [https://www.nutrient.io/blog/top-10-ways-to-generate-pdfs-in-python/](https://www.nutrient.io/blog/top-10-ways-to-generate-pdfs-in-python/)  
49. Python PDF Generation from HTML with WeasyPrint \- Jonathan Bowman, [https://www.bowmanjd.com/python-weasyprint-pdf/](https://www.bowmanjd.com/python-weasyprint-pdf/)  
50. Lot Tracking, Traceability and Barcode Applications in MES Systems, [https://www.trexakademi.com/en/digital-tool/lot-tracking-traceability-and-barcode-applications-in-mes-systems-49](https://www.trexakademi.com/en/digital-tool/lot-tracking-traceability-and-barcode-applications-in-mes-systems-49)  
51. An Introduction to ZPL \- Labelary, [https://labelary.com/zpl.html](https://labelary.com/zpl.html)  
52. Print .lbl Files on Zebra Printers with Python | PDF | Software Engineering \- Scribd, [https://www.scribd.com/document/738407982/Python-how-to-print-a-lbl-file-on-Zebra-printer-Stack-Overflow](https://www.scribd.com/document/738407982/Python-how-to-print-a-lbl-file-on-Zebra-printer-Stack-Overflow)  
53. zpl · PyPI, [https://pypi.org/project/zpl/](https://pypi.org/project/zpl/)  
54. mtking2/py-zebra-zpl: A Python library to design and generate printable ZPL2 code. \- GitHub, [https://github.com/mtking2/py-zebra-zpl](https://github.com/mtking2/py-zebra-zpl)  
55. system.mes.trace.getTraceabilityData, [https://docs.sepasoft.com/articles/user-manual/system-mes-trace-gettraceabilitydata-lotnumber-lotsequencenumber-fanoutlimit-depthlimit-includesupp](https://docs.sepasoft.com/articles/user-manual/system-mes-trace-gettraceabilitydata-lotnumber-lotsequencenumber-fanoutlimit-depthlimit-includesupp)  
56. Appendix B Sample ERD Exercises – Database Design – 2nd Edition \- BC Open Textbooks, [https://opentextbc.ca/dbdesign01/back-matter/appendix-b-erd-exercises/](https://opentextbc.ca/dbdesign01/back-matter/appendix-b-erd-exercises/)  
57. Entity Relationship Diagram (ERD) \- What is an ER Diagram? \- SmartDraw, [https://www.smartdraw.com/entity-relationship-diagram/](https://www.smartdraw.com/entity-relationship-diagram/)  
58. MES 제작, 생산성 30% 증가시키는 스마트 팩토리 전략 \- 크몽, [https://kmong.com/article/3088--MES-%EC%A0%9C%EC%9E%91-%EC%83%9D%EC%82%B0%EC%84%B1-30-%EC%A6%9D%EA%B0%80%EC%8B%9C%ED%82%A4%EB%8A%94-%EC%8A%A4%EB%A7%88%ED%8A%B8-%ED%8C%A9%ED%86%A0%EB%A6%AC-%EC%A0%84%EB%9E%B5](https://kmong.com/article/3088--MES-%EC%A0%9C%EC%9E%91-%EC%83%9D%EC%82%B0%EC%84%B1-30-%EC%A6%9D%EA%B0%80%EC%8B%9C%ED%82%A4%EB%8A%94-%EC%8A%A4%EB%A7%88%ED%8A%B8-%ED%8C%A9%ED%86%A0%EB%A6%AC-%EC%A0%84%EB%9E%B5)  
59. 스마트공장지원사업 | SAP ERP MES 동시 구축 가능할까?, [https://blog.irisinfotech.co.kr/entry/11](https://blog.irisinfotech.co.kr/entry/11)  
60. Integrating MES with Odoo ERP: A Blueprint for Metals & Mining Plants, [https://rowwad.qa/mes-odoo-erp-mining-integration/](https://rowwad.qa/mes-odoo-erp-mining-integration/)  
61. MES와 ERP, 스마트팩토리에서의 역할 분담, [https://rblog252026.tistory.com/123](https://rblog252026.tistory.com/123)