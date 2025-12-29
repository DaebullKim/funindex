import streamlit as st
import streamlit.components.v1 as components

st.markdown("""
<style>
    /* 본문 영역(Main Container)의 여백을 0에 가깝게 줄임 */
    .block-container {
        padding-top: 5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;  /* 왼쪽 여백 축소 */
        padding-right: 1rem !important; /* 오른쪽 여백 축소 */
        max-width: 100% !important;     /* 전체 너비 사용 */
    }
</style>
""", unsafe_allow_html=True)

col_main, col_sub, col_empty = st.columns([4, 2, 5.3])

with col_main:
    st.title("[랭킹] 유통 플랫폼")

with col_sub:
    st.markdown(
        """
        <div style='
            text-align: right; 
            padding-top: 50px;       /* 1. 타이틀과 높이(Baseline) 맞추기 위해 살짝 늘림 */
            padding-right: 10px;     /* 2. 불필요한 오른쪽 여백 축소 (40px -> 10px) */
            color: black; 
            font-size: 1.2rem;       /* 3. 글자 크기 축소 (2rem은 너무 큽니다 -> 1.2~1.5rem 추천) */
            font-weight: bold;
            white-space: nowrap;     /* 4. [핵심] 절대 줄바꿈 하지 마라! (강제 명령) */
            margin-bottom: 0px;      /* 5. 아래 임베딩과 딱 붙게 하단 여백 제거 */
        '>
            ☟하단 버튼 클릭시 변경☟
        </div>
        """, 
        unsafe_allow_html=True
    )

with col_empty:
    # 3. 오른쪽: 그냥 비워둠 (이게 있어야 글자가 오른쪽 끝으로 안 도망감)
    st.empty()

tableau_embed_code = """
<div class='tableauPlaceholder' id='viz1766910300482' style='position: relative'><noscript><a href='#'><img alt='랭킹 대시보드 ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;00&#47;00_1_17669102682340&#47;sheet6&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='00_1_17669102682340&#47;sheet6' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;00&#47;00_1_17669102682340&#47;sheet6&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='ko-KR' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1766910300482');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='1600px';vizElement.style.height='927px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='1600px';vizElement.style.height='927px';} else { vizElement.style.width='100%';vizElement.style.height='1627px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
"""

# HTML 렌더링
components.html(tableau_embed_code, width=1650, height=970, scrolling=True)