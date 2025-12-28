import streamlit as st
import json
import os
import re

# -----------------------------------------------------------------------------
# 1. CSS 스타일링
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    .persona-title {
        color: #FF4B4B;
        font-weight: bold;
        font-size: 1.6rem;
        margin-bottom: 5px;
    }
    .persona-one-liner {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        font-weight: 500;
        margin-bottom: 20px;
        line-height: 1.5;
    }
    /* 인스타 감성 해시태그 스타일 */
    .hashtag-badge {
        background-color: #fceceb; /* 연한 붉은색 배경 */
        color: #d93025;            /* 진한 붉은색 글씨 */
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-right: 8px;
        display: inline-block;
        margin-bottom: 10px;
    }
    /* 댓글 스타일 */
    .comment-box {
        background-color: #444; /* 어두운 배경 (이미지 참고) */
        color: #fff;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-style: italic;
        font-size: 0.95rem;
    }
    .comment-header {
        font-size: 1.1rem;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 유틸리티 함수
# -----------------------------------------------------------------------------
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def get_image_path(platform, filename):
    path = os.path.join("data", "images", platform, filename)
    if not os.path.exists(path) and not path.endswith(".png"):
        path += ".png"
    return path if os.path.exists(path) else None

# -----------------------------------------------------------------------------
# 3. 상태 관리
# -----------------------------------------------------------------------------
if "an_platform" not in st.session_state:
    st.session_state.an_platform = "steam"
if "an_selected_segment" not in st.session_state:
    st.session_state.an_selected_segment = 0 

# -----------------------------------------------------------------------------
# 4. 화면 구성 로직
# -----------------------------------------------------------------------------

# [Level 1] 플랫폼 선택
c_plat1, c_plat2 = st.columns(2)
with c_plat1:
    if st.button("Steam", type="primary" if st.session_state.an_platform == "steam" else "secondary", use_container_width=True):
        st.session_state.an_platform = "steam"
        st.session_state.an_selected_segment = 0
        st.rerun()
with c_plat2:
    if st.button("YouTube", type="primary" if st.session_state.an_platform == "youtube" else "secondary", use_container_width=True):
        st.session_state.an_platform = "youtube"
        st.session_state.an_selected_segment = 0
        st.rerun()

# [Level 2] 세그먼트 선택
platform = st.session_state.an_platform
current_seg = st.session_state.an_selected_segment

if platform == "steam":
    seg_names = [
        "0. 휴면 구매자", "1. 장기 몰입형 휴식자", "2. 조용한 꾸준 플레이어", "3. 하드코어 몰입형 분석가",
        "4. 간헐적 만족 플레이어", "5. 구매 후 실망 이탈후보", "6. 영향력 높은 선별 비평가", "7. 충성도 높은 몰입 비평가"
    ]
    rows = [st.columns(4), st.columns(4)]
else: # YouTube
    seg_names = [
        "0. 수동적 세계관 여행자", "1. 과몰입 서사 덕후", "2. 엄격한 성능 감별사", 
        "3. 소수 정예 길마", "4. 진심 모드 장인", "5. 조용한 충성 고수"
    ]
    rows = [st.columns(6)]

st.write("") 

for i, name in enumerate(seg_names):
    if platform == "steam":
        row_idx = i // 4
        col_idx = i % 4
    else:
        row_idx = 0
        col_idx = i
        
    with rows[row_idx][col_idx]:
        label = name
        btn_type = "primary" if current_seg == i else "secondary"
        if st.button(label, key=f"seg_btn_{i}", type=btn_type, use_container_width=True):
            st.session_state.an_selected_segment = i
            st.rerun()

st.divider()

# -----------------------------------------------------------------------------
# 5. 콘텐츠 렌더링
# -----------------------------------------------------------------------------
json_path = os.path.join("data", "insights", f"{platform}_persona.json")
full_data = load_json(json_path)

seg_data = None
if full_data and "segments" in full_data:
    for seg in full_data["segments"]:
        if seg.get("segment_id") == current_seg:
            seg_data = seg
            break

# 레이아웃: [좌] 차트 모음 / [우] 텍스트 설명
c_radar, c_text = st.columns([1.2, 1.8])

# [Left Column] 차트 영역
with c_radar:
    # 1. 레이더 차트
    img_prefix = "08_radar_seg_" if platform == "steam" else "04_radar_"
    img_path = get_image_path(platform, f"{img_prefix}{current_seg}")
    if img_path:
        st.image(img_path, caption=f"{platform.upper()} - Segment {current_seg} Radar", use_container_width=True)
    else:
        st.container(border=True, height=400).write(f"이미지 없음: {img_prefix}{current_seg}")

    st.write("")
    st.write("")
    st.markdown("##### 📊 상세 지표 분석")
    

    # 2. Top Topics 이미지 (추가된 부분)
    if platform == "steam":
        topic_img = f"top_topic_segment_{current_seg}.png"
    else:
        topic_img = f"02_2_top_topics_per_segment_{current_seg}.png"
        
    path_topic = get_image_path(platform, topic_img)
    if path_topic:
        st.image(path_topic, caption="Top Topics per Segment", use_container_width=True)
    else:
        st.container(border=True, height=200).write(f"[이미지 필요]\n{topic_img}")


    st.write("")
    
    # 3. Topic Lift 이미지
    lift_img = f"02_3_topic_lift_segment_{current_seg}.png"
    path = get_image_path(platform, lift_img)
    if path:
        st.image(path, caption="Topic Lift Analysis", use_container_width=True)
    else:
        st.container(border=True, height=200).write(f"[이미지 필요] {lift_img}")

    st.write("") 

    # 4. Topdiff Mirror 이미지
    mirror_img = f"12_topdiff_mirror_segment_{current_seg}.png" if platform == "steam" else f"09_topdiff_mirror_segment_{current_seg}.png"
    path = get_image_path(platform, mirror_img)
    if path:
        st.image(path, caption="Topdiff Mirror Analysis", use_container_width=True)
    else:
        st.container(border=True, height=200).write(f"[이미지 필요] {mirror_img}")


# [Right Column] 텍스트 설명 영역
with c_text:
    if seg_data:
        profile = seg_data.get("persona_profile", {})
        
        # 1. 페르소나 이름
        st.markdown(f"<div class='persona-title'>{profile.get('persona_name', 'N/A')}</div>", unsafe_allow_html=True)
        
        # 2. 인스타 감성 해시태그 (#우선순위 #수익화)
        priority = profile.get('target_priority', '-')
        money = profile.get('monetization_potential', '-')
        
        st.markdown(f"""
        <div style='margin-bottom: 10px;'>
            <span class='hashtag-badge'>#우선순위: {priority}</span>
            <span class='hashtag-badge'>#수익화: {money}</span>
        </div>
        """, unsafe_allow_html=True)

        # 3. 한줄 요약
        one_liner = profile.get('one_liner', '')
        if one_liner:
            st.markdown(f"<div class='persona-one-liner'>💡 {one_liner}</div>", unsafe_allow_html=True)
        
        # 4. 탭 구성 (상세 설명 탭 추가)
        tab1, tab2, tab3, tab4 = st.tabs(["📝 특징", "📖 상세 설명", "🎯 니즈/페인포인트", "✅ 액션 플랜"])
        
        with tab1:
            st.markdown("**주요 특징**")
            for char in profile.get('key_characteristics', []):
                st.markdown(f"- {char}")
            # 기존 하단의 description은 tab2로 이동

        with tab2:
            st.markdown("**📝 세그먼트 상세 설명**")
            st.write(profile.get('description', '설명 데이터가 없습니다.'))

        with tab3:
            # 좌우 분할 (Needs / Pain Points)
            c_needs, c_pains = st.columns(2)
            with c_needs:
                st.markdown("**Needs (니즈)**")
                for item in profile.get('needs', []):
                    st.markdown(f"- {item}")
            with c_pains:
                st.markdown("**Pain Points (불만)**")
                for item in profile.get('pain_points', []):
                    st.markdown(f"- {item}")

        with tab4:
            st.markdown("**Recommended Actions**")
            for action in profile.get('recommended_actions', []):
                st.markdown(f"- {action}")
        
        st.divider()

        # 5. 대표 댓글 (탭 외부 하단 고정)
        st.markdown("<div class='comment-header'>🗣️ 대표 댓글 (Voice of User)</div>", unsafe_allow_html=True)
        
        # JSON 구조: segment -> evidence_refs -> evidence_type == 'quote' -> value
        evidence_list = profile.get('evidence_refs', [])
        
        # evidence_type이 'quote'인 것만 필터링
        quotes = [e for e in evidence_list if e.get('evidence_type') == 'quote']
        
        if quotes:
            for q in quotes:
                # 댓글 내용 (value 키 사용)
                content = q.get('value', '')
                if content:
                    content = re.sub(r'~~(.*?)~~', r'<del>\1</del>', content)
                    st.markdown(f"<div class='comment-box'>“{content}”</div>", unsafe_allow_html=True)
        else:
            st.caption("이 세그먼트에 등록된 대표 댓글이 없습니다.")

    else:
        st.warning(f"Segment {current_seg}에 대한 JSON 데이터가 없습니다.")