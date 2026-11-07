from pathlib import Path
import json
from app.models.schemas import RetrievedChunk

class DocumentStore:
    def __init__(self, data_dir: str): self.data_dir=Path(data_dir); self.docs=[]
    def load(self):
        self.docs=[]
        if not self.data_dir.exists(): return self.docs
        for path in sorted(self.data_dir.rglob("*.json")):
            payload=json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload,dict): payload=[payload]
            for d in payload:
                content=d["content"]
                # lightweight paragraph chunks, stable IDs
                paragraphs=[x.strip() for x in content.split("\n\n") if x.strip()]
                if not paragraphs: paragraphs=[content]
                for i,p in enumerate(paragraphs):
                    self.docs.append(RetrievedChunk(
                        chunk_id=f'{d["document_id"]}::c{i+1}', document_id=d["document_id"], title=d["title"], content=p,
                        source=str(path), department=d["department"], document_type=d["document_type"], access_level=d["access_level"], created_date=d["created_date"]
                    ))
        return self.docs
