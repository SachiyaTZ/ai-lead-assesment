from collections import Counter
async def research_node(state):
    docs=state.get("retrieved_documents",[]); max_subtasks=6
    batches=[docs[i:i+3] for i in range(0,len(docs),3)][:max_subtasks]
    findings=[]
    for idx,b in enumerate(batches,1):
        text=" ".join(x.content.lower() for x in b)
        keys=[k for k in ["connection pool exhaustion","provider timeout","deployment regression","redis outage","duplicate processing","database saturation","certificate expiry","network packet loss"] if k in text]
        findings.append({"batch":idx,"documents":[x.document_id for x in b],"root_causes":keys})
    counts=Counter(c for f in findings for c in f["root_causes"])
    return {"analysis_result":{"batches":findings,"recurring_root_causes":dict(counts)},"recursion_depth":min(1,state.get("recursion_depth",0)+1),"activity":state.get("activity",[])+[{"type":"state","node":"research","status":"completed","message":f"Analyzed {len(batches)} bounded research batches"}]}
