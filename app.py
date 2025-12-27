import streamlit as st

# 페이지 설정
p_dashboard = st.Page("views/dashboard.py", title="대시보드 (Tableau)", icon="📊", default=True)
p_analysis = st.Page("views/analysis.py", title="군집 분석 (Cluster)", icon="🧩")
p_rag = st.Page("views/rag.py", title="게임 추천 (RAG)", icon="🎮")

# 네비게이션 그룹핑
pg = st.navigation({
    "Analytics": [p_dashboard, p_analysis,p_rag]
})

st.set_page_config(layout="wide", page_title="Game Fun Index Analysis")
pg.run()