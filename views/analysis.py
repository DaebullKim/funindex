import streamlit as st
import json
import os
import time

# -----------------------------------------------------------------------------
# 1. CSS 스타일링 (호버 효과, 버튼 스타일, 텍스트 스타일)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* 이미지 호버 시 확대 효과 */
    .hover-zoom {
        transition: transform 0.3s ease;
    }
    .hover-zoom:hover {
        transform: scale(1.05);
        cursor: pointer;
    }
    
    /* 플랫폼 선택 버튼 스타일 */
    div.stButton > button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
    }
    
    /* JSON 인사이트 박스 스타일 */
    .insight-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
    }
    
    /* 상세 페이지 텍스트 스타일 */
    .persona-title {
        color: #FF4B4B;
        font-weight: bold;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 유틸리티 함수
# -----------------------------------------------------------------------------
def load_json(path):
    """JSON 파일 로드"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def get_image_path(platform, filename):
    """이미지 경로 생성 (없으면 None)"""
    path = os.path.join("data", "images", platform, filename)
    # 확장자 자동 처리
    if not os.path.exists(path) and not path.endswith(".png"):
        path += ".png"
    return path if os.path.exists(path) else None

def render_insight_section(insight_data):
    """(메인용) JSON 인사이트 출력"""
    if not insight_data or "overall_insights" not in insight_data:
        st.warning("인사이트 데이터가 없습니다.")
        return

    data = insight_data["overall_insights"]
    
    with st.container(border=True):
        st.subheader("💡 Overall Insights")
        
        # Key Findings
        st.markdown("**📌 Key Findings**")
        for item in data.get("key_findings", []):
            st.markdown(f"- {item}")
        
        st.divider()
        
        # Priority Segments
        priority = data.get("priority_segments", {})
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**🔥 Impact (성장)**: `{priority.get('impact_top', [])}`")
        with c2:
            st.markdown(f"**🚨 Urgency (리스크)**: `{priority.get('urgency_top', [])}`")
            
        st.divider()
        
        # Patterns (취소선 제거 로직 포함)
        with st.expander("패턴 및 요약 보기"):
            st.markdown("**Cross Segment Patterns**")
            for pat in data.get("cross_segment_patterns", []):
                st.markdown(f"- {pat}")
            st.markdown("**Summary**")
            
            raw_summary = data.get("market_segmentation_summary", "")
            clean_summary = raw_summary.replace("~~", "").replace("~", "-") # 마크다운 취소선 방지
            st.caption(clean_summary)

# -----------------------------------------------------------------------------
# 3. 상태 관리
# -----------------------------------------------------------------------------
if "an_platform" not in st.session_state:
    st.session_state.an_platform = "steam"
if "an_view_mode" not in st.session_state:
    st.session_state.an_view_mode = "main"
if "an_selected_segment" not in st.session_state:
    st.session_state.an_selected_segment = None

# -----------------------------------------------------------------------------
# 4. 메인 화면 렌더링
# -----------------------------------------------------------------------------
def render_main_dashboard():
    platform = st.session_state.an_platform
    
    # 상단 필터
    c1, c2, c3 = st.columns([6, 1, 1])
    with c2:
        if st.button("Steam", type="primary" if platform == "steam" else "secondary", use_container_width=True):
            st.session_state.an_platform = "steam"
            st.rerun()
    with c3:
        if st.button("YouTube", type="primary" if platform == "youtube" else "secondary", use_container_width=True):
            st.session_state.an_platform = "youtube"
            st.rerun()

    st.title(f"📊 {platform.upper()} Analysis Dashboard")

    # 세그먼트 레이더 그리드
    st.subheader("🧩 Segment Radar Overview")
    
    if platform == "steam":
        seg_count = 8
        img_prefix = "08_radar_seg_"
    else:
        seg_count = 6
        img_prefix = "04_radar_"

    cols = st.columns(4)
    for i in range(seg_count):
        col = cols[i % 4]
        with col:
            img_path = get_image_path(platform, f"{img_prefix}{i}")
            if img_path:
                st.image(img_path, use_container_width=True)
            else:
                st.info(f"Img: {i}")

            if st.button(f"🔍 Seg {i} 상세", key=f"btn_seg_{i}", use_container_width=True):
                st.session_state.an_selected_segment = i
                st.session_state.an_view_mode = "segment"
                st.rerun()
        
        if (i + 1) % 4 == 0: pass 

    st.divider()

    # Top Topics & Overall Insights
    col_topics, col_insights = st.columns([1.5, 1])
    with col_topics:
        topic_img = "02_2_top_topics_per_segment.png"
        path = get_image_path(platform, topic_img)
        if path:
            st.image(path, caption="Topic Modeling per Segment", use_container_width=True)
        else:
            st.warning(f"이미지 없음: {topic_img}")

    with col_insights:
        json_file = f"{platform}_persona.json"
        json_path = os.path.join("data", "insights", json_file)
        insight_data = load_json(json_path)
        render_insight_section(insight_data)

    # 하단 차트 (플랫폼별 분기)
    st.divider()
    if platform == "steam":
        r3_c1, r3_c2, r3_c3 = st.columns(3)
        with r3_c1: st.image(get_image_path("steam", "03_vote_influence_bar.png") or "http://via.placeholder.com/300", use_container_width=True)
        with r3_c2: st.image(get_image_path("steam", "05_is_viral_rate_bar.png") or "http://via.placeholder.com/300", use_container_width=True)
        with r3_c3: st.image(get_image_path("steam", "02_1_segment_topic_heatmap.png") or "http://via.placeholder.com/300", use_container_width=True)
        
        r4_c1, r4_c2, r4_c3 = st.columns(3)
        with r4_c1: st.image(get_image_path("steam", "14_recent_activity_box.png") or "http://via.placeholder.com/300", use_container_width=True)
        with r4_c2: st.image(get_image_path("steam", "13_sentiment_stacked.png") or "http://via.placeholder.com/300", use_container_width=True)
        with r4_c3: st.image(get_image_path("steam", "11_influence_bubble.png") or "http://via.placeholder.com/300", use_container_width=True)

        r5_c1, r5_c2 = st.columns(2)
        with r5_c1: st.image(get_image_path("steam", "09_pca2d.png") or "http://via.placeholder.com/300", use_container_width=True)
        with r5_c2: st.image(get_image_path("steam", "10_tsne2d.png") or "http://via.placeholder.com/300", use_container_width=True)

    else: # YouTube
        r3_c1, r3_c2, r3_c3 = st.columns(3)
        with r3_c1: st.image(get_image_path("youtube", "07_1_votes_bar.png") or "http://via.placeholder.com/300", use_container_width=True)
        with r3_c2: st.image(get_image_path("youtube", "07_2_replies_bar.png") or "http://via.placeholder.com/300", use_container_width=True)
        with r3_c3: st.image(get_image_path("youtube", "07_3_comment_engagement_bar.png") or "http://via.placeholder.com/300", use_container_width=True)
        
        r4_c1, r4_c2, r4_c3 = st.columns(3)
        with r4_c1: st.image(get_image_path("youtube", "07_4_viral_potential_bar.png") or "http://via.placeholder.com/300", use_container_width=True)
        with r4_c2: st.image(get_image_path("youtube", "07_5_is_viral_bar.png") or "http://via.placeholder.com/300", use_container_width=True)
        with r4_c3: st.image(get_image_path("youtube", "08_influence_bubble.png") or "http://via.placeholder.com/300", use_container_width=True)

        r5_c1, r5_c2 = st.columns(2)
        with r5_c1: st.image(get_image_path("youtube", "05_pca2d_multicolor.png") or "http://via.placeholder.com/300", use_container_width=True)
        with r5_c2: st.image(get_image_path("youtube", "06_tsne2d_multicolor.png") or "http://via.placeholder.com/300", use_container_width=True)

# -----------------------------------------------------------------------------
# 5. 세그먼트 상세 화면 렌더링 (업데이트됨)
# -----------------------------------------------------------------------------
def render_segment_detail():
    seg_id = st.session_state.an_selected_segment
    platform = st.session_state.an_platform
    
    # 1. 상단 뒤로가기 버튼
    if st.button("⬅️ 전체 대시보드로 돌아가기"):
        st.session_state.an_view_mode = "main"
        st.session_state.an_selected_segment = None
        st.rerun()
    
    # 2. 제목
    st.title(f"🔍 Segment {seg_id} 상세 분석 ({platform})")
    
    # 3. JSON 데이터 로드 및 해당 세그먼트 찾기
    json_path = os.path.join("data", "insights", f"{platform}_persona.json")
    full_data = load_json(json_path)
    
    seg_data = None
    if full_data and "segments" in full_data:
        # segment_id가 일치하는 데이터 찾기
        for seg in full_data["segments"]:
            if seg.get("segment_id") == seg_id:
                seg_data = seg
                break
    
    # 4. 상단 레이아웃 (레이더 + 텍스트)
    c_radar, c_text = st.columns([1, 2])
    
    # [Left] 레이더 차트
    with c_radar:
        img_prefix = "08_radar_seg_" if platform == "steam" else "04_radar_"
        img_path = get_image_path(platform, f"{img_prefix}{seg_id}")
        if img_path:
            st.image(img_path, caption=f"Segment {seg_id} Radar Profile", use_container_width=True)
        else:
            st.container(border=True, height=300).write("레이더 이미지 없음")
            
    # [Right] 페르소나 정의 (JSON 파싱)
    with c_text:
        st.subheader("📝 세그먼트 정의 및 특성")
        
        if seg_data:
            profile = seg_data.get("persona_profile", {})
            
            # 페르소나 이름 & 한줄 요약
            st.markdown(f"<div class='persona-title'>{profile.get('persona_name', 'N/A')}</div>", unsafe_allow_html=True)
            st.info(f"💡 {profile.get('one_liner', '')}")
            
            # 상세 설명
            with st.expander("상세 설명 보기", expanded=True):
                st.write(profile.get('description', ''))
                
            # 주요 특징 (Key Char)
            st.markdown("**📌 Key Characteristics**")
            for char in profile.get('key_characteristics', []):
                st.markdown(f"- {char}")
                
            # 권장 액션 (Recommended Actions)
            if profile.get('recommended_actions'):
                st.markdown("**✅ Recommended Actions**")
                for action in profile.get('recommended_actions', []):
                    st.markdown(f"- {action}")
        else:
            st.warning(f"Segment {seg_id}에 대한 JSON 데이터가 없습니다.")

    st.divider()
    
    # 5. 하단 레이아웃 (Topic Lift & Topdiff Mirror)
    c_lift, c_mirror = st.columns(2)
    
    with c_lift:
        # 파일명 매핑 (Steam vs Youtube)
        # Steam: 02_3_topic_lift_segment_{id}
        # Youtube: 02_3_topic_lift_segment_{id} (동일 가정, 와이어프레임 따름)
        lift_img = f"02_3_topic_lift_segment_{seg_id}.png"
        path = get_image_path(platform, lift_img)
        
        if path:
            st.image(path, use_container_width=True)
        else:
            st.container(border=True, height=250).write(f"[이미지 필요]\n{lift_img}")
            
    with c_mirror:
        # 파일명 매핑 (Steam vs Youtube)
        # Steam: 12_topdiff_mirror_segment_{id}
        # Youtube: 09_topdiff_mirror_segment_{id}
        if platform == "steam":
            mirror_img = f"12_topdiff_mirror_segment_{seg_id}.png"
        else:
            mirror_img = f"09_topdiff_mirror_segment_{seg_id}.png"
            
        path = get_image_path(platform, mirror_img)
        
        if path:
            st.image(path, use_container_width=True)
        else:
            st.container(border=True, height=250).write(f"[이미지 필요]\n{mirror_img}")

# -----------------------------------------------------------------------------
# 6. 실행 로직
# -----------------------------------------------------------------------------
if st.session_state.an_view_mode == "main":
    render_main_dashboard()
elif st.session_state.an_view_mode == "segment":
    render_segment_detail()