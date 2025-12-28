import streamlit as st
import json
import os

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
        font-size: 1.5rem;
        margin-bottom: 10px;
    }
    .persona-one-liner {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        font-weight: 500;
        margin-bottom: 20px;
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
    seg_count = 8
    seg_names = [
        "휴면 구매자", "장기 몰입형 휴식자", "조용한 꾸준 플레이어", "하드코어 몰입형 분석가",
        "간헐적 만족 플레이어", "구매 후 실망 이탈후보", "영향력 높은 선별 비평가", "충성도 높은 몰입 비평가"
    ]
else: # YouTube
    seg_count = 6
    seg_names = [
        "수동적 세계관 여행자", "과몰입 서사 덕후", "엄경한 성능 감별사", 
        "소수 정예 길마", "진심 모드 장인", "조용한 충성 고수"
    ]

st.write("") 
cols = st.columns(seg_count)
for i in range(seg_count):
    with cols[i]:
        label = seg_names[i] if i < len(seg_names) else f"Seg {i}"
        
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

# 레이아웃: [좌] 차트 모음 (레이더 + 상세지표) / [우] 텍스트 설명
c_radar, c_text = st.columns([1.2, 1.8])

# [Left Column] 차트 영역
with c_radar:
    # 1. 레이더 차트 + 그래프
    img_prefix = "08_radar_seg_" if platform == "steam" else "04_radar_"
    img_path = get_image_path(platform, f"{img_prefix}{current_seg}")
    if img_path:
        st.image(img_path, caption=f"{platform.upper()} - Segment {current_seg} Radar", use_container_width=True)
    else:
        st.container(border=True, height=400).write(f"이미지 없음: {img_prefix}{current_seg}")
    st.write("")
    st.write("")
    st.markdown("##### 📊 상세 지표 분석") # 구분감 있게 헤더 추가
    
    # 2. Topic Lift 이미지
    lift_img = f"02_3_topic_lift_segment_{current_seg}.png"
    path = get_image_path(platform, lift_img)
    if path:
        st.image(path, caption="Topic Lift Analysis", use_container_width=True)
    else:
        st.container(border=True, height=200).write(f"[이미지 필요] {lift_img}")

    st.write("") # 간격

    # 3. Topdiff Mirror 이미지
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
        st.markdown(f"<div class='persona-title'>{profile.get('persona_name', 'N/A')}</div>", unsafe_allow_html=True)
        one_liner = profile.get('one_liner', '')
        if one_liner:
            st.markdown(f"<div class='persona-one-liner'>💡 {one_liner}</div>", unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["📝 특징", "🎯 니즈/페인포인트", "✅ 액션 플랜"])
        with tab1:
            st.markdown("**주요 특징**")
            for char in profile.get('key_characteristics', []):
                st.markdown(f"- {char}")
            st.caption(profile.get('description', ''))
        with tab2:
            st.markdown("**Needs (니즈)**")
            for item in profile.get('needs', []):
                st.markdown(f"- {item}")
            st.markdown("**Pain Points (불만)**")
            for item in profile.get('pain_points', []):
                st.markdown(f"- {item}")
        with tab3:
            st.markdown("**Recommended Actions**")
            for action in profile.get('recommended_actions', []):
                st.markdown(f"- {action}")
            st.markdown("---")
            st.write(f"**우선순위:** {profile.get('target_priority', '-')}")
            st.write(f"**수익화 잠재력:** {profile.get('monetization_potential', '-')}")
    else:
        st.warning(f"Segment {current_seg}에 대한 JSON 데이터가 없습니다.")