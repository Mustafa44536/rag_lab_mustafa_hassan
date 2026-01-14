import json
from pathlib import Path

import azure.functions as func
import lancedb
from sentence_transformers import SentenceTransformer

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

DATA_DIR = Path("data")
DB_DIR = Path("knowledge_base")
TABLE_NAME = "transcripts"

_model = None
_table = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def _get_table():
    global _table
    if _table is None:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        db = lancedb.connect(str(DB_DIR))
        _table = db.open_table(TABLE_NAME) if TABLE_NAME in db.table_names() else None
    return _table

def _ensure_index():
    global _table
    if _get_table() is not None:
        return

    files = sorted(list(DATA_DIR.glob("*.md")) + list(DATA_DIR.glob("*.txt")))
    if not files:
        raise RuntimeError("No .md or .txt files found in /data")

    model = _get_model()
    db = lancedb.connect(str(DB_DIR))

    records = []
    for fp in files:
        text = fp.read_text(encoding="utf-8", errors="ignore").strip()
        if not text:
            continue
        vec = model.encode(text).tolist()
        records.append({"id": fp.stem, "source": fp.name, "text": text, "vector": vec})

    if not records:
        raise RuntimeError("All documents were empty")

    _table = db.create_table(TABLE_NAME, data=records)

@app.function_name(name="rag_query")
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

        _ensure_index()
        table = _get_table()
        if table is None:
            raise RuntimeError("Vector table not available")

        model = _get_model()
        qvec = model.encode(question).tolist()

        results = table.search(qvec).limit(3).to_list()

        return func.HttpResponse(
            json.dumps({"question": question, "matches": results}, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )
