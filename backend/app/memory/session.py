import asyncio
from collections import defaultdict
class SessionMemory:
    def __init__(self,max_recent:int=8): self.max_recent=max_recent; self._data=defaultdict(lambda:{"turns":[],"summary":"","entities":{}}); self._lock=asyncio.Lock()
    async def get(self,cid:str):
        async with self._lock: return dict(self._data[cid])
    async def add_turn(self,cid:str,user:str,assistant:str,citations:list[str]):
        async with self._lock:
            d=self._data[cid]; d["turns"].append({"user":user,"assistant":assistant,"citations":citations}); d["turns"]=d["turns"][-self.max_recent:]
            d["summary"]=" | ".join(x["user"][:120] for x in d["turns"][-4:])
    async def clear(self,cid:str):
        async with self._lock: self._data.pop(cid,None)
