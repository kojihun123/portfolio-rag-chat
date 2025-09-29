## 프로젝트 소개
FastAPI와 PostgreSQL(pgvector)로 문서를 임베딩·검색하는 RAG 백엔드입니다. 문서 upsert와 코사인 기반 유사도 검색 API를 제공합니다.

## 기술 스택
FastAPI · SQLAlchemy 2 · asyncpg · PostgreSQL(pgvector) · sentence-transformers · Docker Compose

## 폴더 구조
`	ext
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── schemas.py
│   ├── routers/
│   │   └── documents.py
│   └── services/
│       └── docs.py
├── docker-compose.yml
└── requirements.txt
web/
└── app/page.tsx
`

## 사전 요구사항
- Docker Desktop
- Python 3.11+
- Git
- (선택) Node.js 18+

## 빠른 시작 (Windows PowerShell)
- DB 실행: cd backend && docker compose up -d
- 가상환경: python -m venv .venv → .\.venv\Scripts\Activate.ps1
- 의존성 설치: pip install -r requirements.txt
- 서버 실행: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
- (선택) 프론트: cd ..\web && npm install && npm run dev

## .env 예시 (backend/.env)
`ash
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
`

## 스모크 테스트
- POST /documents (meta 사용 권장, metadata도 허용)
  `ash
  curl -X POST http://localhost:8000/documents ^
    -H "Content-Type: application/json" ^
    -d "{\"id\":\"doc-1\",\"content\":\"FastAPI 예제 문서\",\"meta\":{\"lang\":\"ko\"}}"
  `
- GET /documents/search?q=fastapi&k=3
  `ash
  curl "http://localhost:8000/documents/search?q=fastapi&k=3"
  `

## Git 사용법
- 최초 push: git init && git add . && git commit -m "init" && git branch -M main && git remote add origin <repo> && git push -u origin main
- 다른 PC에서: git clone <repo> → 사전 요구사항 설치 → cd backend && docker compose up -d → 가상환경 구성 → uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

## 트러블슈팅
- 포트 충돌 시 ackend/docker-compose.yml의 5432:5432 등을 비어 있는 포트로 조정
- PowerShell 실행 정책 오류: Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
- DB 연결 실패: 컨테이너 기동 상태와 .env의 DB 계정 정보를 재확인
- pgvector/JSONB 바인딩 문제: SQLAlchemy indparam에 Vector(...), JSONB 타입이 선언되었는지 확인
