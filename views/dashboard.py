import streamlit as st
import streamlit.components.v1 as components

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

st.title("[랭킹] 유통 플랫폼")
    
st.markdown("""
<div style='
    background-color: #f0f2f6;      /* 연한 회색 배경 */
    padding: 15px 20px;             /* 안쪽 여백 */
    border-radius: 10px;            /* 둥근 모서리 */
    border-left: 5px solid #ff4b4b; /* 왼쪽 빨간색 포인트 선 */
    margin-bottom: 10px;            /* 아래쪽 여백 */
    font-size: 1rem;                /* 글자 크기 */
    color: #31333F;                 /* 글자 색상 */
'>
    <span style='font-weight: bold;'>대시보드 활용 가이드</span><br>
    이 대시보드는 <b>Steam</b>과 <b>Mobile</b> 플랫폼의 유통 랭킹을 시각화하여 보여줍니다.<br>
    상단의 탭을 전환하여 플랫폼별 데이터를 확인하고, 하단 리스트를 클릭하여 상세 정보를 확인하세요.<br>
    <ul>
        <li>원본 점수 : 1위 100점 ~ 20위 5점<br></li>
        <li><b>점수 : 랭킹에 들어온 횟수 x 원본 점수 <br></li>
    </ul>
    <span style='font-size: 0.9rem; color: #555;'>대시보드 우측 하단의 <전체 화면에서 보기>로 확대 보기 가능.</span>
</div>
""", unsafe_allow_html=True)


st.markdown(
        """
        <div style='
            text-align: center; 
            padding-top: 0px;       
            padding-right: 10px;     
            color: black; 
            font-size: 1.2rem;       
            font-weight: bold;
            white-space: nowrap;     
            margin-bottom: 0px;      
        '>
            ☟하단 탭 클릭 시 랭킹, 플랫폼 변경☟
        </div>
        """, 
        unsafe_allow_html=True
    )    


tableau_embed_code = """
<div class='tableauPlaceholder' id='viz1766910300482' style='position: relative'><noscript><a href='#'><img alt='랭킹 대시보드 ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;00&#47;00_1_17669102682340&#47;sheet6&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='00_1_17669102682340&#47;sheet6' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;00&#47;00_1_17669102682340&#47;sheet6&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='ko-KR' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1766910300482');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='1600px';vizElement.style.height='927px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='1600px';vizElement.style.height='927px';} else { vizElement.style.width='100%';vizElement.style.height='1627px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
"""

# HTML 렌더링
components.html(tableau_embed_code, width=1650, height=970, scrolling=True)