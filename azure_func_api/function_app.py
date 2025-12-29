import json
import azure.functions as func

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load env (local.settings.json locally, App Settings in Azure)
load_dotenv()

# Add repo root to import backend/
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

from backend.rag import RAGChatbot

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
bot = RAGChatbot(top_k=3)

@app.route(route="rag/query", methods=["POST"])
def rag_query(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        question = (body.get("question") or "").strip()
        if not question:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'question'"}),
                status_code=400,
                mimetype="application/json",
            )

        answer = bot.answer(question)
        return func.HttpResponse(
            json.dumps({"answer": answer}),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )
