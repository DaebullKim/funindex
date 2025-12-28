import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
import re
import threading
import time

# -----------------------------------------------------------------------------
# 1. 백그라운드 작업 관리자 (Job Manager) - 핵심!
# -----------------------------------------------------------------------------
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
        if self.is_running: return # 이미 돌고 있으면 패스
        if self.doc_embeddings is not None: return # 이미 결과 있으면 패스
        
        self.is_running = True
        self.error_msg = None
        self.progress = 0.0
        
        # 별도의 쓰레드(일꾼) 생성해서 보냄
        thread = threading.Thread(target=self._run_embedding, args=(df_rag, api_key))
        thread.start()

    def _run_embedding(self, df_rag, api_key):
        """실제 임베딩 작업 (백그라운드에서 실행됨)"""
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
                    # API 에러 발생 시 잠시 대기 후 재시도 혹은 에러 처리
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

# [중요] 이 관리자는 페이지를 이동해도 메모리에 살아있음 (@st.cache_resource)
@st.cache_resource
def get_job_manager():
    return EmbeddingJobManager()

# -----------------------------------------------------------------------------
# 2. 기본 설정 및 데이터 로드
# -----------------------------------------------------------------------------
st.title("[추천 시스템] LLM RAG")

# Job Manager 불러오기
manager = get_job_manager()

# API Key 설정
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""

if st.session_state.gemini_api_key:
    try:
        genai.configure(api_key=st.session_state.gemini_api_key)
    except: pass

is_expanded = not bool(st.session_state.gemini_api_key)
with st.expander("🔑 Google Gemini API Key 설정", expanded=is_expanded):
    input_key = st.text_input("API Key 입력", type="password", value=st.session_state.gemini_api_key)
    if st.button("API Key 적용"):
        st.session_state.gemini_api_key = input_key
        st.rerun()

# 데이터 로드
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

# -----------------------------------------------------------------------------
# 3. 임베딩 작업 실행 및 상태 모니터링 UI
# -----------------------------------------------------------------------------
if df_main is not None and st.session_state.gemini_api_key:
    # 1. 아직 시작 안 했고, 결과도 없으면 -> 시작
    if not manager.is_running and manager.doc_embeddings is None:
        manager.start_job(df_rag, st.session_state.gemini_api_key)
        st.rerun() # 시작했으니 화면 갱신
        
    # 2. 실행 중이면 -> 진행률 표시 바 보여주기
    elif manager.is_running:
        status_container = st.container(border=True)
        with status_container:
            st.info(f"🔄 {manager.status_text}")
            st.progress(manager.progress)
            st.caption("💡 팁: 이 작업은 백그라운드에서 계속됩니다. 다른 페이지를 다녀오셔도 됩니다!")
            
            # 실시간 갱신을 위해 1초마다 리런 (페이지가 계속 깜빡일 수 있음)
            # 사용자가 보고 있을 때만 갱신
            time.sleep(1) 
            st.rerun()
            
    # 3. 에러 났으면
    elif manager.error_msg:
        st.error(f"🚨 {manager.error_msg}")
        if st.button("다시 시도"):
            # 매니저 초기화 꼼수
            manager.doc_embeddings = None
            manager.error_msg = None
            st.rerun()

# -----------------------------------------------------------------------------
# 4. 분석 옵션 (사이드바)
# -----------------------------------------------------------------------------
if df_main is None: st.stop()

with st.sidebar:
    st.header("🎛️ 분석 옵션")
    input_vector = []
    dim_cols = ["아트", "연출", "서사", "조작감", "시스템복잡도", "컨텐츠설계량", "엔진", "네트워크", "운영", "BM"]
    dim_map = {"아트": "D01", "연출": "D02", "서사": "D03", "조작감": "D04", "시스템복잡도": "D05", "컨텐츠설계량": "D06", "엔진": "D07", "네트워크": "D08", "운영": "D09", "BM": "D10"}
    
    for col_name in dim_cols:
        val = st.slider(col_name, 1, 5, 3)
        input_vector.append((val - 1) / 4.0)
    
    st.divider()
    run_btn = st.button("🚀 게임 추천 실행", type="primary", use_container_width=True)

# -----------------------------------------------------------------------------
# 5. 결과 화면
# -----------------------------------------------------------------------------
if run_btn:
    st.divider()
    
    # 추천 로직 (기존과 동일)
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

    # [수정] 매니저에서 결과 가져오기
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
                # 매니저의 결과 데이터 사용
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