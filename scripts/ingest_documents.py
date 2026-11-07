"""Illustrative Pinecone ingestion. Uses OpenAI embeddings when credentials are configured."""
import asyncio, os, json
from pathlib import Path
from openai import AsyncOpenAI
from pinecone import Pinecone
async def main():
    api=os.environ["OPENAI_API_KEY"]; pkey=os.environ["PINECONE_API_KEY"]; index_name=os.environ["PINECONE_INDEX_NAME"]; ns=os.getenv("PINECONE_NAMESPACE","enterprise")
    client=AsyncOpenAI(api_key=api); index=Pinecone(api_key=pkey).Index(index_name); vectors=[]
    for path in (Path(__file__).resolve().parents[1]/"data").rglob("*.json"):
        d=json.loads(path.read_text()); emb=(await client.embeddings.create(model=os.getenv("EMBEDDING_MODEL","text-embedding-3-small"),input=d["content"])).data[0].embedding
        vectors.append({"id":d["document_id"],"values":emb,"metadata":{k:d[k] for k in ["document_id","title","department","document_type","access_level","created_date"]}|{"content":d["content"]}})
    await asyncio.to_thread(index.upsert,vectors=vectors,namespace=ns); print(f"Upserted {len(vectors)} documents")
if __name__=="__main__": asyncio.run(main())
