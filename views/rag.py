import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
import re

# -----------------------------------------------------------------------------
# 1. 기본 설정 및 API Key 입력 (수정됨)
# -----------------------------------------------------------------------------
st.title("게임 장르 추천 시스템")

# [NEW] API Key 입력 UI
# border=True로 박스를 쳐서 강조합니다.
with st.container(border=True):
    st.markdown("### 🔑 Gemini API Key 설정")
    st.caption("AI 분석 기능을 사용하기 위해 Google Gemini API Key가 필요합니다.")
    
    # type="password"를 쓰면 기본적으로 가려지고, 오른쪽 눈 아이콘으로 토글 가능합니다.
    user_api_key = st.text_input(
        label="API Key를 입력하세요",
        type="password", 
        placeholder="sk-...",
        help="입력된 키는 저장되지 않으며, 세션이 종료되면 사라집니다."
    )

    if user_api_key:
        try:
            genai.configure(api_key=user_api_key)
            st.success("API Key가 적용되었습니다! ✅")
        except Exception as e:
            st.error(f"API Key 설정 중 오류가 발생했습니다: {e}")
    else:
        st.warning("⚠️ API Key가 입력되지 않았습니다. 추천 기능은 작동하지만 AI 상세 분석(RAG)은 제한됩니다.")


# -----------------------------------------------------------------------------
# 2. 데이터 로드 및 전처리
# -----------------------------------------------------------------------------
def sanitize_text(s: str) -> str:
    if pd.isna(s): return ""
    s = str(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

@st.cache_data
def load_data():
    try:
        # 1. 데이터 로드
        df_dim = pd.read_csv("data/GAME_DIM_D1_D10.csv")
        df_rag = pd.read_csv("data/GAME_DIM_CLASSIFIED_END.csv")
        df_tag = pd.read_csv("data/TAG_STEAM_GAME.csv")

        # 2. APPID 통일 (문자열 변환)
        for df in [df_dim, df_rag, df_tag]:
            # 컬럼명 정규화
            col_map = {c: "APPID" for c in df.columns if "appid" in c.lower().replace("_", "")}
            df.rename(columns=col_map, inplace=True)
            if "APPID" in df.columns:
                df['APPID'] = df['APPID'].astype(str)

        # 3. 데이터 조인
        df_merged = pd.merge(df_dim, df_tag, on='APPID', how='inner', suffixes=('', '_tag'))
        
        return df_merged, df_rag
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return None, None

# -----------------------------------------------------------------------------
# 3. RAG용 임베딩 준비
# -----------------------------------------------------------------------------
@st.cache_resource
def prepare_rag_embeddings(df_rag):
    """
    API Key가 있을 때만 실행되어 임베딩 데이터를 생성합니다.
    """
    documents = []
    quote_cols = [c for c in df_rag.columns if "quote" in c.lower()]
    
    with st.spinner("RAG 데이터(Quote)를 임베딩 중입니다... (최초 1회만 실행)"):
        for _, row in df_rag.iterrows():
            appid = row['APPID']
            game_name = row.get('game_name', f"Game {appid}")
            
            for col in quote_cols:
                quote = sanitize_text(row[col])
                if not quote: continue
                
                dim_code = col.split("_")[0].upper() # D01
                
                documents.append({
                    "APPID": appid,
                    "game_name": game_name,
                    "dim": dim_code,
                    "text": f"[{dim_code}] {quote}",
                    "raw_quote": quote
                })
    
    if not documents: return None, None
    
    df_docs = pd.DataFrame(documents)
    
    try:
        model = "models/text-embedding-004"
        texts = df_docs['text'].tolist()
        embeddings = []
        batch_size = 50
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            result = genai.embed_content(model=model, content=batch)
            embeddings.extend(result['embedding'])
            
        return df_docs, np.array(embeddings)
        
    except Exception as e:
        st.error(f"임베딩 생성 실패 (API Key를 확인하세요): {e}")
        return None, None

# 데이터 로드
df_main, df_rag = load_data()

# [중요] API Key가 입력되었을 때만 임베딩 생성 함수 호출
df_docs, doc_embeddings = None, None
if df_main is not None and user_api_key:
    df_docs, doc_embeddings = prepare_rag_embeddings(df_rag)

# -----------------------------------------------------------------------------
# 4. UI 구성 (사이드바)
# -----------------------------------------------------------------------------
if df_main is None: st.stop()

with st.sidebar:
    st.header("Team Preference")
    st.info("팀이 추구하는 재미 요소(1~5점)를 설정하세요.")
    
    input_vector = []
    dim_cols = [
        "아트", "연출", "서사", "조작감", "시스템복잡도", 
        "컨텐츠설계량", "엔진", "네트워크", "운영", "BM"
    ] 
    
    dim_map = {
        "아트": "D01", "연출": "D02", "서사": "D03", "조작감": "D04", 
        "시스템복잡도": "D05", "컨텐츠설계량": "D06", "엔진": "D07", 
        "네트워크": "D08", "운영": "D09", "BM": "D10"
    }
    
    for col_name in dim_cols:
        val = st.slider(col_name, 1, 5, 3)
        input_vector.append((val - 1) / 4.0)

    run_btn = st.button("게임 추천 및 분석 실행", type="primary")

# -----------------------------------------------------------------------------
# 5. 메인 로직 실행
# -----------------------------------------------------------------------------
if run_btn:
    # 5-1. 게임 추천 (수학적 계산이므로 API Key 없어도 작동 가능)
    target_cols = dim_cols
    game_features = df_main[target_cols].values
    user_features = np.array(input_vector).reshape(1, -1)
    
    similarity = cosine_similarity(user_features, game_features).flatten()
    df_main['match_score'] = similarity
    df_top5 = df_main.sort_values(by='match_score', ascending=False).head(5)
    
    # 5-2. 결과 화면 (요약)
    st.subheader("추천 결과 요약")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("##### 추천 장르 (Top 2)")
        genre_col = 'TARGET_GENRE' if 'TARGET_GENRE' in df_main.columns else 'genre'
        if genre_col in df_top5.columns:
            st.dataframe(df_top5[genre_col].value_counts().head(2), use_container_width=True)
        else:
            st.info("장르 컬럼 없음")
            
    with c2:
        st.markdown("##### 추천 게임 (Top 5)")
        display_cols = ['APPID', 'game_name', 'match_score']
        valid_cols = [c for c in display_cols if c in df_top5.columns]
        st.dataframe(
            df_top5[valid_cols].style.format({"match_score": "{:.4f}"}),
            use_container_width=True, hide_index=True
        )

    st.divider()
    
    # 5-3. 상세 분석 (API Key 필요)
    st.subheader("상세 근거 및 AI 분석")
    
    if not user_api_key:
        st.warning("⚠️ API Key가 입력되지 않아 상세 AI 분석(RAG) 결과를 표시할 수 없습니다.")
    
    for idx, row in df_top5.iterrows():
        appid = str(row['APPID'])
        name = row.get('game_name', f"Game {appid}")
        score = row['match_score']
        
        with st.container(border=True):
            st.markdown(f"### {name} <small>(유사도: {score:.3f})</small>", unsafe_allow_html=True)
            
            col_spec, col_rag = st.columns([1, 1])
            
            # [왼쪽] 기술 스펙 (데이터 기반)
            with col_spec:
                st.caption("기술 스펙 (D7~D10)")
                tech_cols = ['engine', 'network', 'update', 'business_model']
                tech_data = {k: row.get(k, 'N/A') for k in tech_cols if k in row.index}
                st.table(pd.DataFrame([tech_data]))

            # [오른쪽] Quote-RAG (AI 기반)
            with col_rag:
                st.caption("유저 반응 분석 (RAG)")
                
                # API Key와 임베딩 데이터가 모두 있어야 실행
                if user_api_key and df_docs is not None and doc_embeddings is not None:
                    game_indices = df_docs[df_docs['APPID'] == appid].index.tolist()
                    
                    if game_indices:
                        top_dim_idx = np.argmax(input_vector) 
                        target_kor_col = dim_cols[top_dim_idx]  
                        target_code = dim_map[target_kor_col]
                        
                        query = f"이 게임의 {target_kor_col}에 대한 긍정적인 평가나 특징"
                        
                        try:
                            # 해당 게임 임베딩 추출
                            game_embeddings = doc_embeddings[game_indices]
                            
                            # 쿼리 임베딩
                            q_vec = genai.embed_content(model="models/text-embedding-004", content=query)['embedding']
                            q_vec = np.array(q_vec).reshape(1, -1)
                            
                            # 유사도 계산
                            sims = cosine_similarity(q_vec, game_embeddings).flatten()
                            best_idx = np.argmax(sims)
                            best_doc = df_docs.iloc[game_indices[best_idx]]
                            
                            st.info(f"**팀 선호 요소({target_kor_col}) 관련 리뷰:**")
                            st.markdown(f"> *\"{best_doc['raw_quote']}\"*")
                            st.caption(f"(관련성: {sims[best_idx]:.4f} / 차원: {best_doc['dim']})")
                        except Exception as e:
                            st.error(f"분석 중 오류: {e}")
                    else:
                        st.write("분석할 리뷰 데이터가 없습니다.")
                elif not user_api_key:
                    st.info("API Key를 입력하면 AI 분석 결과를 볼 수 있습니다.")
                else:
                    st.write("임베딩 데이터를 준비하는 중입니다.")