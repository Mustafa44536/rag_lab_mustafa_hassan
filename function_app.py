import json
import azure.functions as func

from backend.rag_service import answer_question

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="rag/query", methods=["POST"])
def rag_query(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Body must be valid JSON"}),
            status_code=400,
            mimetype="application/json",
        )

    question = (body.get("question") or "").strip()
    if not question:
        return func.HttpResponse(
            json.dumps({"error": "Missing field: question"}),
            status_code=400,
            mimetype="application/json",
        )

    try:
        result = answer_question(question)
        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )
