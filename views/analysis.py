import streamlit as st
import json
import os
import re


# 1. CSS 스타일링
st.markdown("""
<style>
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        white-space: normal !important;
        height: auto !important;
        min-height: 40px !important;
        padding: 2px 5px !important;
        line-height: 1.2 !important;
        font-size: 14px !important;
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
    .hashtag-badge {
        background-color: #fceceb;
        color: #d93025;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-right: 8px;
        display: inline-block;
        margin-bottom: 10px;
    }
    .comment-box {
        background-color: #444; 
        color: #fff;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        font-style: italic;
        font-size: 1.0rem;
        border-left: 5px solid #FF4B4B;
        text-align: center; /* 댓글 내용 중앙 정렬 */
    }
    .centered-header {
        text-align: center;
        font-weight: bold;
        font-size: 1.5rem;
        margin-top: 30px;
        margin-bottom: 20px;
        border-top: 1px solid #eee;
        padding-top: 30px;
    }
    .graph-header {
        font-weight: bold;
        font-size: 1.3rem;
        margin-top: 40px;
        margin-bottom: 15px;
        padding-left: 10px;
        border-left: 5px solid #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)

st.title("[고객 유형] 세그먼트 분석")


# 2. 유틸리티 함수
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

# 3. 상태 관리
if "an_platform" not in st.session_state:
    st.session_state.an_platform = "steam"
if "an_selected_segment" not in st.session_state:
    st.session_state.an_selected_segment = 0 


# 4. 화면 구성 로직 (버튼 및 선택)

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
        "0. 확산주도", "1. 비판/불만", "2. 공감/지지", 
        "3. 관망/탐색", "4. 팬덤/옹호", "5. 기타"
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


# 5. 콘텐츠 렌더링
json_path = os.path.join("data", "insights", f"{platform}_persona.json")
full_data = load_json(json_path)

# 데이터 준비
seg_data = None
profile = {}

if full_data and "segments" in full_data:
    for seg in full_data["segments"]:
        if seg.get("segment_id") == current_seg:
            seg_data = seg
            profile = seg_data.get("persona_profile", {})
            break

if not seg_data:
    st.warning(f"Segment {current_seg}에 대한 JSON 데이터가 없습니다.")
    st.stop()


# 1순위: 상단 영역 (레이더 차트 + 설명)
c_radar, c_info = st.columns([1.3, 1.7])

with c_radar:
    # 레이더 차트 (좌측)
    img_prefix = "08_radar_seg_" if platform == "steam" else "04_radar_"
    img_path = get_image_path(platform, f"{img_prefix}{current_seg}")
    if img_path:
        st.image(img_path, caption=f"{platform.upper()} - Segment {current_seg} Radar", use_container_width=True)
    else:
        st.container(border=True, height=400).write(f"이미지 없음: {img_prefix}{current_seg}")

with c_info:
    # 설명들 (우측)
    # 1. 이름
    st.markdown(f"<div class='persona-title'>{profile.get('persona_name', 'N/A')}</div>", unsafe_allow_html=True)
    
    # 2. 해시태그
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
    
    # 4. 탭
    tab1, tab2, tab3, tab4 = st.tabs(["📝 특징", "📖 상세 설명", "🎯 니즈/페인포인트", "✅ 액션 플랜"])
    
    with tab1:
        st.markdown("**주요 특징**")
        for char in profile.get('key_characteristics', []):
            st.markdown(f"- {char}")
    
    with tab2:
        st.markdown("**📝 세그먼트 상세 설명**")
        st.write(profile.get('description', '설명 데이터가 없습니다.'))

    with tab3:
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


# 2순위: 대표 댓글 (중앙)
st.markdown("<div class='centered-header'>🗣️ 대표 댓글 (Voice of User)</div>", unsafe_allow_html=True)

evidence_list = profile.get('evidence_refs', [])
quotes = [e for e in evidence_list if e.get('evidence_type') in ['quote', 'quite']]

if quotes:
    # 댓글 여러 개일 경우 grid 사용 여부는 선택 (여기선 1열로 큼직하게)
    for q in quotes:
        content = q.get('value', '')
        if content:
            # 취소선 처리
            content = re.sub(r'~~(.*?)~~', r'<del>\1</del>', content)
            st.markdown(f"<div class='comment-box'>“{content}”</div>", unsafe_allow_html=True)
else:
    st.info("이 세그먼트에 등록된 대표 댓글이 없습니다.")


# 3, 4, 5순위: 상세 지표 그래프 (하단 나열)
st.write("")
st.markdown("### 📊 상세 지표 분석")

# 3순위: Top Topics
st.markdown("<div class='graph-header'>1. 주요 토픽 (Top Topics)</div>", unsafe_allow_html=True)
if platform == "steam":
    topic_img = f"top_topic_segment_{current_seg}.png"
else:
    topic_img = f"02_2_top_topics_per_segment_{current_seg}.png"

path_topic = get_image_path(platform, topic_img)
if path_topic:
    st.image(path_topic, use_container_width=True)
else:
    st.error(f"이미지 없음: {topic_img}")


# 4순위: Topic Lift
st.markdown("<div class='graph-header'>2. 토픽 리프트 (Topic Lift)</div>", unsafe_allow_html=True)
lift_img = f"02_3_topic_lift_segment_{current_seg}.png"
path_lift = get_image_path(platform, lift_img)
if path_lift:
    st.image(path_lift, use_container_width=True)
else:
    st.error(f"이미지 없음: {lift_img}")


# 5순위: Topdiff Mirror
st.markdown("<div class='graph-header'>3. 긍/부정 비교 (Topdiff Mirror)</div>", unsafe_allow_html=True)
mirror_img = f"12_topdiff_mirror_segment_{current_seg}.png" if platform == "steam" else f"09_topdiff_mirror_segment_{current_seg}.png"
path_mirror = get_image_path(platform, mirror_img)
if path_mirror:
    st.image(path_mirror, use_container_width=True)
else:
    st.error(f"이미지 없음: {mirror_img}")