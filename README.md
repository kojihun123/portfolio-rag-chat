## 프로젝트 소개
FastAPI와 PostgreSQL(pgvector)을 사용해 문서를 저장하고 검색하는 RAG 기반 챗봇입니다. 문서를 등록한 뒤 LLM에 질문하면 관련 문서 내용을 인용해 답변해 줍니다.

## 기술 스택
FastAPI, SQLAlchemy 2, asyncpg, PostgreSQL (pgvector), sentence-transformers, Docker Compose, OpenAI Responses API

## 요구 사항
- Docker Desktop
- Python 3.11+
- Git
- (선택) Node.js 18+

## 실행 방법 (Windows PowerShell 기준)
1. DB 컨테이너: `cd backend && docker compose up -d`
2. 가상환경: `python -m venv .venv` → `.\\.venv\\Scripts\\Activate.ps1`
3. 패키지 설치: `pip install -r requirements.txt`
4. 백엔드 서버: `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
5. (선택) 프런트: `cd ..\\web && npm install && npm run dev`
6. VS Code Python 인터프리터를 `.venv`로 지정하세요.

## Postgres 접속 팁
- 컨테이너 쉘: `docker exec -it portfolio-chat-db /bin/bash`
- psql 예시: `PGPASSWORD=<비밀번호> psql -U rag -d ragdb`
- 로컬 도구 사용 시 호스트/포트는 `.env`의 DB 설정을 참고하세요.

## .env (backend/.env)
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ragdb
DB_USER=rag
DB_PASSWORD=rag-password
EMBEDDING_MODEL_NAME=intfloat/multilingual-e5-large
EMBEDDING_DIM=1024
OPENAI_API_KEY=
OPENAI_MODEL_NAME=gpt-4o-mini
OPENAI_TEMPERATURE=0.3
TOP_K=5
MAX_TOKENS=512
```

## API 빠른 테스트
- 문서 등록 `POST /documents`
  ```bash
  curl -X POST http://localhost:8000/documents \
    -H "Content-Type: application/json" \
    -d '{"id":"doc-1","content":"FastAPI 소개","meta":{"lang":"ko"}}'
  ```
- 문서 검색 `GET /documents/search`
  ```bash
  curl "http://localhost:8000/documents/search?q=fastapi&k=3"
  ```
- 채팅 `POST /chat`
  ```bash
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"message":"포트폴리오 봇 소개해줘", "session_id": "demo-session"}'
  ```

## 현재 구현 사항
- **문서 저장/검색**: `POST /documents`, `GET /documents/search` 제공. pgvector 기반 코사인 유사도로 문서 검색.
- **임베딩 파이프라인**: SentenceTransformer 로딩, `Vector` 컬럼/`JSONB` 메타데이터 처리 정리.
- **RAG 챗봇**: `/chat` 엔드포인트가 `services/chat.py`의 `ask_llm`을 호출. 대화 세션/메시지 저장, 문서 검색 결과를 컨텍스트로 주입해 OpenAI Responses API로 답변 생성.
- **세션 관리**: 요청에 `session_id`가 없으면 새 세션 발급. 메시지는 `messages` 테이블에 사용자/어시스턴트 역할로 저장.

## 앞으로 할 일
- **에러/로그 개선**: OpenAI 호출 실패, DB 예외에 대한 로깅 및 사용자 피드백 정비.
- **테스트**: 서비스 및 라우터에 대한 단위/통합 테스트 작성.
- **CORS 등 운영 설정**: 프런트엔드와 연동 시 필요한 CORS, 보안 헤더, rate limit.
- **추가 검색 옵션**: 텍스트 유사도(pg_trgm) 기반 검색 API 추가 고려.
- **프런트 연동**: 웹 프런트에서 `/chat` 흐름 연결 및 UI 개선.

## Git 초기 셋업
- 첫 커밋/푸시: `git init && git add . && git commit -m "init" && git branch -M main && git remote add origin <repo> && git push -u origin main`
- 다른 PC: `git clone <repo>` → 위 실행 절차 반복 → `uvicorn app.main:app --reload`

## 기타 팁
- 포워드 포트가 겹칠 경우 `backend/docker-compose.yml`의 포트를 조정하세요.
- PowerShell 스크립트 실행이 막혀 있으면 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- `.env` 누락/오타로 DB 연결이 안 될 수 있으니 꼭 확인하세요.