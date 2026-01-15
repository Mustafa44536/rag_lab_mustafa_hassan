# rag_lab_mustafa_hassan
Detta projekt är en enkel implementation av RAG (Retrieval Augmented Generation) där en språkmodell kombineras med en lokal kunskapsbas för att ge mer faktabaserade svar.
Projektet är en del av kursen AI Engineering – RAG Lab.

# Vad gör projektet?
Dokument lagras i en lokal kunskapsbas
Frågor embedas och matchas mot dokumenten (vector search)
Relevant kontext hämtas
En LLM genererar ett svar baserat på den hämtade kontexten
Svar exponeras via:
FastAPI (lokalt)
Azure Functions
Streamlit-frontend
# Tekniker som används
Python
FastAPI
Azure Functions
LanceDB
SentenceTransformers
PydanticAI
Streamlit
Gemini (Google LLM)
# Projektstruktur
rag_lab_mustafa_hassan/
│
├── backend/
│   ├── rag.py              # RAG-logik (retrieval + agent)
│   ├── rag_service.py      # Delad service för API & Azure Function
│
├── frontend/
│   └── app.py              # Streamlit frontend
│
├── knowledge_base/         # Dokument som används i RAG
├── api.py                  # FastAPI-app
├── function_app.py         # Azure Functions entrypoint
├── host.json               # Azure Functions config
├── ingestion.py            # Indexering av dokument
└── requirements.txt
## Installation (lokalt)

### 1. Skapa virtuell miljö
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
2. Installera beroenden
pip install -r requirements.txt
Steg 1 – Indexera dokument
Dokumenten i knowledge_base/ måste indexeras innan frågor kan ställas.
python ingestion.py
Steg 2 – Starta FastAPI
python -m uvicorn api:app --host 127.0.0.1 --port 8001
Testa API
curl -X POST http://127.0.0.1:8001/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is RAG?"}'
Steg 3 – Azure Functions (lokalt)
func start
Testa Azure Function
curl -X POST http://127.0.0.1:7071/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is RAG?"}'
Steg 4 – Streamlit frontend
streamlit run frontend/app.py
Öppna i webbläsaren:
http://localhost:8501
Deployment (Azure Functions)
Projektet kan deployas till Azure Functions.
func azure functionapp publish <FUNCTION_APP_NAME>
Endpoint:
https://<FUNCTION_APP_NAME>.azurewebsites.net/api/rag/query