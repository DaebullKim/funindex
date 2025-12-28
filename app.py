import streamlit as st

# 페이지 설정
p_dashboard = st.Page("views/dashboard.py", title="[랭킹] 유통 플랫폼", icon="📊", default=True)
p_dashboard2 = st.Page("views/dashboard2.py", title="[KPI] STEAM 상위 랭킹", icon="📈")
p_analysis = st.Page("views/analysis.py", title="[고객 유형] 세그먼트 분석", icon="🧩")
p_rag = st.Page("views/rag.py", title="[추천 시스템] LLM RAG", icon="🎮")

# 네비게이션 그룹핑
pg = st.navigation({
    "Analytics": [p_dashboard,p_dashboard2, p_analysis,p_rag]
})

st.set_page_config(layout="wide", page_title="Game Fun Index Analysis")
pg.run()