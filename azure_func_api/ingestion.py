from pathlib import Path

import lancedb
from sentence_transformers import SentenceTransformer

DATA_DIR = Path("data")
DB_DIR = Path("knowledge_base")
TABLE_NAME = "transcripts"

def main() -> None:
    files = sorted(list(DATA_DIR.glob("*.md")) + list(DATA_DIR.glob("*.txt")))
    if not files:
        raise RuntimeError("No .md or .txt files found in /data")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    DB_DIR.mkdir(parents=True, exist_ok=True)
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

    if TABLE_NAME in db.table_names():
        table = db.open_table(TABLE_NAME)
        table.add(records)
    else:
        db.create_table(TABLE_NAME, data=records)

    print(f"✅ Ingested {len(records)} documents into {DB_DIR}/{TABLE_NAME}")

if __name__ == "__main__":
    main()
