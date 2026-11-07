import asyncio, math, re
from collections import Counter
from datetime import date
from app.models.schemas import RetrievedChunk, SearchFilters
from app.rag.embeddings import HashEmbedding, cosine
from app.security.injection import sanitize_retrieved_content

class HybridRetriever:
    def __init__(self, documents:list[RetrievedChunk], dense_weight=.65, sparse_weight=.35):
        self.documents=documents; self.dw=dense_weight; self.sw=sparse_weight; self.emb=HashEmbedding(); self._doc_vecs={}
    async def prepare(self):
        self._doc_vecs={d.chunk_id:await self.emb.embed(d.content) for d in self.documents}
    def _filter(self,d,f:SearchFilters):
        if f.department and d.department.lower()!=f.department.lower(): return False
        if f.document_type and d.document_type.lower()!=f.document_type.lower(): return False
        if f.access_level and d.access_level.lower()!=f.access_level.lower(): return False
        dd=date.fromisoformat(d.created_date)
        if f.date_from and dd<f.date_from:return False
        if f.date_to and dd>f.date_to:return False
        return True
    @staticmethod
    def _tokens(s): return re.findall(r"[a-z0-9]+",s.lower())
    def _bm25(self,q,docs):
        qt=self._tokens(q); tokenized=[self._tokens(d.content) for d in docs]; N=len(docs) or 1; avg=sum(map(len,tokenized))/N or 1
        df=Counter(); [df.update(set(ts)) for ts in tokenized]
        scores=[]
        for ts in tokenized:
            tf=Counter(ts); score=0.0
            for t in qt:
                if not df[t]: continue
                idf=math.log(1+(N-df[t]+.5)/(df[t]+.5)); score += idf*(tf[t]*2.2)/(tf[t]+1.2*(1-.75+.75*len(ts)/avg))
            scores.append(score)
        m=max(scores,default=0) or 1; return [s/m for s in scores]
    async def search(self, query:str, filters:SearchFilters|None=None)->list[RetrievedChunk]:
        filters=filters or SearchFilters(); docs=[d for d in self.documents if self._filter(d,filters)]
        if not docs:return []
        if not self._doc_vecs: await self.prepare()
        qv=await self.emb.embed(query)
        dense=[(cosine(qv,self._doc_vecs[d.chunk_id])+1)/2 for d in docs]
        sparse=self._bm25(query,docs)
        out=[]
        for d,ds,ss in zip(docs,dense,sparse):
            clean,_=sanitize_retrieved_content(d.content)
            out.append(d.model_copy(update={"content":clean,"dense_score":ds,"sparse_score":ss,"hybrid_score":self.dw*ds+self.sw*ss}))
        out.sort(key=lambda x:x.hybrid_score,reverse=True)
        # dedupe chunk IDs; top-k
        return out[:filters.top_k]
