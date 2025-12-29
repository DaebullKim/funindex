import streamlit as st
import streamlit.components.v1 as components

#st.title("[KPI] STEAM 상위 랭킹")
#st.subheader("우측 게임명/아이콘 클릭시 변경")
#st.text("우측 게임명/아이콘 클릭시 변경")
#st.caption("우측 게임명/아이콘 클릭시 변경")

st.markdown("""
<style>
    .block-container {
        padding-top: 5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;  
        padding-right: 1rem !important; 
        max-width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("[KPI] STEAM 상위 랭킹")

st.markdown("""
<div style='
    background-color: #f0f2f6;
    padding: 15px 20px;
    border-radius: 10px;
    border-left: 5px solid #ff4b4b;
    margin-bottom: 20px;
    font-size: 1rem;
    color: #31333F !important;
'>
    <span style='font-weight: bold;'>KPI 대시보드 활용 가이드</span><br>
    우측 랭킹 리스트에서 <b>게임명</b>이나 <b>아이콘</b>을 클릭하면 좌측의 상세 데이터가 해당 게임으로 변경됩니다.<br>
    선택한 게임의 <b>KPI 지표, CCU(동시접속자) 추이, 주제별 긍/부정 비율, 감정 키워드 워드클라우드</b>를 한눈에 확인할 수 있습니다.
    <ul>
        <li><b>KPI & CCU:</b> 핵심 성과 지표와 동시 접속자 추이를 통해 게임의 현재 흥행도를 진단합니다.</li>
        <li><b>긍/부정 비율 & 워드클라우드:</b> 유저들의 <b>실제 여론</b>을 시각화하여, <br>
            데이터 너머의 <b>구체적인 불만 요소</b>와 <b>핵심 칭찬 포인트</b>를 즉각적으로 파악하고 운영 전략에 반영할 수 있습니다.</li>
    </ul>
    우측 하단의 전체 화면에서 보기로 확대 가능.
</div>
""", unsafe_allow_html=True)

st.markdown(
        """
        <div style='
            text-align: right; 
            padding-top: 0px;       /* 1. 타이틀과 높이(Baseline) 맞추기 위해 살짝 늘림 */
            padding-right: 10px;     /* 2. 불필요한 오른쪽 여백 축소 (40px -> 10px) */
            color: black; 
            font-size: 1.2rem;       /* 3. 글자 크기 축소 (2rem은 너무 큽니다 -> 1.2~1.5rem 추천) */
            font-weight: bold;
            white-space: nowrap;     /* 4. [핵심] 절대 줄바꿈 하지 마라! (강제 명령) */
            margin-bottom: 0px;      /* 5. 아래 임베딩과 딱 붙게 하단 여백 제거 */
        '>
            ☟하단 게임명 클릭 시 게임 변경
        </div>
        """, 
        unsafe_allow_html=True
    )

tableau_embed_code = """
<div class='tableauPlaceholder' id='viz1766910297801' style='position: relative'><noscript><a href='#'><img alt='ㄹㅇ리얼대시보드ㄹㅇ ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;04&#47;04__1227_col&#47;sheet9&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='04__1227_col&#47;sheet9' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;04&#47;04__1227_col&#47;sheet9&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='ko-KR' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1766910297801');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='1600px';vizElement.style.height='927px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='1600px';vizElement.style.height='927px';} else { vizElement.style.width='100%';vizElement.style.height='1877px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
"""

# HTML 렌더링
components.html(tableau_embed_code, width=1650, height=970, scrolling=True)