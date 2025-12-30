import streamlit as st
import os
import base64

def render_clickable_image(image_path, caption, key_name):
    # 1. 현재 탭과 일치하는지 확인 (선택 여부)
    is_selected = (st.session_state.home_selected_tab == key_name)
    # CSS 클래스 결정
    class_name = "nav-card active" if is_selected else "nav-card"
    
    # 이미지 소스 처리
    if image_path.startswith("http"):
        img_src = image_path
    else:
        if os.path.exists(image_path):
            with open(image_path, "rb") as f:
                data = f.read()
                encoded = base64.b64encode(data).decode()
            img_src = f"data:image/png;base64,{encoded}"
        else:
            # 파일 없으면 플레이스홀더
            img_src = f"https://placehold.co/400x300/png?text={caption}"

    # HTML 생성
    html_code = f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <div class="{class_name}">
            <img src="{img_src}" style="width: 100%; display: block; object-fit: cover;">
        </div>
        <div class="nav-text">
            {caption}
        </div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

def get_img_path(filename):
    path = os.path.join("data", "images", filename)
    if os.path.exists(path):
        return path
    else:
        return f"https://placehold.co/400x300/png?text={filename}"

# 1. 초기 상태 설정 (현재 선택된 탭 관리)
if "home_selected_tab" not in st.session_state:
    st.session_state.home_selected_tab = "ranking"  # 기본값: 랭킹 탭

# 탭 선택 변경 함수
def set_tab(tab_name):
    st.session_state.home_selected_tab = tab_name

# 2. CSS 스타일링 (카드 디자인 및 버튼)
st.markdown("""
<style>
    /* 네비게이션 이미지 카드 */
    .nav-card {
        border-radius: 15px;
        overflow: hidden;
        transition: all 0.3s ease; /* 부드러운 전환 */
        
        /* 기본 상태: 어둡고, 흑백이고, 작음 */
        border: 4px solid transparent;
        opacity: 0.6;
        filter: grayscale(100%);
        transform: scale(1.0);
    }

    /* 마우스 Hover - 선택 안 된 것만 반응 */
    .nav-card:not(.active):hover {
        opacity: 0.85;           /* 조금 더 밝게 */
        filter: grayscale(40%);  /* 색이 살짝 돔 */
        transform: scale(1.02);  /* 살짝 커짐 */
        cursor: pointer;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }

    /* 선택된 상태 - 가장 밝고 큼 + 빨간 테두리 */
    .nav-card.active {
        opacity: 1.0;            /* 완전 선명 */
        filter: grayscale(0%);   /* 완전 컬러 */
        transform: scale(1.05);  /* 가장 큼 */
        
        border: 4px solid #ff4b4b;
        box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.4);
    }

    /* 텍스트 스타일 */
    .nav-text {
        text-align: center;
        margin-top: 8px;
        font-size: 1rem;
        transition: all 0.3s ease;
        color: #777;
    }
    .nav-card.active + .nav-text { /* 이미지가 active일 때 형제 텍스트 */
        color: #ff4b4b;
        font-weight: bold;
    }
    /* 설명 박스 스타일 (카드) */
    .info-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        margin-top: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .info-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #31333F;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
    .info-content li {
        margin-bottom: 8px;
        font-size: 1rem;
        color: #555;
    }
    /* 버튼 꽉 차게 */
    div.stButton > button {
        width: 100%;
        border-radius: 20px; /* 알약 모양 */
        height: 50px;
    }
</style>
""", unsafe_allow_html=True)

st.title("게임 재미 분석 플랫폼")
st.markdown('''
<div class="sub-desc">
    데이터 기반의 <b>랭킹 분석</b>부터 <b>AI 페르소나 진단</b>, <b>맞춤형 게임 추천</b>까지.<br>
    게임의 흥행 요소를 다각도로 분석하여 성공적인 개발과 운영 전략을 지원하는 통합 솔루션입니다.
</div>
''', unsafe_allow_html=True)
st.divider()

# 3. 상단 이미지 영역
col_img1, col_img2, col_img3, col_img4 = st.columns(4)

img_files = {
    "ranking": "trophy.png",
    "kpi": "graph.png",
    "segment": "people.png",
    "rag": "chip2.png"
}

def get_img_path(filename):
    return os.path.join("data", "images", filename)

# 이미지 찐빠 방지
def get_img_path(filename):
    path = os.path.join("data", "images", filename)
    # 파일이 있으면 경로 반환, 없으면 임시 이미지 URL 반환
    if os.path.exists(path):
        return path
    else:
        return f"https://placehold.co/400x300/png?text={filename}"

with col_img1:
    render_clickable_image(get_img_path(img_files["ranking"]), "유통 플랫폼 랭킹", "ranking")

with col_img2:
    render_clickable_image(get_img_path(img_files["kpi"]), "STEAM 심층 분석", "kpi")

with col_img3:
    render_clickable_image(get_img_path(img_files["segment"]), "고객 세그먼트", "segment")

with col_img4:
    render_clickable_image(get_img_path(img_files["rag"]), "AI 추천 시스템", "rag")
    
st.write("")

# 4. 중간 탭 버튼 영역
current = st.session_state.home_selected_tab

c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("[랭킹] 유통 플랫폼", 
                 type="primary" if current == "ranking" else "secondary", 
                 use_container_width=True):
        set_tab("ranking")
        st.rerun()

with c2:
    if st.button("[KPI] STEAM 상위 랭킹", 
                 type="primary" if current == "kpi" else "secondary", 
                 use_container_width=True):
        set_tab("kpi")
        st.rerun()

with c3:
    if st.button("[고객 유형] 세그먼트", 
                 type="primary" if current == "segment" else "secondary", 
                 use_container_width=True):
        set_tab("segment")
        st.rerun()

with c4:
    if st.button("[추천] LLM RAG", 
                 type="primary" if current == "rag" else "secondary", 
                 use_container_width=True):
        set_tab("rag")
        st.rerun()

# 5. 하단 설명 영역 (동적 렌더링)
content_data = {
    "ranking": {
        "title": "유통 플랫폼 랭킹 대시보드",
        "comp": [
            "<b>Steam vs Mobile 통합 랭킹:</b> 주요 플랫폼의 실시간 인기 게임 순위를 비교합니다.",
            "<b>점수 기반 정렬:</b> 단순 랭킹이 아닌, 복합 점수를 기반으로 한 진성 인기 순위를 제공합니다.",
            "<b>국가별 차트:</b> 주요 국가(KR, JP, CN, US 등)의 트렌드를 국기 아이콘과 함께 직관적으로 파악합니다."
        ],
        "usage": [
            "현재 시장을 지배하고 있는 경쟁작들의 리스트를 빠르게 스캐닝하세요.",
            "원본 랭킹과 자체 산정 점수 랭킹을 비교하여 <b>'숨겨진 알짜 게임'</b>을 발굴할 수 있습니다.",
            "Steam과 Mobile 간의 장르적 트렌드 차이를 분석하여 플랫폼 전략을 수립하세요."
        ]
    },
    "kpi": {
        "title": "STEAM 상위 랭킹 심층 KPI 분석",
        "comp": [
            "<b>핵심 지표(KPI):</b> 장르, 추천율, 이탈률, 재미지수 등 게임의 건강 상태를 나타내는 지표 시각화.",
            "<b>CCU(동시접속자) 추이:</b> 출시 이후 현재까지의 트래픽 변동 그래프.",
            "<b>Voice of User:</b> 워드클라우드 및 긍/부정 비율 차트를 통한 여론 분석."
        ],
        "usage": [
            "우측 리스트에서 경쟁 게임을 클릭하여 상세 데이터를 조회하세요.",
            "<b>워드클라우드</b>를 통해 유저들이 <b>열광</b>하는 포인트와 <b>불만 요소</b>를 키워드로 파악하세요.",
            "<b>CCU 그래프</b>의 꺾이는 지점과 업데이트 이력을 대조하여 운영 성과를 측정할 수 있습니다."
        ]
    },
    "segment": {
        "title": "고객 유형(Persona) 세그먼트 분석",
        "comp": [
            "<b>8가지 페르소나 분류:</b> 유저 행동 패턴에 기반한 8가지 상세 고객 군집(Cluster) 정의.",
            "<b>Radar Chart:</b> 각 그룹의 성향(전투, 소셜, 탐험 등)을 방사형 그래프로 비교.",
            "<b>상세 프로필 카드:</b> 그룹별 니즈(Needs), 페인포인트(Pain Points), 추천 액션 플랜 제공."
        ],
        "usage": [
            "우리 게임의 타겟 유저층이 어떤 페르소나에 해당하는지 확인하세요.",
            "<b>'이탈 위험군'</b>이나 <b>'충성 고객군'</b>을 클릭하여 그들의 구체적인 불만 사항과 특징을 파악하세요.",
            "각 <b>페르소나</b>별 맞춤형 마케팅 및 업데이트 전략을 수립하는 데 활용하세요."
        ]
    },
    "rag": {
        "title": "LLM RAG 기반 게임 추천 시스템",
        "comp": [
            "<b>팀 역량 입력 패널:</b> 기획, 아트, 클라이언트 등 팀별 보유 역량 점수화 (1~5점).",
            "<b>Vector Search 엔진:</b> 입력된 역량과 가장 유사한 성공 방정식을 가진 게임 탐색.",
            "<b>Generative AI 분석:</b> LLM이 실제 리뷰 데이터를 분석하여 우리 팀에 딱 맞는 조언 생성."
        ],
        "usage": [
            "현재 우리 개발팀의 강점과 약점을 슬라이더로 입력하세요.",
            "AI가 추천하는 <b>'성공 가능성이 높은 장르'</b>와 <b>'벤치마킹 대상 게임'</b>을 확인하세요.",
            "단순 추천을 넘어, <i>'왜 이 게임이 우리 팀과 맞는지'</i>에 대한 AI의 상세한 근거를 참고하세요."
        ]
    }
}

# 선택된 데이터 가져오기
selected_data = content_data[current]

# 화면 그리기 (2단 컬럼 구성)
st.write("")
st.markdown(f"### {selected_data['title']}")

col_desc1, col_desc2 = st.columns(2)

# [좌측] 대시보드 구성
with col_desc1:
    comp_html = "".join([f"<li>{item}</li>" for item in selected_data['comp']])
    st.markdown(f"""
    <div class='info-card'>
        <div class='info-title'>📊 대시보드 구성</div>
        <ul class='info-content' style='padding-left: 20px;'>
            {comp_html}
        </ul>
    </div>
    """, unsafe_allow_html=True)

# [우측] 활용 방법
with col_desc2:
    usage_html = "".join([f"<li>{item}</li>" for item in selected_data['usage']])
    st.markdown(f"""
    <div class='info-card'>
        <div class='info-title'>💡 활용 방법</div>
        <ul class='info-content' style='padding-left: 20px;'>
            {usage_html}
        </ul>
    </div>
    """, unsafe_allow_html=True)