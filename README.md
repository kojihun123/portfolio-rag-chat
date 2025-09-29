## 프로젝트 소개
FastAPI와 PostgreSQL(pgvector)로 문서를 임베딩하고 검색하는 RAG 백엔드입니다. 문서 upsert와 코사인 기반 검색 API를 제공합니다.

## 기술 스택
FastAPI, SQLAlchemy 2, asyncpg, PostgreSQL(pgvector), sentence-transformers, Docker Compose

## 사전 요구사항
- Docker Desktop
- Python 3.11+
- Git
- (선택) Node.js 18+

## 빠른 시작 (Windows PowerShell)
- DB 실행: `cd backend && docker compose up -d`
- 가상환경: `python -m venv .venv` -> `.\\.venv\\Scripts\\Activate.ps1`
- 의존성 설치: `pip install -r requirements.txt`
- 서버 실행: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- (선택) 프론트: `cd ..\\web && npm install && npm run dev`

## .env 예시 (backend/.env)
```env
DB_HOST=
DB_PORT=5432
DB_NAME=
DB_USER=
DB_PASSWORD=
EMBEDDING_MODEL_NAME=intfloat/multilingual-e5-large
EMBEDDING_DIM=1024
OPENAI_API_KEY=
OPENAI_MODEL_NAME=gpt-4o-mini
OPENAI_TEMPERATURE=0.3
TOP_K=5
MAX_TOKENS=512
```

## 스모크 테스트
- `POST /documents` (meta 사용 권장, metadata도 허용)
  ```bash
  curl -X POST http://localhost:8000/documents \
    -H "Content-Type: application/json" \
    -d '{"id":"doc-1","content":"FastAPI 예제 문서","meta":{"lang":"ko"}}'
  ```
- `GET /documents/search?q=fastapi&k=3`
  ```bash
  curl "http://localhost:8000/documents/search?q=fastapi&k=3"
  ```

## Git 사용법
- 최초 push: `git init && git add . && git commit -m "init" && git branch -M main && git remote add origin <repo> && git push -u origin main`
- 다른 PC에서: `git clone <repo>` -> 사전 요구사항 설치 -> `cd backend && docker compose up -d` -> 가상환경 구성 -> `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

## 트러블슈팅
- 포트 충돌 시 `backend/docker-compose.yml`의 `5432:5432` 등을 비어 있는 포트로 조정
- PowerShell 실행 정책 오류: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
- DB 연결 실패: 컨테이너 기동 상태와 `.env`의 DB 계정 정보를 재확인
- pgvector 또는 JSONB 바인딩 오류: SQLAlchemy `bindparam`에 `Vector(...)`, `JSONB` 타입이 설정돼 있는지 확인


## 진행 상황 요약

### ✅ 마지막으로 한 작업
- **DB/모델/스키마 정리**: `Document / ChatSession / Message` 모델 확정(`meta` ←→ DB 컬럼 `"metadata"`), 스키마에서 `meta/metadata` 모두 입력 허용.
- **DB 초기화 & 인덱스**: 앱 시작 시 테이블 자동 생성 + `docs.embedding`에 **HNSW (vector_cosine_ops)** 인덱스 생성.
- **임베딩 & 검색**: `embedding.py`(문장→벡터, 정규화) / `retriever.py`(코사인 거리 `<=>` 사용) 구현.
- **문서 업서트 & 검색 API**: `POST /documents`(임베딩 저장, **JSONB/Vector 타입 바인딩**) / `GET /documents/search` 동작 확인.
- **개발 편의**: Docker로 Postgres 실행, 로컬에서 서버 구동 및 curl로 스모크 테스트 완료. Git 기본 브랜치 **master**로 운용.

### ▶️ 다음으로 할 작업
- **/chat 구현**: `services/chat.py` + `routers/chat.py` — 검색 결과 컨텍스트로 RAG 답변 생성(OPENAI 연동) 및 대화 내역 저장.
- **CORS 허용(개발용)**: 프론트에서 API 호출 가능하게 설정.
- **텍스트 검색 보완(선택)**: `pg_trgm` 확장 + GIN 인덱스, `GET /documents/text-search` 추가.
- **시드/임포트 스크립트**: 포트폴리오 문서 일괄 적재 스크립트.
- **프론트 연동(선택)**: `/chat` 연결, `session_id`로 대화 이어가기 & `sources` 표시.
