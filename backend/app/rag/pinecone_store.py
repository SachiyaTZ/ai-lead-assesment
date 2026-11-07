"""Pinecone adapter. The POC defaults to local deterministic retrieval so it is runnable without credentials.
Set USE_PINECONE=true and ingest with scripts/ingest_documents.py for enterprise-like operation.
"""
from app.core.config import get_settings

class PineconeStore:
    def __init__(self):
        self.settings=get_settings(); self._index=None
    def connect(self):
        if not self.settings.pinecone_api_key: raise RuntimeError("PINECONE_API_KEY is required")
        from pinecone import Pinecone
        pc=Pinecone(api_key=self.settings.pinecone_api_key)
        self._index=pc.Index(self.settings.pinecone_index_name)
        return self._index
    async def upsert(self,vectors:list[dict]):
        import asyncio
        index=self._index or self.connect()
        return await asyncio.to_thread(index.upsert,vectors=vectors,namespace=self.settings.pinecone_namespace)
