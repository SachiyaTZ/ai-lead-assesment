import hashlib, math, re
class HashEmbedding:
    """Deterministic local embedding used when OpenAI credentials are absent."""
    def __init__(self, dims:int=256): self.dims=dims
    async def embed(self,text:str)->list[float]:
        v=[0.0]*self.dims
        for tok in re.findall(r"[a-z0-9]+",text.lower()):
            h=int(hashlib.sha256(tok.encode()).hexdigest()[:16],16); idx=h%self.dims; v[idx]+=1.0 if (h>>8)&1 else -1.0
        n=math.sqrt(sum(x*x for x in v)) or 1.0
        return [x/n for x in v]

def cosine(a,b): return sum(x*y for x,y in zip(a,b))
