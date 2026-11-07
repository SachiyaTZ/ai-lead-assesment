import json, os, uuid, requests, streamlit as st
API=os.getenv("API_BASE_URL","http://localhost:8000/api/v1")
st.set_page_config(page_title="Enterprise AI Assistant",layout="wide")
if "token" not in st.session_state: st.session_state.token=None
if "conversation_id" not in st.session_state: st.session_state.conversation_id=str(uuid.uuid4())
if "messages" not in st.session_state: st.session_state.messages=[]
if "activity" not in st.session_state: st.session_state.activity=[]

st.title("Enterprise AI Assistant")
with st.sidebar:
    st.header("Session")
    if not st.session_state.token:
        email=st.selectbox("Demo user",["viewer@company.com","analyst@company.com","admin@company.com"])
        pw={"viewer@company.com":"Viewer123!","analyst@company.com":"Analyst123!","admin@company.com":"Admin123!"}[email]
        password=st.text_input("Password",value=pw,type="password")
        if st.button("Login",use_container_width=True):
            r=requests.post(f"{API}/auth/login",json={"email":email,"password":password},timeout=15)
            if r.ok:
                x=r.json(); st.session_state.token=x["access_token"]; st.session_state.role=x["role"]; st.rerun()
            else: st.error(r.text)
    else:
        st.write("Role:",st.session_state.get("role")); st.code(st.session_state.conversation_id)
        if st.button("New Conversation",use_container_width=True):
            st.session_state.conversation_id=str(uuid.uuid4()); st.session_state.messages=[]; st.session_state.activity=[]; st.rerun()
        if st.button("Logout",use_container_width=True): st.session_state.clear(); st.rerun()

left,right=st.columns([2,1])
with right:
    st.subheader("Agent Activity")
    activity_box=st.empty()
    activity_box.markdown("\n".join(f"- **{e.get('node','event')}** — {e.get('status','')} {e.get('message','')}" for e in st.session_state.activity) or "No activity yet.")
with left:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if prompt:=st.chat_input("Ask about policies, incidents, runbooks, services..."):
        if not st.session_state.token: st.warning("Log in first."); st.stop()
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            out=st.empty(); answer=""; st.session_state.activity=[]
            headers={"Authorization":f"Bearer {st.session_state.token}"}
            with requests.post(f"{API}/chat/stream",json={"message":prompt,"conversation_id":st.session_state.conversation_id},headers=headers,stream=True,timeout=120) as r:
                if not r.ok: st.error(r.text); st.stop()
                for raw in r.iter_lines():
                    if not raw or not raw.startswith(b"data: "): continue
                    event=json.loads(raw[6:])
                    if event.get("type")=="token": answer+=event["content"]; out.markdown(answer+"▌")
                    elif event.get("type")=="done": st.session_state.conversation_id=event["conversation_id"]
                    else:
                        st.session_state.activity.append(event); activity_box.markdown("\n".join(f"- **{e.get('node','event')}** — {e.get('status','')} {e.get('message','')}" for e in st.session_state.activity))
            out.markdown(answer); st.session_state.messages.append({"role":"assistant","content":answer})
