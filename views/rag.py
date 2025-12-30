import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
import re
import threading
import time


# 1. 백그라운드 작업 관리자
class EmbeddingJobManager:
    def __init__(self):
        self.is_running = False      # 실행 중인지 여부
        self.progress = 0.0          # 진행률 (0.0 ~ 1.0)
        self.status_text = ""        # 현재 상태 메시지
        self.df_docs = None          # 결과 데이터 (문서)
        self.doc_embeddings = None   # 결과 데이터 (임베딩)
        self.error_msg = None        # 에러 메시지

    def start_job(self, df_rag, api_key):
        """백그라운드 쓰레드 시작"""
        if self.is_running: return 
        if self.doc_embeddings is not None: return 
        
        self.is_running = True
        self.error_msg = None
        self.progress = 0.0
        
        # 쓰레드 생성
        thread = threading.Thread(target=self._run_embedding, args=(df_rag, api_key))
        thread.start()

    def _run_embedding(self, df_rag, api_key):
        """실제 백그라운드 임베딩 작업"""
        try:
            genai.configure(api_key=api_key)
            
            # 데이터 전처리
            documents = []
            quote_cols = [c for c in df_rag.columns if "quote" in c.lower()]
            
            self.status_text = "데이터 전처리 중..."
            
            for _, row in df_rag.iterrows():
                appid = row['APPID']
                game_name = row.get('game_name', f"Game {appid}")
                for col in quote_cols:
                    quote = str(row[col]) if pd.notna(row[col]) else ""
                    quote = re.sub(r"\s+", " ", quote).strip()
                    if not quote: continue
                    dim_code = col.split("_")[0].upper()
                    documents.append({
                        "APPID": appid, "game_name": game_name,
                        "dim": dim_code, "text": f"[{dim_code}] {quote}",
                        "raw_quote": quote
                    })
            
            if not documents:
                self.error_msg = "분석할 텍스트 데이터가 없습니다."
                self.is_running = False
                return

            self.df_docs = pd.DataFrame(documents)
            texts = self.df_docs['text'].tolist()
            embeddings = []
            batch_size = 50
            total_batches = len(texts) // batch_size + 1
            
            model = "models/text-embedding-004"
            
            # 배치 처리 및 진행률 업데이트
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                try:
                    result = genai.embed_content(model=model, content=batch)
                    embeddings.extend(result['embedding'])
                except Exception as e:
                    print(f"Error: {e}")
                    time.sleep(1)
                
                # 진행률 업데이트
                current_batch = (i // batch_size) + 1
                self.progress = min(current_batch / total_batches, 0.99)
                self.status_text = f"임베딩 생성 중... ({int(self.progress * 100)}%)"
            
            self.doc_embeddings = np.array(embeddings)
            self.status_text = "완료!"
            self.progress = 1.0
            
        except Exception as e:
            self.error_msg = f"임베딩 실패: {e}"
        finally:
            self.is_running = False

# 메모리에 저장 (세션 스테이트 사용)
def get_job_manager():
    if 'my_job_manager' not in st.session_state:
        st.session_state.my_job_manager = EmbeddingJobManager()
    return st.session_state.my_job_manager



# 2. 기본 설정 및 데이터 로드
st.title("[추천 시스템] LLM RAG")

# 상태 초기화
if 'rag_analysis_done' not in st.session_state:
    st.session_state.rag_analysis_done = False

# [설명 카드] 실행 전(False)일 때만 표시
if not st.session_state.rag_analysis_done:
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px 25px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-bottom: 25px; font-size: 1rem; color: #31333F; line-height: 1.6;'>
    <span style='font-weight: bold; font-size: 1.1rem;'>💡 개발팀 역량 기반 게임 추천 가이드</span><br>
    각 팀의 보유 역량을 <b>1점(낮음) ~ 5점(높음)</b>으로 평가하여 <b>사이드바</b>에 입력해 주세요.<br>
    입력된 데이터를 바탕으로 우리 팀에 가장 적합한 <b>게임 장르</b>와 <b>유사 게임</b>을 추천해 드립니다.<br><br>
<div style='background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #ddd;'>
    <b>🎨 아트팀:</b> 아트, 연출<br>
    <b>📖 스토리팀:</b> 서사<br>
    <b>📝 기획팀:</b> 시스템복잡도, 컨텐츠설계량<br>
    <b>💻 클라이언트팀:</b> 엔진, 네트워크<br>
    <b>🚀 운영팀:</b> 운영, BM<br>
    <b>🎮 공통:</b> 조작감
</div>
    <br>
    👉 <b>설정 완료 후:</b> 사이드바의 <b style='color:#d93025'>'🚀 게임 추천 실행'</b> 버튼을 눌러주세요.
</div>
    """, unsafe_allow_html=True)

# Job Manager 불러오기
manager = get_job_manager()

# API Key 설정 UI
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""

if st.session_state.gemini_api_key:
    try:
        genai.configure(api_key=st.session_state.gemini_api_key)
    except: pass

has_key = bool(st.session_state.gemini_api_key)
expander_title = "✅ Google Gemini API Key 설정 완료" if has_key else "🔑 Google Gemini API Key 설정 (필수)"
is_expanded = not has_key 

if has_key:
    st.success("API Key가 정상적으로 등록되었습니다. 분석 기능을 사용할 수 있습니다!", icon="✅")

with st.expander(expander_title, expanded=is_expanded):
    input_key = st.text_input("API Key 입력 (본 시스템은 API Key를 수집하지 않습니다.)", type="password", value=st.session_state.gemini_api_key)
    if st.button("API Key 적용"):
        st.session_state.gemini_api_key = input_key
        st.rerun()


# 3. 임베딩 작업 상태 모니터링 UI
if manager.is_running:
    st.write("") # 약간의 여백
    status_container = st.container(border=True)
    with status_container:
        st.info(f"🔄 {manager.status_text}")
        st.progress(manager.progress)
        st.caption("💡 팁: 이 작업은 백그라운드에서 계속됩니다. 다른 페이지를 다녀오셔도 됩니다!")
        
        # 실시간 갱신을 위해 1초마다 리런
        time.sleep(1) 
        st.rerun()
        
elif manager.error_msg:
    st.error(f"🚨 {manager.error_msg}")
    if st.button("다시 시도"):
        manager.doc_embeddings = None
        manager.error_msg = None
        st.rerun()

# 4. 분석 결과 예시 화면 (Preview)
if not st.session_state.rag_analysis_done:
    st.divider()
    st.subheader("👀 분석 결과 예시 (Preview)")
    st.caption("※ 모든 역량을 '보통(3점)'으로 설정했을 때의 예시 화면입니다. 실제 실행 시 AI가 사용자의 설정을 바탕으로 실시간 분석합니다.")

    # 1. 예시 요약 테이블
    ex_c1, ex_c2 = st.columns([1, 2])
    with ex_c1:
        st.markdown("**📌 추천 장르 Top 2**")
        st.dataframe(pd.DataFrame({
            "Genre": ["Adventure", "Simulation"],
            "Count": [3, 2]
        }), use_container_width=True, hide_index=True)
    with ex_c2:
        st.markdown("**🏆 추천 게임 Top 5**")
        st.dataframe(pd.DataFrame({
            "APPID": ["12345", "67890", "11223", "44556", "99887"],
            "game_name": ["Dave the Diver", "Stardew Valley", "Subnautica", "Terraria", "Factorio"],
            "match_score": ["0.9852", "0.9710", "0.9540", "0.9320", "0.9105"]
        }), use_container_width=True, hide_index=True)

    st.write("") # 여백

    # 2. 예시 상세 카드
    st.subheader("🧐 상세 근거 및 AI 분석 (예시)")
    
    with st.container(border=True):
        st.markdown("### 1. Dave the Diver <small>(유사도: 0.985)</small>", unsafe_allow_html=True)
        col_ex_spec, col_ex_rag = st.columns([1, 1])
        
        with col_ex_spec:
            st.caption("🛠️ 기술 스펙 (D7~D10)")
            st.table(pd.DataFrame([{
                "engine": "Unity",
                "network": "Single-player",
                "update": "High",
                "business_model": "Package"
            }]))

        with col_ex_rag:
            st.caption("💬 유저 반응 분석 (RAG)")
            st.info("**팀 선호 요소(시스템복잡도) 관련 리뷰:**")
            st.markdown("> *\"이 게임은 경영 시뮬레이션과 해양 탐험 액션이 절묘하게 조화되어 있습니다. 시스템이 깊이 있으면서도 튜토리얼이 친절해 복잡하게 느껴지지 않는 점이 최고입니다.\"*")
            st.caption("(관련성: 0.8912)")


# 5. 데이터 로드 및 임베딩 자동 시작 로직
@st.cache_data
def load_data():
    try:
        df_dim = pd.read_csv("data/GAME_DIM_D1_D10.csv")
        df_rag = pd.read_csv("data/GAME_DIM_CLASSIFIED_END.csv")
        df_tag = pd.read_csv("data/TAG_STEAM_GAME.csv")
        for df in [df_dim, df_rag, df_tag]:
            col_map = {c: "APPID" for c in df.columns if "appid" in c.lower().replace("_", "")}
            df.rename(columns=col_map, inplace=True)
            if "APPID" in df.columns: df['APPID'] = df['APPID'].astype(str)
        df_merged = pd.merge(df_dim, df_tag, on='APPID', how='inner', suffixes=('', '_tag'))
        return df_merged, df_rag
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return None, None

df_main, df_rag = load_data()

# [자동 시작] 데이터 있고 + 키 있고 + 아직 안 돌렸으면 -> start_job 호출
if df_main is not None and st.session_state.gemini_api_key:
    if not manager.is_running and manager.doc_embeddings is None:
        manager.start_job(df_rag, st.session_state.gemini_api_key)
        st.rerun()


# 6. 분석 옵션 (사이드바)
if df_main is None: st.stop()

with st.sidebar:
    st.header("🎛️ 분석 옵션")
    input_vector = []
    dim_cols = ["아트", "연출", "서사", "조작감", "시스템복잡도", "컨텐츠설계량", "엔진", "네트워크", "운영", "BM"]
    
    for col_name in dim_cols:
        val = st.slider(col_name, 1, 5, 3)
        input_vector.append((val - 1) / 4.0)
    
    st.divider()
    # 버튼 클릭 시 상태 변경 -> 예시 화면 사라짐 + 결과 화면 등장
    if st.button("🚀 게임 추천 실행", type="primary", use_container_width=True):
        st.session_state.rag_analysis_done = True 
        st.rerun()

# 7. 결과 화면 (실제 분석 결과)
if st.session_state.rag_analysis_done:
    st.divider()
    
    # 추천 로직
    target_cols = dim_cols
    game_features = df_main[target_cols].values
    user_features = np.array(input_vector).reshape(1, -1)
    similarity = cosine_similarity(user_features, game_features).flatten()
    df_main['match_score'] = similarity
    df_top5 = df_main.sort_values(by='match_score', ascending=False).head(5)

    # 요약 화면
    st.subheader("📊 추천 결과 요약")
    c1, c2 = st.columns([1, 2])
    with c1:
        genre_col = 'TARGET_GENRE' if 'TARGET_GENRE' in df_main.columns else 'genre'
        if genre_col in df_top5.columns: st.dataframe(df_top5[genre_col].value_counts().head(2), use_container_width=True)
    with c2:
        display_cols = ['APPID', 'game_name', 'match_score']
        valid_cols = [c for c in display_cols if c in df_top5.columns]
        st.dataframe(df_top5[valid_cols].style.format({"match_score": "{:.4f}"}), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("🧐 상세 근거 및 AI 분석")

    # 매니저 상태 체크 (결과 화면에서도 진행 중일 수 있으므로)
    if not st.session_state.gemini_api_key:
        st.warning("⚠️ API Key가 없습니다.")
    elif manager.is_running:
        st.warning("⏳ AI 분석 데이터 생성 중입니다... (상단 진행률 확인)")
    elif manager.doc_embeddings is None:
        st.warning("⚠️ 분석 데이터 준비 실패.")
    
    # 상세 카드
    for idx, row in df_top5.iterrows():
        appid = str(row['APPID'])
        name = row.get('game_name', f"Game {appid}")
        score = row['match_score']
        
        with st.container(border=True):
            st.markdown(f"### {name} <small>(유사도: {score:.3f})</small>", unsafe_allow_html=True)
            col_spec, col_rag = st.columns([1, 1])
            
            with col_spec:
                st.caption("🛠️ 기술 스펙 (D7~D10)")
                tech_cols = ['engine', 'network', 'update', 'business_model']
                tech_data = {k: row.get(k, 'N/A') for k in tech_cols if k in row.index}
                st.table(pd.DataFrame([tech_data]))

            with col_rag:
                st.caption("💬 유저 반응 분석 (RAG)")
                if manager.doc_embeddings is not None and manager.df_docs is not None:
                    game_indices = manager.df_docs[manager.df_docs['APPID'] == appid].index.tolist()
                    if game_indices:
                        top_dim_idx = np.argmax(input_vector)
                        target_kor_col = dim_cols[top_dim_idx]
                        query = f"이 게임의 {target_kor_col}에 대한 긍정적인 평가나 특징"
                        try:
                            game_embeddings = manager.doc_embeddings[game_indices]
                            q_vec = genai.embed_content(model="models/text-embedding-004", content=query)['embedding']
                            q_vec = np.array(q_vec).reshape(1, -1)
                            sims = cosine_similarity(q_vec, game_embeddings).flatten()
                            best_idx = np.argmax(sims)
                            best_doc = manager.df_docs.iloc[game_indices[best_idx]]
                            
                            st.info(f"**팀 선호 요소({target_kor_col}) 관련 리뷰:**")
                            st.markdown(f"> *\"{best_doc['raw_quote']}\"*")
                            st.caption(f"(관련성: {sims[best_idx]:.4f})")
                        except Exception as e:
                            st.error("분석 중 오류 발생")
                    else:
                        st.write("관련 리뷰 없음")
                else:
                    st.info("AI 분석 데이터가 아직 준비되지 않았습니다.")
                    
    # [팁] 결과를 보고 다시 처음으로 돌아가고 싶다면?
    if st.button("🔄 조건 변경 및 다시 검색"):
        st.session_state.rag_analysis_done = False
        st.rerun()